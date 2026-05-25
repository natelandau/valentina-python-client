"""Pydantic models for Global Admin API responses."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from vclient.constants import PermissionLevel


class DeveloperCompanyPermission(BaseModel):
    """Company permission entry for a developer.

    Represents a single company access grant with its permission level.
    """

    company_id: str
    name: str | None
    permission: PermissionLevel


class Developer(BaseModel):
    """Response model for a developer.

    Represents a developer account returned from the API with all its properties.
    """

    id: str
    date_created: datetime
    date_modified: datetime
    username: str
    email: str
    key_generated: datetime | None
    is_global_admin: bool
    companies: list[DeveloperCompanyPermission]


class DeveloperWithApiKey(Developer):
    """Developer response that includes the generated API key.

    Only returned when generating a new API key. The key will not be shown again.
    """

    api_key: str | None


# -----------------------------------------------------------------------------
# Request Body Models
# -----------------------------------------------------------------------------


class DeveloperCreate(BaseModel):
    """Request body for creating a new developer.

    Used to construct the JSON payload for developer creation.
    """

    username: str
    email: str
    is_global_admin: bool = False


class DeveloperUpdate(BaseModel):
    """Request body for updating a developer.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    username: str | None = None
    email: str | None = None
    is_global_admin: bool | None = None


class ServerLogEntry(BaseModel):
    """A single parsed server log entry from the admin logs tail endpoint.

    Every field is nullable because individual log lines may omit values or fail
    to parse as structured JSON (in which case ``raw`` holds the original line).
    """

    timestamp: str | None = None
    level: str | None = None
    name: str | None = None
    message: str | None = None
    exception: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)
    raw: str | None = None


@dataclass(frozen=True)
class ServerLogArchive:
    """A downloaded server-log zip archive.

    Pairs the server-provided ``Content-Disposition`` filename with the raw zip
    bytes so callers can write the archive straight to disk.
    """

    filename: str
    content: bytes


__all__ = [
    "Developer",
    "DeveloperCompanyPermission",
    "DeveloperCreate",
    "DeveloperUpdate",
    "DeveloperWithApiKey",
    "ServerLogArchive",
    "ServerLogEntry",
]
