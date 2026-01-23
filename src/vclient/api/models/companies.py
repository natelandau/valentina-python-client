"""Pydantic models for Company API responses."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# Type aliases for permission levels (replaces StrEnum classes)
PermissionLevel = Literal["USER", "ADMIN", "OWNER", "REVOKE"]
"""Permission levels for company access."""

ManageCampaignPermission = Literal["UNRESTRICTED", "STORYTELLER"]
"""Permissions for managing a campaign."""

GrantXPPermission = Literal["UNRESTRICTED", "PLAYER", "STORYTELLER"]
"""Permissions for adding XP to a character."""

FreeTraitChangesPermission = Literal["UNRESTRICTED", "WITHIN_24_HOURS", "STORYTELLER"]
"""Permissions for updating character trait values."""


class CompanySettings(BaseModel):
    """Settings configuration for a company.

    Controls various permissions and configuration options for the company.
    """

    character_autogen_xp_cost: int | None = Field(
        default=10,
        ge=0,
        le=100,
        description="The cost to autogen XP for a character.",
    )
    character_autogen_num_choices: int | None = Field(
        default=3,
        ge=1,
        le=10,
        description="The number of characters generated for a user to select from.",
    )
    permission_manage_campaign: ManageCampaignPermission | None = Field(
        default="UNRESTRICTED",
        description="Permission level required to manage campaigns.",
    )
    permission_grant_xp: GrantXPPermission | None = Field(
        default="UNRESTRICTED",
        description="Permission level required to grant XP.",
    )
    permission_free_trait_changes: FreeTraitChangesPermission | None = Field(
        default="UNRESTRICTED",
        description="Permission level required for free trait changes.",
    )


class Company(BaseModel):
    """Response model for a company.

    Represents a company entity returned from the API with all its properties and settings.
    """

    id: str | None = Field(default=None, description="MongoDB document ObjectID.")
    date_created: datetime | None = Field(
        default=None,
        description="Timestamp when the company was created.",
    )
    date_modified: datetime | None = Field(
        default=None,
        description="Timestamp when the company was last modified.",
    )
    name: str = Field(..., min_length=3, max_length=50, description="Company name.")
    description: str | None = Field(
        default=None,
        min_length=3,
        description="Company description.",
    )
    email: str = Field(..., description="Company contact email.")
    user_ids: list[str] = Field(
        default_factory=list,
        description="List of user IDs associated with the company.",
    )
    settings: CompanySettings | None = Field(
        default=None,
        description="Company settings and configuration.",
    )


class CompanyPermissions(BaseModel):
    """Response model for company permission grants.

    Returned when granting or modifying developer access to a company.
    """

    company_id: str = Field(..., description="The company ID.")
    name: str | None = Field(default=None, description="The company name.")
    permission: PermissionLevel = Field(..., description="The permission level granted.")


# -----------------------------------------------------------------------------
# Request Body Models
# -----------------------------------------------------------------------------


class CreateCompanyRequest(BaseModel):
    """Request body for creating a new company.

    Used to construct the JSON payload for company creation.
    """

    name: str = Field(..., min_length=3, max_length=50, description="Company name.")
    email: str = Field(..., description="Company contact email.")
    description: str | None = Field(default=None, min_length=3, description="Company description.")
    settings: CompanySettings | None = Field(default=None, description="Company settings.")


class UpdateCompanyRequest(BaseModel):
    """Request body for updating a company.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    name: str | None = Field(default=None, min_length=3, max_length=50, description="Company name.")
    email: str | None = Field(default=None, description="Company contact email.")
    description: str | None = Field(default=None, min_length=3, description="Company description.")
    settings: CompanySettings | None = Field(default=None, description="Company settings.")


class GrantAccessRequest(BaseModel):
    """Request body for granting developer access to a company."""

    developer_id: str = Field(..., description="The developer ID to grant access to.")
    permission: PermissionLevel = Field(..., description="The permission level to grant.")
