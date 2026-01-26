"""Pydantic models for CampaignChapter entities."""

from datetime import datetime

from pydantic import BaseModel, Field


class CampaignChapter(BaseModel):
    """Response model for a campaign chapter.

    Represents a chapter within a campaign book, containing notes and assets.
    """

    id: str | None = Field(default=None, description="MongoDB document ObjectID.")
    date_created: datetime = Field(..., description="Timestamp when the chapter was created.")
    date_modified: datetime = Field(
        ..., description="Timestamp when the chapter was last modified."
    )
    name: str = Field(..., description="Chapter name (3-50 characters).")
    description: str | None = Field(default=None, description="Chapter description.")
    asset_ids: list[str] = Field(default_factory=list, description="List of associated asset IDs.")
    number: int = Field(..., description="Chapter number within the book.")
    book_id: str = Field(..., description="ID of the parent book.")


class CreateChapterRequest(BaseModel):
    """Request body for creating a new campaign chapter."""

    name: str = Field(..., description="Chapter name (3-50 characters).")
    description: str | None = Field(default=None, description="Chapter description.")


class UpdateChapterRequest(BaseModel):
    """Request body for updating a campaign chapter."""

    name: str | None = Field(default=None, description="Chapter name (3-50 characters).")
    description: str | None = Field(default=None, description="Chapter description.")


class RenumberChapterRequest(BaseModel):
    """Request body for renumbering a campaign chapter."""

    number: int = Field(..., ge=1, description="New book number (must be >= 1).")
