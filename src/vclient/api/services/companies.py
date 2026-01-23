"""Service for interacting with the Companies API."""

from collections.abc import AsyncIterator

from vclient.api.endpoints import Endpoints
from vclient.api.models.companies import (
    Company,
    CompanyPermissions,
    CompanySettings,
    CreateCompanyRequest,
    GrantAccessRequest,
    PermissionLevel,
    UpdateCompanyRequest,
)
from vclient.api.models.pagination import PaginatedResponse
from vclient.api.services.base import BaseService


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
        limit: int = 10,
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
        response = await self._get_paginated(
            Endpoints.COMPANIES,
            limit=limit,
            offset=offset,
        )
        return PaginatedResponse(
            items=[Company.model_validate(item) for item in response.items],
            limit=response.limit,
            offset=response.offset,
            total=response.total,
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
        name: str,
        email: str,
        *,
        description: str | None = None,
        settings: CompanySettings | None = None,
    ) -> Company:
        """Create a new company in the system.

        You are automatically granted OWNER permission for the new company, giving you
        full administrative control, including the ability to grant permissions to
        other developers.

        Args:
            name: Company name (3-50 characters).
            email: Company contact email.
            description: Optional company description (min 3 characters).
            settings: Optional company settings configuration.

        Returns:
            The newly created Company object.

        Raises:
            ValidationError: If the request data is invalid.
        """
        body = CreateCompanyRequest(
            name=name,
            email=email,
            description=description,
            settings=settings,
        )

        response = await self._post(
            Endpoints.COMPANIES,
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Company.model_validate(response.json())

    async def update(
        self,
        company_id: str,
        *,
        name: str | None = None,
        email: str | None = None,
        description: str | None = None,
        settings: CompanySettings | None = None,
    ) -> Company:
        """Modify a company's properties.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            company_id: The ID of the company to update.
            name: New company name (3-50 characters).
            email: New company contact email.
            description: New company description (min 3 characters).
            settings: New company settings configuration.

        Returns:
            The updated Company object.

        Raises:
            NotFoundError: If the company does not exist.
            AuthorizationError: If you don't have admin-level access.
            ValidationError: If the request data is invalid.
        """
        body = UpdateCompanyRequest(
            name=name,
            email=email,
            description=description,
            settings=settings,
        )

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
            ValidationError: If trying to remove the last owner.
        """
        body = GrantAccessRequest(developer_id=developer_id, permission=permission)

        response = await self._post(
            Endpoints.COMPANY_ACCESS.format(company_id=company_id),
            json=body.model_dump(mode="json"),
        )
        return CompanyPermissions.model_validate(response.json())
