"""Tests for vclient.services.base."""

import httpx
import pytest
import respx

from vclient.constants import API_KEY_HEADER, IDEMPOTENCY_KEY_HEADER
from vclient.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from vclient.models.pagination import PaginatedResponse
from vclient.services.base import BaseService

pytestmark = pytest.mark.anyio


class TestBaseServiceRequest:
    """Tests for BaseService._request method."""

    @respx.mock
    async def test_successful_get_request(self, base_service, base_url):
        """Verify successful GET requests return response."""
        # Given: A mocked API endpoint that returns success
        route = respx.get(f"{base_url}/test-path").respond(200, json={"success": True})

        # When: Making a GET request
        response = await base_service._get("/test-path")

        # Then: Response contains expected data
        assert route.called
        assert response.status_code == 200
        assert response.json() == {"success": True}

    @respx.mock
    async def test_request_with_params(self, base_service, base_url):
        """Verify query parameters are passed correctly."""
        # Given: A mocked endpoint expecting specific params
        route = respx.get(f"{base_url}/test", params={"key": "value"}).respond(200, json={})

        # When: Making a GET request with params
        await base_service._get("/test", params={"key": "value"})

        # Then: Request was made with correct params
        assert route.called

    @respx.mock
    async def test_post_with_json_body(self, base_service, base_url):
        """Verify POST request sends JSON body correctly."""
        # Given: A mocked POST endpoint
        route = respx.post(f"{base_url}/items").respond(201, json={"id": 1})

        # When: Making a POST request with JSON body
        response = await base_service._post("/items", json={"name": "test"})

        # Then: Request was made with correct body
        assert route.called
        assert response.status_code == 201
        request = route.calls.last.request
        assert b'"name"' in request.content


