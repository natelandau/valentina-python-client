"""Service for interacting with the Global Admin API."""

import re
from collections.abc import AsyncIterator, Sequence
from datetime import datetime

from vclient.constants import (
    DEFAULT_LOG_TAIL_LIMIT,
    DEFAULT_PAGE_LIMIT,
    MAX_LOG_TAIL_LIMIT,
    MIN_LOG_TAIL_LIMIT,
    AuditEntityType,
    AuditLogInclude,
    AuditOperation,
    LogLevel,
)
from vclient.endpoints import Endpoints
from vclient.models import (
    AuditLog,
    AuditLogDetail,
    Developer,
    DeveloperCreate,
    DeveloperUpdate,
    DeveloperWithApiKey,
    PaginatedResponse,
    ServerLogArchive,
    ServerLogEntry,
)
from vclient.services._audit_params import _build_audit_params
from vclient.services.base import BaseService

_CONTENT_DISPOSITION_FILENAME = re.compile(r'filename=(?:"([^"]+)"|([^;]+))', re.IGNORECASE)


def _filename_from_content_disposition(header: str | None, *, fallback: str) -> str:
    """Extract the attachment filename from a Content-Disposition header.

    Return ``fallback`` when the header is absent or contains no filename so callers
    always get a usable name for the downloaded archive.

    Args:
        header: The raw Content-Disposition header value, or None.
        fallback: Filename to return when none can be parsed.

    Returns:
        The parsed filename, or the fallback.
    """
    if not header:
        return fallback
    match = _CONTENT_DISPOSITION_FILENAME.search(header)
    if not match:
        return fallback
    return (match.group(1) or match.group(2)).strip()


