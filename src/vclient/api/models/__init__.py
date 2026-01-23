"""Data models for API responses."""

from vclient.api.models.companies import (
    Company,
    CompanyPermission,
    CompanyPermissions,
    CompanySettings,
    CreateCompanyRequest,
    GrantAccessRequest,
    PermissionManageCampaign,
    PermissionsFreeTraitChanges,
    PermissionsGrantXP,
    UpdateCompanyRequest,
)
from vclient.api.models.pagination import PaginatedResponse

__all__ = [
    "Company",
    "CompanyPermission",
    "CompanyPermissions",
    "CompanySettings",
    "CreateCompanyRequest",
    "GrantAccessRequest",
    "PaginatedResponse",
    "PermissionManageCampaign",
    "PermissionsFreeTraitChanges",
    "PermissionsGrantXP",
    "UpdateCompanyRequest",
]
