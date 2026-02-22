"""Shared Pydantic models used across multiple services."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, Field

from vclient.constants import (
    AssetParentType,
    AssetType,
    CharacterClass,
    GameVersion,
    SpecialtyType,
    WerewolfRenown,
)

# -----------------------------------------------------------------------------
# Utility  Models
# -----------------------------------------------------------------------------


class NameDescriptionSubDocument(BaseModel):
    """Name and description base model. Use this for sub-documents that have a name and description."""

    name: str | None = None
    description: str | None = None


# -----------------------------------------------------------------------------
# Asset Models
# -----------------------------------------------------------------------------


class Asset(BaseModel):
    """Response model for an S3 asset.

    Represents a file asset stored in S3, including its URL and metadata.
    """

    id: str
    date_created: datetime
    date_modified: datetime
    asset_type: AssetType
    mime_type: str
    original_filename: str
    public_url: str
    uploaded_by: str
    company_id: str
    parent_type: AssetParentType | None = None
    parent_id: str | None = None


# -----------------------------------------------------------------------------
# Note Models
# -----------------------------------------------------------------------------


class Note(BaseModel):
    """Response model for a note.

    Represents a note attached to a user, campaign, or other entity.
    """

    id: str
    date_created: datetime
    date_modified: datetime
    title: str
    content: str


class NoteCreate(BaseModel):
    """Request body for creating a new note.

    Used to construct the JSON payload for note creation.
    """

    title: str = Field(min_length=3, max_length=50)
    content: str = Field(min_length=3)


class NoteUpdate(BaseModel):
    """Request body for updating a note.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    title: Annotated[str, Field(min_length=3, max_length=50)] | None = None
    content: Annotated[str, Field(min_length=3)] | None = None


# -----------------------------------------------------------------------------
# Statistics Models
# -----------------------------------------------------------------------------


class RollStatistics(BaseModel):
    """Aggregated dice roll statistics for a user, campaign, or character.

    Contains success rates, critical frequencies, and most-used traits
    for analyzing gameplay patterns.
    """

    botches: int
    successes: int
    failures: int
    criticals: int
    total_rolls: int
    average_difficulty: float | None = None
    average_pool: float | None = None
    top_traits: list[dict[str, Any]] = Field(default_factory=list)
    criticals_percentage: float
    success_percentage: float
    failure_percentage: float
    botch_percentage: float


# -----------------------------------------------------------------------------
# Trait Models
# -----------------------------------------------------------------------------


class Trait(BaseModel):
    """Response model for a trait.

    Represents a trait assigned to a character.
    """

    id: str
    name: str
    description: str | None = None
    date_created: datetime
    date_modified: datetime
    link: str | None = None
    show_when_zero: bool = True
    max_value: int = 5
    min_value: int = 0
    is_custom: bool = False
    initial_cost: int = 1
    upgrade_cost: int = 2

    sheet_section_name: str | None = None
    sheet_section_id: str | None = None
    parent_category_name: str | None = None
    parent_category_id: str
    custom_for_character_id: str | None = None
    advantage_category_id: str | None = None
    advantage_category_name: str | None = None

    character_classes: list[CharacterClass] = Field(default_factory=list)
    game_versions: list[GameVersion] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Character Special Models
# -----------------------------------------------------------------------------


class WerewolfGift(BaseModel):
    """Response model for a werewolf gift."""

    id: str
    name: str
    description: str | None = None
    game_versions: list[GameVersion] = Field(default_factory=list)
    date_created: datetime
    date_modified: datetime
    renown: WerewolfRenown
    cost: str | None = None
    duration: str | None = None
    dice_pool: list[str] = Field(default_factory=list)
    opposing_pool: list[str] = Field(default_factory=list)
    minimum_renown: int | None = None
    is_native_gift: bool = False
    notes: str | None = None
    tribe_id: str | None = None
    auspice_id: str | None = None


class WerewolfRite(BaseModel):
    """Response model for a werewolf gift."""

    id: str
    name: str
    description: str | None = None
    game_versions: list[GameVersion] = Field(default_factory=list)
    date_created: datetime
    date_modified: datetime
    pool: str | None = None


class CharacterSpecialty(BaseModel):
    """A character specialty for a trait."""

    name: str
    type: SpecialtyType
    description: str


__all__ = [
    "Asset",
    "CharacterSpecialty",
    "NameDescriptionSubDocument",
    "Note",
    "NoteCreate",
    "NoteUpdate",
    "RollStatistics",
    "Trait",
    "WerewolfGift",
    "WerewolfRite",
]
