"""Service for interacting with the Global Admin API."""

from collections.abc import AsyncIterator

from vclient.constants import DEFAULT_PAGE_LIMIT
from vclient.endpoints import Endpoints
from vclient.models import (
    Developer,
    DeveloperCreate,
    DeveloperUpdate,
    DeveloperWithApiKey,
    PaginatedResponse,
)
from vclient.services.base import BaseService


class GlobalAdminService(BaseService):
    """Service for global admin operations in the Valentina API.

    Provides methods to create, retrieve, update, and delete developer accounts,
    as well as manage API keys. Requires global admin privileges.

    Example:
        >>> async with VClient() as client:
        ...     developers = await client.global_admin.list_all()
        ...     developer = await client.global_admin.get("developer_id")
    """

    async def get_page(
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

    async def list_all(self, *, is_global_admin: bool | None = None) -> list[Developer]:
        """Retrieve all developer accounts.

        Automatically paginates through all results. Use `get_page()` for paginated access
        or `iter_all()` for memory-efficient streaming of large datasets.

        Args:
            is_global_admin: Optional filter by global admin status.

        Returns:
            A list of all Developer objects.
        """
        return [developer async for developer in self.iter_all(is_global_admin=is_global_admin)]

    async def iter_all(
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
            >>> async for developer in client.global_admin.iter_all():
            ...     print(developer.username)
        """
        params = {}
        if is_global_admin is not None:
            params["is_global_admin"] = is_global_admin

        async for item in self._iter_all_pages(
            Endpoints.ADMIN_DEVELOPERS,
            limit=limit,
            params=params if params else None,
        ):
            yield Developer.model_validate(item)

    async def get(self, developer_id: str) -> Developer:
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

    async def create(
        self,
        username: str,
        email: str,
        *,
        is_global_admin: bool = False,
    ) -> Developer:
        """Create a new developer account.

        This creates the account but does not create an API key or grant access to any
        companies. Be certain to generate an API key after account creation.

        Args:
            username: Developer username.
            email: Developer email address.
            is_global_admin: Whether the developer should have global admin privileges.

        Returns:
            The newly created Developer object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
            AuthorizationError: If you don't have global admin privileges.
        """
        body = self._validate_request(
            DeveloperCreate,
            username=username,
            email=email,
            is_global_admin=is_global_admin,
        )
        response = await self._post(
            Endpoints.ADMIN_DEVELOPERS,
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Developer.model_validate(response.json())

    async def update(
        self,
        developer_id: str,
        *,
        username: str | None = None,
        email: str | None = None,
        is_global_admin: bool | None = None,
    ) -> Developer:
        """Modify a developer account's properties.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            developer_id: The ID of the developer to update.
            username: New developer username.
            email: New developer email address.
            is_global_admin: New global admin status.

        Returns:
            The updated Developer object.

        Raises:
            NotFoundError: If the developer does not exist.
            AuthorizationError: If you don't have global admin privileges.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            DeveloperUpdate,
            username=username,
            email=email,
            is_global_admin=is_global_admin,
        )
        response = await self._patch(
            Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Developer.model_validate(response.json())

    async def delete(self, developer_id: str) -> None:
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