class TestBaseServiceErrorHandling:
    """Tests for BaseService error handling."""

    @pytest.mark.parametrize(
        ("status_code", "expected_exception"),
        [
            (400, ValidationError),
            (401, AuthenticationError),
            (403, AuthorizationError),
            (404, NotFoundError),
            (409, ConflictError),
            (429, RateLimitError),
            (500, ServerError),
            (502, ServerError),
            (503, ServerError),
            (418, APIError),
        ],
    )
    @respx.mock
    async def test_error_status_codes_raise_correct_exception(
        self, base_service, base_url, status_code, expected_exception, mocker
    ):
        """Verify error status codes raise appropriate exceptions."""
        # Given: Mock sleep to avoid delays on 429 retries
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: A mocked endpoint returning an error status
        respx.get(f"{base_url}/error").respond(status_code, json={"detail": "Error message"})

        # When/Then: Making a request raises the expected exception
        with pytest.raises(expected_exception) as exc_info:
            await base_service._get("/error")

        assert exc_info.value.status_code == status_code
        assert "Error message" in exc_info.value.message

    @respx.mock
    async def test_error_with_non_json_response(self, base_service, base_url):
        """Verify error handling when response is not JSON."""
        # Given: A mocked endpoint returning plain text error
        respx.get(f"{base_url}/error").respond(500, text="Internal Server Error")

        # When/Then: Making a request raises ServerError with text message
        with pytest.raises(ServerError) as exc_info:
            await base_service._get("/error")

        assert "Internal Server Error" in exc_info.value.message

    @respx.mock
    async def test_validation_error_includes_invalid_parameters(self, base_service, base_url):
        """Verify ValidationError includes invalid_parameters from response."""
        # Given: A mocked endpoint returning a validation error with invalid_parameters
        respx.post(f"{base_url}/users").respond(
            400,
            json={
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

        # When/Then: Making a request raises ValidationError with invalid_parameters
        with pytest.raises(ValidationError) as exc_info:
            await base_service._post("/users", json={"email": "test@example.com"})

        assert exc_info.value.status_code == 400
        assert len(exc_info.value.invalid_parameters) == 2
        assert exc_info.value.invalid_parameters[0]["field"] == "name"
        assert exc_info.value.title == "Bad Request"
        assert exc_info.value.instance == "/api/v1/companies/abc123/users"

    @respx.mock
    async def test_rate_limit_error_includes_retry_after(self, base_service, base_url, mocker):
        """Verify RateLimitError includes retry_after from Retry-After header."""
        # Given: Mock sleep to avoid actual delays during retries
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: A mocked endpoint returning 429 with Retry-After header
        respx.get(f"{base_url}/limited").respond(
            429,
            json={
                "status": 429,
                "title": "Too Many Requests",
                "detail": "You are being rate limited.",
                "instance": "/api/v1/companies",
            },
            headers={"Retry-After": "60"},
        )

        # When/Then: Making a request raises RateLimitError with retry_after
        with pytest.raises(RateLimitError) as exc_info:
            await base_service._get("/limited")

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60
        assert exc_info.value.title == "Too Many Requests"

    @respx.mock
    async def test_rate_limit_error_without_retry_after_header(
        self, base_service, base_url, mocker
    ):
        """Verify RateLimitError works without Retry-After header."""
        # Given: Mock sleep to avoid actual delays during retries
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: A mocked endpoint returning 429 without Retry-After header
        respx.get(f"{base_url}/limited").respond(
            429,
            json={"detail": "Rate limit exceeded"},
        )

        # When/Then: Making a request raises RateLimitError with retry_after=None
        with pytest.raises(RateLimitError) as exc_info:
            await base_service._get("/limited")

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after is None

    @respx.mock
    async def test_rate_limit_error_with_invalid_retry_after_header(
        self, base_service, base_url, mocker
    ):
        """Verify RateLimitError handles invalid Retry-After header gracefully."""
        # Given: Mock sleep to avoid actual delays during retries
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: A mocked endpoint returning 429 with non-numeric Retry-After
        respx.get(f"{base_url}/limited").respond(
            429,
            json={"detail": "Rate limit exceeded"},
            headers={"Retry-After": "invalid"},
        )

        # When/Then: Making a request raises RateLimitError with retry_after=None
        with pytest.raises(RateLimitError) as exc_info:
            await base_service._get("/limited")

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after is None


class TestBaseServiceHTTPMethods:
    """Tests for BaseService HTTP method helpers."""

    @respx.mock
    @pytest.mark.parametrize(
        ("method", "status"),
        [
            ("GET", 200),
            ("POST", 201),
            ("PUT", 200),
            ("PATCH", 200),
            ("DELETE", 204),
        ],
    )
    async def test_http_methods(self, base_service, base_url, method, status):
        """Verify HTTP methods make correct requests."""
        # Given: A mocked endpoint for the HTTP method
        route = getattr(respx, method.lower())(f"{base_url}/path").respond(
            status, json={} if method != "DELETE" else None
        )

        # When: Calling the corresponding method
        service_method = getattr(base_service, f"_{method.lower()}")
        if method in ("POST", "PUT", "PATCH"):
            await service_method("/path", json={"data": "value"})
        else:
            await service_method("/path")

        # Then: Correct HTTP method was used
        assert route.called
        assert route.calls.last.request.method == method


class TestBaseServiceIdempotency:
    """Tests for BaseService idempotency key support."""

    @respx.mock
    @pytest.mark.parametrize(
        ("method", "path", "status", "key"),
        [
            ("POST", "/items", 201, "post-key"),
            ("PUT", "/items/1", 200, "put-key"),
            ("PATCH", "/items/1", 200, "patch-key"),
        ],
    )
    async def test_explicit_idempotency_key(
        self, base_service, base_url, api_key, method, path, status, key
    ):
        """Verify requests include explicit idempotency key and preserve other headers."""
        # Given: A mocked endpoint
        route = getattr(respx, method.lower())(f"{base_url}{path}").respond(status, json={})

        # When: Making a request with explicit idempotency key
        service_method = getattr(base_service, f"_{method.lower()}")
        await service_method(path, json={}, idempotency_key=key)

        # Then: Request includes the idempotency key header and other headers
        assert route.called
        request = route.calls.last.request
        assert request.headers.get(IDEMPOTENCY_KEY_HEADER) == key
        assert request.headers.get(API_KEY_HEADER) == api_key

    @respx.mock
    async def test_post_without_idempotency_key(self, base_service, base_url):
        """Verify POST request without idempotency key has no header."""
        # Given: A mocked POST endpoint
        route = respx.post(f"{base_url}/items").respond(201, json={})

        # When: Making a POST request without idempotency key
        await base_service._post("/items", json={})

        # Then: Request does not include idempotency key header
        assert route.called
        request = route.calls.last.request
        assert IDEMPOTENCY_KEY_HEADER not in request.headers

    def test_generate_idempotency_key(self):
        """Verify generated idempotency keys are valid UUIDs and unique."""
        # When: Generating an idempotency key
        key = BaseService._generate_idempotency_key()

        # Then: Key is a valid UUID format (8-4-4-4-12 hex chars)
        assert len(key) == 36
        assert key.count("-") == 4

        # When: Generating 100 idempotency keys
        keys = {BaseService._generate_idempotency_key() for _ in range(100)}

        # Then: All keys are unique
        assert len(keys) == 100

    @respx.mock
    @pytest.mark.parametrize(
        ("method", "path", "status"),
        [
            ("POST", "/items", 201),
            ("PUT", "/items/1", 200),
            ("PATCH", "/items/1", 200),
        ],
    )
    async def test_auto_generates_idempotency_key_when_enabled(
        self, base_service_with_auto_idempotency, base_url, api_key, method, path, status
    ):
        """Verify requests auto-generate idempotency key and preserve other headers."""
        # Given: A mocked endpoint
        route = getattr(respx, method.lower())(f"{base_url}{path}").respond(status, json={})

        # When: Making a request without explicit idempotency key
        service_method = getattr(base_service_with_auto_idempotency, f"_{method.lower()}")
        await service_method(path, json={})

        # Then: Request includes an auto-generated idempotency key header and other headers
        assert route.called
        request = route.calls.last.request
        key = request.headers.get(IDEMPOTENCY_KEY_HEADER)
        assert key is not None
        assert len(key) == 36
        assert key.count("-") == 4
        assert request.headers.get(API_KEY_HEADER) == api_key

    @respx.mock
    async def test_explicit_key_takes_precedence_over_auto(
        self, base_service_with_auto_idempotency, base_url, api_key
    ):
        """Verify explicit idempotency key takes precedence and preserves other headers."""
        # Given: A mocked POST endpoint
        route = respx.post(f"{base_url}/items").respond(201, json={})

        # When: Making a POST request with explicit idempotency key
        await base_service_with_auto_idempotency._post(
            "/items", json={}, idempotency_key="explicit-key"
        )

        # Then: Request uses the explicit key and preserves other headers
        assert route.called
        request = route.calls.last.request
        assert request.headers.get(IDEMPOTENCY_KEY_HEADER) == "explicit-key"
        assert request.headers.get(API_KEY_HEADER) == api_key


class TestBaseServicePagination:
    """Tests for BaseService pagination methods."""

    @respx.mock
    async def test_get_paginated(self, base_service, base_url):
        """Verify _get_paginated returns PaginatedResponse."""
        # Given: A mocked paginated endpoint
        route = respx.get(f"{base_url}/items", params={"limit": "10", "offset": "0"}).respond(
            200,
            json={
                "items": [{"id": 1}, {"id": 2}],
                "limit": 10,
                "offset": 0,
                "total": 2,
            },
        )

        # When: Calling _get_paginated
        result = await base_service._get_paginated("/items")

        # Then: Returns a PaginatedResponse with correct data
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.total == 2

    @respx.mock
    async def test_get_paginated_with_custom_limit_offset(self, base_service, base_url):
        """Verify _get_paginated accepts custom limit and offset."""
        # Given: A mocked paginated endpoint expecting custom params
        route = respx.get(f"{base_url}/items", params={"limit": "25", "offset": "50"}).respond(
            200,
            json={"items": [], "limit": 25, "offset": 50, "total": 100},
        )

        # When: Calling _get_paginated with custom limit and offset
        await base_service._get_paginated("/items", limit=25, offset=50)

        # Then: Request was made with correct params
        assert route.called

    @respx.mock
    async def test_get_paginated_clamps_limit(self, base_service, base_url):
        """Verify limit is clamped to valid range."""
        # Given: A mocked endpoint expecting max limit (100)
        route = respx.get(f"{base_url}/items", params={"limit": "100", "offset": "0"}).respond(
            200,
            json={"items": [], "limit": 100, "offset": 0, "total": 0},
        )

        # When: Calling _get_paginated with excessive limit
        await base_service._get_paginated("/items", limit=999)

        # Then: Request was made with clamped limit
        assert route.called

    @respx.mock
    async def test_iter_all_pages(self, base_service, base_url):
        """Verify _iter_all_pages iterates through all pages."""
        # Given: Mocked endpoints for 3 pages of data
        respx.get(f"{base_url}/items", params={"limit": "2", "offset": "0"}).respond(
            200,
            json={
                "items": [{"id": 1}, {"id": 2}],
                "limit": 2,
                "offset": 0,
                "total": 5,
            },
        )
        respx.get(f"{base_url}/items", params={"limit": "2", "offset": "2"}).respond(
            200,
            json={
                "items": [{"id": 3}, {"id": 4}],
                "limit": 2,
                "offset": 2,
                "total": 5,
            },
        )
        respx.get(f"{base_url}/items", params={"limit": "2", "offset": "4"}).respond(
            200,
            json={
                "items": [{"id": 5}],
                "limit": 2,
                "offset": 4,
                "total": 5,
            },
        )

        # When: Iterating through all pages
        items = [item async for item in base_service._iter_all_pages("/items", limit=2)]

        # Then: All items from all pages are returned
        assert len(items) == 5
        assert [item["id"] for item in items] == [1, 2, 3, 4, 5]

    @respx.mock
    async def test_get_all(self, base_service, base_url):
        """Verify _get_all returns all items as a list."""
        # Given: A mocked paginated endpoint with all items in one page
        respx.get(f"{base_url}/items").respond(
            200,
            json={
                "items": [{"id": 1}, {"id": 2}, {"id": 3}],
                "limit": 100,
                "offset": 0,
                "total": 3,
            },
        )

        # When: Calling _get_all
        items = await base_service._get_all("/items")

        # Then: All items are returned as a list
        assert len(items) == 3
        assert isinstance(items, list)


class TestBaseServiceRateLimitHeaderParsing:
    """Tests for BaseService rate limit header parsing."""

    def test_parse_rate_limit_header_t_value(self):
        """Verify parsing the 't' parameter from RateLimit header."""
        # Given: A RateLimit header with t value
        header = '"default";r=10;t=5'

        # When: Parsing the t parameter
        result = BaseService._parse_rate_limit_header_value(header, "t")

        # Then: The correct value is returned
        assert result == 5

    def test_parse_rate_limit_header_r_value(self):
        """Verify parsing the 'r' parameter from RateLimit header."""
        # Given: A RateLimit header with r value
        header = '"default";r=47;t=0'

        # When: Parsing the r parameter
        result = BaseService._parse_rate_limit_header_value(header, "r")

        # Then: The correct value is returned
        assert result == 47

    def test_parse_rate_limit_header_missing_parameter(self):
        """Verify parsing returns None for missing parameter."""
        # Given: A RateLimit header without the requested parameter
        header = '"default";r=10'

        # When: Parsing a missing parameter
        result = BaseService._parse_rate_limit_header_value(header, "t")

        # Then: None is returned
        assert result is None

    def test_parse_rate_limit_header_multiple_policies(self):
        """Verify parsing works with multiple comma-separated policies."""
        # Given: A RateLimit header with multiple policies
        header = '"burst";r=8;t=0, "sustained";r=95;t=0'

        # When: Parsing the r parameter (gets first policy's value)
        result = BaseService._parse_rate_limit_header_value(header, "r")

        # Then: The first policy's value is returned
        assert result == 8

    def test_parse_rate_limit_header_invalid_value(self):
        """Verify parsing handles non-numeric values gracefully."""
        # Given: A RateLimit header with invalid numeric value
        header = '"default";r=invalid;t=5'

        # When: Parsing the invalid parameter
        result = BaseService._parse_rate_limit_header_value(header, "r")

        # Then: None is returned
        assert result is None

    @respx.mock
    async def test_rate_limit_error_includes_remaining_from_header(
        self, base_service, base_url, mocker
    ):
        """Verify RateLimitError includes remaining tokens from RateLimit header."""
        # Given: Mock sleep to avoid actual delays during retries
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: A mocked endpoint returning 429 with RateLimit header
        respx.get(f"{base_url}/limited").respond(
            429,
            json={"detail": "Rate limit exceeded"},
            headers={"RateLimit": '"default";r=0;t=5'},
        )

        # When/Then: Making a request raises RateLimitError with remaining
        with pytest.raises(RateLimitError) as exc_info:
            await base_service._get("/limited")

        assert exc_info.value.remaining == 0
        assert exc_info.value.retry_after == 5

    @respx.mock
    async def test_rate_limit_prefers_rate_limit_header_over_retry_after(
        self, base_service, base_url, mocker
    ):
        """Verify RateLimit header 't' value is preferred over Retry-After."""
        # Given: Mock sleep to avoid actual delays during retries
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: A mocked endpoint with both RateLimit and Retry-After headers
        respx.get(f"{base_url}/limited").respond(
            429,
            json={"detail": "Rate limit exceeded"},
            headers={
                "RateLimit": '"default";r=0;t=10',
                "Retry-After": "60",
            },
        )

        # When/Then: Making a request uses RateLimit header value
        with pytest.raises(RateLimitError) as exc_info:
            await base_service._get("/limited")

        # RateLimit t=10 should be preferred over Retry-After: 60
        assert exc_info.value.retry_after == 10

    @respx.mock
    async def test_rate_limit_falls_back_to_retry_after_header(
        self, base_service, base_url, mocker
    ):
        """Verify Retry-After header is used when RateLimit header lacks 't' value."""
        # Given: Mock sleep to avoid actual delays during retries
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: A mocked endpoint with only Retry-After header
        respx.get(f"{base_url}/limited").respond(
            429,
            json={"detail": "Rate limit exceeded"},
            headers={"Retry-After": "30"},
        )

        # When/Then: Making a request uses Retry-After header value
        with pytest.raises(RateLimitError) as exc_info:
            await base_service._get("/limited")

        assert exc_info.value.retry_after == 30


class TestBaseServiceRateLimitRetry:
    """Tests for BaseService rate limit auto-retry behavior."""

    @respx.mock
    async def test_auto_retry_on_rate_limit_success(self, vclient, base_url, mocker):
        """Verify request is retried on 429 and succeeds after retry."""
        # Given: An endpoint that returns 429 once then succeeds
        route = respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.Response(
                    429,
                    json={"detail": "Rate limited"},
                    headers={"RateLimit": '"default";r=0;t=0'},
                ),
                httpx.Response(200, json={"success": True}),
            ]
        )

        # Given: Mock asyncio.sleep to avoid actual delays
        mock_sleep = mocker.patch("vclient.services.base.asyncio.sleep")

        # When: Making a request
        from vclient.services.base import BaseService

        service = BaseService(vclient)
        response = await service._get("/test")

        # Then: Request was retried and succeeded
        assert route.call_count == 2
        assert response.status_code == 200
        assert response.json() == {"success": True}
        mock_sleep.assert_called_once()

    @respx.mock
    async def test_auto_retry_max_retries_exceeded(self, vclient, base_url, mocker):
        """Verify RateLimitError is raised after max retries are exhausted."""
        # Given: An endpoint that always returns 429
        route = respx.get(f"{base_url}/test").respond(
            429,
            json={"detail": "Rate limited"},
            headers={"RateLimit": '"default";r=0;t=1'},
        )

        # Given: Mock asyncio.sleep to avoid actual delays
        mocker.patch("vclient.services.base.asyncio.sleep")

        # When/Then: Making a request raises RateLimitError after max retries
        from vclient.services.base import BaseService

        service = BaseService(vclient)
        with pytest.raises(RateLimitError):
            await service._get("/test")

        # Then: Request was attempted max_retries + 1 times (initial + retries)
        # Default max_retries is 3, so 4 total attempts
        assert route.call_count == 4

    @respx.mock
    async def test_auto_retry_disabled_via_config(self, base_url, api_key):
        """Verify no retry when auto_retry_rate_limit is disabled."""
        # Given: An endpoint that returns 429
        route = respx.get(f"{base_url}/test").respond(
            429,
            json={"detail": "Rate limited"},
            headers={"RateLimit": '"default";r=0;t=1'},
        )

        # When/Then: Making a request raises RateLimitError immediately
        from vclient import VClient
        from vclient.services.base import BaseService

        async with VClient(
            base_url=base_url, api_key=api_key, auto_retry_rate_limit=False
        ) as client:
            service = BaseService(client)
            with pytest.raises(RateLimitError):
                await service._get("/test")

        # Then: Only one request was made (no retries)
        assert route.call_count == 1

    @respx.mock
    async def test_auto_retry_respects_retry_after_from_header(self, vclient, base_url, mocker):
        """Verify retry delay uses the 't' value from RateLimit header."""
        # Given: An endpoint that returns 429 with t=5 then succeeds
        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.Response(
                    429,
                    json={"detail": "Rate limited"},
                    headers={"RateLimit": '"default";r=0;t=5'},
                ),
                httpx.Response(200, json={"success": True}),
            ]
        )

        # Given: Mock asyncio.sleep to capture the delay
        mock_sleep = mocker.patch("vclient.services.base.asyncio.sleep")

        # When: Making a request
        from vclient.services.base import BaseService

        service = BaseService(vclient)
        await service._get("/test")

        # Then: Sleep was called with a delay >= 5 seconds (base from header)
        # Note: actual delay includes jitter, so we check it's at least 5
        call_args = mock_sleep.call_args[0][0]
        assert call_args >= 5.0

    @respx.mock
    async def test_auto_retry_exponential_backoff(self, vclient, base_url, mocker):
        """Verify retry delay increases exponentially."""
        # Given: An endpoint that returns 429 three times then succeeds
        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.Response(
                    429,
                    json={"detail": "Rate limited"},
                    headers={"RateLimit": '"default";r=0;t=0'},
                ),
                httpx.Response(
                    429,
                    json={"detail": "Rate limited"},
                    headers={"RateLimit": '"default";r=0;t=0'},
                ),
                httpx.Response(
                    429,
                    json={"detail": "Rate limited"},
                    headers={"RateLimit": '"default";r=0;t=0'},
                ),
                httpx.Response(200, json={"success": True}),
            ]
        )

        # Given: Mock asyncio.sleep to capture the delays
        mock_sleep = mocker.patch("vclient.services.base.asyncio.sleep")

        # When: Making a request
        from vclient.services.base import BaseService

        service = BaseService(vclient)
        await service._get("/test")

        # Then: Sleep was called 3 times with increasing delays
        assert mock_sleep.call_count == 3

        # Get the base delays (before jitter)
        delays = [call[0][0] for call in mock_sleep.call_args_list]

        # Each delay should be roughly double the previous (exponential backoff)
        # With default retry_delay=1.0: attempt 0 -> ~1s, attempt 1 -> ~2s, attempt 2 -> ~4s
        # Account for jitter (up to 25%)
        assert delays[0] >= 1.0  # 1 * 2^0 = 1
        assert delays[1] >= 2.0  # 1 * 2^1 = 2
        assert delays[2] >= 4.0  # 1 * 2^2 = 4

    @respx.mock
    async def test_non_rate_limit_errors_not_retried(self, base_service, base_url, mocker):
        """Verify non-429 errors are not retried."""
        # Given: An endpoint that returns 500
        route = respx.get(f"{base_url}/test").respond(
            500,
            json={"detail": "Server error"},
        )

        # Given: Mock asyncio.sleep
        mock_sleep = mocker.patch("vclient.services.base.asyncio.sleep")

        # When/Then: Making a request raises ServerError immediately
        with pytest.raises(ServerError):
            await base_service._get("/test")

        # Then: Only one request was made (no retries)
        assert route.call_count == 1
        mock_sleep.assert_not_called()
