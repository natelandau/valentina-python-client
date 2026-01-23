"""API client for the vclient service."""

from vclient.api.client import VClient
from vclient.api.config import APIConfig
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
from vclient.api.models import PaginatedResponse

__all__ = [
    "APIConfig",
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "NotFoundError",
    "PaginatedResponse",
    "RateLimitError",
    "ServerError",
    "VClient",
    "ValidationError",
]
