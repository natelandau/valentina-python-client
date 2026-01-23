"""Valentina API client library."""

from vclient.api import (
    APIConfig,
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    VClient,
    companies_service,
    configure_default_client,
    default_client,
    global_admin_service,
    system_service,
)

__all__ = [
    "APIConfig",
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "VClient",
    "ValidationError",
    "companies_service",
    "configure_default_client",
    "default_client",
    "global_admin_service",
    "system_service",
]
