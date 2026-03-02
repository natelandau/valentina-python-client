# AUTO-GENERATED — do not edit. Run 'uv run duty generate_sync' to regenerate.
"""Service for interacting with the Campaign Books Chapters API."""
import mimetypes
from collections.abc import Iterator
from typing import TYPE_CHECKING

from vclient._sync.services.base import SyncBaseService
from vclient.constants import DEFAULT_PAGE_LIMIT
from vclient.endpoints import Endpoints
from vclient.models import (
    Asset,
    CampaignChapter,
    ChapterCreate,
    ChapterUpdate,
    Note,
    NoteCreate,
    NoteUpdate,
    PaginatedResponse,
    _ChapterRenumber,
)

if TYPE_CHECKING:
    from vclient._sync.client import SyncVClient

class SyncChaptersService(SyncBaseService):
    """Service for managing campaign book chapters within a campaign book in the Valentina API."""

    def __init__(self, client: "SyncVClient", company_id: str, user_id: str, campaign_id: str, book_id: str) -> None:
        """Initialize the service scoped to a specific company, user, campaign, and book."""
        super().__init__(client)
        self._company_id = company_id
        self._user_id = user_id
        self._campaign_id = campaign_id
        self._book_id = book_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id, user_id, campaign_id, and book_id plus any extra params."""
        return endpoint.format(company_id=self._company_id, user_id=self._user_id, campaign_id=self._campaign_id, book_id=self._book_id, **kwargs)

    def get_page(self, *, limit: int=DEFAULT_PAGE_LIMIT, offset: int=0) -> PaginatedResponse[CampaignChapter]:
        """Retrieve a paginated page of campaign book chapters."""
        return self._get_paginated_as(self._format_endpoint(Endpoints.BOOK_CHAPTERS), CampaignChapter, limit=limit, offset=offset)

    def list_all(self) -> list[CampaignChapter]:
        """Retrieve all campaign book chapters."""
        return [chapter for chapter in self.iter_all()]

    def iter_all(self, *, limit: int=100) -> Iterator[CampaignChapter]:
        """Iterate through all campaign book chapters."""
        for item in self._iter_all_pages(self._format_endpoint(Endpoints.BOOK_CHAPTERS), limit=limit):
            yield CampaignChapter.model_validate(item)

    def get(self, chapter_id: str) -> CampaignChapter:
        """Retrieve a specific campaign book chapter."""
        response = self._get(self._format_endpoint(Endpoints.BOOK_CHAPTER, chapter_id=chapter_id))
        return CampaignChapter.model_validate(response.json())

    def create(self, request: ChapterCreate | None=None, **kwargs) -> CampaignChapter:
        """Create a new campaign book chapter.

        Args:
            request: A ChapterCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for ChapterCreate if request is not provided.
                Accepts: name (str, required), description (str | None).
        """
        body = request if request is not None else ChapterCreate(**kwargs)
        response = self._post(self._format_endpoint(Endpoints.BOOK_CHAPTERS), json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"))
        return CampaignChapter.model_validate(response.json())

    def update(self, chapter_id: str, request: ChapterUpdate | None=None, **kwargs) -> CampaignChapter:
        """Update a campaign book chapter.

        Args:
            chapter_id: The ID of the chapter to update.
            request: A ChapterUpdate model, OR pass fields as keyword arguments.
            **kwargs: Fields for ChapterUpdate if request is not provided.
                Accepts: name (str | None), description (str | None).
        """
        body = request if request is not None else ChapterUpdate(**kwargs)
        response = self._patch(self._format_endpoint(Endpoints.BOOK_CHAPTER, chapter_id=chapter_id), json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"))
        return CampaignChapter.model_validate(response.json())

    def delete(self, chapter_id: str) -> None:
        """Delete a campaign book chapter."""
        self._delete(self._format_endpoint(Endpoints.BOOK_CHAPTER, chapter_id=chapter_id))

    def renumber(self, chapter_id: str, number: int) -> CampaignChapter:
        """Renumber a campaign book chapter."""
        response = self._put(self._format_endpoint(Endpoints.BOOK_CHAPTER_NUMBER, chapter_id=chapter_id), json=_ChapterRenumber(number=number).model_dump(exclude_none=True, exclude_unset=True, mode="json"))
        return CampaignChapter.model_validate(response.json())

    def get_notes_page(self, chapter_id: str, *, limit: int=DEFAULT_PAGE_LIMIT, offset: int=0) -> PaginatedResponse[Note]:
        """Retrieve a paginated page of notes for a chapter.

        Args:
            chapter_id: The ID of the chapter whose notes to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Note objects and pagination metadata.

        Raises:
            NotFoundError: If the chapter does not exist.
            AuthorizationError: If you don't have access.
        """
        return self._get_paginated_as(self._format_endpoint(Endpoints.BOOK_CHAPTER_NOTES, chapter_id=chapter_id), Note, limit=limit, offset=offset)

    def list_all_notes(self, chapter_id: str) -> list[Note]:
        """Retrieve all notes for a chapter.

        Automatically paginates through all results. Use `get_notes_page()` for paginated
        access or `iter_all_notes()` for memory-efficient streaming of large datasets.

        Args:
            chapter_id: The ID of the chapter whose notes to list.

        Returns:
            A list of all Note objects.

        Raises:
            NotFoundError: If the chapter does not exist.
            AuthorizationError: If you don't have access.
        """
        return [note for note in self.iter_all_notes(chapter_id)]

    def iter_all_notes(self, chapter_id: str, *, limit: int=100) -> Iterator[Note]:
        """Iterate through all notes for a chapter.

        Yields individual notes, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            chapter_id: The ID of the chapter whose notes to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Note objects.

        Example:
            >>> async for note in chapters.iter_all_notes("chapter_id"):
            ...     print(note.title)
        """
        for item in self._iter_all_pages(self._format_endpoint(Endpoints.BOOK_CHAPTER_NOTES, chapter_id=chapter_id), limit=limit):
            yield Note.model_validate(item)

    def get_note(self, chapter_id: str, note_id: str) -> Note:
        """Retrieve a specific note including its content and metadata.

        Args:
            chapter_id: The ID of the chapter that owns the note.
            note_id: The ID of the note to retrieve.

        Returns:
            The Note object with full details.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have access.
        """
        response = self._get(self._format_endpoint(Endpoints.BOOK_CHAPTER_NOTE, chapter_id=chapter_id, note_id=note_id))
        return Note.model_validate(response.json())

    def create_note(self, chapter_id: str, request: NoteCreate | None=None, **kwargs) -> Note:
        """Create a new note for a chapter.

        Notes support markdown formatting for rich text content.

        Args:
            chapter_id: The ID of the chapter to create the note for.
            request: A NoteCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for NoteCreate if request is not provided.
                Accepts: title (str, required), content (str, required).

        Returns:
            The newly created Note object.

        Raises:
            NotFoundError: If the chapter does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(NoteCreate, **kwargs)
        response = self._post(self._format_endpoint(Endpoints.BOOK_CHAPTER_NOTES, chapter_id=chapter_id), json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"))
        return Note.model_validate(response.json())

    def update_note(self, chapter_id: str, note_id: str, request: NoteUpdate | None=None, **kwargs) -> Note:
        """Modify a note's content.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            chapter_id: The ID of the chapter that owns the note.
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
        response = self._patch(self._format_endpoint(Endpoints.BOOK_CHAPTER_NOTE, chapter_id=chapter_id, note_id=note_id), json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"))
        return Note.model_validate(response.json())

    def delete_note(self, chapter_id: str, note_id: str) -> None:
        """Remove a note from a chapter.

        This action cannot be undone.

        Args:
            chapter_id: The ID of the chapter that owns the note.
            note_id: The ID of the note to delete.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        self._delete(self._format_endpoint(Endpoints.BOOK_CHAPTER_NOTE, chapter_id=chapter_id, note_id=note_id))

    def get_assets_page(self, chapter_id: str, *, limit: int=DEFAULT_PAGE_LIMIT, offset: int=0) -> PaginatedResponse[Asset]:
        """Retrieve a paginated page of assets for a chapter.

        Args:
            chapter_id: The ID of the chapter whose assets to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Asset objects and pagination metadata.

        Raises:
            NotFoundError: If the chapter does not exist.
            AuthorizationError: If you don't have access.
        """
        return self._get_paginated_as(self._format_endpoint(Endpoints.BOOK_CHAPTER_ASSETS, chapter_id=chapter_id), Asset, limit=limit, offset=offset)

    def list_all_assets(self, chapter_id: str) -> list[Asset]:
        """Retrieve all assets for a chapter.

        Automatically paginates through all results. Use `get_assets_page()` for paginated
        access or `iter_all_assets()` for memory-efficient streaming of large datasets.

        Args:
            chapter_id: The ID of the chapter whose assets to list.

        Returns:
            A list of all Asset objects.

        Raises:
            NotFoundError: If the chapter does not exist.
            AuthorizationError: If you don't have access.
        """
        return [asset for asset in self.iter_all_assets(chapter_id)]

    def iter_all_assets(self, chapter_id: str, *, limit: int=100) -> Iterator[Asset]:
        """Iterate through all assets for a chapter.

        Yields individual assets, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            chapter_id: The ID of the chapter whose assets to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Asset objects.

        Example:
            >>> async for asset in chapters.iter_all_assets("chapter_id"):
            ...     print(asset.original_filename)
        """
        for item in self._iter_all_pages(self._format_endpoint(Endpoints.BOOK_CHAPTER_ASSETS, chapter_id=chapter_id), limit=limit):
            yield Asset.model_validate(item)

    def get_asset(self, chapter_id: str, asset_id: str) -> Asset:
        """Retrieve details of a specific asset including its URL and metadata.

        Args:
            chapter_id: The ID of the chapter that owns the asset.
            asset_id: The ID of the asset to retrieve.

        Returns:
            The Asset object with full details.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have access.
        """
        response = self._get(self._format_endpoint(Endpoints.BOOK_CHAPTER_ASSET, chapter_id=chapter_id, asset_id=asset_id))
        return Asset.model_validate(response.json())

    def upload_asset(self, chapter_id: str, filename: str, content: bytes, content_type: str | None=None) -> Asset:
        """Upload a new asset for a chapter.

        Uploads a file to S3 storage and associates it with the chapter.

        Args:
            chapter_id: The ID of the chapter to upload the asset for.
            filename: The original filename of the asset.
            content: The raw bytes of the file to upload.
            content_type: The MIME type of the file. If not provided, inferred from filename.

        Returns:
            The created Asset object with the public URL and metadata.

        Raises:
            NotFoundError: If the chapter does not exist.
            AuthorizationError: If you don't have appropriate access.
            ValidationError: If the file is invalid or exceeds size limits.
        """
        if content_type is None:
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        response = self._post_file(self._format_endpoint(Endpoints.BOOK_CHAPTER_ASSET_UPLOAD, chapter_id=chapter_id), file=(filename, content, content_type))
        return Asset.model_validate(response.json())

    def delete_asset(self, chapter_id: str, asset_id: str) -> None:
        """Delete an asset from a chapter.

        This action cannot be undone. The asset file is permanently removed.

        Args:
            chapter_id: The ID of the chapter that owns the asset.
            asset_id: The ID of the asset to delete.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        self._delete(self._format_endpoint(Endpoints.BOOK_CHAPTER_ASSET, chapter_id=chapter_id, asset_id=asset_id))
