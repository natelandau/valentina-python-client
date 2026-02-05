"""Pydantic models for Company API responses."""

from datetime import datetime

from pydantic import BaseModel, Field

from vclient.constants import (
    FreeTraitChangesPermission,
    GrantXPPermission,
    ManageCampaignPermission,
    PermissionLevel,
)
from vclient.models.users import User


class CompanySettings(BaseModel):
    """Settings configuration for a company.

    Controls various permissions and configuration options for the company.
    Used in both response and request contexts; defaults support partial updates.
    """

    character_autogen_xp_cost: int | None = None
    character_autogen_num_choices: int | None = None
    permission_manage_campaign: ManageCampaignPermission | None = None
    permission_grant_xp: GrantXPPermission | None = None
    permission_free_trait_changes: FreeTraitChangesPermission | None = None


class Company(BaseModel):
    """Response model for a company.

    Represents a company entity returned from the API with all its properties and settings.
    """

    id: str
    date_created: datetime
    date_modified: datetime
    name: str
    description: str | None
    email: str
    user_ids: list[str]
    settings: CompanySettings | None


class CompanyPermissions(BaseModel):
    """Response model for company permission grants.

    Returned when granting or modifying developer access to a company.
    """

    company_id: str
    name: str | None
    permission: PermissionLevel


class NewCompanyResponse(BaseModel):
    """Response model for creating a new company.

    Returned when a new company is created.
    """

    company: Company
    admin_user: User


# -----------------------------------------------------------------------------
# Request Body Models
# -----------------------------------------------------------------------------


class CompanyCreate(BaseModel):
    """Request body for creating a new company.

    Used to construct the JSON payload for company creation.
    """

    name: str = Field(min_length=3, max_length=50)
    email: str
    description: str | None = Field(default=None, min_length=3)
    settings: CompanySettings | None = None


class CompanyUpdate(BaseModel):
    """Request body for updating a company.

    Only include fields that need to be changed; omitted fields remain unchanged.
    """

    name: str | None = Field(default=None, min_length=3, max_length=50)
    email: str | None = None
    description: str | None = Field(default=None, min_length=3)
    settings: CompanySettings | None = None


class _GrantAccess(BaseModel):
    """Internal request body for granting developer access to a company."""

    developer_id: str
    permission: PermissionLevel


__all__ = [
    "Company",
    "CompanyCreate",
    "CompanyPermissions",
    "CompanySettings",
    "CompanyUpdate",
    "NewCompanyResponse",
    "_GrantAccess",
]
