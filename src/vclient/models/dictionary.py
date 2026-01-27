"""Pydantic models for Dictionary API responses and requests."""

from datetime import datetime

from pydantic import BaseModel, Field


class DictionaryTerm(BaseModel):
    """Response model for a dictionary term."""

    id: str
    term: str
    definition: str | None = None
    link: str | None = None
    synonyms: list[str] = Field(default_factory=list)
    date_created: datetime
    date_modified: datetime


class CreateDictionaryTermRequest(BaseModel):
    """Request body for creating a dictionary term."""

    term: str
    definition: str | None = None
    link: str | None = None
    synonyms: list[str] = Field(default_factory=list)


class UpdateDictionaryTermRequest(BaseModel):
    """Request body for updating a dictionary term."""

    term: str | None = None
    definition: str | None = None
    link: str | None = None
    synonyms: list[str] | None = None