class GlobalAdminService(BaseService):
    """Service for global admin operations in the Valentina API.

    Provides cross-company management of developer accounts and their API keys,
    plus server log access. Requires global admin privileges.

    Example:
        >>> async with VClient() as client:
        ...     developers = await client.global_admin.list_all_developers()
        ...     developer = await client.global_admin.get_developer("developer_id")
    """

    async def get_developer_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        is_global_admin: bool | None = None,
    ) -> PaginatedResponse[Developer]:
        """Retrieve a paginated page of developer accounts.

        Requires global admin privileges.

        Args:
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).
            is_global_admin: Optional filter by global admin status.

        Returns:
            A PaginatedResponse containing Developer objects and pagination metadata.
        """
        params = {"is_global_admin": is_global_admin} if is_global_admin is not None else None
        return await self._get_paginated_as(
            Endpoints.ADMIN_DEVELOPERS,
            Developer,
            limit=limit,
            offset=offset,
            params=params,
        )

    async def list_all_developers(self, *, is_global_admin: bool | None = None) -> list[Developer]:
        """Retrieve all developer accounts.

        Automatically paginates through all results. Use `get_developer_page()` for paginated
        access or `iter_all_developers()` for memory-efficient streaming of large datasets.

        Args:
            is_global_admin: Optional filter by global admin status.

        Returns:
            A list of all Developer objects.
        """
        return [
            developer
            async for developer in self.iter_all_developers(is_global_admin=is_global_admin)
        ]

    async def iter_all_developers(
        self,
        *,
        limit: int = 100,
        is_global_admin: bool | None = None,
    ) -> AsyncIterator[Developer]:
        """Iterate through all developer accounts.

        Yields individual developers, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            limit: Items per page (default 100 for efficiency).
            is_global_admin: Optional filter by global admin status.

        Yields:
            Individual Developer objects.

        Example:
            >>> async for developer in client.global_admin.iter_all_developers():
            ...     print(developer.username)
        """
        params = {}
        if is_global_admin is not None:
            params["is_global_admin"] = is_global_admin

        async for item in self._iter_all_pages(
            Endpoints.ADMIN_DEVELOPERS,
            limit=limit,
            params=params or None,
        ):
            yield Developer.model_validate(item)

    async def get_developer(self, developer_id: str) -> Developer:
        """Retrieve detailed information about a specific developer.

        Args:
            developer_id: The ID of the developer to retrieve.

        Returns:
            The Developer object with full details.

        Raises:
            NotFoundError: If the developer does not exist.
            AuthorizationError: If you don't have global admin privileges.
        """
        response = await self._get(Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id))
        return Developer.model_validate(response.json())

    async def create_developer(
        self,
        request: DeveloperCreate | None = None,
        **kwargs,
    ) -> Developer:
        """Create a new developer account.

        This creates the account but does not create an API key or grant access to any
        companies. Be certain to generate an API key after account creation.

        Args:
            request: A DeveloperCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for DeveloperCreate if request is not provided.
                Accepts: username (str, required), email (str, required),
                is_global_admin (bool, default False).

        Returns:
            The newly created Developer object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
            AuthorizationError: If you don't have global admin privileges.
        """
        body = request if request is not None else self._validate_request(DeveloperCreate, **kwargs)
        response = await self._post(
            Endpoints.ADMIN_DEVELOPERS,
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Developer.model_validate(response.json())

    async def update_developer(
        self,
        developer_id: str,
        request: DeveloperUpdate | None = None,
        **kwargs,
    ) -> Developer:
        """Modify a developer account's properties.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            developer_id: The ID of the developer to update.
            request: A DeveloperUpdate model, OR pass fields as keyword arguments.
            **kwargs: Fields for DeveloperUpdate if request is not provided.
                Accepts: username (str | None), email (str | None),
                is_global_admin (bool | None).

        Returns:
            The updated Developer object.

        Raises:
            NotFoundError: If the developer does not exist.
            AuthorizationError: If you don't have global admin privileges.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(DeveloperUpdate, **kwargs)
        response = await self._patch(
            Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Developer.model_validate(response.json())

    async def delete_developer(self, developer_id: str) -> None:
        """Remove a developer account from the system.

        The developer's API key will be invalidated immediately.

        Args:
            developer_id: The ID of the developer to delete.

        Raises:
            NotFoundError: If the developer does not exist.
            AuthorizationError: If you don't have global admin privileges.
        """
        await self._delete(Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id))

    async def create_api_key(self, developer_id: str) -> DeveloperWithApiKey:
        """Generate a new API key for a developer.

        Their current key will be immediately invalidated. Be certain to save the
        API key as it will not be displayed again.

        Args:
            developer_id: The ID of the developer to generate a key for.

        Returns:
            The Developer object with the new API key included.

        Raises:
            NotFoundError: If the developer does not exist.
            AuthorizationError: If you don't have global admin privileges.
        """
        response = await self._post(
            Endpoints.ADMIN_DEVELOPER_NEW_KEY.format(developer_id=developer_id)
        )
        return DeveloperWithApiKey.model_validate(response.json())

    async def get_audit_log_page(
        self,
        developer_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        company_id: str | None = None,
        acting_user_id: str | None = None,
        user_id: str | None = None,
        campaign_id: str | None = None,
        book_id: str | None = None,
        chapter_id: str | None = None,
        character_id: str | None = None,
        entity_type: AuditEntityType | None = None,
        operation: AuditOperation | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        include: Sequence[AuditLogInclude] | None = None,
    ) -> PaginatedResponse[AuditLog] | PaginatedResponse[AuditLogDetail]:
        """Retrieve a paginated page of audit log entries for a developer.

        Use filter parameters to narrow results by entity, operation, user, or time range.
        Pass ``include=["request_details"]`` to receive full HTTP request forensics in each
        entry (returns AuditLogDetail instead of AuditLog).

        Args:
            developer_id: The ID of the developer whose audit logs to retrieve.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).
            company_id: Filter by company ID.
            acting_user_id: Filter by the user who performed the action.
            user_id: Filter by the user affected by the action.
            campaign_id: Filter by campaign ID.
            book_id: Filter by book ID.
            chapter_id: Filter by chapter ID.
            character_id: Filter by character ID.
            entity_type: Filter by entity type (e.g., "CAMPAIGN", "CHARACTER").
            operation: Filter by operation type (CREATE, UPDATE, DELETE).
            date_from: Return logs on or after this datetime.
            date_to: Return logs on or before this datetime.
            include: Additional data to include. Pass ["request_details"] for HTTP forensics.

        Returns:
            A PaginatedResponse containing AuditLog (or AuditLogDetail) objects.

        Raises:
            NotFoundError: If the developer does not exist.
            AuthorizationError: If you don't have global admin privileges.
        """
        model = AuditLogDetail if include and "request_details" in include else AuditLog
        params = _build_audit_params(
            company_id=company_id,
            acting_user_id=acting_user_id,
            user_id=user_id,
            campaign_id=campaign_id,
            book_id=book_id,
            chapter_id=chapter_id,
            character_id=character_id,
            entity_type=entity_type,
            operation=operation,
            date_from=date_from,
            date_to=date_to,
            include=include,
        )
        return await self._get_paginated_as(
            Endpoints.ADMIN_DEVELOPER_AUDIT_LOGS.format(developer_id=developer_id),
            model,
            limit=limit,
            offset=offset,
            params=params,
        )

    async def list_all_audit_logs(
        self,
        developer_id: str,
        *,
        company_id: str | None = None,
        acting_user_id: str | None = None,
        user_id: str | None = None,
        campaign_id: str | None = None,
        book_id: str | None = None,
        chapter_id: str | None = None,
        character_id: str | None = None,
        entity_type: AuditEntityType | None = None,
        operation: AuditOperation | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        include: Sequence[AuditLogInclude] | None = None,
    ) -> list[AuditLog] | list[AuditLogDetail]:
        """Retrieve all audit log entries for a developer.

        Automatically paginates through all results. Use ``get_audit_log_page()`` for
        paginated access or ``iter_all_audit_logs()`` for memory-efficient streaming.

        Args:
            developer_id: The ID of the developer whose audit logs to retrieve.
            company_id: Filter by company ID.
            acting_user_id: Filter by the user who performed the action.
            user_id: Filter by the user affected by the action.
            campaign_id: Filter by campaign ID.
            book_id: Filter by book ID.
            chapter_id: Filter by chapter ID.
            character_id: Filter by character ID.
            entity_type: Filter by entity type (e.g., "CAMPAIGN", "CHARACTER").
            operation: Filter by operation type (CREATE, UPDATE, DELETE).
            date_from: Return logs on or after this datetime.
            date_to: Return logs on or before this datetime.
            include: Additional data to include. Pass ["request_details"] for HTTP forensics.

        Returns:
            A list of all AuditLog (or AuditLogDetail) objects.

        Raises:
            NotFoundError: If the developer does not exist.
            AuthorizationError: If you don't have global admin privileges.
        """
        return [
            log
            async for log in self.iter_all_audit_logs(
                developer_id,
                company_id=company_id,
                acting_user_id=acting_user_id,
                user_id=user_id,
                campaign_id=campaign_id,
                book_id=book_id,
                chapter_id=chapter_id,
                character_id=character_id,
                entity_type=entity_type,
                operation=operation,
                date_from=date_from,
                date_to=date_to,
                include=include,
            )
        ]

    async def iter_all_audit_logs(
        self,
        developer_id: str,
        *,
        limit: int = 100,
        company_id: str | None = None,
        acting_user_id: str | None = None,
        user_id: str | None = None,
        campaign_id: str | None = None,
        book_id: str | None = None,
        chapter_id: str | None = None,
        character_id: str | None = None,
        entity_type: AuditEntityType | None = None,
        operation: AuditOperation | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        include: Sequence[AuditLogInclude] | None = None,
    ) -> AsyncIterator[AuditLog] | AsyncIterator[AuditLogDetail]:
        """Iterate through all audit log entries for a developer.

        Yields individual audit log entries, automatically fetching subsequent pages
        until all matching entries have been retrieved.

        Args:
            developer_id: The ID of the developer whose audit logs to retrieve.
            limit: Items per page (default 100 for efficiency).
            company_id: Filter by company ID.
            acting_user_id: Filter by the user who performed the action.
            user_id: Filter by the user affected by the action.
            campaign_id: Filter by campaign ID.
            book_id: Filter by book ID.
            chapter_id: Filter by chapter ID.
            character_id: Filter by character ID.
            entity_type: Filter by entity type (e.g., "CAMPAIGN", "CHARACTER").
            operation: Filter by operation type (CREATE, UPDATE, DELETE).
            date_from: Return logs on or after this datetime.
            date_to: Return logs on or before this datetime.
            include: Additional data to include. Pass ["request_details"] for HTTP forensics.

        Yields:
            Individual AuditLog (or AuditLogDetail) objects.

        Raises:
            NotFoundError: If the developer does not exist.
            AuthorizationError: If you don't have global admin privileges.
        """
        model = AuditLogDetail if include and "request_details" in include else AuditLog
        params = _build_audit_params(
            company_id=company_id,
            acting_user_id=acting_user_id,
            user_id=user_id,
            campaign_id=campaign_id,
            book_id=book_id,
            chapter_id=chapter_id,
            character_id=character_id,
            entity_type=entity_type,
            operation=operation,
            date_from=date_from,
            date_to=date_to,
            include=include,
        )
        async for item in self._iter_all_pages(
            Endpoints.ADMIN_DEVELOPER_AUDIT_LOGS.format(developer_id=developer_id),
            limit=limit,
            params=params,
        ):
            yield model.model_validate(item)

    async def tail_logs(
        self,
        *,
        level: LogLevel | None = None,
        limit: int = DEFAULT_LOG_TAIL_LIMIT,
    ) -> list[ServerLogEntry]:
        """Tail the most recent server log entries, newest first.

        Inspect on-disk server logs without shelling into the host. Requires global
        admin privileges and that file logging is enabled on the server.

        Args:
            level: Minimum log level to include. Defaults to the server's configured
                level when omitted.
            limit: Maximum number of entries to return. Clamped to 1-500 (default 100).

        Returns:
            A list of ServerLogEntry objects, newest first.

        Raises:
            AuthorizationError: If you don't have global admin privileges.
            ConflictError: If file logging is not enabled on the server.
        """
        clamped_limit = min(max(limit, MIN_LOG_TAIL_LIMIT), MAX_LOG_TAIL_LIMIT)
        params = self._build_params(level=level, limit=clamped_limit)
        response = await self._get(Endpoints.ADMIN_LOGS, params=params)
        return [ServerLogEntry.model_validate(item) for item in response.json()]

    async def download_logs(self) -> ServerLogArchive:
        """Download a zip archive of the server log files.

        Stream the active log file plus rotated backups as a single zip. Requires
        global admin privileges and that file logging is enabled on the server.

        Returns:
            A ServerLogArchive with the server-provided filename and raw zip bytes.

        Raises:
            AuthorizationError: If you don't have global admin privileges.
            ConflictError: If file logging is not enabled or no log files exist.
        """
        response = await self._get(
            Endpoints.ADMIN_LOGS_DOWNLOAD, headers={"Accept": "application/zip"}
        )
        filename = _filename_from_content_disposition(
            response.headers.get("Content-Disposition"), fallback="vapi-logs.zip"
        )
        return ServerLogArchive(filename=filename, content=response.content)
