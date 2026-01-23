"""API client for the vclient service."""

from vclient.api.client import VClient
from vclient.api.config import APIConfig
from vclient.api.endpoints import Endpoints
from vclient.api.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from vclient.api.models import (
    Company,
    CompanyPermission,
    CompanyPermissions,
    CompanySettings,
    CreateCompanyRequest,
    GrantAccessRequest,
    PaginatedResponse,
    PermissionManageCampaign,
    PermissionsFreeTraitChanges,
    PermissionsGrantXP,
    UpdateCompanyRequest,
)
from vclient.api.services import CompaniesService

__all__ = [
    "APIConfig",
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "CompaniesService",
    "Company",
    "CompanyPermission",
    "CompanyPermissions",
    "CompanySettings",
    "ConflictError",
    "CreateCompanyRequest",
    "Endpoints",
    "GrantAccessRequest",
    "NotFoundError",
    "PaginatedResponse",
    "PermissionManageCampaign",
    "PermissionsFreeTraitChanges",
    "PermissionsGrantXP",
    "RateLimitError",
    "ServerError",
    "UpdateCompanyRequest",
    "VClient",
    "ValidationError",
]
