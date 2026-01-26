"""Pydantic models for Character Trait API responses and requests."""

from typing import Annotated

from pydantic import BaseModel, Field

from .shared import Trait


class CharacterTrait(BaseModel):
    """Response model for a character trait."""

    id: str
    character_id: str
    value: int
    trait: Trait


class AssignCharacterTraitRequest(BaseModel):
    """Request model for assigning a character trait."""

    trait_id: str
    value: int


class CreateCharacterTraitRequest(BaseModel):
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


class CharacterTraitValueChangeRequest(BaseModel):
    """Request model for changing the value of a character trait."""

    num_dots: int
