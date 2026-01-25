"""Pydantic models for CampaignBook entities."""

from datetime import datetime

from pydantic import BaseModel, Field


class CampaignBook(BaseModel):
    """Response model for a campaign book.

    Represents a book within a campaign, containing notes and assets.
    """

    id: str | None = Field(default=None, description="MongoDB document ObjectID.")
    date_created: datetime = Field(..., description="Timestamp when the book was created.")
    date_modified: datetime = Field(..., description="Timestamp when the book was last modified.")
    name: str = Field(..., description="Book name (3-50 characters).")
    description: str | None = Field(default=None, description="Book description.")
    asset_ids: list[str] = Field(default_factory=list, description="List of associated asset IDs.")
    number: int = Field(..., description="Book number within the campaign.")
    campaign_id: str = Field(..., description="ID of the parent campaign.")


class CreateBookRequest(BaseModel):
    """Request body for creating a new campaign book.

    Used to construct the JSON payload for book creation.
    """

    name: str = Field(..., min_length=3, max_length=50, description="Book name (3-50 characters).")
    description: str | None = Field(
        default=None, min_length=3, description="Book description (minimum 3 characters)."
    )
    asset_ids: list[str] = Field(
        default_factory=list, description="List of asset IDs to associate."
    )


class UpdateBookRequest(BaseModel):
    """Request body for updating a campaign book.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    name: str | None = Field(
        default=None, min_length=3, max_length=50, description="New book name (3-50 characters)."
    )
    description: str | None = Field(
        default=None, min_length=3, description="New book description (minimum 3 characters)."
    )
    asset_ids: list[str] | None = Field(
        default=None, description="New list of asset IDs to associate."
    )


class RenumberBookRequest(BaseModel):
    """Request body for renumbering a campaign book.

    Changes the book's position number within the campaign.
    """

    number: int = Field(..., ge=1, description="New book number (must be >= 1).")
