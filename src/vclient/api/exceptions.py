"""Custom exceptions for the API client.

Exceptions follow RFC 9457 Problem Details format for HTTP APIs.
See: https://docs.valentina-noir.com/technical/errors/
"""

from typing import Any


class APIError(Exception):
    """Base exception for API errors following RFC 9457 Problem Details format.

    All API errors include standard fields from RFC 9457:
    - status: HTTP status code
    - title: Short, human-readable summary of the problem type
    - detail: Human-readable explanation specific to this occurrence
    - instance: URI reference identifying the specific occurrence
    """

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
            response_data: Raw response data from the API (RFC 9457 Problem Details).
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

    @property
    def title(self) -> str | None:
        """Get the RFC 9457 title field - short problem type summary."""
        return self.response_data.get("title")

    @property
    def detail(self) -> str | None:
        """Get the RFC 9457 detail field - human-readable explanation."""
        return self.response_data.get("detail")

    @property
    def instance(self) -> str | None:
        """Get the RFC 9457 instance field - URI reference to this occurrence."""
        return self.response_data.get("instance")


class AuthenticationError(APIError):
    """Raised when authentication fails (401 Unauthorized).

    Indicates the API key is missing or invalid.
    """


class AuthorizationError(APIError):
    """Raised when authorization fails (403 Forbidden).

    Indicates the API key is valid but lacks permission for the requested action.
    """


class NotFoundError(APIError):
    """Raised when a resource is not found (404 Not Found)."""


class ConflictError(APIError):
    """Raised when there is a conflict (409 Conflict).

    Common cause is reusing an idempotency key with a different request body.
    """


class ValidationError(APIError):
    """Raised when request validation fails (400 Bad Request).

    Validation errors include an `invalid_parameters` array identifying
    which fields failed validation with specific error messages.
    """

    @property
    def invalid_parameters(self) -> list[dict[str, str]]:
        """Get the list of invalid parameters from validation errors.

        Returns:
            List of dicts with 'field' and 'message' keys describing validation failures.
        """
        return self.response_data.get("invalid_parameters", [])


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429 Too Many Requests).

    Check the `retry_after` property for the number of seconds to wait before retrying.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        *,
        retry_after: int | None = None,
    ) -> None:
        """Initialize the rate limit error.

        Args:
            message: Human-readable error message.
            status_code: HTTP status code from the response.
            response_data: Raw response data from the API (RFC 9457 Problem Details).
            retry_after: Number of seconds to wait before retrying (from Retry-After header).
        """
        super().__init__(message, status_code, response_data)
        self._retry_after = retry_after

    @property
    def retry_after(self) -> int | None:
        """Get the number of seconds to wait before retrying.

        Returns:
            Number of seconds from the Retry-After header, or None if not provided.
        """
        return self._retry_after


class ServerError(APIError):
    """Raised when the server returns a 5xx error.

    Indicates an unexpected server error. Consider implementing retry logic
    with exponential backoff for these errors.
    """
