"""Pydantic models for Campaign API responses and requests."""

from datetime import datetime

from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Campaign Response Models
# -----------------------------------------------------------------------------


class Campaign(BaseModel):
    """Response model for a campaign.

    Represents a campaign entity returned from the API with all properties.
    Campaigns are containers for characters, books, chapters, and other game content.
    """

    id: str
    date_created: datetime
    date_modified: datetime
    name: str
    description: str | None = None
    asset_ids: list[str] = Field(default_factory=list)
    desperation: int = 0
    danger: int = 0
    company_id: str


# -----------------------------------------------------------------------------
# Campaign Request Models
# -----------------------------------------------------------------------------


class CreateCampaignRequest(BaseModel):
    """Request body for creating a new campaign.

    Used to construct the JSON payload for campaign creation.
    """

    name: str = Field(min_length=3, max_length=50)
    description: str | None = Field(default=None, min_length=3)
    asset_ids: list[str] = Field(default_factory=list)
    desperation: int = Field(default=0, ge=0, le=5)
    danger: int = Field(default=0, ge=0, le=5)


class UpdateCampaignRequest(BaseModel):
    """Request body for updating a campaign.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    name: str | None = Field(default=None, min_length=3, max_length=50)
    description: str | None = Field(default=None, min_length=3)
    asset_ids: list[str] | None = None
    desperation: int | None = Field(default=None, ge=0, le=5)
    danger: int | None = Field(default=None, ge=0, le=5)
