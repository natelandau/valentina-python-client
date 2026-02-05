"""Service for interacting with the Characters API."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from vclient.constants import (
    DEFAULT_PAGE_LIMIT,
    CharacterClass,
    CharacterInventoryType,
    CharacterStatus,
    CharacterType,
    GameVersion,
)
from vclient.endpoints import Endpoints
from vclient.models import (
    AssignCharacterTraitRequest,
    Character,
    CharacterCreate,
    CharacterUpdate,
    EdgeAndPerks,
    HunterAttributesCreate,
    HunterAttributesUpdate,
    InventoryItem,
    InventoryItemCreate,
    InventoryItemUpdate,
    MageAttributes,
    Note,
    NoteCreate,
    NoteUpdate,
    PaginatedResponse,
    Perk,
    RollStatistics,
    S3Asset,
    VampireAttributesCreate,
    VampireAttributesUpdate,
    WerewolfAttributesCreate,
    WerewolfAttributesUpdate,
    WerewolfGift,
    WerewolfRite,
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

    # -------------------------------------------------------------------------
    # Character CRUD Methods
    # -------------------------------------------------------------------------

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

        Returns:
            A PaginatedResponse containing Character objects and pagination metadata.
        """
        params: dict[str, str | int] = {}
        if user_player_id is not None:
            params["user_player_id"] = user_player_id
        if user_creator_id is not None:
            params["user_creator_id"] = user_creator_id
        if character_class is not None:
            params["character_class"] = character_class
        if character_type is not None:
            params["character_type"] = character_type
        if status is not None:
            params["status"] = status

        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CHARACTERS),
            Character,
            limit=limit,
            offset=offset,
            params=params if params else None,
        )

    async def list_all(
        self,
        *,
        user_player_id: str | None = None,
        user_creator_id: str | None = None,
        character_class: CharacterClass | None = None,
        character_type: CharacterType | None = None,
        status: CharacterStatus | None = None,
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

        Yields:
            Individual Character objects.

        Example:
            >>> async for character in characters.iter_all():
            ...     print(character.name)
        """
        params: dict[str, str | int] = {}
        if user_player_id is not None:
            params["user_player_id"] = user_player_id
        if user_creator_id is not None:
            params["user_creator_id"] = user_creator_id
        if character_class is not None:
            params["character_class"] = character_class
        if character_type is not None:
            params["character_type"] = character_type
        if status is not None:
            params["status"] = status

        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.CHARACTERS),
            limit=limit,
            params=params if params else None,
        ):
            yield Character.model_validate(item)

    async def get(self, character_id: str) -> Character:
        """Retrieve detailed information about a specific character.

        Fetches the character including traits, status, and biographical data.

        Args:
            character_id: The ID of the character to retrieve.

        Returns:
            The Character object with full details.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.CHARACTER, character_id=character_id)
        )
        return Character.model_validate(response.json())

    async def create(
        self,
        *,
        age: int | None = None,
        biography: str | None = None,
        character_class: CharacterClass,
        character_type: CharacterType | None = None,
        concept_id: str | None = None,
        demeanor: str | None = None,
        game_version: GameVersion,
        name_first: str,
        name_last: str,
        name_nick: str | None = None,
        nature: str | None = None,
        user_player_id: str | None = None,
        traits: list[AssignCharacterTraitRequest] | None = None,
        vampire_attributes: VampireAttributesCreate | None = None,
        werewolf_attributes: WerewolfAttributesCreate | None = None,
        hunter_attributes: HunterAttributesCreate | None = None,
        mage_attributes: MageAttributes | None = None,
    ) -> Character:
        """Create a new character within the campaign.

        The character is associated with both a creator user (who made the character)
        and a player user (who controls the character). If no player is specified,
        the creator becomes the player.

        Args:
            age: Character's age.
            biography: Character biography (minimum 3 characters).
            character_class: Character class (VAMPIRE, WEREWOLF, MAGE, etc.).
            character_type: Character type (PLAYER, NPC, STORYTELLER, DEVELOPER).
            concept_id: ID of the character concept.
            demeanor: Character's demeanor (3-50 characters).
            game_version: Game version for character sheet (V4 or V5).
            hunter_attributes: Hunter-specific attributes.
            name_first: Character's first name (minimum 3 characters).
            name_last: Character's last name (minimum 3 characters).
            name_nick: Character's nickname (3-50 characters).
            nature: Character's nature (3-50 characters).
            user_player_id: ID of the user who will play the character.
            traits: List of traits to assign to the character.
            vampire_attributes: Vampire-specific attributes.
            werewolf_attributes: Werewolf-specific attributes.
            mage_attributes: Mage-specific attributes.

        Returns:
            The newly created Character object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
            AuthorizationError: If you don't have appropriate access.
        """
        body = self._validate_request(
            CharacterCreate,
            character_class=character_class,
            game_version=game_version,
            name_first=name_first,
            name_last=name_last,
            type=character_type,
            name_nick=name_nick,
            age=age,
            biography=biography,
            demeanor=demeanor,
            nature=nature,
            concept_id=concept_id,
            user_player_id=user_player_id,
            traits=traits,
            vampire_attributes=vampire_attributes,
            werewolf_attributes=werewolf_attributes,
            hunter_attributes=hunter_attributes,
            mage_attributes=mage_attributes,
        )
        response = await self._post(
            self._format_endpoint(Endpoints.CHARACTERS),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Character.model_validate(response.json())

    async def update(
        self,
        character_id: str,
        *,
        character_class: CharacterClass | None = None,
        character_type: CharacterType | None = None,
        game_version: GameVersion | None = None,
        status: CharacterStatus | None = None,
        name_first: str | None = None,
        name_last: str | None = None,
        name_nick: str | None = None,
        age: int | None = None,
        biography: str | None = None,
        demeanor: str | None = None,
        nature: str | None = None,
        concept_id: str | None = None,
        user_player_id: str | None = None,
        vampire_attributes: VampireAttributesUpdate | None = None,
        werewolf_attributes: WerewolfAttributesUpdate | None = None,
        mage_attributes: MageAttributes | None = None,
        hunter_attributes: HunterAttributesUpdate | None = None,
    ) -> Character:
        """Modify a character's properties.

        Only include fields that need to be changed; omitted fields remain unchanged.
        Use trait-specific endpoints to modify character traits.

        Note: Only the character's player or a storyteller can update the character.

        Args:
            character_id: The ID of the character to update.
            character_class: New character class.
            character_type: New character type.
            game_version: New game version.
            hunter_attributes: Hunter-specific attributes.
            status: New character status (ALIVE or DEAD).
            name_first: New first name (minimum 3 characters).
            name_last: New last name (minimum 3 characters).
            name_nick: New nickname (3-50 characters).
            age: New age.
            biography: New biography (minimum 3 characters).
            demeanor: New demeanor (3-50 characters).
            nature: New nature (3-50 characters).
            concept_id: New concept ID.
            user_player_id: New player user ID.
            vampire_attributes: Vampire-specific attributes.
            werewolf_attributes: Werewolf-specific attributes.
            mage_attributes: Mage-specific attributes.
            hunter_attributes: Hunter-specific attributes.

        Returns:
            The updated Character object.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            CharacterUpdate,
            character_class=character_class,
            type=character_type,
            game_version=game_version,
            status=status,
            name_first=name_first,
            name_last=name_last,
            name_nick=name_nick,
            age=age,
            biography=biography,
            demeanor=demeanor,
            nature=nature,
            concept_id=concept_id,
            user_player_id=user_player_id,
            vampire_attributes=vampire_attributes,
            werewolf_attributes=werewolf_attributes,
            hunter_attributes=hunter_attributes,
            mage_attributes=mage_attributes,
        )
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

    # -------------------------------------------------------------------------
    # Asset Methods
    # -------------------------------------------------------------------------

    async def list_assets(
        self,
        character_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[S3Asset]:
        """Retrieve a paginated list of assets for a campaign.

        Args:
            character_id: The ID of the character whose assets to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing S3Asset objects and pagination metadata.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have access.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CHARACTER_ASSETS, character_id=character_id),
            S3Asset,
            limit=limit,
            offset=offset,
        )

    async def get_asset(
        self,
        character_id: str,
        asset_id: str,
    ) -> S3Asset:
        """Retrieve details of a specific asset including its URL and metadata.

        Args:
            character_id: The ID of the character that owns the asset.
            asset_id: The ID of the asset to retrieve.

        Returns:
            The S3Asset object with full details.

        Raises:
            NotFoundError: If the asset does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.CHARACTER_ASSET, character_id=character_id, asset_id=asset_id
            )
        )
        return S3Asset.model_validate(response.json())

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
        content_type: str = "application/octet-stream",
    ) -> S3Asset:
        """Upload a new asset for a campaign.

        Uploads a file to S3 storage and associates it with the campaign.

        Args:
            character_id: The ID of the character to upload the asset for.
            filename: The original filename of the asset.
            content: The raw bytes of the file to upload.
            content_type: The MIME type of the file (default: application/octet-stream).

        Returns:
            The created S3Asset object with the public URL and metadata.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have appropriate access.
            ValidationError: If the file is invalid or exceeds size limits.
        """
        response = await self._post_file(
            self._format_endpoint(Endpoints.CHARACTER_ASSET_UPLOAD, character_id=character_id),
            file=(filename, content, content_type),
        )
        return S3Asset.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Notes Methods
    # -------------------------------------------------------------------------

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
        title: str,
        content: str,
    ) -> Note:
        """Create a new note for a character.

        Notes support markdown formatting for rich text content.

        Args:
            character_id: The ID of the character to create the note for.
            title: The note title (3-50 characters).
            content: The note content (minimum 3 characters, supports markdown).

        Returns:
            The newly created Note object.

        Raises:
            NotFoundError: If the character does not exist.
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
            self._format_endpoint(Endpoints.CHARACTER_NOTES, character_id=character_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Note.model_validate(response.json())

    async def update_note(
        self,
        character_id: str,
        note_id: str,
        *,
        title: str | None = None,
        content: str | None = None,
    ) -> Note:
        """Modify a note's content.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            character_id: The ID of the character that owns the note.
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

    # -------------------------------------------------------------------------
    # Character Inventory Methods
    # -------------------------------------------------------------------------

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
        name: str,
        type: CharacterInventoryType,  # noqa: A002
        description: str | None = None,
    ) -> InventoryItem:
        """Create a new inventory item for a character.

        Args:
            character_id: The ID of the character to create the inventory item for.
            name: The name of the inventory item (3-50 characters).
            type: The type of the inventory item.
            description: The description of the inventory item (minimum 3 characters, supports markdown).

        Returns:
            The newly created InventoryItem object.

        Raises:
            NotFoundError: If the character does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            InventoryItemCreate,
            name=name,
            type=type,
            description=description,
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
        *,
        name: str | None = None,
        type: CharacterInventoryType | None = None,  # noqa: A002
        description: str | None = None,
    ) -> InventoryItem:
        """Modify an inventory item's content.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            character_id: The ID of the character that owns the inventory item.
            item_id: The ID of the inventory item to update.
            name: New inventory item name (3-50 characters).
            type: New inventory item type.
            description: New inventory item description (minimum 3 characters, supports markdown).

        Returns:
            The updated InventoryItem object.

        Raises:
            NotFoundError: If the inventory item does not exist.
            AuthorizationError: If you don't have appropriate access.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            InventoryItemUpdate,
            name=name,
            type=type,
            description=description,
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

    # -------------------------------------------------------------------------
    # Werewolf Gift Methods
    # -------------------------------------------------------------------------

    async def get_gifts_page(
        self,
        character_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[WerewolfGift]:
        """Retrieve a paginated page of werewolf gifts for a character.

        Args:
            character_id: The ID of the character whose werewolf gifts to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing WerewolfGift objects and pagination metadata.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CHARACTER_WEREWOLF_GIFTS, character_id=character_id),
            WerewolfGift,
            limit=limit,
            offset=offset,
        )

    async def list_all_gifts(
        self,
        character_id: str,
    ) -> list[WerewolfGift]:
        """Retrieve all werewolf gifts for a character.

        Automatically paginates through all results. Use `get_gifts_page()` for paginated
        access or `iter_all_gifts()` for memory-efficient streaming of large datasets.

        Args:
            character_id: The ID of the character whose werewolf gifts to list.

        Returns:
            A list of all WerewolfGift objects.
        """
        return [gift async for gift in self.iter_all_gifts(character_id)]

    async def iter_all_gifts(
        self,
        character_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[WerewolfGift]:
        """Iterate through all werewolf gifts for a character.

        Yields individual werewolf gifts, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            character_id: The ID of the character whose werewolf gifts to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual WerewolfGift objects.
        """
        async for gift in self._iter_all_pages(
            self._format_endpoint(Endpoints.CHARACTER_WEREWOLF_GIFTS, character_id=character_id),
            limit=limit,
        ):
            yield WerewolfGift.model_validate(gift)

    async def get_gift(
        self,
        character_id: str,
        werewolf_gift_id: str,
    ) -> WerewolfGift:
        """Retrieve a specific werewolf gift including its content and metadata.

        Args:
            character_id: The ID of the character that owns the werewolf gift.
            werewolf_gift_id: The ID of the werewolf gift to retrieve.

        Returns:
            The WerewolfGift object with full details.

        Raises:
            NotFoundError: If the werewolf gift does not exist.
            AuthorizationError: If you don't have access.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.CHARACTER_WEREWOLF_GIFT_DETAIL,
                character_id=character_id,
                werewolf_gift_id=werewolf_gift_id,
            )
        )

        return WerewolfGift.model_validate(response.json())

    async def add_gift(
        self,
        character_id: str,
        werewolf_gift_id: str,
    ) -> WerewolfGift:
        """Add a werewolf gift to a character.

        Args:
            character_id: The ID of the character to add the werewolf gift to.
            werewolf_gift_id: The ID of the werewolf gift to add.
        """
        response = await self._post(
            self._format_endpoint(
                Endpoints.CHARACTER_WEREWOLF_GIFT_DETAIL,
                character_id=character_id,
                werewolf_gift_id=werewolf_gift_id,
            )
        )
        return WerewolfGift.model_validate(response.json())

    async def remove_gift(
        self,
        character_id: str,
        werewolf_gift_id: str,
    ) -> WerewolfGift:
        """Remove a werewolf gift from a character.

        Args:
            character_id: The ID of the character to remove the werewolf gift from.
            werewolf_gift_id: The ID of the werewolf gift to remove.
        """
        response = await self._delete(
            self._format_endpoint(
                Endpoints.CHARACTER_WEREWOLF_GIFT_DETAIL,
                character_id=character_id,
                werewolf_gift_id=werewolf_gift_id,
            )
        )
        return WerewolfGift.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Werewolf Rite Methods
    # -------------------------------------------------------------------------
    async def get_rites_page(
        self,
        character_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[WerewolfRite]:
        """Retrieve a paginated page of werewolf rites for a character.

        Args:
            character_id: The ID of the character whose werewolf rites to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing WerewolfRite objects and pagination metadata.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CHARACTER_WEREWOLF_RITES, character_id=character_id),
            WerewolfRite,
            limit=limit,
            offset=offset,
        )

    async def list_all_rites(
        self,
        character_id: str,
    ) -> list[WerewolfRite]:
        """Retrieve all werewolf rites for a character.

        Automatically paginates through all results. Use `get_rites_page()` for paginated
        access or `iter_all_rites()` for memory-efficient streaming of large datasets.

        Args:
            character_id: The ID of the character whose werewolf rites to list.

        Returns:
            A list of all WerewolfRite objects.
        """
        return [rite async for rite in self.iter_all_rites(character_id)]

    async def iter_all_rites(
        self,
        character_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[WerewolfRite]:
        """Iterate through all werewolf rites for a character.

        Yields individual werewolf rites, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            character_id: The ID of the character whose werewolf rites to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual WerewolfRite objects.
        """
        async for rite in self._iter_all_pages(
            self._format_endpoint(Endpoints.CHARACTER_WEREWOLF_RITES, character_id=character_id),
            limit=limit,
        ):
            yield WerewolfRite.model_validate(rite)

    async def get_rite(
        self,
        character_id: str,
        werewolf_rite_id: str,
    ) -> WerewolfRite:
        """Retrieve a specific werewolf rite including its content and metadata.

        Args:
            character_id: The ID of the character that owns the werewolf rite.
            werewolf_rite_id: The ID of the werewolf rite to retrieve.

        Returns:
            The WerewolfRite object with full details.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.CHARACTER_WEREWOLF_RITE_DETAIL,
                character_id=character_id,
                werewolf_rite_id=werewolf_rite_id,
            )
        )
        return WerewolfRite.model_validate(response.json())

    async def add_rite(
        self,
        character_id: str,
        werewolf_rite_id: str,
    ) -> WerewolfRite:
        """Add a werewolf rite to a character.

        Args:
            character_id: The ID of the character to add the werewolf rite to.
            werewolf_rite_id: The ID of the werewolf rite to add.
        """
        response = await self._post(
            self._format_endpoint(
                Endpoints.CHARACTER_WEREWOLF_RITE_DETAIL,
                character_id=character_id,
                werewolf_rite_id=werewolf_rite_id,
            )
        )
        return WerewolfRite.model_validate(response.json())

    async def remove_rite(
        self,
        character_id: str,
        werewolf_rite_id: str,
    ) -> WerewolfRite:
        """Remove a werewolf rite from a character.

        Args:
            character_id: The ID of the character to remove the werewolf rite from.
            werewolf_rite_id: The ID of the werewolf rite to remove.
        """
        response = await self._delete(
            self._format_endpoint(
                Endpoints.CHARACTER_WEREWOLF_RITE_DETAIL,
                character_id=character_id,
                werewolf_rite_id=werewolf_rite_id,
            )
        )
        return WerewolfRite.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Hunter Edge Methods
    # -------------------------------------------------------------------------
    async def get_edges_page(
        self,
        character_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[EdgeAndPerks]:
        """Retrieve a paginated page of hunter edges for a character.

        Args:
            character_id: The ID of the character whose hunter edges to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing EdgeAndPerks objects and pagination metadata.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CHARACTER_HUNTER_EDGES, character_id=character_id),
            EdgeAndPerks,
            limit=limit,
            offset=offset,
        )

    async def list_all_edges(
        self,
        character_id: str,
    ) -> list[EdgeAndPerks]:
        """Retrieve all hunter edges for a character.

        Automatically paginates through all results. Use `get_edges_page()` for paginated
        access or `iter_all_edges()` for memory-efficient streaming of large datasets.
        """
        return [edge async for edge in self.iter_all_edges(character_id)]

    async def iter_all_edges(
        self,
        character_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[EdgeAndPerks]:
        """Iterate through all hunter edges for a character.

        Yields individual hunter edges, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            character_id: The ID of the character whose hunter edges to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual EdgeAndPerks objects.
        """
        async for edge in self._iter_all_pages(
            self._format_endpoint(Endpoints.CHARACTER_HUNTER_EDGES, character_id=character_id),
            limit=limit,
        ):
            yield EdgeAndPerks.model_validate(edge)

    async def get_edge(
        self,
        character_id: str,
        hunter_edge_id: str,
    ) -> EdgeAndPerks:
        """Retrieve a specific hunter edge including its perks.

        Args:
            character_id: The ID of the character that owns the hunter edge.
            hunter_edge_id: The ID of the hunter edge to retrieve.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.CHARACTER_HUNTER_EDGE_DETAIL,
                character_id=character_id,
                hunter_edge_id=hunter_edge_id,
            )
        )
        return EdgeAndPerks.model_validate(response.json())

    async def add_edge(
        self,
        character_id: str,
        hunter_edge_id: str,
    ) -> EdgeAndPerks:
        """Add a hunter edge to a character.

        Args:
            character_id: The ID of the character to add the hunter edge to.
            hunter_edge_id: The ID of the hunter edge to add.
        """
        response = await self._post(
            self._format_endpoint(
                Endpoints.CHARACTER_HUNTER_EDGE_DETAIL,
                character_id=character_id,
                hunter_edge_id=hunter_edge_id,
            )
        )
        return EdgeAndPerks.model_validate(response.json())

    async def remove_edge(
        self,
        character_id: str,
        hunter_edge_id: str,
    ) -> EdgeAndPerks:
        """Remove a hunter edge from a character.

        Args:
            character_id: The ID of the character to remove the hunter edge from.
            hunter_edge_id: The ID of the hunter edge to remove.
        """
        response = await self._delete(
            self._format_endpoint(
                Endpoints.CHARACTER_HUNTER_EDGE_DETAIL,
                character_id=character_id,
                hunter_edge_id=hunter_edge_id,
            )
        )
        return EdgeAndPerks.model_validate(response.json())

    async def get_edge_perks_page(
        self,
        character_id: str,
        hunter_edge_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[Perk]:
        """Retrieve the perks for a specific hunter edge.

        Args:
            character_id: The ID of the character that owns the hunter edge.
            hunter_edge_id: The ID of the hunter edge to retrieve the perks for.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).
        """
        return await self._get_paginated_as(
            self._format_endpoint(
                Endpoints.CHARACTER_HUNTER_EDGE_PERKS,
                character_id=character_id,
                hunter_edge_id=hunter_edge_id,
            ),
            Perk,
            limit=limit,
            offset=offset,
        )

    async def list_all_edge_perks(
        self,
        character_id: str,
        hunter_edge_id: str,
    ) -> list[Perk]:
        """Retrieve all perks for a specific hunter edge.

        Automatically paginates through all results. Use `get_edge_perks_page()` for paginated
        access or `iter_all_edge_perks()` for memory-efficient streaming of large datasets.

        Args:
            character_id: The ID of the character that owns the hunter edge.
            hunter_edge_id: The ID of the hunter edge to retrieve the perks for.
        """
        return [perk async for perk in self.iter_all_edge_perks(character_id, hunter_edge_id)]

    async def iter_all_edge_perks(
        self,
        character_id: str,
        hunter_edge_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[Perk]:
        """Iterate through all perks for a specific hunter edge.

        Yields individual perks, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            character_id: The ID of the character that owns the hunter edge.
            hunter_edge_id: The ID of the hunter edge to iterate the perks for.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Perk objects.
        """
        async for perk in self._iter_all_pages(
            self._format_endpoint(
                Endpoints.CHARACTER_HUNTER_EDGE_PERKS,
                character_id=character_id,
                hunter_edge_id=hunter_edge_id,
            ),
            limit=limit,
        ):
            yield Perk.model_validate(perk)

    async def get_edge_perk(
        self,
        character_id: str,
        hunter_edge_id: str,
        hunter_edge_perk_id: str,
    ) -> Perk:
        """Retrieve a specific perk for a hunter edge.

        Args:
            character_id: The ID of the character that owns the hunter edge.
            hunter_edge_id: The ID of the hunter edge to retrieve the perk for.
            hunter_edge_perk_id: The ID of the hunter edge perk to retrieve.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.CHARACTER_HUNTER_EDGE_PERK_DETAIL,
                character_id=character_id,
                hunter_edge_id=hunter_edge_id,
                hunter_edge_perk_id=hunter_edge_perk_id,
            )
        )
        return Perk.model_validate(response.json())

    async def add_edge_perk(
        self,
        character_id: str,
        hunter_edge_id: str,
        hunter_edge_perk_id: str,
    ) -> Perk:
        """Add a perk to a hunter edge.

        Args:
            character_id: The ID of the character to add the perk to.
            hunter_edge_id: The ID of the hunter edge to add the perk to.
            hunter_edge_perk_id: The ID of the hunter edge perk to add.

        Returns:
            The added Perk object.
        """
        response = await self._post(
            self._format_endpoint(
                Endpoints.CHARACTER_HUNTER_EDGE_PERK_DETAIL,
                character_id=character_id,
                hunter_edge_id=hunter_edge_id,
                hunter_edge_perk_id=hunter_edge_perk_id,
            )
        )
        return Perk.model_validate(response.json())

    async def remove_edge_perk(
        self,
        character_id: str,
        hunter_edge_id: str,
        hunter_edge_perk_id: str,
    ) -> Perk:
        """Remove a perk from a hunter edge.

        Args:
            character_id: The ID of the character to remove the perk from.
            hunter_edge_id: The ID of the hunter edge to remove the perk from.
            hunter_edge_perk_id: The ID of the hunter edge perk to remove.

        Returns:
            The removed Perk object.
        """
        response = await self._delete(
            self._format_endpoint(
                Endpoints.CHARACTER_HUNTER_EDGE_PERK_DETAIL,
                character_id=character_id,
                hunter_edge_id=hunter_edge_id,
                hunter_edge_perk_id=hunter_edge_perk_id,
            )
        )
        return Perk.model_validate(response.json())
