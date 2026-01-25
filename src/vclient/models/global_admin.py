"""Pydantic models for Global Admin API responses."""

from datetime import datetime

from pydantic import BaseModel

from vclient.models.companies import PermissionLevel


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


class CreateDeveloperRequest(BaseModel):
    """Request body for creating a new developer.

    Used to construct the JSON payload for developer creation.
    """

    username: str
    email: str
    is_global_admin: bool = False


class UpdateDeveloperRequest(BaseModel):
    """Request body for updating a developer.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    username: str | None = None
    email: str | None = None
    is_global_admin: bool | None = None
