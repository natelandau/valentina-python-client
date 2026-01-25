"""Pydantic models for Developer API responses."""

from datetime import datetime

from pydantic import BaseModel

from vclient.models.companies import PermissionLevel


class MeDeveloperCompanyPermission(BaseModel):
    """Company permission entry for the current developer.

    Represents a single company access grant with its permission level.
    """

    company_id: str
    name: str | None
    permission: PermissionLevel


class MeDeveloper(BaseModel):
    """Response model for the current developer.

    Represents the authenticated developer's account returned from the API.
    """

    id: str
    date_created: datetime
    date_modified: datetime
    username: str
    email: str
    key_generated: datetime | None
    companies: list[MeDeveloperCompanyPermission]


class MeDeveloperWithApiKey(MeDeveloper):
    """Developer response that includes the generated API key.

    Only returned when regenerating the API key. The key will not be shown again.
    """

    api_key: str


# -----------------------------------------------------------------------------
# Request Body Models
# -----------------------------------------------------------------------------


class UpdateMeDeveloperRequest(BaseModel):
    """Request body for updating the current developer profile.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    username: str | None = None
    email: str | None = None
