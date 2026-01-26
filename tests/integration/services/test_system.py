"""Tests for vclient.services.system."""

import pytest
import respx

from vclient.endpoints import Endpoints
from vclient.models import SystemHealth
from vclient.services import SystemService

pytestmark = pytest.mark.anyio


@pytest.fixture
def health_response_data() -> dict:
    """Return sample health response data."""
    return {
        "database_status": "online",
        "cache_status": "online",
        "version": "0.7.0",
    }


class TestSystemServiceHealth:
    """Tests for SystemService.health method."""

    @respx.mock
    async def test_health_returns_system_health(self, vclient, base_url, health_response_data):
        """Verify health returns SystemHealth object."""
        # Given: A mocked health endpoint
        route = respx.get(f"{base_url}{Endpoints.HEALTH}").respond(200, json=health_response_data)

        # When: Calling health
        result = await vclient.system.health()

        # Then: Returns SystemHealth object with correct data
        assert route.called
        assert isinstance(result, SystemHealth)
        assert result.database_status == "online"
        assert result.cache_status == "online"
        assert result.version == "0.7.0"

    @respx.mock
    async def test_health_with_offline_database(self, vclient, base_url):
        """Verify health correctly reports offline database."""
        # Given: A mocked endpoint with offline database
        response_data = {
            "database_status": "offline",
            "cache_status": "online",
            "version": "0.7.0",
        }
        route = respx.get(f"{base_url}{Endpoints.HEALTH}").respond(200, json=response_data)

        # When: Calling health
        result = await vclient.system.health()

        # Then: Returns correct offline status
        assert route.called
        assert result.database_status == "offline"
        assert result.cache_status == "online"

    @respx.mock
    async def test_health_with_offline_cache(self, vclient, base_url):
        """Verify health correctly reports offline cache."""
        # Given: A mocked endpoint with offline cache
        response_data = {
            "database_status": "online",
            "cache_status": "offline",
            "version": "0.7.0",
        }
        route = respx.get(f"{base_url}{Endpoints.HEALTH}").respond(200, json=response_data)

        # When: Calling health
        result = await vclient.system.health()

        # Then: Returns correct offline status
        assert route.called
        assert result.database_status == "online"
        assert result.cache_status == "offline"

    @respx.mock
    async def test_health_with_all_services_offline(self, vclient, base_url):
        """Verify health correctly reports all services offline."""
        # Given: A mocked endpoint with all services offline
        response_data = {
            "database_status": "offline",
            "cache_status": "offline",
            "version": "0.7.0",
        }
        route = respx.get(f"{base_url}{Endpoints.HEALTH}").respond(200, json=response_data)

        # When: Calling health
        result = await vclient.system.health()

        # Then: Returns correct offline status for all services
        assert route.called
        assert result.database_status == "offline"
        assert result.cache_status == "offline"


class TestSystemServiceClientIntegration:
    """Tests for VClient.system property."""

    async def test_system_property_returns_service(self, vclient):
        """Verify system property returns SystemService instance."""
        # When: Accessing the system property
        service = vclient.system

        # Then: Returns a SystemService instance
        assert isinstance(service, SystemService)

    async def test_system_property_cached(self, vclient):
        """Verify system property returns same instance on multiple calls."""
        # When: Accessing the system property multiple times
        service1 = vclient.system
        service2 = vclient.system

        # Then: Returns the same instance
        assert service1 is service2
