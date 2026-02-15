"""Service for interacting with the Companies API."""

from collections.abc import AsyncIterator

from vclient.constants import DEFAULT_PAGE_LIMIT, PermissionLevel
from vclient.endpoints import Endpoints
from vclient.models import (
    Company,
    CompanyCreate,
    CompanyPermissions,
    CompanyUpdate,
    NewCompanyResponse,
    PaginatedResponse,
    _GrantAccess,
)
from vclient.services.base import BaseService


class CompaniesService(BaseService):
    """Service for managing companies in the Valentina API.

    Provides methods to create, retrieve, update, and delete companies,
    as well as manage developer access permissions.

    Example:
        >>> async with VClient() as client:
        ...     companies = await client.companies.list()
        ...     company = await client.companies.get("company_id")
    """

    async def get_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[Company]:
        """Retrieve a paginated page of companies you have access to.

        Only companies where you have been granted at least user-level permissions are returned.

        Args:
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Company objects and pagination metadata.
        """
        return await self._get_paginated_as(
            Endpoints.COMPANIES,
            Company,
            limit=limit,
            offset=offset,
        )

    async def list_all(self) -> list[Company]:
        """Retrieve all companies you have access to.

        Automatically paginates through all results. Use `get_page()` for paginated access
        or `iter_all()` for memory-efficient streaming of large datasets.

        Returns:
            A list of all Company objects.
        """
        return [company async for company in self.iter_all()]

    async def iter_all(self, *, limit: int = 100) -> AsyncIterator[Company]:
        """Iterate through all companies you have access to.

        Yields individual companies, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Company objects.

        Example:
            >>> async for company in client.companies.iter_all():
            ...     print(company.name)
        """
        async for item in self._iter_all_pages(Endpoints.COMPANIES, limit=limit):
            yield Company.model_validate(item)

    async def get(self, company_id: str) -> Company:
        """Retrieve detailed information about a specific company.

        Fetches the company including its settings and configuration.

        Args:
            company_id: The ID of the company to retrieve.

        Returns:
            The Company object with full details.

        Raises:
            NotFoundError: If the company does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(Endpoints.COMPANY.format(company_id=company_id))
        return Company.model_validate(response.json())

    async def create(
        self,
        request: CompanyCreate | None = None,
        **kwargs,
    ) -> NewCompanyResponse:
        """Create a new company in the system.

        You are automatically granted OWNER permission for the new company, giving you
        full administrative control, including the ability to grant permissions to
        other developers.

        Args:
            request: A CompanyCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for CompanyCreate if request is not provided.
                Accepts: name (str, required), email (str, required),
                description (str | None), settings (CompanySettings | None).

        Returns:
            The newly created NewCompanyResponse object containing the company and admin user.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(CompanyCreate, **kwargs)
        response = await self._post(
            Endpoints.COMPANIES,
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return NewCompanyResponse.model_validate(response.json())

    async def update(
        self,
        company_id: str,
        request: CompanyUpdate | None = None,
        **kwargs,
    ) -> Company:
        """Modify a company's properties.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            company_id: The ID of the company to update.
            request: A CompanyUpdate model, OR pass fields as keyword arguments.
            **kwargs: Fields for CompanyUpdate if request is not provided.
                Accepts: name (str | None), email (str | None),
                description (str | None), settings (CompanySettings | None).

        Returns:
            The updated Company object.

        Raises:
            NotFoundError: If the company does not exist.
            AuthorizationError: If you don't have admin-level access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(CompanyUpdate, **kwargs)
        response = await self._patch(
            Endpoints.COMPANY.format(company_id=company_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Company.model_validate(response.json())

    async def delete(self, company_id: str) -> None:
        """Delete a company from the system.

        This is a destructive action that archives the company and all associated data.

        Args:
            company_id: The ID of the company to delete.

        Raises:
            NotFoundError: If the company does not exist.
            AuthorizationError: If you don't have owner-level access.
        """
        await self._delete(Endpoints.COMPANY.format(company_id=company_id))

    async def grant_access(
        self,
        company_id: str,
        developer_id: str,
        permission: PermissionLevel,
    ) -> CompanyPermissions:
        """Add, update, or revoke a developer's permission level for a company.

        Valid permission levels are USER, ADMIN, and OWNER. Set permission to REVOKE
        to revoke access entirely.

        Args:
            company_id: The ID of the company.
            developer_id: The ID of the developer to grant/modify access for.
            permission: The permission level to grant (USER, ADMIN, OWNER, or REVOKE).

        Returns:
            The CompanyPermissions object confirming the granted permission.

        Raises:
            NotFoundError: If the company or developer does not exist.
            AuthorizationError: If you don't have owner-level access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If trying to remove the last owner.
        """
        body = self._validate_request(
            _GrantAccess,
            developer_id=developer_id,
            permission=permission,
        )
        response = await self._post(
            Endpoints.COMPANY_ACCESS.format(company_id=company_id),
            json=body.model_dump(mode="json"),
        )
        return CompanyPermissions.model_validate(response.json())
