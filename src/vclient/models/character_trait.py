"""Pydantic models for Character Trait API responses and requests."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter

from vclient.constants import DamageType, TrackerAction, TraitModifyCurrency

from .shared import Trait


class CharacterTraitSpecialty(BaseModel):
    """Response model for a specialty on an ability trait."""

    id: str
    name: str
    date_created: datetime
    date_modified: datetime


class HealthLevel(BaseModel):
    """One V4 health level with its dice penalty and the damage marked on it."""

    name: str
    penalty: int | None = Field(
        default=None, description="Dice pool penalty at this level. None for Incapacitated."
    )
    mark: DamageType | None = Field(
        default=None, description="Damage marked on this level, or None when empty."
    )


class CounterTracker(BaseModel):
    """Tracker for a trait whose current value is spent and regained in play, such as V4 Willpower."""

    type: Literal["COUNTER"] = "COUNTER"
    size: int = Field(..., description="Maximum, equal to the trait's value.")
    current: int = Field(..., description="Points currently available.")


class DamageTracker(BaseModel):
    """Damage track used by V5 Willpower and by Health in both game versions.

    The V4-only fields (``bashing``, ``lethal``, ``levels``, ``current_penalty``) are ``None``
    for V5.
    """

    type: Literal["DAMAGE"] = "DAMAGE"
    size: int = Field(..., description="Number of boxes on the track.")
    superficial: int
    aggravated: int
    boxes: list[DamageType | None] = Field(
        default_factory=list,
        description="One entry per box in severity order, padded with None for empty boxes.",
    )
    is_impaired: bool
    bashing: int | None = None
    lethal: int | None = None
    levels: list[HealthLevel] | None = None
    current_penalty: int | None = Field(
        default=None,
        description="Dice pool penalty from the most severe marked V4 level. None on V5, and on V4 "
        "when Incapacitated is marked.",
    )


class StainsTracker(BaseModel):
    """Tracker for V5 Humanity stains."""

    type: Literal["STAINS"] = "STAINS"
    humanity: int
    stain_capacity: int = Field(..., description="Boxes left for stains, 10 minus Humanity.")
    stains: int
    is_impaired: bool
    willpower_damage_applied: int | None = Field(
        default=None,
        description="Stains that overflowed into Willpower damage. Set only on action responses.",
    )


# In-play tracker state for a trait; pydantic picks the variant from ``type``.
Tracker = Annotated[CounterTracker | DamageTracker | StainsTracker, Field(discriminator="type")]

_TRACKER_ADAPTER: TypeAdapter[Tracker] = TypeAdapter(Tracker)


class Health(DamageTracker):
    """A character's health track: a damage track plus V4 extra health levels."""

    extra_levels: int = Field(
        default=0, description="Health levels added on top of the base track."
    )


class CharacterTrait(BaseModel):
    """Response model for a character trait."""

    id: str
    character_id: str
    value: int
    trait: Trait
    specialties: list[CharacterTraitSpecialty] = Field(
        default_factory=list,
        description="Active specialties on the trait, oldest first. Only abilities have specialties.",
    )
    tracker: Tracker | None = Field(
        default=None,
        description="In-play tracker state, or None when the trait has no tracker for the "
        "character's game version.",
    )


class TrackerStateSet(BaseModel):
    """Request model for setting a trait tracker's full state.

    Set only the fields for the tracker's type: ``current`` for counters (required),
    ``superficial`` and ``aggravated`` for damage tracks, ``stains`` for stains.
    """

    current: int | None = Field(default=None, ge=0)
    superficial: int | None = Field(default=None, ge=0)
    aggravated: int | None = Field(default=None, ge=0)
    stains: int | None = Field(default=None, ge=0)


class HealthStateSet(BaseModel):
    """Request model for setting a character's full health state.

    V4 uses ``bashing``, ``lethal``, and ``aggravated``; V5 uses ``superficial`` and
    ``aggravated``. ``extra_levels`` applies to both. Omitted fields reset to 0.
    """

    extra_levels: int = Field(default=0, ge=0)
    superficial: int = Field(default=0, ge=0)
    aggravated: int = Field(default=0, ge=0)
    bashing: int = Field(default=0, ge=0)
    lethal: int = Field(default=0, ge=0)


