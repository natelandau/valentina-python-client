"""Pydantic models for Dicreoll API responses and requests."""

from datetime import datetime

from pydantic import BaseModel, Field

from vclient.constants import DiceSize, RollResultType


class DiceRollResultSchema(BaseModel):
    """Represent the result of a dice roll."""

    total_result: int | None = None
    total_result_type: RollResultType
    total_result_humanized: str | None = None
    total_dice_roll: list[int] = Field(default_factory=list)
    player_roll: list[int] = Field(default_factory=list)
    desperation_roll: list[int] = Field(default_factory=list)
    total_dice_roll_emoji: str | None = None
    total_dice_roll_shortcode: str | None = None
    player_roll_emoji: str | None = None
    player_roll_shortcode: str | None = None
    desperation_roll_emoji: str | None = None
    desperation_roll_shortcode: str | None = None


class Dicreoll(BaseModel):
    """Response model for a dicreoll."""

    id: str
    date_created: datetime
    date_modified: datetime
    dice_size: DiceSize
    difficulty: int | None = None
    num_dice: int
    num_desperation_dice: int = 0
    comment: str | None = None
    trait_ids: list[str] = Field(default_factory=list)
    user_id: str | None = None
    character_id: str | None = None
    campaign_id: str | None = None
    company_id: str
    result: DiceRollResultSchema | None = None


class CreateDicreollRequest(BaseModel):
    """Request body for creating a dicreoll."""

    dice_size: DiceSize
    difficulty: int | None = None
    num_dice: int
    num_desperation_dice: int = 0
    comment: str | None = None
    trait_ids: list[str] = Field(default_factory=list)
    character_id: str | None = None
    campaign_id: str | None = None


class CreateDicreollQuickrollRequest(BaseModel):
    """Request body for creating a dicreoll quickroll."""

    quickroll_id: str
    character_id: str
    comment: str | None = None
    difficulty: int = 6
    num_desperation_dice: int = 0
