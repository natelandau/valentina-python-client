"""Tests for vclient.api.services.base."""

import pytest
import respx

from vclient.api import APIConfig, VClient
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

BASE_URL = "https://test.api.com"


class ConcreteService(BaseService):
    """Concrete implementation of BaseService for testing."""


@pytest.fixture
async def client() -> VClient:
    """Create a VClient for testing."""
    config = APIConfig(base_url=BASE_URL, api_key="test-key")
    client = VClient(config=config)
    yield client
    await client.close()


@pytest.fixture
def service(client) -> ConcreteService:
    """Create a ConcreteService for testing."""
    return ConcreteService(client)


class TestBaseServiceRequest:
    """Tests for BaseService._request method."""

    @respx.mock
    async def test_successful_get_request(self, service):
        """Test that successful GET requests return response."""
        route = respx.get(f"{BASE_URL}/test-path").respond(200, json={"success": True})

        response = await service._get("/test-path")

        assert route.called
        assert response.status_code == 200
        assert response.json() == {"success": True}

    @respx.mock
    async def test_request_with_params(self, service):
        """Test that query parameters are passed correctly."""
        route = respx.get(f"{BASE_URL}/test", params={"key": "value"}).respond(200, json={})

        await service._get("/test", params={"key": "value"})

        assert route.called

    @respx.mock
    async def test_post_with_json_body(self, service):
        """Test POST request with JSON body."""
        route = respx.post(f"{BASE_URL}/items").respond(201, json={"id": 1})

        response = await service._post("/items", json={"name": "test"})

        assert route.called
        assert response.status_code == 201
        # Verify the request body
        request = route.calls.last.request
        assert b'"name"' in request.content


class TestBaseServiceErrorHandling:
    """Tests for BaseService error handling."""

    @pytest.mark.parametrize(
        ("status_code", "expected_exception"),
        [
            (401, AuthenticationError),
            (403, AuthorizationError),
            (404, NotFoundError),
            (409, ConflictError),
            (422, ValidationError),
            (429, RateLimitError),
            (500, ServerError),
            (502, ServerError),
            (503, ServerError),
            (400, APIError),
            (418, APIError),
        ],
    )
    @respx.mock
    async def test_error_status_codes_raise_correct_exception(
        self, service, status_code, expected_exception
    ):
        """Test that error status codes raise appropriate exceptions."""
        respx.get(f"{BASE_URL}/error").respond(status_code, json={"detail": "Error message"})

        with pytest.raises(expected_exception) as exc_info:
            await service._get("/error")

        assert exc_info.value.status_code == status_code
        assert "Error message" in exc_info.value.message

    @respx.mock
    async def test_error_with_non_json_response(self, service):
        """Test error handling when response is not JSON."""
        respx.get(f"{BASE_URL}/error").respond(500, text="Internal Server Error")

        with pytest.raises(ServerError) as exc_info:
            await service._get("/error")

        assert "Internal Server Error" in exc_info.value.message


class TestBaseServiceHTTPMethods:
    """Tests for BaseService HTTP method helpers."""

    @respx.mock
    async def test_get_method(self, service):
        """Test _get method."""
        route = respx.get(f"{BASE_URL}/path").respond(200, json={})

        await service._get("/path")

        assert route.called
        assert route.calls.last.request.method == "GET"

    @respx.mock
    async def test_post_method(self, service):
        """Test _post method."""
        route = respx.post(f"{BASE_URL}/path").respond(201, json={})

        await service._post("/path", json={"data": "value"})

        assert route.called
        assert route.calls.last.request.method == "POST"

    @respx.mock
    async def test_put_method(self, service):
        """Test _put method."""
        route = respx.put(f"{BASE_URL}/path").respond(200, json={})

        await service._put("/path", json={"data": "value"})

        assert route.called
        assert route.calls.last.request.method == "PUT"

    @respx.mock
    async def test_patch_method(self, service):
        """Test _patch method."""
        route = respx.patch(f"{BASE_URL}/path").respond(200, json={})

        await service._patch("/path", json={"data": "value"})

        assert route.called
        assert route.calls.last.request.method == "PATCH"

    @respx.mock
    async def test_delete_method(self, service):
        """Test _delete method."""
        route = respx.delete(f"{BASE_URL}/path").respond(204)

        await service._delete("/path")

        assert route.called
        assert route.calls.last.request.method == "DELETE"


