"""Custom exceptions for the API client."""

from typing import Any


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the API error.

        Args:
            message: Human-readable error message.
            status_code: HTTP status code from the response.
            response_data: Raw response data from the API.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(APIError):
    """Raised when authentication fails (401)."""


class AuthorizationError(APIError):
    """Raised when authorization fails (403)."""


class NotFoundError(APIError):
    """Raised when a resource is not found (404)."""


class ConflictError(APIError):
    """Raised when there is a conflict (409), such as idempotency key reuse with different body."""


class ValidationError(APIError):
    """Raised when request validation fails (422)."""


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429)."""


class ServerError(APIError):
    """Raised when the server returns a 5xx error."""
