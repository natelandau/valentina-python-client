"""Tests for vclient.api.exceptions."""

import pytest

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


class TestAPIError:
    """Tests for APIError base class."""

    def test_init_with_message_only(self):
        """Verify creating an error with just a message."""
        # When: Creating an error with message only
        error = APIError("Something went wrong")

        # Then: Message is set and defaults are applied
        assert error.message == "Something went wrong"
        assert error.status_code is None
        assert error.response_data == {}

    def test_init_with_all_params(self):
        """Verify creating an error with all parameters."""
        # When: Creating an error with all parameters
        error = APIError(
            message="Not found",
            status_code=404,
            response_data={"detail": "Resource not found"},
        )

        # Then: All values are stored
        assert error.message == "Not found"
        assert error.status_code == 404
        assert error.response_data == {"detail": "Resource not found"}

    def test_str_with_status_code(self):
        """Verify string representation includes status code."""
        # Given: An error with status code
        error = APIError("Bad request", status_code=400)

        # When/Then: String representation includes status code
        assert str(error) == "[400] Bad request"

    def test_str_without_status_code(self):
        """Verify string representation without status code."""
        # Given: An error without status code
        error = APIError("Unknown error")

        # When/Then: String representation is just the message
        assert str(error) == "Unknown error"

    def test_is_exception(self):
        """Verify APIError is a proper exception."""
        # Given: An error message
        msg = "Test error"

        # When/Then: Error can be raised and caught
        with pytest.raises(APIError) as exc_info:
            raise APIError(msg, status_code=500)

        assert exc_info.value.status_code == 500


class TestSpecificErrors:
    """Tests for specific error subclasses."""

    @pytest.mark.parametrize(
        ("error_class", "expected_parent"),
        [
            (AuthenticationError, APIError),
            (AuthorizationError, APIError),
            (NotFoundError, APIError),
            (ConflictError, APIError),
            (ValidationError, APIError),
            (RateLimitError, APIError),
            (ServerError, APIError),
        ],
    )
    def test_inheritance(self, error_class, expected_parent):
        """Verify all error classes inherit from APIError."""
        # When/Then: Error class is a subclass of expected parent
        assert issubclass(error_class, expected_parent)

    @pytest.mark.parametrize(
        ("error_class", "message"),
        [
            (AuthenticationError, "Invalid API key"),
            (AuthorizationError, "Permission denied"),
            (NotFoundError, "Resource not found"),
            (ConflictError, "Idempotency key conflict"),
            (ValidationError, "Invalid input"),
            (RateLimitError, "Too many requests"),
            (ServerError, "Internal server error"),
        ],
    )
    def test_can_raise_and_catch(self, error_class, message):
        """Verify specific errors can be raised and caught."""
        # When/Then: Specific error can be raised and caught
        with pytest.raises(error_class) as exc_info:
            raise error_class(message, status_code=400)

        assert message in str(exc_info.value)

    def test_catch_specific_error_as_api_error(self):
        """Verify specific errors can be caught as APIError."""
        # Given: A specific error type
        msg = "Not found"

        # When/Then: Specific error can be caught as base APIError
        with pytest.raises(APIError):
            raise NotFoundError(msg, status_code=404)
