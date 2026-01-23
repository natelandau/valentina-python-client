"""Pydantic models for System API responses."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ServiceStatus(StrEnum):
    """Status of a system service or dependency."""

    ONLINE = "online"
    OFFLINE = "offline"


class SystemHealth(BaseModel):
    """Response model for system health check.

    Represents the health status of the API and its dependencies including
    database and cache connectivity.
    """

    database_status: ServiceStatus = Field(
        ...,
        description="Current status of the database connection.",
    )
    cache_status: ServiceStatus = Field(
        ...,
        description="Current status of the cache connection.",
    )
    version: str = Field(
        default="0.0.0",
        description="Current API version.",
    )
