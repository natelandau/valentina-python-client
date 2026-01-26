"""Pydantic models for Character API responses and requests."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from vclient.constants import (
    CharacterClass,
    CharacterInventoryType,
    CharacterStatus,
    CharacterType,
    GameVersion,
    HunterEdgeType,
)

# -----------------------------------------------------------------------------
# Nested Models
# -----------------------------------------------------------------------------


class CharacterSpecialty(BaseModel):
    """A character specialty for a trait."""

    id: str | None = Field(default=None, description="MongoDB document ObjectID.")
    name: str = Field(..., description="Name of the specialty.")
    trait_id: str | None = Field(default=None, description="ID of the associated trait.")


class VampireAttributes(BaseModel):
    """Vampire-specific character attributes."""

    clan_id: str | None = Field(default=None, description="ID of the vampire clan.")
    clan_name: str | None = Field(default=None, description="Name of the vampire clan.")
    generation: int | None = Field(default=None, description="Vampire generation.")
    sire: str | None = Field(default=None, description="Name of the vampire's sire.")
    bane: dict[str, Any] | None = Field(default=None, description="Clan bane details.")
    compulsion: dict[str, Any] | None = Field(default=None, description="Clan compulsion details.")


class WerewolfAttributes(BaseModel):
    """Werewolf-specific character attributes."""

    tribe_id: str | None = Field(default=None, description="ID of the werewolf tribe.")
    tribe_name: str | None = Field(default=None, description="Name of the werewolf tribe.")
    auspice_id: str | None = Field(default=None, description="ID of the werewolf auspice.")
    auspice_name: str | None = Field(default=None, description="Name of the werewolf auspice.")
    pack_name: str | None = Field(default=None, description="Name of the werewolf's pack.")


class MageAttributes(BaseModel):
    """Mage-specific character attributes."""

    sphere: str | None = Field(default=None, description="Primary sphere of magic.")


class HunterEdgePerk(BaseModel):
    """A perk associated with a hunter edge."""

    id: str = Field(..., description="MongoDB document ObjectID.")
    name: str = Field(..., description="Name of the perk.")
    description: str | None = Field(default=None, description="Description of the perk.")


class HunterEdge(BaseModel):
    """A hunter edge with associated perks."""

    id: str = Field(..., description="MongoDB document ObjectID.")
    name: str = Field(..., description="Name of the edge.")
    description: str | None = Field(default=None, description="Description of the edge.")
    pool: str | None = Field(default=None, description="Dice pool for the edge.")
    system: str | None = Field(default=None, description="System rules for the edge.")
    type: str | None = Field(default=None, description="Type of hunter edge.")
    perks: list[HunterEdgePerk] = Field(default_factory=list, description="Associated perks.")


class HunterAttributes(BaseModel):
    """Hunter-specific character attributes."""

    creed: str | None = Field(default=None, description="Hunter creed.")
    edges: list[HunterEdge] = Field(default_factory=list, description="Hunter edges.")


# -----------------------------------------------------------------------------
# Character Response Model
# -----------------------------------------------------------------------------


class Character(BaseModel):
    """Response model for a character.

    Represents a character entity returned from the API with all properties.
    Characters are player or non-player entities within a campaign.
    """

    id: str | None = Field(default=None, description="MongoDB document ObjectID.")
    date_created: datetime | None = Field(
        default=None, description="Timestamp when the character was created."
    )
    date_modified: datetime | None = Field(
        default=None, description="Timestamp when the character was last modified."
    )
    date_killed: datetime | None = Field(
        default=None, description="Timestamp when the character was killed."
    )

    # Core fields
    character_class: CharacterClass = Field(..., description="Character class.")
    type: CharacterType = Field(default="PLAYER", description="Character type.")
    game_version: GameVersion = Field(..., description="Game version for character sheet.")
    status: CharacterStatus = Field(default="ALIVE", description="Character status.")
    starting_points: int = Field(default=0, description="Starting experience points.")

    # Identity
    name_first: str = Field(..., min_length=3, description="Character's first name.")
    name_last: str = Field(..., min_length=3, description="Character's last name.")
    name_nick: str | None = Field(
        default=None, min_length=3, max_length=50, description="Character's nickname."
    )
    name: str = Field(..., description="Character's display name.")
    name_full: str = Field(..., description="Character's full name.")

    # Biography
    age: int | None = Field(default=None, description="Character's age.")
    biography: str | None = Field(default=None, min_length=3, description="Character biography.")
    demeanor: str | None = Field(
        default=None, min_length=3, max_length=50, description="Character's demeanor."
    )
    nature: str | None = Field(
        default=None, min_length=3, max_length=50, description="Character's nature."
    )
    concept_id: str | None = Field(default=None, description="ID of the character concept.")

    # Relationships
    user_creator_id: str = Field(..., description="ID of the user who created the character.")
    user_player_id: str = Field(..., description="ID of the user who plays the character.")
    company_id: str = Field(..., description="ID of the company.")
    campaign_id: str = Field(..., description="ID of the campaign.")

    # Assets and traits
    asset_ids: list[str] = Field(default_factory=list, description="List of asset IDs.")
    character_trait_ids: list[str] = Field(
        default_factory=list, description="List of character trait IDs."
    )
    specialties: list[CharacterSpecialty] = Field(
        default_factory=list, description="List of character specialties."
    )

    # Class-specific attributes
    vampire_attributes: VampireAttributes | None = Field(
        default=None, description="Vampire-specific attributes."
    )
    werewolf_attributes: WerewolfAttributes | None = Field(
        default=None, description="Werewolf-specific attributes."
    )
    mage_attributes: MageAttributes | None = Field(
        default=None, description="Mage-specific attributes."
    )
    hunter_attributes: HunterAttributes | None = Field(
        default=None, description="Hunter-specific attributes."
    )


# -----------------------------------------------------------------------------
# Character Request Models
# -----------------------------------------------------------------------------


class CreateCharacterRequest(BaseModel):
    """Request body for creating a new character.

    Used to construct the JSON payload for character creation.
    """

    character_class: CharacterClass = Field(..., description="Character class.")
    game_version: GameVersion = Field(..., description="Game version for character sheet.")
    name_first: str = Field(..., min_length=3, description="Character's first name.")
    name_last: str = Field(..., min_length=3, description="Character's last name.")

    # Optional fields
    type: CharacterType | None = Field(default=None, description="Character type.")
    name_nick: str | None = Field(
        default=None, min_length=3, max_length=50, description="Character's nickname."
    )
    age: int | None = Field(default=None, description="Character's age.")
    biography: str | None = Field(default=None, min_length=3, description="Character biography.")
    demeanor: str | None = Field(
        default=None, min_length=3, max_length=50, description="Character's demeanor."
    )
    nature: str | None = Field(
        default=None, min_length=3, max_length=50, description="Character's nature."
    )
    concept_id: str | None = Field(default=None, description="ID of the character concept.")
    user_player_id: str | None = Field(
        default=None, description="ID of the user who will play the character."
    )
    asset_ids: list[str] | None = Field(default=None, description="List of asset IDs.")


class UpdateCharacterRequest(BaseModel):
    """Request body for updating a character.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    character_class: CharacterClass | None = Field(default=None, description="Character class.")
    type: CharacterType | None = Field(default=None, description="Character type.")
    game_version: GameVersion | None = Field(
        default=None, description="Game version for character sheet."
    )
    status: CharacterStatus | None = Field(default=None, description="Character status.")

    name_first: str | None = Field(
        default=None, min_length=3, description="Character's first name."
    )
    name_last: str | None = Field(default=None, min_length=3, description="Character's last name.")
    name_nick: str | None = Field(
        default=None, min_length=3, max_length=50, description="Character's nickname."
    )

    age: int | None = Field(default=None, description="Character's age.")
    biography: str | None = Field(default=None, min_length=3, description="Character biography.")
    demeanor: str | None = Field(
        default=None, min_length=3, max_length=50, description="Character's demeanor."
    )
    nature: str | None = Field(
        default=None, min_length=3, max_length=50, description="Character's nature."
    )
    concept_id: str | None = Field(default=None, description="ID of the character concept.")

    user_player_id: str | None = Field(
        default=None, description="ID of the user who plays the character."
    )
    asset_ids: list[str] | None = Field(default=None, description="List of asset IDs.")
    date_killed: datetime | None = Field(
        default=None, description="Timestamp when the character was killed."
    )


