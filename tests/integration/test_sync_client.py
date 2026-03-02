"""Smoke tests for the synchronous SyncVClient."""

import pytest
import respx
from httpx import Response

from vclient import SyncVClient, sync_system_service
from vclient.endpoints import Endpoints
from vclient.exceptions import NotFoundError
from vclient.models import SystemHealth


@pytest.fixture
def sync_client(base_url, api_key):
    """Return a SyncVClient for testing."""
    client = SyncVClient(base_url=base_url, api_key=api_key, timeout=10.0)
    yield client
    client.close()


@pytest.fixture
def health_response_data() -> dict:
    """Return sample health response data."""
    return {
        "database_status": "online",
        "cache_status": "online",
        "version": "0.7.0",
    }


@pytest.fixture
def company_response_data() -> dict:
    """Return sample company response data."""
    return {
        "id": "507f1f77bcf86cd799439011",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "name": "Test Company",
        "description": "A test company",
        "email": "test@example.com",
        "user_ids": ["user1", "user2"],
        "resources_modified_at": "2024-01-15T10:30:00Z",
        "settings": {
            "character_autogen_xp_cost": 10,
            "character_autogen_num_choices": 3,
            "permission_manage_campaign": "UNRESTRICTED",
            "permission_grant_xp": "UNRESTRICTED",
            "permission_free_trait_changes": "UNRESTRICTED",
        },
    }


@pytest.fixture
def paginated_companies_response(company_response_data) -> dict:
    """Return sample paginated companies response."""
    return {
        "items": [company_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


class TestSyncClientContextManager:
    """Tests for SyncVClient context manager behavior."""

    def test_context_manager_enter_exit(self, base_url, api_key):
        """Verify the sync client opens and closes correctly via `with` statement."""
        # When: Using SyncVClient as a context manager
        with SyncVClient(base_url=base_url, api_key=api_key) as client:
            # Then: Client is open inside the block
            assert client.is_closed is False

        # And: Client is closed after exiting
        assert client.is_closed is True


class TestSyncClientGetRequest:
    """Tests for SyncVClient GET requests."""

    @respx.mock
    def test_get_request_returns_model(self, sync_client, base_url, health_response_data):
        """Verify a GET request returns the correct Pydantic model."""
        # Given: A mocked health endpoint
        route = respx.get(f"{base_url}{Endpoints.HEALTH}").respond(200, json=health_response_data)

        # When: Calling health()
        result = sync_client.system.health()

        # Then: Returns a SystemHealth model with correct data
        assert route.called
        assert isinstance(result, SystemHealth)
        assert result.database_status == "online"
        assert result.cache_status == "online"
        assert result.version == "0.7.0"


class TestSyncClientErrorHandling:
    """Tests for SyncVClient error handling."""

    @respx.mock
    def test_404_raises_not_found_error(self, sync_client, base_url):
        """Verify a 404 response raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        respx.get(f"{base_url}{Endpoints.HEALTH}").respond(404, json={"detail": "Not found"})

        # When/Then: Calling health() raises NotFoundError
        with pytest.raises(NotFoundError) as exc_info:
            sync_client.system.health()

        assert exc_info.value.status_code == 404


class TestSyncClientPagination:
    """Tests for SyncVClient paginated responses."""

    @respx.mock
    def test_paginated_request(self, sync_client, base_url, paginated_companies_response):
        """Verify paginated GET returns items and total count."""
        # Given: A mocked companies endpoint with paginated response
        route = respx.get(f"{base_url}{Endpoints.COMPANIES}").respond(
            200, json=paginated_companies_response
        )

        # When: Calling get_page()
        result = sync_client.companies.get_page()

        # Then: Returns paginated response with correct items and total
        assert route.called
        assert len(result.items) == 1
        assert result.total == 1
        assert result.items[0].name == "Test Company"


class TestSyncClientRetry:
    """Tests for SyncVClient retry behavior."""

    @respx.mock
    def test_retry_on_429(self, base_url, api_key, health_response_data):
        """Verify the client retries after a 429 and succeeds on the second attempt."""
        # Given: A client with fast retry settings
        client = SyncVClient(
            base_url=base_url,
            api_key=api_key,
            max_retries=1,
            retry_delay=0.01,
        )

        # And: A mock that returns 429 first, then 200
        route = respx.get(f"{base_url}{Endpoints.HEALTH}").mock(
            side_effect=[
                Response(
                    429,
                    json={"detail": "Rate limited"},
                    headers={"Retry-After": "0"},
                ),
                Response(200, json=health_response_data),
            ]
        )

        try:
            # When: Calling health()
            result = client.system.health()

            # Then: The route was called twice and the result is correct
            assert route.call_count == 2
            assert isinstance(result, SystemHealth)
            assert result.version == "0.7.0"
        finally:
            client.close()


class TestSyncFactoryFunctions:
    """Tests for sync factory functions."""

    @respx.mock
    def test_sync_factory_function(self, base_url, api_key, health_response_data):
        """Verify sync factory functions use the default client."""
        # Given: A SyncVClient registered as default via context manager
        with SyncVClient(base_url=base_url, api_key=api_key) as _client:
            route = respx.get(f"{base_url}{Endpoints.HEALTH}").respond(
                200, json=health_response_data
            )

            # When: Using the factory function
            system = sync_system_service()
            result = system.health()

            # Then: Returns correct result using the default client
            assert route.called
            assert isinstance(result, SystemHealth)
            assert result.version == "0.7.0"
