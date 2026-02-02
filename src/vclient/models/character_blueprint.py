"""Pydantic models for Character Blueprint API responses and requests."""

from datetime import datetime

from pydantic import BaseModel, Field

from vclient.constants import CharacterClass, GameVersion, HunterEdgeType, WerewolfRenown

from .shared import CharacterSpecialty, NameDescriptionSubDocument


class SheetSection(BaseModel):
    """Response model for a character blueprint section."""

    id: str
    name: str
    description: str | None = None
    character_classes: list[CharacterClass] = Field(default_factory=list)
    date_created: datetime
    date_modified: datetime
    game_versions: list[GameVersion] = Field(default_factory=list)
    show_when_empty: bool
    order: int


class TraitCategory(BaseModel):
    """Response model for a character blueprint category."""

    id: str
    name: str
    description: str | None = None
    character_classes: list[CharacterClass] = Field(default_factory=list)
    date_created: datetime
    date_modified: datetime
    game_versions: list[GameVersion] = Field(default_factory=list)
    parent_sheet_section_id: str
    initial_cost: int
    upgrade_cost: int
    order: int
    show_when_empty: bool


class VampireClan(BaseModel):
    """Response model for a vampire clan."""

    id: str
    name: str
    description: str | None = None
    date_created: datetime
    date_modified: datetime
    game_version: GameVersion

    discipline_ids: list[str] = Field(default_factory=list)
    bane: NameDescriptionSubDocument | None = None
    variant_bane: NameDescriptionSubDocument | None = None
    compulsion: NameDescriptionSubDocument | None = None
    link: str | None = None


class WerewolfAuspice(BaseModel):
    """Response model for a werewolf auspice."""

    id: str
    name: str
    description: str | None = None
    date_created: datetime
    date_modified: datetime
    game_version: GameVersion

    gift_ids: list[str] = Field(default_factory=list)
    link: str | None = None


class WerewolfTribe(BaseModel):
    """Response model for a werewolf tribe."""

    id: str
    name: str
    description: str | None = None
    date_created: datetime
    date_modified: datetime
    game_version: GameVersion

    renown: WerewolfRenown
    patron_spirit: str | None = None
    favor: str | None = None
    ban: str | None = None
    gift_ids: list[str] = Field(default_factory=list)
    link: str | None = None


class HunterEdge(BaseModel):
    """Hunter edge model."""

    id: str
    name: str
    description: str | None = None
    date_created: datetime
    date_modified: datetime
    game_version: GameVersion

    pool: str | None = None
    system: str | None = None
    type: HunterEdgeType | None = None
    perk_ids: list[str] = Field(default_factory=list)


class HunterEdgePerk(BaseModel):
    """Hunter edge perk model."""

    id: str
    name: str
    description: str | None = None
    date_created: datetime
    date_modified: datetime
    game_version: GameVersion

    edge_id: str | None = None


class CharacterConcept(BaseModel):
    """Character concept model."""

    id: str
    name: str
    description: str | None = None
    date_created: datetime
    date_modified: datetime
    examples: list[str]
    max_specialties: int = Field(default=1)
    specialties: list[CharacterSpecialty] = Field(default_factory=list)
    favored_ability_names: list[str] = Field(default_factory=list)
