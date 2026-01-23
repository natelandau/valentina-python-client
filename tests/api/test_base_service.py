"""Tests for vclient.api.services.base."""

import pytest
import respx

from vclient.api.constants import IDEMPOTENCY_KEY_HEADER
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
from vclient.api.models.pagination import PaginatedResponse
from vclient.api.services.base import BaseService

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
        self, base_service, base_url, status_code, expected_exception
    ):
        """Verify error status codes raise appropriate exceptions."""
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
    async def test_rate_limit_error_includes_retry_after(self, base_service, base_url):
        """Verify RateLimitError includes retry_after from Retry-After header."""
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
    async def test_rate_limit_error_without_retry_after_header(self, base_service, base_url):
        """Verify RateLimitError works without Retry-After header."""
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
    async def test_rate_limit_error_with_invalid_retry_after_header(self, base_service, base_url):
        """Verify RateLimitError handles invalid Retry-After header gracefully."""
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
    async def test_get_method(self, base_service, base_url):
        """Verify _get method makes GET request."""
        # Given: A mocked GET endpoint
        route = respx.get(f"{base_url}/path").respond(200, json={})

        # When: Calling _get method
        await base_service._get("/path")

        # Then: GET request was made
        assert route.called
        assert route.calls.last.request.method == "GET"

    @respx.mock
    async def test_post_method(self, base_service, base_url):
        """Verify _post method makes POST request."""
        # Given: A mocked POST endpoint
        route = respx.post(f"{base_url}/path").respond(201, json={})

        # When: Calling _post method
        await base_service._post("/path", json={"data": "value"})

        # Then: POST request was made
        assert route.called
        assert route.calls.last.request.method == "POST"

    @respx.mock
    async def test_put_method(self, base_service, base_url):
        """Verify _put method makes PUT request."""
        # Given: A mocked PUT endpoint
        route = respx.put(f"{base_url}/path").respond(200, json={})

        # When: Calling _put method
        await base_service._put("/path", json={"data": "value"})

        # Then: PUT request was made
        assert route.called
        assert route.calls.last.request.method == "PUT"

    @respx.mock
    async def test_patch_method(self, base_service, base_url):
        """Verify _patch method makes PATCH request."""
        # Given: A mocked PATCH endpoint
        route = respx.patch(f"{base_url}/path").respond(200, json={})

        # When: Calling _patch method
        await base_service._patch("/path", json={"data": "value"})

        # Then: PATCH request was made
        assert route.called
        assert route.calls.last.request.method == "PATCH"

    @respx.mock
    async def test_delete_method(self, base_service, base_url):
        """Verify _delete method makes DELETE request."""
        # Given: A mocked DELETE endpoint
        route = respx.delete(f"{base_url}/path").respond(204)

        # When: Calling _delete method
        await base_service._delete("/path")

        # Then: DELETE request was made
        assert route.called
        assert route.calls.last.request.method == "DELETE"


class TestBaseServiceIdempotency:
    """Tests for BaseService idempotency key support."""

    @respx.mock
    async def test_post_with_idempotency_key(self, base_service, base_url):
        """Verify POST request includes idempotency key header."""
        # Given: A mocked POST endpoint
        route = respx.post(f"{base_url}/items").respond(201, json={})

        # When: Making a POST request with idempotency key
        await base_service._post("/items", json={}, idempotency_key="my-key-123")

        # Then: Request includes the idempotency key header
        assert route.called
        request = route.calls.last.request
        assert request.headers.get(IDEMPOTENCY_KEY_HEADER) == "my-key-123"

    @respx.mock
    async def test_put_with_idempotency_key(self, base_service, base_url):
        """Verify PUT request includes idempotency key header."""
        # Given: A mocked PUT endpoint
        route = respx.put(f"{base_url}/items/1").respond(200, json={})

        # When: Making a PUT request with idempotency key
        await base_service._put("/items/1", json={}, idempotency_key="put-key")

        # Then: Request includes the idempotency key header
        assert route.called
        request = route.calls.last.request
        assert request.headers.get(IDEMPOTENCY_KEY_HEADER) == "put-key"

    @respx.mock
    async def test_patch_with_idempotency_key(self, base_service, base_url):
        """Verify PATCH request includes idempotency key header."""
        # Given: A mocked PATCH endpoint
        route = respx.patch(f"{base_url}/items/1").respond(200, json={})

        # When: Making a PATCH request with idempotency key
        await base_service._patch("/items/1", json={}, idempotency_key="patch-key")

        # Then: Request includes the idempotency key header
        assert route.called
        request = route.calls.last.request
        assert request.headers.get(IDEMPOTENCY_KEY_HEADER) == "patch-key"

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

    def test_generate_idempotency_key_format(self):
        """Verify generated idempotency keys are valid UUIDs."""
        # When: Generating an idempotency key
        key = BaseService._generate_idempotency_key()

        # Then: Key is a valid UUID format (8-4-4-4-12 hex chars)
        assert len(key) == 36
        assert key.count("-") == 4

    def test_generate_idempotency_key_unique(self):
        """Verify generated keys are unique."""
        # When: Generating 100 idempotency keys
        keys = {BaseService._generate_idempotency_key() for _ in range(100)}

        # Then: All keys are unique
        assert len(keys) == 100


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
