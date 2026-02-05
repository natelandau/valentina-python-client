"""Service for interacting with the Campaign Books API."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from vclient.constants import DEFAULT_PAGE_LIMIT
from vclient.endpoints import Endpoints
from vclient.models import (
    BookCreate,
    BookUpdate,
    CampaignBook,
    Note,
    NoteCreate,
    NoteUpdate,
    PaginatedResponse,
    S3Asset,
    _BookRenumber,
)
from vclient.services.base import BaseService

if TYPE_CHECKING:
    from vclient.client import VClient


class BooksService(BaseService):
    """Service for managing campaign books within a campaign in the Valentina API.

    This service is scoped to a specific company, user, and campaign at initialization time.
    All methods operate within that context.

    Provides methods to create, retrieve, update, and delete campaign books,
    as well as access book notes and assets.

    Example:
        >>> async with VClient() as client:
        ...     books = client.books("company_id", "user_id", "campaign_id")
        ...     all_books = await books.list_all()
        ...     book = await books.get("book_id")
    """

    def __init__(self, client: "VClient", company_id: str, user_id: str, campaign_id: str) -> None:
        """Initialize the service scoped to a specific company, user, and campaign.

        Args:
            client: The VClient instance to use for requests.
            company_id: The ID of the company to operate within.
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.
        """
        super().__init__(client)
        self._company_id = company_id
        self._user_id = user_id
        self._campaign_id = campaign_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id, user_id, campaign_id plus any extra params."""
        return endpoint.format(
            company_id=self._company_id,
            user_id=self._user_id,
            campaign_id=self._campaign_id,
            **kwargs,
        )

    # -------------------------------------------------------------------------
    # Book CRUD Methods
    # -------------------------------------------------------------------------

    async def get_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[CampaignBook]:
        """Retrieve a paginated page of campaign books.

        Args:
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing CampaignBook objects and pagination metadata.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CAMPAIGN_BOOKS),
            CampaignBook,
            limit=limit,
            offset=offset,
        )

    async def list_all(self) -> list[CampaignBook]:
        """Retrieve all campaign books.

        Automatically paginates through all results. Use `get_page()` for paginated access
        or `iter_all()` for memory-efficient streaming of large datasets.

        Returns:
            A list of all CampaignBook objects.
        """
        return [book async for book in self.iter_all()]

    async def iter_all(
        self,
        *,
        limit: int = 100,
    ) -> AsyncIterator[CampaignBook]:
        """Iterate through all campaign books.

        Yields individual books, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual CampaignBook objects.

        Example:
            >>> async for book in books.iter_all():
            ...     print(book.name)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.CAMPAIGN_BOOKS),
            limit=limit,
        ):
            yield CampaignBook.model_validate(item)

    async def get(self, book_id: str) -> CampaignBook:
        """Retrieve detailed information about a specific campaign book.

        Fetches the book including its notes and assets.

        Args:
            book_id: The ID of the book to retrieve.

        Returns:
            The CampaignBook object with full details.

        Raises:
            NotFoundError: If the book does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(self._format_endpoint(Endpoints.CAMPAIGN_BOOK, book_id=book_id))
        return CampaignBook.model_validate(response.json())

    async def create(
        self,
        name: str,
        *,
        description: str | None = None,
    ) -> CampaignBook:
        """Create a new campaign book.

        Args:
            name: Book name (3-50 characters).
            description: Optional book description (minimum 3 characters).

        Returns:
            The newly created CampaignBook object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
            AuthorizationError: If you don't have book management privileges.
        """
        body = self._validate_request(
            BookCreate,
            name=name,
            description=description,
        )
        response = await self._post(
            self._format_endpoint(Endpoints.CAMPAIGN_BOOKS),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return CampaignBook.model_validate(response.json())

    async def update(
        self,
        book_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> CampaignBook:
        """Modify a campaign book's properties.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            book_id: The ID of the book to update.
            name: New book name (3-50 characters).
            description: New book description (minimum 3 characters).

        Returns:
            The updated CampaignBook object.

        Raises:
            NotFoundError: If the book does not exist.
            AuthorizationError: If you don't have book management privileges.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            BookUpdate,
            name=name,
            description=description,
        )
        response = await self._patch(
            self._format_endpoint(Endpoints.CAMPAIGN_BOOK, book_id=book_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return CampaignBook.model_validate(response.json())

    async def delete(self, book_id: str) -> None:
        """Remove a campaign book from the system.

        Associated notes and assets will no longer be accessible.
        This action cannot be undone.

        Args:
            book_id: The ID of the book to delete.

        Raises:
            NotFoundError: If the book does not exist.
            AuthorizationError: If you don't have book management privileges.
        """
        await self._delete(self._format_endpoint(Endpoints.CAMPAIGN_BOOK, book_id=book_id))

    async def renumber(self, book_id: str, number: int) -> CampaignBook:
        """Change the book's position number within the campaign.

        Renumbering a book will shift other books as needed to maintain
        a contiguous sequence.

        Args:
            book_id: The ID of the book to renumber.
            number: New book number (must be >= 1).

        Returns:
            The updated CampaignBook object with the new number.

        Raises:
            NotFoundError: If the book does not exist.
            AuthorizationError: If you don't have book management privileges.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(_BookRenumber, number=number)
        response = await self._put(
            self._format_endpoint(Endpoints.CAMPAIGN_BOOK_NUMBER, book_id=book_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return CampaignBook.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Notes Methods
    # -------------------------------------------------------------------------

    async def get_notes_page(
        self,
        book_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[Note]:
        """Retrieve a paginated page of notes for a book.

        Args:
            book_id: The ID of the book whose notes to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Note objects and pagination metadata.

        Raises:
            NotFoundError: If the book does not exist.
            AuthorizationError: If you don't have access.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.BOOK_NOTES, book_id=book_id),
            Note,
            limit=limit,
            offset=offset,
        )

    async def list_all_notes(
        self,
        book_id: str,
    ) -> list[Note]:
        """Retrieve all notes for a book.

        Automatically paginates through all results. Use `get_notes_page()` for paginated
        access or `iter_all_notes()` for memory-efficient streaming of large datasets.

        Args:
            book_id: The ID of the book whose notes to list.

        Returns:
            A list of all Note objects.

        Raises:
            NotFoundError: If the book does not exist.
            AuthorizationError: If you don't have access.
        """
        return [note async for note in self.iter_all_notes(book_id)]

    async def iter_all_notes(
        self,
        book_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[Note]:
        """Iterate through all notes for a book.

        Yields individual notes, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            book_id: The ID of the book whose notes to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Note objects.

        Example:
            >>> async for note in books.iter_all_notes("book_id"):
            ...     print(note.title)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.BOOK_NOTES, book_id=book_id),
            limit=limit,
        ):
            yield Note.model_validate(item)

    async def get_note(
        self,
        book_id: str,
        note_id: str,
    ) -> Note:
        """Retrieve a specific note including its content and metadata.

        Args:
            book_id: The ID of the book that owns the note.
            note_id: The ID of the note to retrieve.

        Returns:
            The Note object with full details.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.BOOK_NOTE, book_id=book_id, note_id=note_id)
        )
        return Note.model_validate(response.json())

    async def create_note(
        self,
        book_id: str,
        title: str,
        content: str,
    ) -> Note:
        """Create a new note for a book.

        Notes support markdown formatting for rich text content.

        Args:
            book_id: The ID of the book to create the note for.
            title: The note title (3-50 characters).
            content: The note content (minimum 3 characters, supports markdown).

        Returns:
            The newly created Note object.

        Raises:
            NotFoundError: If the book does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            NoteCreate,
            title=title,
            content=content,
        )
        response = await self._post(
            self._format_endpoint(Endpoints.BOOK_NOTES, book_id=book_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Note.model_validate(response.json())

    async def update_note(
        self,
        book_id: str,
        note_id: str,
        *,
        title: str | None = None,
        content: str | None = None,
    ) -> Note:
        """Modify a note's content.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            book_id: The ID of the book that owns the note.
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
            NoteUpdate,
            title=title,
            content=content,
        )
        response = await self._patch(
            self._format_endpoint(Endpoints.BOOK_NOTE, book_id=book_id, note_id=note_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Note.model_validate(response.json())

    async def delete_note(
        self,
        book_id: str,
        note_id: str,
    ) -> None:
        """Remove a note from a book.

        This action cannot be undone.

        Args:
            book_id: The ID of the book that owns the note.
            note_id: The ID of the note to delete.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(Endpoints.BOOK_NOTE, book_id=book_id, note_id=note_id)
        )

    # -------------------------------------------------------------------------
    # Asset Methods
    # -------------------------------------------------------------------------

    async def list_assets(
        self,
        book_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[S3Asset]:
        """Retrieve a paginated list of assets for a book.

        Args:
            book_id: The ID of the book whose assets to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing S3Asset objects and pagination metadata.

        Raises:
            NotFoundError: If the book does not exist.
            AuthorizationError: If you don't have access.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.BOOK_ASSETS, book_id=book_id),
            S3Asset,
            limit=limit,
            offset=offset,
        )

    async def get_asset(
        self,
        book_id: str,
        asset_id: str,
    ) -> S3Asset:
        """Retrieve details of a specific asset including its URL and metadata.

        Args:
            book_id: The ID of the book that owns the asset.
            asset_id: The ID of the asset to retrieve.

        Returns:
            The S3Asset object with full details.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.BOOK_ASSET, book_id=book_id, asset_id=asset_id)
        )
        return S3Asset.model_validate(response.json())

    async def upload_asset(
        self,
        book_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> S3Asset:
        """Upload a new asset for a book.

        Uploads a file to S3 storage and associates it with the book.

        Args:
            book_id: The ID of the book to upload the asset for.
            filename: The original filename of the asset.
            content: The raw bytes of the file to upload.
            content_type: The MIME type of the file (default: application/octet-stream).

        Returns:
            The created S3Asset object with the public URL and metadata.

        Raises:
            NotFoundError: If the book does not exist.
            AuthorizationError: If you don't have appropriate access.
            ValidationError: If the file is invalid or exceeds size limits.
        """
        response = await self._post_file(
            self._format_endpoint(Endpoints.BOOK_ASSET_UPLOAD, book_id=book_id),
            file=(filename, content, content_type),
        )
        return S3Asset.model_validate(response.json())

    async def delete_asset(
        self,
        book_id: str,
        asset_id: str,
    ) -> None:
        """Delete an asset from a book.

        This action cannot be undone. The asset file is permanently removed.

        Args:
            book_id: The ID of the book that owns the asset.
            asset_id: The ID of the asset to delete.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(Endpoints.BOOK_ASSET, book_id=book_id, asset_id=asset_id)
        )