class TestBaseServiceIdempotency:
    """Tests for BaseService idempotency key support."""

    @respx.mock
    async def test_post_with_idempotency_key(self, service):
        """Test POST request includes idempotency key header."""
        route = respx.post(f"{BASE_URL}/items").respond(201, json={})

        await service._post("/items", json={}, idempotency_key="my-key-123")

        assert route.called
        request = route.calls.last.request
        assert request.headers.get(IDEMPOTENCY_KEY_HEADER) == "my-key-123"

    @respx.mock
    async def test_put_with_idempotency_key(self, service):
        """Test PUT request includes idempotency key header."""
        route = respx.put(f"{BASE_URL}/items/1").respond(200, json={})

        await service._put("/items/1", json={}, idempotency_key="put-key")

        assert route.called
        request = route.calls.last.request
        assert request.headers.get(IDEMPOTENCY_KEY_HEADER) == "put-key"

    @respx.mock
    async def test_patch_with_idempotency_key(self, service):
        """Test PATCH request includes idempotency key header."""
        route = respx.patch(f"{BASE_URL}/items/1").respond(200, json={})

        await service._patch("/items/1", json={}, idempotency_key="patch-key")

        assert route.called
        request = route.calls.last.request
        assert request.headers.get(IDEMPOTENCY_KEY_HEADER) == "patch-key"

    @respx.mock
    async def test_post_without_idempotency_key(self, service):
        """Test POST request without idempotency key has no header."""
        route = respx.post(f"{BASE_URL}/items").respond(201, json={})

        await service._post("/items", json={})

        assert route.called
        request = route.calls.last.request
        assert IDEMPOTENCY_KEY_HEADER not in request.headers

    def test_generate_idempotency_key_format(self):
        """Test that generated idempotency keys are valid UUIDs."""
        key = BaseService._generate_idempotency_key()
        # UUID format: 8-4-4-4-12 hex chars
        assert len(key) == 36
        assert key.count("-") == 4

    def test_generate_idempotency_key_unique(self):
        """Test that generated keys are unique."""
        keys = {BaseService._generate_idempotency_key() for _ in range(100)}
        assert len(keys) == 100


class TestBaseServicePagination:
    """Tests for BaseService pagination methods."""

    @respx.mock
    async def test_get_paginated(self, service):
        """Test _get_paginated returns PaginatedResponse."""
        route = respx.get(f"{BASE_URL}/items", params={"limit": "10", "offset": "0"}).respond(
            200,
            json={
                "items": [{"id": 1}, {"id": 2}],
                "limit": 10,
                "offset": 0,
                "total": 2,
            },
        )

        result = await service._get_paginated("/items")

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.total == 2

    @respx.mock
    async def test_get_paginated_with_custom_limit_offset(self, service):
        """Test _get_paginated with custom limit and offset."""
        route = respx.get(f"{BASE_URL}/items", params={"limit": "25", "offset": "50"}).respond(
            200,
            json={"items": [], "limit": 25, "offset": 50, "total": 100},
        )

        await service._get_paginated("/items", limit=25, offset=50)

        assert route.called

    @respx.mock
    async def test_get_paginated_clamps_limit(self, service):
        """Test that limit is clamped to valid range."""
        # Should be clamped to 100 (max)
        route = respx.get(f"{BASE_URL}/items", params={"limit": "100", "offset": "0"}).respond(
            200,
            json={"items": [], "limit": 100, "offset": 0, "total": 0},
        )

        await service._get_paginated("/items", limit=999)

        assert route.called

    @respx.mock
    async def test_iter_all_pages(self, service):
        """Test _iter_all_pages iterates through all pages."""
        # Set up routes for 3 pages
        respx.get(f"{BASE_URL}/items", params={"limit": "2", "offset": "0"}).respond(
            200,
            json={
                "items": [{"id": 1}, {"id": 2}],
                "limit": 2,
                "offset": 0,
                "total": 5,
            },
        )
        respx.get(f"{BASE_URL}/items", params={"limit": "2", "offset": "2"}).respond(
            200,
            json={
                "items": [{"id": 3}, {"id": 4}],
                "limit": 2,
                "offset": 2,
                "total": 5,
            },
        )
        respx.get(f"{BASE_URL}/items", params={"limit": "2", "offset": "4"}).respond(
            200,
            json={
                "items": [{"id": 5}],
                "limit": 2,
                "offset": 4,
                "total": 5,
            },
        )

        items = [item async for item in service._iter_all_pages("/items", limit=2)]

        assert len(items) == 5
        assert [item["id"] for item in items] == [1, 2, 3, 4, 5]

    @respx.mock
    async def test_get_all(self, service):
        """Test _get_all returns all items as a list."""
        respx.get(f"{BASE_URL}/items").respond(
            200,
            json={
                "items": [{"id": 1}, {"id": 2}, {"id": 3}],
                "limit": 100,
                "offset": 0,
                "total": 3,
            },
        )

        items = await service._get_all("/items")

        assert len(items) == 3
        assert isinstance(items, list)
