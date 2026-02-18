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
    is_global: bool = False
    company_id: str | None = None


class DictionaryTermCreate(BaseModel):
    """Request body for creating a dictionary term."""

    term: str
    definition: str | None = None
    link: str | None = None
    synonyms: list[str] = Field(default_factory=list)


class DictionaryTermUpdate(BaseModel):
    """Request body for updating a dictionary term."""

    term: str | None = None
    definition: str | None = None
    link: str | None = None
    synonyms: list[str] | None = None


__all__ = [
    "DictionaryTerm",
    "DictionaryTermCreate",
    "DictionaryTermUpdate",
]
