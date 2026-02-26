"""Pydantic models for User API responses and requests."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from vclient.constants import UserRole

# -----------------------------------------------------------------------------
# Nested/Shared Models
# -----------------------------------------------------------------------------


class DiscordProfile(BaseModel):
    """Discord profile information for a user.

    Contains Discord account details for integration with Discord bots.
    All fields are optional as not all users have Discord linked.
    """

    id: str | None = None
    username: str | None = None
    global_name: str | None = None
    avatar_id: str | None = None
    avatar_url: str | None = None
    discriminator: str | None = None
    email: str | None = None
    verified: bool | None = None


class CampaignExperience(BaseModel):
    """Experience points and cool points for a user in a specific campaign.

    Tracks the user's progression within a campaign including current XP available
    for spending, total XP earned, and cool points.
    """

    campaign_id: str
    xp_current: int = 0
    xp_total: int = 0
    cool_points: int = 0


# -----------------------------------------------------------------------------
# User Response Models
# -----------------------------------------------------------------------------


class User(BaseModel):
    """Response model for a user.

    Represents a user entity returned from the API with all properties including
    their role, Discord profile, and campaign experience.
    """

    id: str
    date_created: datetime
    date_modified: datetime
    name_first: str | None = None
    name_last: str | None = None
    username: str
    email: str
    role: UserRole | None = None
    company_id: str
    discord_profile: DiscordProfile | None = None
    campaign_experience: list[CampaignExperience] = Field(default_factory=list)
    asset_ids: list[str] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# User Request Models
# -----------------------------------------------------------------------------


class UserCreate(BaseModel):
    """Request body for creating a new user.

    Used to construct the JSON payload for user creation.
    """

    name_first: Annotated[str, Field(min_length=3, max_length=50)] | None = None
    name_last: Annotated[str, Field(min_length=3, max_length=50)] | None = None
    username: str = Field(min_length=3, max_length=50)
    email: str
    role: UserRole
    discord_profile: DiscordProfile | None = None
    requesting_user_id: str


class UserUpdate(BaseModel):
    """Request body for updating a user.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    name_first: Annotated[str, Field(min_length=3, max_length=50)] | None = None
    name_last: Annotated[str, Field(min_length=3, max_length=50)] | None = None
    username: Annotated[str, Field(min_length=3, max_length=50)] | None = None
    email: str | None = None
    role: UserRole | None = None
    discord_profile: DiscordProfile | None = None
    requesting_user_id: str


# -----------------------------------------------------------------------------
# Quickroll Models
# -----------------------------------------------------------------------------


class Quickroll(BaseModel):
    """Response model for a quickroll.

    Represents a pre-configured dice pool for frequently used trait combinations,
    allowing faster gameplay.
    """

    id: str
    date_created: datetime
    date_modified: datetime
    name: str
    description: str | None = None
    user_id: str
    trait_ids: list[str] = Field(default_factory=list)


class QuickrollCreate(BaseModel):
    """Request body for creating a new quickroll.

    Used to construct the JSON payload for quickroll creation.
    """

    name: str = Field(min_length=3, max_length=50)
    description: Annotated[str, Field(min_length=3)] | None = None
    trait_ids: list[str] = Field(default_factory=list)


class QuickrollUpdate(BaseModel):
    """Request body for updating a quickroll.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    name: Annotated[str, Field(min_length=3, max_length=50)] | None = None
    description: Annotated[str, Field(min_length=3)] | None = None
    trait_ids: list[str] | None = None


# -----------------------------------------------------------------------------
# Experience Models
# -----------------------------------------------------------------------------


class _ExperienceAddRemove(BaseModel):
    """Internal request body for adding or removing experience points.

    Used to construct the JSON payload for XP/CP modifications.
    """

    amount: int
    campaign_id: str
    requesting_user_id: str


__all__ = [
    "CampaignExperience",
    "DiscordProfile",
    "Quickroll",
    "QuickrollCreate",
    "QuickrollUpdate",
    "User",
    "UserCreate",
    "UserUpdate",
    "_ExperienceAddRemove",
]
