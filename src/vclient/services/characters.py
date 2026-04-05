"""Service for interacting with the Characters API."""

import mimetypes
from collections.abc import AsyncIterator, Sequence
from typing import TYPE_CHECKING, Any

from vclient.constants import (
    DEFAULT_PAGE_LIMIT,
    CharacterClass,
    CharacterInclude,
    CharacterStatus,
    CharacterType,
)
from vclient.endpoints import Endpoints
from vclient.models import (
    Asset,
    Character,
    CharacterCreate,
    CharacterDetail,
    CharacterFullSheet,
    CharacterUpdate,
    FullSheetTraitCategory,
    InventoryItem,
    InventoryItemCreate,
    InventoryItemUpdate,
    Note,
    NoteCreate,
    NoteUpdate,
    PaginatedResponse,
    RollStatistics,
)
from vclient.services.base import BaseService

if TYPE_CHECKING:
    from vclient.client import VClient


class CharactersService(BaseService):
    """Service for managing characters within a campaign in the Valentina API.

    This service is scoped to a specific company, user, and campaign at initialization time.
    All methods operate within that context.

    Provides methods to create, retrieve, update, and delete characters.

    Example:
        >>> async with VClient() as client:
        ...     characters = client.characters("company_id", "user_id", "campaign_id")
        ...     all_characters = await characters.list_all()
        ...     character = await characters.get("character_id")
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
        """Format an endpoint with scoped IDs plus any extra params."""
        return endpoint.format(
            company_id=self._company_id,
            user_id=self._user_id,
            campaign_id=self._campaign_id,
            **kwargs,
        )

    # Character CRUD Methods

    async def get_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        user_player_id: str | None = None,
        user_creator_id: str | None = None,
        character_class: CharacterClass | None = None,
        character_type: CharacterType | None = None,
        status: CharacterStatus | None = None,
        is_temporary: bool = False,
    ) -> PaginatedResponse[Character]:
        """Retrieve a paginated page of characters.

        Args:
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).
            user_player_id: Filter by player user ID.
            user_creator_id: Filter by creator user ID.
            character_class: Filter by character class.
            character_type: Filter by character type.
            status: Filter by character status.
            is_temporary: Filter for temporary characters.

        Returns:
            A PaginatedResponse containing Character objects and pagination metadata.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CHARACTERS),
            Character,
            limit=limit,
            offset=offset,
            params=self._build_params(
                user_player_id=user_player_id,
                user_creator_id=user_creator_id,
                character_class=character_class,
                character_type=character_type,
                status=status,
                is_temporary=is_temporary,
            ),
        )

    async def list_all(
        self,
        *,
        user_player_id: str | None = None,
        user_creator_id: str | None = None,
        character_class: CharacterClass | None = None,
        character_type: CharacterType | None = None,
        status: CharacterStatus | None = None,
        is_temporary: bool = False,
    ) -> list[Character]:
        """Retrieve all characters.

        Automatically paginates through all results. Use `get_page()` for paginated access
        or `iter_all()` for memory-efficient streaming of large datasets.

        Args:
            user_player_id: Filter by player user ID.
            user_creator_id: Filter by creator user ID.
            character_class: Filter by character class.
            character_type: Filter by character type.
            status: Filter by character status.
            is_temporary: Filter for temporary characters.

        Returns:
            A list of all Character objects.
        """
        return [
            character
            async for character in self.iter_all(
                user_player_id=user_player_id,
                user_creator_id=user_creator_id,
                character_class=character_class,
                character_type=character_type,
                status=status,
                is_temporary=is_temporary,
            )
        ]

    async def iter_all(
        self,
        *,
        limit: int = 100,
        user_player_id: str | None = None,
        user_creator_id: str | None = None,
        character_class: CharacterClass | None = None,
        character_type: CharacterType | None = None,
        status: CharacterStatus | None = None,
        is_temporary: bool = False,
    ) -> AsyncIterator[Character]:
        """Iterate through all characters.

        Yields individual characters, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            limit: Items per page (default 100 for efficiency).
            user_player_id: Filter by player user ID.
            user_creator_id: Filter by creator user ID.
            character_class: Filter by character class.
            character_type: Filter by character type.
            status: Filter by character status.
            is_temporary: Whether to filter for temporary characters.

        Yields:
            Individual Character objects.

        Example:
            >>> async for character in characters.iter_all():
            ...     print(character.name)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.CHARACTERS),
            limit=limit,
            params=self._build_params(
                user_player_id=user_player_id,
                user_creator_id=user_creator_id,
                character_class=character_class,
                character_type=character_type,
                status=status,
                is_temporary=is_temporary,
            ),
        ):
            yield Character.model_validate(item)

    async def get(
        self,
        character_id: str,
        *,
        include: Sequence[CharacterInclude] | None = None,
    ) -> CharacterDetail:
        """Retrieve detailed information about a specific character.

        Fetches the character including traits, status, and biographical data.
        Optionally embed child resources directly in the response.

        Args:
            character_id: The ID of the character to retrieve.
            include: Child resources to embed in the response. Valid values are
                ``"traits"``, ``"inventory"``, ``"notes"``, and ``"assets"``.

        Returns:
            The CharacterDetail object with full details and any requested embeds.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have access.
        """
        params: dict[str, Any] = {}
        if include:
            params["include"] = list(include)

        response = await self._get(
            self._format_endpoint(Endpoints.CHARACTER, character_id=character_id),
            params=params or None,
        )
        return CharacterDetail.model_validate(response.json())

    async def create(
        self,
        request: CharacterCreate | None = None,
        **kwargs,
    ) -> Character:
        """Create a new character within the campaign.

        The character is associated with both a creator user (who made the character)
        and a player user (who controls the character). If no player is specified,
        the creator becomes the player.

        Args:
            request: A CharacterCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for CharacterCreate if request is not provided.
                Required: character_class (CharacterClass), game_version (GameVersion),
                name_first (str), name_last (str).
                Optional: type (CharacterType), name_nick (str), age (int),
                biography (str), demeanor (str), nature (str), concept_id (str),
                user_player_id (str), traits (list), vampire_attributes, etc.

        Returns:
            The newly created Character object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
            AuthorizationError: If you don't have appropriate access.
        """
        body = request if request is not None else self._validate_request(CharacterCreate, **kwargs)
        response = await self._post(
            self._format_endpoint(Endpoints.CHARACTERS),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Character.model_validate(response.json())

    async def update(
        self,
        character_id: str,
        request: CharacterUpdate | None = None,
        **kwargs,
    ) -> Character:
        """Modify a character's properties.

        Only include fields that need to be changed; omitted fields remain unchanged.
        Use trait-specific endpoints to modify character traits.

        Note: Only the character's player or a storyteller can update the character.

        Args:
            character_id: The ID of the character to update.
            request: A CharacterUpdate model, OR pass fields as keyword arguments.
            **kwargs: Fields for CharacterUpdate if request is not provided.
                All fields are optional: character_class, type, game_version, status,
                name_first, name_last, name_nick, age, biography, demeanor, nature,
                concept_id, user_player_id, vampire_attributes, werewolf_attributes, etc.

        Returns:
            The updated Character object.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(CharacterUpdate, **kwargs)
        response = await self._patch(
            self._format_endpoint(Endpoints.CHARACTER, character_id=character_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Character.model_validate(response.json())

    async def delete(self, character_id: str) -> None:
        """Remove a character from the campaign.

        The character will no longer be accessible. This action cannot be undone.

        Note: Only the character's player or a storyteller can delete the character.

        Args:
            character_id: The ID of the character to delete.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(self._format_endpoint(Endpoints.CHARACTER, character_id=character_id))

    async def get_statistics(
        self,
        character_id: str,
        *,
        num_top_traits: int = 5,
    ) -> RollStatistics:
        """Retrieve aggregated dice roll statistics for a specific character.

        Includes success rates, critical frequencies, most-used traits, etc.

        Args:
            character_id: The ID of the character to get statistics for.
            num_top_traits: Number of top traits to include (default 5).

        Returns:
            RollStatistics object with aggregated statistics.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.CHARACTER_STATISTICS, character_id=character_id),
            params={"num_top_traits": num_top_traits},
        )
        return RollStatistics.model_validate(response.json())

    async def get_full_sheet(
        self,
        character_id: str,
        *,
        include_available_traits: bool = False,
    ) -> CharacterFullSheet:
        """Retrieve the full character sheet with all traits organized hierarchically.

        Returns the character data along with the complete trait hierarchy organized as
        sections > categories > subcategories > character traits. Optionally include
        available traits the character could add.

        Args:
            character_id: The ID of the character to get the full sheet for.
            include_available_traits: Include unassigned standard traits in each
                category and subcategory. Defaults to False.

        Returns:
            CharacterFullSheet with nested trait hierarchy.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have access.
        """
        params = self._build_params(
            include_available_traits=include_available_traits or None,
        )
        response = await self._get(
            self._format_endpoint(Endpoints.CHARACTER_FULL_SHEET, character_id=character_id),
            params=params,
        )
        return CharacterFullSheet.model_validate(response.json())

    async def get_full_sheet_category(
        self,
        character_id: str,
        category_id: str,
        *,
        include_available_traits: bool = False,
    ) -> FullSheetTraitCategory:
        """Retrieve a single category slice of the character's full sheet.

        Fetch one category with its subcategories and traits, enabling efficient
        UI refreshes after a trait edit without rebuilding the entire sheet.

        Args:
            character_id: The ID of the character.
            category_id: The ID of the trait category to retrieve.
            include_available_traits: Include unassigned standard traits in the
                category and its subcategories. Defaults to False.

        Returns:
            FullSheetTraitCategory with nested subcategories and traits.

        Raises:
            NotFoundError: If the character or category does not exist.
            AuthorizationError: If you don't have access.
        """
        params = self._build_params(
            include_available_traits=include_available_traits or None,
        )
        response = await self._get(
            self._format_endpoint(
                Endpoints.CHARACTER_FULL_SHEET_CATEGORY,
                character_id=character_id,
                category_id=category_id,
            ),
            params=params,
        )
        return FullSheetTraitCategory.model_validate(response.json())

    # Asset Methods

    async def get_assets_page(
        self,
        character_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[Asset]:
        """Retrieve a paginated page of assets for a character.

        Args:
            character_id: The ID of the character whose assets to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Asset objects and pagination metadata.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have access.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CHARACTER_ASSETS, character_id=character_id),
            Asset,
            limit=limit,
            offset=offset,
        )

    async def list_all_assets(
        self,
        character_id: str,
    ) -> list[Asset]:
        """Retrieve all assets for a character.

        Automatically paginates through all results. Use `get_assets_page()` for paginated
        access or `iter_all_assets()` for memory-efficient streaming of large datasets.

        Args:
            character_id: The ID of the character whose assets to list.

        Returns:
            A list of all Asset objects.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have access.
        """
        return [asset async for asset in self.iter_all_assets(character_id)]

    async def iter_all_assets(
        self,
        character_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[Asset]:
        """Iterate through all assets for a character.

        Yields individual assets, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            character_id: The ID of the character whose assets to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Asset objects.

        Example:
            >>> async for asset in characters.iter_all_assets("character_id"):
            ...     print(asset.original_filename)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.CHARACTER_ASSETS, character_id=character_id),
            limit=limit,
        ):
            yield Asset.model_validate(item)

    async def get_asset(
        self,
        character_id: str,
        asset_id: str,
    ) -> Asset:
        """Retrieve details of a specific asset including its URL and metadata.

        Args:
            character_id: The ID of the character that owns the asset.
            asset_id: The ID of the asset to retrieve.

        Returns:
            The Asset object with full details.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.CHARACTER_ASSET, character_id=character_id, asset_id=asset_id
            )
        )
        return Asset.model_validate(response.json())

    async def delete_asset(
        self,
        character_id: str,
        asset_id: str,
    ) -> None:
        """Delete an asset from a campaign.

        This action cannot be undone. The asset file is permanently removed.

        Args:
            character_id: The ID of the character that owns the asset.
            asset_id: The ID of the asset to delete.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(
                Endpoints.CHARACTER_ASSET, character_id=character_id, asset_id=asset_id
            )
        )

    async def upload_asset(
        self,
        character_id: str,
        filename: str,
        content: bytes,
        content_type: str | None = None,
    ) -> Asset:
        """Upload a new asset for a campaign.

        Uploads a file to S3 storage and associates it with the campaign.

        Args:
            character_id: The ID of the character to upload the asset for.
            filename: The original filename of the asset.
            content: The raw bytes of the file to upload.
            content_type: The MIME type of the file. If not provided, inferred from filename.

        Returns:
            The created Asset object with the public URL and metadata.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have appropriate access.
            ValidationError: If the file is invalid or exceeds size limits.
        """
        if content_type is None:
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        response = await self._post_file(
            self._format_endpoint(Endpoints.CHARACTER_ASSET_UPLOAD, character_id=character_id),
            file=(filename, content, content_type),
        )
        return Asset.model_validate(response.json())

    # Notes Methods

    async def get_notes_page(
        self,
        character_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[Note]:
        """Retrieve a paginated page of notes for a character.

        Args:
            character_id: The ID of the character whose notes to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Note objects and pagination metadata.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have access.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CHARACTER_NOTES, character_id=character_id),
            Note,
            limit=limit,
            offset=offset,
        )

    async def list_all_notes(
        self,
        character_id: str,
    ) -> list[Note]:
        """Retrieve all notes for a character.

        Automatically paginates through all results. Use `get_notes_page()` for paginated
        access or `iter_all_notes()` for memory-efficient streaming of large datasets.

        Args:
            character_id: The ID of the character whose notes to list.

        Returns:
            A list of all Note objects.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have access.
        """
        return [note async for note in self.iter_all_notes(character_id)]

    async def iter_all_notes(
        self,
        character_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[Note]:
        """Iterate through all notes for a character.

        Yields individual notes, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            character_id: The ID of the character whose notes to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Note objects.

        Example:
            >>> async for note in characters.iter_all_notes("character_id"):
            ...     print(note.title)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.CHARACTER_NOTES, character_id=character_id),
            limit=limit,
        ):
            yield Note.model_validate(item)

    async def get_note(
        self,
        character_id: str,
        note_id: str,
    ) -> Note:
        """Retrieve a specific note including its content and metadata.

        Args:
            character_id: The ID of the character that owns the note.
            note_id: The ID of the note to retrieve.

        Returns:
            The Note object with full details.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.CHARACTER_NOTE, character_id=character_id, note_id=note_id
            )
        )
        return Note.model_validate(response.json())

    async def create_note(
        self,
        character_id: str,
        request: NoteCreate | None = None,
        **kwargs,
    ) -> Note:
        """Create a new note for a character.

        Notes support markdown formatting for rich text content.

        Args:
            character_id: The ID of the character to create the note for.
            request: A NoteCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for NoteCreate if request is not provided.
                Accepts: title (str, required), content (str, required).

        Returns:
            The newly created Note object.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(NoteCreate, **kwargs)
        response = await self._post(
            self._format_endpoint(Endpoints.CHARACTER_NOTES, character_id=character_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Note.model_validate(response.json())

    async def update_note(
        self,
        character_id: str,
        note_id: str,
        request: NoteUpdate | None = None,
        **kwargs,
    ) -> Note:
        """Modify a note's content.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            character_id: The ID of the character that owns the note.
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
            self._format_endpoint(
                Endpoints.CHARACTER_NOTE, character_id=character_id, note_id=note_id
            ),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Note.model_validate(response.json())

    async def delete_note(
        self,
        character_id: str,
        note_id: str,
    ) -> None:
        """Remove a note from a character.

        This action cannot be undone.

        Args:
            character_id: The ID of the character that owns the note.
            note_id: The ID of the note to delete.

        Raises:
            NotFoundError: If the note does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(
                Endpoints.CHARACTER_NOTE, character_id=character_id, note_id=note_id
            )
        )

    # Character Inventory Methods

    async def get_inventory_page(
        self,
        character_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[InventoryItem]:
        """Retrieve a paginated page of inventory items for a character.

        Args:
            character_id: The ID of the character whose inventory items to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing InventoryItem objects and pagination metadata.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have access.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CHARACTER_INVENTORY, character_id=character_id),
            InventoryItem,
            limit=limit,
            offset=offset,
        )

    async def list_all_inventory(
        self,
        character_id: str,
    ) -> list[InventoryItem]:
        """Retrieve all notes for a character.

        Automatically paginates through all results. Use `get_inventory_page()` for paginated
        access or `iter_all_inventory()` for memory-efficient streaming of large datasets.

        Args:
            character_id: The ID of the character whose inventory items to list.

        Returns:
            A list of all InventoryItem objects.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have access.
        """
        return [item async for item in self.iter_all_inventory(character_id)]

    async def iter_all_inventory(
        self,
        character_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[InventoryItem]:
        """Iterate through all inventory items for a character.

        Yields individual inventory items, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            character_id: The ID of the character whose inventory items to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual InventoryItem objects.

        Example:
            >>> async for item in characters.iter_all_inventory("character_id"):
            ...     print(item.name)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.CHARACTER_INVENTORY, character_id=character_id),
            limit=limit,
        ):
            yield InventoryItem.model_validate(item)

    async def get_inventory_item(
        self,
        character_id: str,
        item_id: str,
    ) -> InventoryItem:
        """Retrieve a specific inventory item including its content and metadata.

        Args:
            character_id: The ID of the character that owns the inventory item.
            item_id: The ID of the inventory item to retrieve.

        Returns:
            The InventoryItem object with full details.

        Raises:
            NotFoundError: If the inventory item does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.CHARACTER_INVENTORY_ITEM, character_id=character_id, item_id=item_id
            )
        )
        return InventoryItem.model_validate(response.json())

    async def create_inventory_item(
        self,
        character_id: str,
        request: InventoryItemCreate | None = None,
        **kwargs,
    ) -> InventoryItem:
        """Create a new inventory item for a character.

        Args:
            character_id: The ID of the character to create the inventory item for.
            request: An InventoryItemCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for InventoryItemCreate if request is not provided.
                Accepts: name (str, required), type (CharacterInventoryType, required),
                description (str | None).

        Returns:
            The newly created InventoryItem object.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = (
            request
            if request is not None
            else self._validate_request(InventoryItemCreate, **kwargs)
        )
        response = await self._post(
            self._format_endpoint(Endpoints.CHARACTER_INVENTORY, character_id=character_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return InventoryItem.model_validate(response.json())

    async def update_inventory_item(
        self,
        character_id: str,
        item_id: str,
        request: InventoryItemUpdate | None = None,
        **kwargs,
    ) -> InventoryItem:
        """Modify an inventory item's content.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            character_id: The ID of the character that owns the inventory item.
            item_id: The ID of the inventory item to update.
            request: An InventoryItemUpdate model, OR pass fields as keyword arguments.
            **kwargs: Fields for InventoryItemUpdate if request is not provided.
                Accepts: name (str | None), type (CharacterInventoryType | None),
                description (str | None).

        Returns:
            The updated InventoryItem object.

        Raises:
            NotFoundError: If the inventory item does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = (
            request
            if request is not None
            else self._validate_request(InventoryItemUpdate, **kwargs)
        )
        response = await self._patch(
            self._format_endpoint(
                Endpoints.CHARACTER_INVENTORY_ITEM, character_id=character_id, item_id=item_id
            ),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return InventoryItem.model_validate(response.json())

    async def delete_inventory_item(
        self,
        character_id: str,
        item_id: str,
    ) -> None:
        """Remove an inventory item from a character.

        This action cannot be undone.

        Args:
            character_id: The ID of the character that owns the inventory item.
            item_id: The ID of the inventory item to delete.

        Raises:
            NotFoundError: If the inventory item does not exist.
            AuthorizationError: If you don't have appropriate access.
        """
        await self._delete(
            self._format_endpoint(
                Endpoints.CHARACTER_INVENTORY_ITEM, character_id=character_id, item_id=item_id
            )
        )
