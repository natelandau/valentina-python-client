"""Service for interacting with the Campaigns API."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from vclient.constants import DEFAULT_PAGE_LIMIT
from vclient.endpoints import Endpoints
from vclient.models.campaigns import (
    Campaign,
    CreateCampaignRequest,
    UpdateCampaignRequest,
)
from vclient.models.pagination import PaginatedResponse
from vclient.models.shared import (
    CreateNoteRequest,
    Note,
    RollStatistics,
    S3Asset,
    UpdateNoteRequest,
)
from vclient.services.base import BaseService

if TYPE_CHECKING:
    from vclient.client import VClient


class CampaignsService(BaseService):
    """Service for managing campaigns within a company in the Valentina API.

    This service is scoped to a specific company and user at initialization time.
    All methods operate within that context.

    Provides methods to create, retrieve, update, and delete campaigns,
    as well as access campaign statistics, assets, and notes.

    Example:
        >>> async with VClient() as client:
        ...     campaigns = client.campaigns("company_id", "user_id")
        ...     all_campaigns = await campaigns.list_all()
        ...     campaign = await campaigns.get("campaign_id")
    """

    def __init__(self, client: "VClient", company_id: str, user_id: str) -> None:
        """Initialize the service scoped to a specific company and user.

        Args:
            client: The VClient instance to use for requests.
            company_id: The ID of the company to operate within.
            user_id: The ID of the user to operate as.
        """
        super().__init__(client)
        self._company_id = company_id
        self._user_id = user_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id and user_id plus any extra params."""
        return endpoint.format(
            company_id=self._company_id,
            user_id=self._user_id,
            **kwargs,
        )

    # -------------------------------------------------------------------------
    # Campaign CRUD Methods
    # -------------------------------------------------------------------------

    async def get_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[Campaign]:
        """Retrieve a paginated page of campaigns.

        Args:
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Campaign objects and pagination metadata.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CAMPAIGNS),
            Campaign,
            limit=limit,
            offset=offset,
        )

    async def list_all(self) -> list[Campaign]:
        """Retrieve all campaigns.

        Automatically paginates through all results. Use `get_page()` for paginated access
        or `iter_all()` for memory-efficient streaming of large datasets.

        Returns:
            A list of all Campaign objects.
        """
        return [campaign async for campaign in self.iter_all()]

    async def iter_all(
        self,
        *,
        limit: int = 100,
    ) -> AsyncIterator[Campaign]:
        """Iterate through all campaigns.

        Yields individual campaigns, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Campaign objects.

        Example:
            >>> async for campaign in campaigns.iter_all():
            ...     print(campaign.name)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.CAMPAIGNS),
            limit=limit,
        ):
            yield Campaign.model_validate(item)

    async def get(self, campaign_id: str) -> Campaign:
        """Retrieve detailed information about a specific campaign.

        Fetches the campaign including desperation and danger levels.

        Args:
            campaign_id: The ID of the campaign to retrieve.

        Returns:
            The Campaign object with full details.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.CAMPAIGN, campaign_id=campaign_id)
        )
        return Campaign.model_validate(response.json())

    async def create(
        self,
        name: str,
        *,
        description: str | None = None,
        desperation: int = 0,
        danger: int = 0,
    ) -> Campaign:
        """Create a new campaign.

        Args:
            name: Campaign name (3-50 characters).
            description: Optional campaign description (minimum 3 characters).
            desperation: Desperation level (0-5, default 0).
            danger: Danger level (0-5, default 0).

        Returns:
            The newly created Campaign object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
            AuthorizationError: If you don't have campaign management privileges.
        """
        body = self._validate_request(
            CreateCampaignRequest,
            name=name,
            description=description,
            desperation=desperation,
            danger=danger,
        )
        response = await self._post(
            self._format_endpoint(Endpoints.CAMPAIGNS),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Campaign.model_validate(response.json())

    async def update(
        self,
        campaign_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        desperation: int | None = None,
        danger: int | None = None,
    ) -> Campaign:
        """Modify a campaign's properties.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            campaign_id: The ID of the campaign to update.
            name: New campaign name (3-50 characters).
            description: New campaign description (minimum 3 characters).
            desperation: New desperation level (0-5).
            danger: New danger level (0-5).

        Returns:
            The updated Campaign object.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have campaign management privileges.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            UpdateCampaignRequest,
            name=name,
            description=description,
            desperation=desperation,
            danger=danger,
        )
        response = await self._patch(
            self._format_endpoint(Endpoints.CAMPAIGN, campaign_id=campaign_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Campaign.model_validate(response.json())

    async def delete(self, campaign_id: str) -> None:
        """Remove a campaign from the system.

        Associated characters, books, and other content will no longer be accessible.
        This action cannot be undone.

        Args:
            campaign_id: The ID of the campaign to delete.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have campaign management privileges.
        """
        await self._delete(self._format_endpoint(Endpoints.CAMPAIGN, campaign_id=campaign_id))

    async def get_statistics(
        self,
        campaign_id: str,
        *,
        num_top_traits: int = 5,
    ) -> RollStatistics:
        """Retrieve aggregated dice roll statistics for a specific campaign.

        Includes success rates, critical frequencies, most-used traits, etc.

        Args:
            campaign_id: The ID of the campaign to get statistics for.
            num_top_traits: Number of top traits to include (default 5).

        Returns:
            RollStatistics object with aggregated statistics.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.CAMPAIGN_STATISTICS, campaign_id=campaign_id),
            params={"num_top_traits": num_top_traits},
        )
        return RollStatistics.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Asset Methods
    # -------------------------------------------------------------------------

    async def list_assets(
        self,
        campaign_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[S3Asset]:
        """Retrieve a paginated list of assets for a campaign.

        Args:
            campaign_id: The ID of the campaign whose assets to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing S3Asset objects and pagination metadata.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have access.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CAMPAIGN_ASSETS, campaign_id=campaign_id),
            S3Asset,
            limit=limit,
            offset=offset,
        )

    async def get_asset(
        self,
        campaign_id: str,
        asset_id: str,
    ) -> S3Asset:
        """Retrieve details of a specific asset including its URL and metadata.

        Args:
            campaign_id: The ID of the campaign that owns the asset.
            asset_id: The ID of the asset to retrieve.

        Returns:
            The S3Asset object with full details.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.CAMPAIGN_ASSET, campaign_id=campaign_id, asset_id=asset_id
            )
        )
        return S3Asset.model_validate(response.json())

    async def delete_asset(
        self,
        campaign_id: str,
        asset_id: str,
    ) -> None:
        """Delete an asset from a campaign.

        This action cannot be undone. The asset file is permanently removed.

        Args:
            campaign_id: The ID of the campaign that owns the asset.
            asset_id: The ID of the asset to delete.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(
                Endpoints.CAMPAIGN_ASSET, campaign_id=campaign_id, asset_id=asset_id
            )
        )

    async def upload_asset(
        self,
        campaign_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> S3Asset:
        """Upload a new asset for a campaign.

        Uploads a file to S3 storage and associates it with the campaign.

        Args:
            campaign_id: The ID of the campaign to upload the asset for.
            filename: The original filename of the asset.
            content: The raw bytes of the file to upload.
            content_type: The MIME type of the file (default: application/octet-stream).

        Returns:
            The created S3Asset object with the public URL and metadata.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have appropriate access.
            ValidationError: If the file is invalid or exceeds size limits.
        """
        response = await self._post_file(
            self._format_endpoint(Endpoints.CAMPAIGN_ASSET_UPLOAD, campaign_id=campaign_id),
            file=(filename, content, content_type),
        )
        return S3Asset.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Notes Methods
    # -------------------------------------------------------------------------

    async def get_notes_page(
        self,
        campaign_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[Note]:
        """Retrieve a paginated page of notes for a campaign.

        Args:
            campaign_id: The ID of the campaign whose notes to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Note objects and pagination metadata.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have access.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CAMPAIGN_NOTES, campaign_id=campaign_id),
            Note,
            limit=limit,
            offset=offset,
        )

    async def list_all_notes(
        self,
        campaign_id: str,
    ) -> list[Note]:
        """Retrieve all notes for a campaign.

        Automatically paginates through all results. Use `get_notes_page()` for paginated
        access or `iter_all_notes()` for memory-efficient streaming of large datasets.

        Args:
            campaign_id: The ID of the campaign whose notes to list.

        Returns:
            A list of all Note objects.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have access.
        """
        return [note async for note in self.iter_all_notes(campaign_id)]

    async def iter_all_notes(
        self,
        campaign_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[Note]:
        """Iterate through all notes for a campaign.

        Yields individual notes, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            campaign_id: The ID of the campaign whose notes to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Note objects.

        Example:
            >>> async for note in campaigns.iter_all_notes("campaign_id"):
            ...     print(note.title)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.CAMPAIGN_NOTES, campaign_id=campaign_id),
            limit=limit,
        ):
            yield Note.model_validate(item)

    async def get_note(
        self,
        campaign_id: str,
        note_id: str,
    ) -> Note:
        """Retrieve a specific note including its content and metadata.

        Args:
            campaign_id: The ID of the campaign that owns the note.
            note_id: The ID of the note to retrieve.

        Returns:
            The Note object with full details.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.CAMPAIGN_NOTE, campaign_id=campaign_id, note_id=note_id)
        )
        return Note.model_validate(response.json())

    async def create_note(
        self,
        campaign_id: str,
        title: str,
        content: str,
    ) -> Note:
        """Create a new note for a campaign.

        Notes support markdown formatting for rich text content.

        Args:
            campaign_id: The ID of the campaign to create the note for.
            title: The note title (3-50 characters).
            content: The note content (minimum 3 characters, supports markdown).

        Returns:
            The newly created Note object.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            CreateNoteRequest,
            title=title,
            content=content,
        )
        response = await self._post(
            self._format_endpoint(Endpoints.CAMPAIGN_NOTES, campaign_id=campaign_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Note.model_validate(response.json())

    async def update_note(
        self,
        campaign_id: str,
        note_id: str,
        *,
        title: str | None = None,
        content: str | None = None,
    ) -> Note:
        """Modify a note's content.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            campaign_id: The ID of the campaign that owns the note.
            note_id: The ID of the note to update.
            title: New note title (3-50 characters).
            content: New note content (minimum 3 characters, supports markdown).

        Returns:
            The updated Note object.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            UpdateNoteRequest,
            title=title,
            content=content,
        )
        response = await self._patch(
            self._format_endpoint(
                Endpoints.CAMPAIGN_NOTE, campaign_id=campaign_id, note_id=note_id
            ),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Note.model_validate(response.json())

    async def delete_note(
        self,
        campaign_id: str,
        note_id: str,
    ) -> None:
        """Remove a note from a campaign.

        This action cannot be undone.

        Args:
            campaign_id: The ID of the campaign that owns the note.
            note_id: The ID of the note to delete.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(Endpoints.CAMPAIGN_NOTE, campaign_id=campaign_id, note_id=note_id)
        )
