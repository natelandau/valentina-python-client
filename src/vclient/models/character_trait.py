"""Pydantic models for Character Trait API responses and requests."""

from typing import Annotated

from pydantic import BaseModel, Field

from vclient.constants import TraitModifyCurrency

from .shared import Trait


class CharacterTrait(BaseModel):
    """Response model for a character trait."""

    id: str
    character_id: str
    value: int
    trait: Trait


class CharacterCreateTraitAssign(BaseModel):
    """Request model for assigning a character trait to a new character."""

    trait_id: str
    value: int


class TraitCreate(BaseModel):
    """Request model for creating a character trait.

    Used to construct the JSON payload for character trait creation.
    """

    name: str
    description: str | None = None
    max_value: Annotated[int, Field(ge=0, le=100, default=5)] = 5
    min_value: Annotated[int, Field(ge=0, le=100, default=0)] = 0
    show_when_zero: bool | None = True
    parent_category_id: str
    initial_cost: int | None = None
    upgrade_cost: int | None = None
    value: int | None = None


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

    current_value: int
    min_value: int
    max_value: int
    xp_current: int
    starting_points_current: int
    options: dict[str, CharacterTraitValueOption]


__all__ = [
    "CharacterCreateTraitAssign",
    "CharacterTrait",
    "CharacterTraitValueOption",
    "CharacterTraitValueOptionsResponse",
    "TraitCreate",
    "_TraitModify",
]
