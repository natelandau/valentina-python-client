"""Pydantic models for User API responses and requests."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

# Type aliases for user-related constrained values
UserRole = Literal["ADMIN", "STORYTELLER", "PLAYER"]
S3AssetType = Literal["image", "text", "audio", "video", "document", "archive", "other"]
S3AssetParentType = Literal[
    "character", "campaign", "campaignbook", "campaignchapter", "user", "company", "unknown"
]


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
    name: str
    email: str
    role: UserRole | None = None
    company_id: str
    discord_profile: DiscordProfile | None = None
    campaign_experience: list[CampaignExperience] = Field(default_factory=list)
    asset_ids: list[str] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# User Request Models
# -----------------------------------------------------------------------------


class CreateUserRequest(BaseModel):
    """Request body for creating a new user.

    Used to construct the JSON payload for user creation.
    """

    name: str = Field(min_length=3, max_length=50)
    email: str
    role: UserRole
    discord_profile: DiscordProfile | None = None
    requesting_user_id: str


class UpdateUserRequest(BaseModel):
    """Request body for updating a user.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    name: str | None = Field(default=None, min_length=3, max_length=50)
    email: str | None = None
    role: UserRole | None = None
    discord_profile: DiscordProfile | None = None
    requesting_user_id: str


# -----------------------------------------------------------------------------
# Statistics Models
# -----------------------------------------------------------------------------


class RollStatistics(BaseModel):
    """Aggregated dice roll statistics for a user or campaign.

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
# Asset Models
# -----------------------------------------------------------------------------


class S3Asset(BaseModel):
    """Response model for an S3 asset.

    Represents a file asset stored in S3, including its URL and metadata.
    """

    id: str
    date_created: datetime
    date_modified: datetime
    file_type: S3AssetType
    original_filename: str
    public_url: str
    uploaded_by: str
    parent_type: S3AssetParentType | None = None


# -----------------------------------------------------------------------------
# Note Models
# -----------------------------------------------------------------------------


class Note(BaseModel):
    """Response model for a note.

    Represents a note attached to a user or other entity.
    """

    id: str
    date_created: datetime
    date_modified: datetime
    title: str
    content: str


class CreateNoteRequest(BaseModel):
    """Request body for creating a new note.

    Used to construct the JSON payload for note creation.
    """

    title: str = Field(min_length=3, max_length=50)
    content: str = Field(min_length=3)


class UpdateNoteRequest(BaseModel):
    """Request body for updating a note.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    title: str | None = Field(default=None, min_length=3, max_length=50)
    content: str | None = Field(default=None, min_length=3)


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


class CreateQuickrollRequest(BaseModel):
    """Request body for creating a new quickroll.

    Used to construct the JSON payload for quickroll creation.
    """

    name: str = Field(min_length=3, max_length=50)
    description: str | None = Field(default=None, min_length=3)
    trait_ids: list[str] = Field(default_factory=list)


class UpdateQuickrollRequest(BaseModel):
    """Request body for updating a quickroll.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    name: str | None = Field(default=None, min_length=3, max_length=50)
    description: str | None = Field(default=None, min_length=3)
    trait_ids: list[str] | None = None


# -----------------------------------------------------------------------------
# Experience Models
# -----------------------------------------------------------------------------


class ExperienceAddRemoveRequest(BaseModel):
    """Request body for adding or removing experience points.

    Used to construct the JSON payload for XP/CP modifications.
    """

    amount: int
    user_id: str
    campaign_id: str