# -----------------------------------------------------------------------------
# Character Inventory Request Models
# -----------------------------------------------------------------------------


class CharacterInventoryItem(BaseModel):
    """A character inventory item."""

    id: str = Field(..., description="MongoDB document ObjectID.")
    character_id: str = Field(..., description="ID of the character.")
    name: str = Field(..., description="Name of the item.")
    type: CharacterInventoryType = Field(..., description="Type of the item.")
    description: str | None = Field(default=None, description="Description of the item.")
    date_created: datetime = Field(..., description="Timestamp when the item was created.")
    date_modified: datetime = Field(..., description="Timestamp when the item was last modified.")


class CreateCharacterInventoryItemRequest(BaseModel):
    """Request body for creating a new character inventory item."""

    name: str = Field(..., description="Name of the item.")
    type: CharacterInventoryType = Field(..., description="Type of the item.")
    description: str | None = Field(default=None, description="Description of the item.")


class UpdateCharacterInventoryItemRequest(BaseModel):
    """Request body for updating a character inventory item."""

    name: str | None = Field(default=None, description="Name of the item.")
    type: CharacterInventoryType | None = Field(default=None, description="Type of the item.")
    description: str | None = Field(default=None, description="Description of the item.")


# -----------------------------------------------------------------------------
# Character Specific Hunter Edge Response Models
# -----------------------------------------------------------------------------


class CharacterPerkDTO(BaseModel):
    """Character perk DTO."""

    id: str
    name: str
    description: str | None = None


class CharacterEdgeAndPerksDTO(BaseModel):
    """Character edge and perks DTO."""

    id: str
    name: str
    description: str | None = None
    pool: str | None = None
    system: str | None = None
    type: HunterEdgeType | None = None
    perks: list[CharacterPerkDTO] = Field(default_factory=list)
