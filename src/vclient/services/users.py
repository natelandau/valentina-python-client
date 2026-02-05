"""Service for interacting with the Users API."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from vclient.constants import DEFAULT_PAGE_LIMIT, UserRole
from vclient.endpoints import Endpoints
from vclient.models import (
    CampaignExperience,
    DiscordProfile,
    Note,
    NoteCreate,
    NoteUpdate,
    PaginatedResponse,
    Quickroll,
    QuickrollCreate,
    QuickrollUpdate,
    RollStatistics,
    S3Asset,
    User,
    UserCreate,
    UserUpdate,
    _ExperienceAddRemove,
)
from vclient.services.base import BaseService

if TYPE_CHECKING:
    from vclient.client import VClient


class UsersService(BaseService):
    """Service for managing users within a company in the Valentina API.

    This service is scoped to a specific company at initialization time.
    All methods operate within that company context.

    Provides methods to create, retrieve, update, and delete users,
    as well as access user statistics and assets.

    Example:
        >>> async with VClient() as client:
        ...     users = client.users("company_id")
        ...     all_users = await users.list_all()
        ...     user = await users.get("user_id")
    """

    def __init__(self, client: "VClient", company_id: str) -> None:
        """Initialize the service scoped to a specific company.

        Args:
            client: The VClient instance to use for requests.
            company_id: The ID of the company to operate within.
        """
        super().__init__(client)
        self._company_id = company_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id plus any extra params."""
        return endpoint.format(company_id=self._company_id, **kwargs)

    # -------------------------------------------------------------------------
    # User CRUD Methods
    # -------------------------------------------------------------------------

    async def get_page(
        self,
        *,
        user_role: UserRole | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[User]:
        """Retrieve a paginated page of users within a company.

        Optionally filter by user role to view specific user types such as players
        or storytellers.

        Args:
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
            self._format_endpoint(Endpoints.USERS),
            User,
            limit=limit,
            offset=offset,
            params=params if params else None,
        )

    async def list_all(
        self,
        *,
        user_role: UserRole | None = None,
    ) -> list[User]:
        """Retrieve all users within a company.

        Automatically paginates through all results. Use `get_page()` for paginated access
        or `iter_all()` for memory-efficient streaming of large datasets.

        Args:
            user_role: Optional role filter (ADMIN, STORYTELLER, PLAYER).

        Returns:
            A list of all User objects.
        """
        return [user async for user in self.iter_all(user_role=user_role)]

    async def iter_all(
        self,
        *,
        user_role: UserRole | None = None,
        limit: int = 100,
    ) -> AsyncIterator[User]:
        """Iterate through all users within a company.

        Yields individual users, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            user_role: Optional role filter (ADMIN, STORYTELLER, PLAYER).
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual User objects.

        Example:
            >>> async for user in users.iter_all():
            ...     print(user.name)
        """
        params = {}
        if user_role is not None:
            params["user_role"] = user_role

        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.USERS),
            limit=limit,
            params=params if params else None,
        ):
            yield User.model_validate(item)

    async def get(self, user_id: str) -> User:
        """Retrieve detailed information about a specific user.

        Fetches the user including their role, experience, and Discord profile.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The User object with full details.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(self._format_endpoint(Endpoints.USER, user_id=user_id))
        return User.model_validate(response.json())

    async def create(
        self,
        request: UserCreate | None = None,
        /,
        **kwargs,
    ) -> User:
        """Create a new user within a company.

        The user is automatically added to the company's user list. The Discord profile
        is optional and is not used for authentication but is included for Discord bot
        integration.

        Args:
            request: A UserCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for UserCreate if request is not provided.
                Accepts: name (str, required), email (str, required),
                role (UserRole, required), requesting_user_id (str, required),
                discord_profile (DiscordProfile | None).

        Returns:
            The newly created User object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
            AuthorizationError: If you don't have admin-level access to the company.
        """
        body = request if request is not None else self._validate_request(UserCreate, **kwargs)
        response = await self._post(
            self._format_endpoint(Endpoints.USERS),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return User.model_validate(response.json())

    async def update(
        self,
        user_id: str,
        request: UserUpdate | None = None,
        /,
        **kwargs,
    ) -> User:
        """Modify a user's properties.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            user_id: The ID of the user to update.
            request: A UserUpdate model, OR pass fields as keyword arguments.
            **kwargs: Fields for UserUpdate if request is not provided.
                Accepts: requesting_user_id (str, required), name (str | None),
                email (str | None), role (UserRole | None),
                discord_profile (DiscordProfile | None).

        Returns:
            The updated User object.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(UserUpdate, **kwargs)
        response = await self._patch(
            self._format_endpoint(Endpoints.USER, user_id=user_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return User.model_validate(response.json())

    async def delete(
        self,
        user_id: str,
        requesting_user_id: str,
    ) -> None:
        """Remove a user from the company.

        The user is removed from the company's user list and their data is archived.

        Args:
            user_id: The ID of the user to delete.
            requesting_user_id: ID of the user making the request.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(Endpoints.USER, user_id=user_id),
            params={"requesting_user_id": requesting_user_id},
        )

    async def get_statistics(
        self,
        user_id: str,
        *,
        num_top_traits: int = 5,
    ) -> RollStatistics:
        """Retrieve aggregated dice roll statistics for a specific user.

        Includes success rates, critical frequencies, most-used traits, etc.

        Args:
            user_id: The ID of the user to get statistics for.
            num_top_traits: Number of top traits to include (default 5).

        Returns:
            RollStatistics object with aggregated statistics.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.USER_STATISTICS, user_id=user_id),
            params={"num_top_traits": num_top_traits},
        )
        return RollStatistics.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Asset Methods
    # -------------------------------------------------------------------------

    async def list_assets(
        self,
        user_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[S3Asset]:
        """Retrieve a paginated list of assets for a user.

        Args:
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
            self._format_endpoint(Endpoints.USER_ASSETS, user_id=user_id),
            S3Asset,
            limit=limit,
            offset=offset,
        )

    async def get_asset(
        self,
        user_id: str,
        asset_id: str,
    ) -> S3Asset:
        """Retrieve details of a specific asset including its URL and metadata.

        Args:
            user_id: The ID of the user who owns the asset.
            asset_id: The ID of the asset to retrieve.

        Returns:
            The S3Asset object with full details.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.USER_ASSET, user_id=user_id, asset_id=asset_id)
        )
        return S3Asset.model_validate(response.json())

    async def delete_asset(
        self,
        user_id: str,
        asset_id: str,
    ) -> None:
        """Delete an asset from a user.

        This action cannot be undone. The asset file is permanently removed.

        Args:
            user_id: The ID of the user who owns the asset.
            asset_id: The ID of the asset to delete.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(Endpoints.USER_ASSET, user_id=user_id, asset_id=asset_id)
        )

    async def upload_asset(
        self,
        user_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> S3Asset:
        """Upload a new asset for a user.

        Uploads a file to S3 storage and associates it with the user.

        Args:
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
            self._format_endpoint(Endpoints.USER_ASSET_UPLOAD, user_id=user_id),
            file=(filename, content, content_type),
        )
        return S3Asset.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Experience Methods
    # -------------------------------------------------------------------------

    async def get_experience(
        self,
        user_id: str,
        campaign_id: str,
    ) -> CampaignExperience:
        """Retrieve a user's experience points and cool points for a specific campaign.

        Creates the experience record automatically if it doesn't exist for the campaign.

        Args:
            user_id: The ID of the user to get experience for.
            campaign_id: The ID of the campaign to get experience for.

        Returns:
            CampaignExperience object with xp_current, xp_total, and cool_points.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.USER_EXPERIENCE_CAMPAIGN, user_id=user_id, campaign_id=campaign_id
            )
        )
        return CampaignExperience.model_validate(response.json())

    async def add_xp(
        self,
        user_id: str,
        campaign_id: str,
        amount: int,
    ) -> CampaignExperience:
        """Award experience points to a user for a specific campaign.

        The XP is added to both the current XP pool (available for spending) and
        the total XP tracker (lifetime earned).

        Args:
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
            _ExperienceAddRemove,
            amount=amount,
            user_id=user_id,
            campaign_id=campaign_id,
        )
        response = await self._post(
            self._format_endpoint(Endpoints.USER_EXPERIENCE_XP_ADD, user_id=user_id),
            json=body.model_dump(mode="json"),
        )
        return CampaignExperience.model_validate(response.json())

    async def remove_xp(
        self,
        user_id: str,
        campaign_id: str,
        amount: int,
    ) -> CampaignExperience:
        """Deduct experience points from a user's current XP pool.

        Returns an error if the user has insufficient XP to complete the deduction.

        Args:
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
            _ExperienceAddRemove,
            amount=amount,
            user_id=user_id,
            campaign_id=campaign_id,
        )
        response = await self._post(
            self._format_endpoint(Endpoints.USER_EXPERIENCE_XP_REMOVE, user_id=user_id),
            json=body.model_dump(mode="json"),
        )
        return CampaignExperience.model_validate(response.json())

    async def add_cool_points(
        self,
        user_id: str,
        campaign_id: str,
        amount: int,
    ) -> CampaignExperience:
        """Award cool points to a user for a specific campaign.

        Cool points are converted to XP automatically based on the company's
        configured exchange rate.

        Args:
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
            _ExperienceAddRemove,
            amount=amount,
            user_id=user_id,
            campaign_id=campaign_id,
        )
        response = await self._post(
            self._format_endpoint(Endpoints.USER_EXPERIENCE_CP_ADD, user_id=user_id),
            json=body.model_dump(mode="json"),
        )
        return CampaignExperience.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Notes Methods
    # -------------------------------------------------------------------------

    async def get_notes_page(
        self,
        user_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[Note]:
        """Retrieve a paginated page of notes for a user.

        Args:
            user_id: The ID of the user whose notes to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Note objects and pagination metadata.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.USER_NOTES, user_id=user_id),
            Note,
            limit=limit,
            offset=offset,
        )

    async def list_all_notes(
        self,
        user_id: str,
    ) -> list[Note]:
        """Retrieve all notes for a user.

        Automatically paginates through all results. Use `get_notes_page()` for paginated
        access or `iter_all_notes()` for memory-efficient streaming of large datasets.

        Args:
            user_id: The ID of the user whose notes to list.

        Returns:
            A list of all Note objects.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        return [note async for note in self.iter_all_notes(user_id)]

    async def iter_all_notes(
        self,
        user_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[Note]:
        """Iterate through all notes for a user.

        Yields individual notes, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            user_id: The ID of the user whose notes to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Note objects.

        Example:
            >>> async for note in users.iter_all_notes("user_id"):
            ...     print(note.title)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.USER_NOTES, user_id=user_id),
            limit=limit,
        ):
            yield Note.model_validate(item)

    async def get_note(
        self,
        user_id: str,
        note_id: str,
    ) -> Note:
        """Retrieve a specific note including its content and metadata.

        Args:
            user_id: The ID of the user who owns the note.
            note_id: The ID of the note to retrieve.

        Returns:
            The Note object with full details.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.USER_NOTE, user_id=user_id, note_id=note_id)
        )
        return Note.model_validate(response.json())

    async def create_note(
        self,
        user_id: str,
        request: NoteCreate | None = None,
        /,
        **kwargs,
    ) -> Note:
        """Create a new note for a user.

        Notes support markdown formatting for rich text content.

        Args:
            user_id: The ID of the user to create the note for.
            request: A NoteCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for NoteCreate if request is not provided.
                Accepts: title (str, required), content (str, required).

        Returns:
            The newly created Note object.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(NoteCreate, **kwargs)
        response = await self._post(
            self._format_endpoint(Endpoints.USER_NOTES, user_id=user_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Note.model_validate(response.json())

    async def update_note(
        self,
        user_id: str,
        note_id: str,
        request: NoteUpdate | None = None,
        /,
        **kwargs,
    ) -> Note:
        """Modify a note's content.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            user_id: The ID of the user who owns the note.
            note_id: The ID of the note to update.
            request: A NoteUpdate model, OR pass fields as keyword arguments.
            **kwargs: Fields for NoteUpdate if request is not provided.
                Accepts: title (str | None), content (str | None).

        Returns:
            The updated Note object.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(NoteUpdate, **kwargs)
        response = await self._patch(
            self._format_endpoint(Endpoints.USER_NOTE, user_id=user_id, note_id=note_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Note.model_validate(response.json())

    async def delete_note(
        self,
        user_id: str,
        note_id: str,
    ) -> None:
        """Remove a note from a user.

        This action cannot be undone.

        Args:
            user_id: The ID of the user who owns the note.
            note_id: The ID of the note to delete.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(Endpoints.USER_NOTE, user_id=user_id, note_id=note_id)
        )

    # -------------------------------------------------------------------------
    # Quickroll Methods
    # -------------------------------------------------------------------------

    async def get_quickrolls_page(
        self,
        user_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[Quickroll]:
        """Retrieve a paginated page of quickrolls for a user.

        Quickrolls are pre-configured dice pools for frequently used trait combinations,
        allowing faster gameplay.

        Args:
            user_id: The ID of the user whose quickrolls to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Quickroll objects and pagination metadata.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.USER_QUICKROLLS, user_id=user_id),
            Quickroll,
            limit=limit,
            offset=offset,
        )

    async def list_all_quickrolls(
        self,
        user_id: str,
    ) -> list[Quickroll]:
        """Retrieve all quickrolls for a user.

        Automatically paginates through all results. Use `get_quickrolls_page()` for
        paginated access or `iter_all_quickrolls()` for memory-efficient streaming.

        Args:
            user_id: The ID of the user whose quickrolls to list.

        Returns:
            A list of all Quickroll objects.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        return [qr async for qr in self.iter_all_quickrolls(user_id)]

    async def iter_all_quickrolls(
        self,
        user_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[Quickroll]:
        """Iterate through all quickrolls for a user.

        Yields individual quickrolls, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            user_id: The ID of the user whose quickrolls to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Quickroll objects.

        Example:
            >>> async for qr in users.iter_all_quickrolls("user_id"):
            ...     print(qr.name)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.USER_QUICKROLLS, user_id=user_id),
            limit=limit,
        ):
            yield Quickroll.model_validate(item)

    async def get_quickroll(
        self,
        user_id: str,
        quickroll_id: str,
    ) -> Quickroll:
        """Retrieve a specific quickroll including its name and trait configuration.

        Args:
            user_id: The ID of the user who owns the quickroll.
            quickroll_id: The ID of the quickroll to retrieve.

        Returns:
            The Quickroll object with full details.

        Raises:
            NotFoundError: If the quickroll does not exist.
            AuthorizationError: If you don't have access to the company.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.USER_QUICKROLL, user_id=user_id, quickroll_id=quickroll_id
            )
        )
        return Quickroll.model_validate(response.json())

    async def create_quickroll(
        self,
        user_id: str,
        request: QuickrollCreate | None = None,
        /,
        **kwargs,
    ) -> Quickroll:
        """Create a new quickroll for a user.

        Define the traits that make up the dice pool. Quickroll names must be unique
        per user.

        Args:
            user_id: The ID of the user to create the quickroll for.
            request: A QuickrollCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for QuickrollCreate if request is not provided.
                Accepts: name (str, required), description (str | None),
                trait_ids (list[str]).

        Returns:
            The newly created Quickroll object.

        Raises:
            NotFoundError: If the user does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(QuickrollCreate, **kwargs)
        response = await self._post(
            self._format_endpoint(Endpoints.USER_QUICKROLLS, user_id=user_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Quickroll.model_validate(response.json())

    async def update_quickroll(
        self,
        user_id: str,
        quickroll_id: str,
        request: QuickrollUpdate | None = None,
        /,
        **kwargs,
    ) -> Quickroll:
        """Modify a quickroll's name or trait configuration.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            user_id: The ID of the user who owns the quickroll.
            quickroll_id: The ID of the quickroll to update.
            request: A QuickrollUpdate model, OR pass fields as keyword arguments.
            **kwargs: Fields for QuickrollUpdate if request is not provided.
                Accepts: name (str | None), description (str | None),
                trait_ids (list[str] | None).

        Returns:
            The updated Quickroll object.

        Raises:
            NotFoundError: If the quickroll does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(QuickrollUpdate, **kwargs)
        response = await self._patch(
            self._format_endpoint(
                Endpoints.USER_QUICKROLL, user_id=user_id, quickroll_id=quickroll_id
            ),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Quickroll.model_validate(response.json())

    async def delete_quickroll(
        self,
        user_id: str,
        quickroll_id: str,
    ) -> None:
        """Remove a quickroll from a user.

        This action cannot be undone.

        Args:
            user_id: The ID of the user who owns the quickroll.
            quickroll_id: The ID of the quickroll to delete.

        Raises:
            NotFoundError: If the quickroll does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(
                Endpoints.USER_QUICKROLL, user_id=user_id, quickroll_id=quickroll_id
            )
        )