class _TrackerAction(BaseModel):
    """Internal request for POST tracker and health action endpoints."""

    action: TrackerAction
    amount: int = Field(default=1, ge=1)
    damage_type: DamageType | None = None


class CharacterCreateTraitAssign(BaseModel):
    """Request model for assigning a character trait to a new character."""

    trait_id: str
    value: int
    tracker: TrackerStateSet | None = Field(
        default=None,
        description="Starting tracker state. Returns 400 if the trait has no tracker for the "
        "character's game version.",
    )


class CharacterTraitAdd(BaseModel):
    """Request model for adding a character trait to an already created character."""

    trait_id: str
    value: int
    currency: TraitModifyCurrency


class TraitCreate(BaseModel):
    """Request model for creating a custom character trait.

    Used to construct the JSON payload for character trait creation. The trait is
    always created at a value of ``1``; the supplied ``currency`` pays for that first dot.
    """

    name: str
    category_id: str
    currency: TraitModifyCurrency
    description: str | None = None
    max_value: Annotated[int, Field(ge=0, le=100, default=5)] = 5
    min_value: Annotated[int, Field(ge=0, le=100, default=0)] = 0
    show_when_zero: bool | None = True
    is_rollable: bool = True
    initial_cost: int | None = None
    upgrade_cost: int | None = None
    count_based_cost_multiplier: int | None = None


class CharacterTraitSpecialtyCreate(BaseModel):
    """Request model for adding a specialty to an ability trait."""

    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Specialty name (3-50 characters), unique on the trait ignoring case.",
    )
    currency: TraitModifyCurrency = "NO_COST"


class CharacterTraitSpecialtyUpdate(BaseModel):
    """Request model for renaming a specialty."""

    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="New specialty name (3-50 characters), unique on the trait ignoring case.",
    )


class _TraitModify(BaseModel):
    """Internal request for PUT /value endpoint."""

    target_value: int
    currency: TraitModifyCurrency


class CharacterTraitValueOption(BaseModel):
    """Response model for a value option for a character trait."""

    direction: str
    point_change: int
    can_use_xp: bool
    xp_after: int
    can_use_starting_points: bool
    starting_points_after: int


class CharacterTraitValueOptionsResponse(BaseModel):
    """Response model for the value options for a character trait."""

    name: str
    current_value: int
    trait: Trait
    xp_current: int
    starting_points_current: int
    options: dict[str, CharacterTraitValueOption]


class BulkAssignTraitSuccess(BaseModel):
    """Single successfully assigned trait in a bulk operation."""

    trait_id: str
    character_trait: CharacterTrait


class BulkAssignTraitFailure(BaseModel):
    """Single failed trait assignment in a bulk operation."""

    trait_id: str
    error: str


class BulkAssignTraitResponse(BaseModel):
    """Response for bulk trait assignment."""

    succeeded: list[BulkAssignTraitSuccess]
    failed: list[BulkAssignTraitFailure]


__all__ = [
    "_TRACKER_ADAPTER",
    "BulkAssignTraitFailure",
    "BulkAssignTraitResponse",
    "BulkAssignTraitSuccess",
    "CharacterCreateTraitAssign",
    "CharacterTrait",
    "CharacterTraitAdd",
    "CharacterTraitSpecialty",
    "CharacterTraitSpecialtyCreate",
    "CharacterTraitSpecialtyUpdate",
    "CharacterTraitValueOption",
    "CharacterTraitValueOptionsResponse",
    "CounterTracker",
    "DamageTracker",
    "Health",
    "HealthLevel",
    "HealthStateSet",
    "StainsTracker",
    "Tracker",
    "TrackerStateSet",
    "TraitCreate",
    "_TrackerAction",
    "_TraitModify",
]
