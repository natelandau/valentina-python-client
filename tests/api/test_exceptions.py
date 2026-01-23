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


class TestRFC9457Properties:
    """Tests for RFC 9457 Problem Details properties on APIError."""

    def test_title_property(self):
        """Verify title property extracts from response_data."""
        # Given: An error with RFC 9457 response data
        error = APIError(
            message="Not found",
            status_code=404,
            response_data={
                "status": 404,
                "title": "Not Found",
                "detail": "Company 'abc123' not found",
                "instance": "/api/v1/companies/abc123",
            },
        )

        # Then: Title property returns the correct value
        assert error.title == "Not Found"

    def test_detail_property(self):
        """Verify detail property extracts from response_data."""
        # Given: An error with RFC 9457 response data
        error = APIError(
            message="Not found",
            status_code=404,
            response_data={
                "status": 404,
                "title": "Not Found",
                "detail": "Company 'abc123' not found",
                "instance": "/api/v1/companies/abc123",
            },
        )

        # Then: Detail property returns the correct value
        assert error.detail == "Company 'abc123' not found"

    def test_instance_property(self):
        """Verify instance property extracts from response_data."""
        # Given: An error with RFC 9457 response data
        error = APIError(
            message="Not found",
            status_code=404,
            response_data={
                "status": 404,
                "title": "Not Found",
                "detail": "Company 'abc123' not found",
                "instance": "/api/v1/companies/abc123",
            },
        )

        # Then: Instance property returns the correct value
        assert error.instance == "/api/v1/companies/abc123"

    def test_properties_return_none_when_missing(self):
        """Verify RFC 9457 properties return None when not in response_data."""
        # Given: An error without RFC 9457 fields
        error = APIError(message="Error", status_code=500, response_data={})

        # Then: All RFC 9457 properties return None
        assert error.title is None
        assert error.detail is None
        assert error.instance is None


class TestValidationError:
    """Tests for ValidationError class."""

    def test_invalid_parameters_property(self):
        """Verify invalid_parameters extracts validation errors from response_data."""
        # Given: A validation error with invalid_parameters
        error = ValidationError(
            message="Validation failed",
            status_code=400,
            response_data={
                "status": 400,
                "title": "Bad Request",
                "detail": "Validation failed for one or more fields.",
                "instance": "/api/v1/companies/abc123/users",
                "invalid_parameters": [
                    {"field": "name", "message": "Field required"},
                    {
                        "field": "role",
                        "message": "Input should be 'ADMIN', 'STORYTELLER' or 'PLAYER'",
                    },
                ],
            },
        )

        # Then: invalid_parameters property returns the list
        assert len(error.invalid_parameters) == 2
        assert error.invalid_parameters[0]["field"] == "name"
        assert error.invalid_parameters[0]["message"] == "Field required"
        assert error.invalid_parameters[1]["field"] == "role"

    def test_invalid_parameters_returns_empty_list_when_missing(self):
        """Verify invalid_parameters returns empty list when not in response_data."""
        # Given: A validation error without invalid_parameters
        error = ValidationError(
            message="Validation failed",
            status_code=400,
            response_data={"detail": "Validation failed"},
        )

        # Then: invalid_parameters returns empty list
        assert error.invalid_parameters == []


class TestRateLimitError:
    """Tests for RateLimitError class."""

    def test_retry_after_property(self):
        """Verify retry_after property returns the value passed to constructor."""
        # Given: A rate limit error with retry_after
        error = RateLimitError(
            message="Too many requests",
            status_code=429,
            response_data={"detail": "You are being rate limited."},
            retry_after=60,
        )

        # Then: retry_after property returns the correct value
        assert error.retry_after == 60

    def test_retry_after_is_none_when_not_provided(self):
        """Verify retry_after is None when not provided."""
        # Given: A rate limit error without retry_after
        error = RateLimitError(
            message="Too many requests",
            status_code=429,
            response_data={"detail": "You are being rate limited."},
        )

        # Then: retry_after is None
        assert error.retry_after is None

    def test_inherits_rfc9457_properties(self):
        """Verify RateLimitError inherits RFC 9457 properties from APIError."""
        # Given: A rate limit error with full RFC 9457 response
        error = RateLimitError(
            message="Too many requests",
            status_code=429,
            response_data={
                "status": 429,
                "title": "Too Many Requests",
                "detail": "You are being rate limited.",
                "instance": "/api/v1/companies",
            },
            retry_after=30,
        )

        # Then: All properties are accessible
        assert error.title == "Too Many Requests"
        assert error.detail == "You are being rate limited."
        assert error.instance == "/api/v1/companies"
        assert error.retry_after == 30


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
            (ServerError, "Internal server error"),
        ],
    )
    def test_can_raise_and_catch(self, error_class, message):
        """Verify specific errors can be raised and caught."""
        # When/Then: Specific error can be raised and caught
        with pytest.raises(error_class) as exc_info:
            raise error_class(message, status_code=400)

        assert message in str(exc_info.value)

    def test_can_raise_and_catch_rate_limit_error(self):
        """Verify RateLimitError can be raised and caught with retry_after."""
        # When/Then: RateLimitError can be raised with retry_after
        with pytest.raises(RateLimitError) as exc_info:
            raise RateLimitError("Too many requests", status_code=429, retry_after=60)

        assert "Too many requests" in str(exc_info.value)
        assert exc_info.value.retry_after == 60

    def test_catch_specific_error_as_api_error(self):
        """Verify specific errors can be caught as APIError."""
        # Given: A specific error type
        msg = "Not found"

        # When/Then: Specific error can be caught as base APIError
        with pytest.raises(APIError):
            raise NotFoundError(msg, status_code=404)
