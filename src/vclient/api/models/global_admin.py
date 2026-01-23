"""Pydantic models for Global Admin API responses."""

from datetime import datetime

from pydantic import BaseModel, Field

from vclient.api.models.companies import CompanyPermission


class DeveloperCompanyPermission(BaseModel):
    """Company permission entry for a developer.

    Represents a single company access grant with its permission level.
    """

    company_id: str = Field(..., description="The company ID.")
    name: str | None = Field(default=None, description="The company name.")
    permission: CompanyPermission = Field(..., description="The permission level.")


class Developer(BaseModel):
    """Response model for a developer.

    Represents a developer account returned from the API with all its properties.
    """

    id: str | None = Field(default=None, description="MongoDB document ObjectID.")
    date_created: datetime | None = Field(
        default=None,
        description="Timestamp when the developer was created.",
    )
    date_modified: datetime | None = Field(
        default=None,
        description="Timestamp when the developer was last modified.",
    )
    username: str = Field(..., description="Developer username.")
    email: str = Field(..., description="Developer email address.")
    key_generated: datetime | None = Field(
        default=None,
        description="Timestamp when the API key was last generated.",
    )
    is_global_admin: bool = Field(
        default=False,
        description="Whether the developer has global admin privileges.",
    )
    companies: list[DeveloperCompanyPermission] = Field(
        default_factory=list,
        description="List of company permissions for this developer.",
    )


class DeveloperWithApiKey(Developer):
    """Developer response that includes the generated API key.

    Only returned when generating a new API key. The key will not be shown again.
    """

    api_key: str | None = Field(
        default=None,
        description="The newly generated API key. Save this immediately.",
    )


# -----------------------------------------------------------------------------
# Request Body Models
# -----------------------------------------------------------------------------


class CreateDeveloperRequest(BaseModel):
    """Request body for creating a new developer.

    Used to construct the JSON payload for developer creation.
    """

    username: str = Field(..., description="Developer username.")
    email: str = Field(..., description="Developer email address.")
    is_global_admin: bool = Field(
        default=False,
        description="Whether the developer has global admin privileges.",
    )


class UpdateDeveloperRequest(BaseModel):
    """Request body for updating a developer.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    username: str | None = Field(default=None, description="Developer username.")
    email: str | None = Field(default=None, description="Developer email address.")
    is_global_admin: bool | None = Field(
        default=None,
        description="Whether the developer has global admin privileges.",
    )
