"""Shared Pydantic models used across multiple services."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

# Type aliases for asset-related constrained values
S3AssetType = Literal["image", "text", "audio", "video", "document", "archive", "other"]
S3AssetParentType = Literal[
    "character", "campaign", "campaignbook", "campaignchapter", "user", "company", "unknown"
]


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

    Represents a note attached to a user, campaign, or other entity.
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
