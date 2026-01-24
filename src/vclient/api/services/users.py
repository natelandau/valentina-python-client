"""Service for interacting with the Users API."""

from collections.abc import AsyncIterator

from vclient.api.constants import DEFAULT_PAGE_LIMIT
from vclient.api.endpoints import Endpoints
from vclient.api.models.pagination import PaginatedResponse
from vclient.api.models.users import (
    CampaignExperience,
    CreateUserRequest,
    DiscordProfile,
    ExperienceAddRemoveRequest,
    RollStatistics,
    S3Asset,
    UpdateUserRequest,
    User,
    UserRole,
)
from vclient.api.services.base import BaseService


class UsersService(BaseService):
    """Service for managing users within a company in the Valentina API.

    Provides methods to create, retrieve, update, and delete users,
    as well as access user statistics and assets.

    Example:
        >>> async with VClient() as client:
        ...     users = await client.users.list_all("company_id")
        ...     user = await client.users.get("company_id", "user_id")
    """

    async def get_page(
        self,
        company_id: str,
        *,
        user_role: UserRole | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[User]:
        """Retrieve a paginated page of users within a company.

        Optionally filter by user role to view specific user types such as players
        or storytellers.

        Args:
            company_id: The ID of the company containing the users.
            user_role: Optional role filter (ADMIN, STORYTELLER, PLAYER).
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing User objects and pagination metadata.
        """
        params = {}
        if user_role is not None:
            params["user_role"] = user_role

        return await self._get_paginated_as(
            Endpoints.USERS.format(company_id=company_id),
            User,
            limit=limit,
            offset=offset,
            params=params if params else None,
        )

    async def list_all(
        self,
        company_id: str,
        *,
        user_role: UserRole | None = None,
    ) -> list[User]:
        """Retrieve all users within a company.

        Automatically paginates through all results. Use `get_page()` for paginated access
        or `iter_all()` for memory-efficient streaming of large datasets.

        Args:
            company_id: The ID of the company containing the users.
            user_role: Optional role filter (ADMIN, STORYTELLER, PLAYER).

        Returns:
            A list of all User objects.
        """
        return [user async for user in self.iter_all(company_id, user_role=user_role)]

    async def iter_all(
        self,
        company_id: str,
        *,
        user_role: UserRole | None = None,
        limit: int = 100,
    ) -> AsyncIterator[User]:
        """Iterate through all users within a company.

        Yields individual users, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            company_id: The ID of the company containing the users.
            user_role: Optional role filter (ADMIN, STORYTELLER, PLAYER).
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual User objects.

        Example:
            >>> async for user in client.users.iter_all("company_id"):
            ...     print(user.name)
        """
        params = {}
        if user_role is not None:
            params["user_role"] = user_role

        async for item in self._iter_all_pages(
            Endpoints.USERS.format(company_id=company_id),
            limit=limit,
            params=params if params else None,
        ):
            yield User.model_validate(item)

    async def get(self, company_id: str, user_id: str) -> User:
        """Retrieve detailed information about a specific user.

        Fetches the user including their role, experience, and Discord profile.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user to retrieve.

        Returns:
            The User object with full details.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(Endpoints.USER.format(company_id=company_id, user_id=user_id))
        return User.model_validate(response.json())

    async def create(
        self,
        company_id: str,
        name: str,
        email: str,
        role: UserRole,
        requesting_user_id: str,
        *,
        discord_profile: DiscordProfile | None = None,
    ) -> User:
        """Create a new user within a company.

        The user is automatically added to the company's user list. The Discord profile
        is optional and is not used for authentication but is included for Discord bot
        integration.

        Args:
            company_id: The ID of the company to add the user to.
            name: User's display name (3-50 characters).
            email: User's email address.
            role: User's role (ADMIN, STORYTELLER, PLAYER).
            requesting_user_id: ID of the user making the request.
            discord_profile: Optional Discord profile information.

        Returns:
            The newly created User object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
            AuthorizationError: If you don't have admin-level access to the company.
        """
        body = self._validate_request(
            CreateUserRequest,
            name=name,
            email=email,
            role=role,
            requesting_user_id=requesting_user_id,
            discord_profile=discord_profile,
        )
        response = await self._post(
            Endpoints.USERS.format(company_id=company_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return User.model_validate(response.json())

    async def update(  # noqa: PLR0913
        self,
        company_id: str,
        user_id: str,
        requesting_user_id: str,
        *,
        name: str | None = None,
        email: str | None = None,
        role: UserRole | None = None,
        discord_profile: DiscordProfile | None = None,
    ) -> User:
        """Modify a user's properties.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user to update.
            requesting_user_id: ID of the user making the request.
            name: New display name (3-50 characters).
            email: New email address.
            role: New role (ADMIN, STORYTELLER, PLAYER).
            discord_profile: New Discord profile information.

        Returns:
            The updated User object.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            UpdateUserRequest,
            name=name,
            email=email,
            role=role,
            discord_profile=discord_profile,
            requesting_user_id=requesting_user_id,
        )
        response = await self._patch(
            Endpoints.USER.format(company_id=company_id, user_id=user_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return User.model_validate(response.json())

    async def delete(
        self,
        company_id: str,
        user_id: str,
        requesting_user_id: str,
    ) -> None:
        """Remove a user from the company.

        The user is removed from the company's user list and their data is archived.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user to delete.
            requesting_user_id: ID of the user making the request.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            Endpoints.USER.format(company_id=company_id, user_id=user_id),
            params={"requesting_user_id": requesting_user_id},
        )

    async def get_statistics(
        self,
        company_id: str,
        user_id: str,
        *,
        num_top_traits: int = 5,
    ) -> RollStatistics:
        """Retrieve aggregated dice roll statistics for a specific user.

        Includes success rates, critical frequencies, most-used traits, etc.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user to get statistics for.
            num_top_traits: Number of top traits to include (default 5).

        Returns:
            RollStatistics object with aggregated statistics.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(
            Endpoints.USER_STATISTICS.format(company_id=company_id, user_id=user_id),
            params={"num_top_traits": num_top_traits},
        )
        return RollStatistics.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Asset Methods
    # -------------------------------------------------------------------------

    async def list_assets(
        self,
        company_id: str,
        user_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[S3Asset]:
        """Retrieve a paginated list of assets for a user.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user whose assets to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing S3Asset objects and pagination metadata.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        return await self._get_paginated_as(
            Endpoints.USER_ASSETS.format(company_id=company_id, user_id=user_id),
            S3Asset,
            limit=limit,
            offset=offset,
        )

    async def get_asset(
        self,
        company_id: str,
        user_id: str,
        asset_id: str,
    ) -> S3Asset:
        """Retrieve details of a specific asset including its URL and metadata.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user who owns the asset.
            asset_id: The ID of the asset to retrieve.

        Returns:
            The S3Asset object with full details.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(
            Endpoints.USER_ASSET.format(company_id=company_id, user_id=user_id, asset_id=asset_id)
        )
        return S3Asset.model_validate(response.json())

    async def delete_asset(
        self,
        company_id: str,
        user_id: str,
        asset_id: str,
    ) -> None:
        """Delete an asset from a user.

        This action cannot be undone. The asset file is permanently removed.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user who owns the asset.
            asset_id: The ID of the asset to delete.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            Endpoints.USER_ASSET.format(company_id=company_id, user_id=user_id, asset_id=asset_id)
        )

    async def upload_asset(
        self,
        company_id: str,
        user_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> S3Asset:
        """Upload a new asset for a user.

        Uploads a file to S3 storage and associates it with the user.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user to upload the asset for.
            filename: The original filename of the asset.
            content: The raw bytes of the file to upload.
            content_type: The MIME type of the file (default: application/octet-stream).

        Returns:
            The created S3Asset object with the public URL and metadata.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have appropriate access.
            ValidationError: If the file is invalid or exceeds size limits.
        """
        response = await self._post_file(
            Endpoints.USER_ASSET_UPLOAD.format(company_id=company_id, user_id=user_id),
            file=(filename, content, content_type),
        )
        return S3Asset.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Experience Methods
    # -------------------------------------------------------------------------

    async def get_experience(
        self,
        company_id: str,
        user_id: str,
        campaign_id: str,
    ) -> CampaignExperience:
        """Retrieve a user's experience points and cool points for a specific campaign.

        Creates the experience record automatically if it doesn't exist for the campaign.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user to get experience for.
            campaign_id: The ID of the campaign to get experience for.

        Returns:
            CampaignExperience object with xp_current, xp_total, and cool_points.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(
            Endpoints.USER_EXPERIENCE_CAMPAIGN.format(
                company_id=company_id, user_id=user_id, campaign_id=campaign_id
            )
        )
        return CampaignExperience.model_validate(response.json())

    async def add_xp(
        self,
        company_id: str,
        user_id: str,
        campaign_id: str,
        amount: int,
    ) -> CampaignExperience:
        """Award experience points to a user for a specific campaign.

        The XP is added to both the current XP pool (available for spending) and
        the total XP tracker (lifetime earned).

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user to award XP to.
            campaign_id: The ID of the campaign to add XP for.
            amount: The amount of XP to add.

        Returns:
            Updated CampaignExperience object.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
        """
        body = self._validate_request(
            ExperienceAddRemoveRequest,
            amount=amount,
            user_id=user_id,
            campaign_id=campaign_id,
        )
        response = await self._post(
            Endpoints.USER_EXPERIENCE_XP_ADD.format(company_id=company_id, user_id=user_id),
            json=body.model_dump(mode="json"),
        )
        return CampaignExperience.model_validate(response.json())

    async def remove_xp(
        self,
        company_id: str,
        user_id: str,
        campaign_id: str,
        amount: int,
    ) -> CampaignExperience:
        """Deduct experience points from a user's current XP pool.

        Returns an error if the user has insufficient XP to complete the deduction.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user to remove XP from.
            campaign_id: The ID of the campaign to remove XP for.
            amount: The amount of XP to remove.

        Returns:
            Updated CampaignExperience object.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the user has insufficient XP.
        """
        body = self._validate_request(
            ExperienceAddRemoveRequest,
            amount=amount,
            user_id=user_id,
            campaign_id=campaign_id,
        )
        response = await self._post(
            Endpoints.USER_EXPERIENCE_XP_REMOVE.format(company_id=company_id, user_id=user_id),
            json=body.model_dump(mode="json"),
        )
        return CampaignExperience.model_validate(response.json())

    async def add_cool_points(
        self,
        company_id: str,
        user_id: str,
        campaign_id: str,
        amount: int,
    ) -> CampaignExperience:
        """Award cool points to a user for a specific campaign.

        Cool points are converted to XP automatically based on the company's
        configured exchange rate.

        Args:
            company_id: The ID of the company containing the user.
            user_id: The ID of the user to award cool points to.
            campaign_id: The ID of the campaign to add cool points for.
            amount: The amount of cool points to add.

        Returns:
            Updated CampaignExperience object.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
        """
        body = self._validate_request(
            ExperienceAddRemoveRequest,
            amount=amount,
            user_id=user_id,
            campaign_id=campaign_id,
        )
        response = await self._post(
            Endpoints.USER_EXPERIENCE_CP_ADD.format(company_id=company_id, user_id=user_id),
            json=body.model_dump(mode="json"),
        )
        return CampaignExperience.model_validate(response.json())
