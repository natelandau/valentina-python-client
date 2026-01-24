"""Custom exceptions for the API client.

Exceptions follow RFC 9457 Problem Details format for HTTP APIs.
See: https://docs.valentina-noir.com/technical/errors/
"""

from typing import TYPE_CHECKING, Any

from pydantic_core import ErrorDetails

if TYPE_CHECKING:
    from pydantic import ValidationError as PydanticValidationError


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
        """Return string representation of the error with full API context.

        Includes RFC 9457 Problem Details fields when available:
        - status code and title
        - detail message
        - instance URI
        """
        parts: list[str] = []

        # Build header: [status_code] title or message
        if self.status_code:
            header = f"[{self.status_code}]"
            if self.title:
                header = f"{header} {self.title}"
            elif self.message:
                header = f"{header} {self.message}"
            parts.append(header)
        elif self.message:
            parts.append(self.message)

        # Add detail if different from title/message
        if self.detail and self.detail not in (self.message, self.title):
            parts.append(f"Detail: {self.detail}")

        # Add instance URI for debugging
        if self.instance:
            parts.append(f"Instance: {self.instance}")

        return " | ".join(parts) if parts else "Unknown API error"

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

    def __str__(self) -> str:
        """Return string representation including validation field errors."""
        base = super().__str__()

        if not self.invalid_parameters:
            return base

        # Format validation errors as "field: message"
        field_errors = [
            f"{param.get('field', 'unknown')}: {param.get('message', 'invalid')}"
            for param in self.invalid_parameters
        ]
        return f"{base} | Fields: {'; '.join(field_errors)}"


class RequestValidationError(APIError):
    """Raised when request data fails client-side validation.

    This occurs before the API request is made, when input parameters
    don't meet the expected format or constraints. Unlike `ValidationError`,
    which is raised for server-side validation failures (HTTP 400), this
    exception is raised locally before any network request.
    """

    def __init__(self, pydantic_error: "PydanticValidationError") -> None:
        """Initialize the request validation error.

        Args:
            pydantic_error: The Pydantic ValidationError that triggered this exception.
        """
        errors = pydantic_error.errors()
        error_details = "; ".join(
            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in errors
        )
        message = f"Request validation failed: {error_details}"
        super().__init__(message, status_code=None, response_data=None)
        self._pydantic_error = pydantic_error

    @property
    def errors(self) -> list[ErrorDetails]:
        """Get structured validation errors from Pydantic.

        Returns:
            List of error dictionaries with 'type', 'loc', 'msg', and 'input' keys.
        """
        return self._pydantic_error.errors()


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429 Too Many Requests).

    Check the `retry_after` property for the number of seconds to wait before retrying.
    The `remaining` property shows how many tokens were left when the limit was hit.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        *,
        retry_after: int | None = None,
        remaining: int | None = None,
    ) -> None:
        """Initialize the rate limit error.

        Args:
            message: Human-readable error message.
            status_code: HTTP status code from the response.
            response_data: Raw response data from the API (RFC 9457 Problem Details).
            retry_after: Number of seconds to wait before retrying (from RateLimit or Retry-After header).
            remaining: Number of tokens remaining in the bucket (from RateLimit header "r" parameter).
        """
        super().__init__(message, status_code, response_data)
        self._retry_after = retry_after
        self._remaining = remaining

    @property
    def retry_after(self) -> int | None:
        """Get the number of seconds to wait before retrying.

        Returns:
            Number of seconds from the RateLimit header "t" parameter or Retry-After header,
            or None if not provided.
        """
        return self._retry_after

    @property
    def remaining(self) -> int | None:
        """Get the number of tokens remaining in the rate limit bucket.

        Returns:
            Number of remaining tokens from the RateLimit header "r" parameter,
            or None if not provided.
        """
        return self._remaining

    def __str__(self) -> str:
        """Return string representation including retry timing information."""
        base = super().__str__()
        extras: list[str] = []

        if self._retry_after is not None:
            extras.append(f"retry_after={self._retry_after}s")
        if self._remaining is not None:
            extras.append(f"remaining={self._remaining}")

        if extras:
            return f"{base} | {', '.join(extras)}"
        return base


class ServerError(APIError):
    """Raised when the server returns a 5xx error.

    Indicates an unexpected server error. Consider implementing retry logic
    with exponential backoff for these errors.
    """
