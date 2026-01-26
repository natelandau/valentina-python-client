"""Tests for vclient.services.developers."""

import json

import pytest
import respx

from vclient.endpoints import Endpoints
from vclient.exceptions import AuthenticationError
from vclient.models import MeDeveloper, MeDeveloperWithApiKey

pytestmark = pytest.mark.anyio


@pytest.fixture
def me_developer_response_data() -> dict:
    """Return sample developer response data."""
    return {
        "id": "507f1f77bcf86cd799439011",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "username": "testuser",
        "email": "test@example.com",
        "key_generated": "2024-01-15T10:30:00Z",
        "companies": [
            {
                "company_id": "company123",
                "name": "Test Company",
                "permission": "USER",
            }
        ],
    }


class TestDeveloperServiceGetMe:
    """Tests for DeveloperService.get_me method."""

    @respx.mock
    async def test_get_me_returns_developer(self, vclient, base_url, me_developer_response_data):
        """Verify get_me returns MeDeveloper object."""
        # Given: A mocked developer me endpoint
        route = respx.get(f"{base_url}{Endpoints.DEVELOPER_ME}").respond(
            200, json=me_developer_response_data
        )

        # When: Getting current developer
        result = await vclient.developer.get_me()

        # Then: Returns MeDeveloper object with correct data
        assert route.called
        assert isinstance(result, MeDeveloper)
        assert result.id == "507f1f77bcf86cd799439011"
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert len(result.companies) == 1
        assert result.companies[0].company_id == "company123"

    @respx.mock
    async def test_get_me_unauthenticated(self, vclient, base_url):
        """Verify get_me raises AuthenticationError when not authenticated."""
        # Given: A mocked endpoint returning 401
        respx.get(f"{base_url}{Endpoints.DEVELOPER_ME}").respond(
            401, json={"detail": "Invalid API key"}
        )

        # When/Then: Getting current developer raises AuthenticationError
        with pytest.raises(AuthenticationError):
            await vclient.developer.get_me()


class TestDeveloperServiceUpdateMe:
    """Tests for DeveloperService.update_me method."""

    @respx.mock
    async def test_update_me_username(self, vclient, base_url, me_developer_response_data):
        """Verify updating username."""
        # Given: A mocked update endpoint
        updated_data = {**me_developer_response_data, "username": "newusername"}
        route = respx.patch(f"{base_url}{Endpoints.DEVELOPER_ME}").respond(200, json=updated_data)

        # When: Updating the developer username
        result = await vclient.developer.update_me(username="newusername")

        # Then: Returns updated MeDeveloper object
        assert route.called
        assert isinstance(result, MeDeveloper)
        assert result.username == "newusername"

        # Verify only username is in request body
        request = route.calls.last.request
        body = json.loads(request.content)
        assert body == {"username": "newusername"}

    @respx.mock
    async def test_update_me_email(self, vclient, base_url, me_developer_response_data):
        """Verify updating email."""
        # Given: A mocked update endpoint
        updated_data = {**me_developer_response_data, "email": "new@example.com"}
        route = respx.patch(f"{base_url}{Endpoints.DEVELOPER_ME}").respond(200, json=updated_data)

        # When: Updating the developer email
        result = await vclient.developer.update_me(email="new@example.com")

        # Then: Returns updated MeDeveloper object
        assert route.called
        assert isinstance(result, MeDeveloper)
        assert result.email == "new@example.com"

        # Verify only email is in request body
        request = route.calls.last.request
        body = json.loads(request.content)
        assert body == {"email": "new@example.com"}

    @respx.mock
    async def test_update_me_multiple_fields(self, vclient, base_url, me_developer_response_data):
        """Verify updating multiple fields."""
        # Given: A mocked update endpoint
        updated_data = {
            **me_developer_response_data,
            "username": "newusername",
            "email": "new@example.com",
        }
        route = respx.patch(f"{base_url}{Endpoints.DEVELOPER_ME}").respond(200, json=updated_data)

        # When: Updating multiple fields
        result = await vclient.developer.update_me(
            username="newusername",
            email="new@example.com",
        )

        # Then: Returns updated MeDeveloper object
        assert route.called
        assert isinstance(result, MeDeveloper)

        # Verify request body has both fields
        request = route.calls.last.request
        body = json.loads(request.content)
        assert body == {"username": "newusername", "email": "new@example.com"}

    @respx.mock
    async def test_update_me_unauthenticated(self, vclient, base_url):
        """Verify update_me raises AuthenticationError when not authenticated."""
        # Given: A mocked endpoint returning 401
        respx.patch(f"{base_url}{Endpoints.DEVELOPER_ME}").respond(
            401, json={"detail": "Invalid API key"}
        )

        # When/Then: Updating raises AuthenticationError
        with pytest.raises(AuthenticationError):
            await vclient.developer.update_me(username="newname")


class TestDeveloperServiceRegenerateApiKey:
    """Tests for DeveloperService.regenerate_api_key method."""

    @respx.mock
    async def test_regenerate_api_key(self, vclient, base_url, me_developer_response_data):
        """Verify regenerating API key returns new key."""
        # Given: A mocked regenerate key endpoint
        response_data = {
            **me_developer_response_data,
            "api_key": "vapi_newkey123",
        }
        route = respx.post(f"{base_url}{Endpoints.DEVELOPER_ME_NEW_KEY}").respond(
            201, json=response_data
        )

        # When: Regenerating the API key
        result = await vclient.developer.regenerate_api_key()

        # Then: Returns MeDeveloperWithApiKey object with the new key
        assert route.called
        assert isinstance(result, MeDeveloperWithApiKey)
        assert result.api_key == "vapi_newkey123"
        assert result.username == "testuser"

    @respx.mock
    async def test_regenerate_api_key_unauthenticated(self, vclient, base_url):
        """Verify regenerate_api_key raises AuthenticationError when not authenticated."""
        # Given: A mocked endpoint returning 401
        respx.post(f"{base_url}{Endpoints.DEVELOPER_ME_NEW_KEY}").respond(
            401, json={"detail": "Invalid API key"}
        )

        # When/Then: Regenerating key raises AuthenticationError
        with pytest.raises(AuthenticationError):
            await vclient.developer.regenerate_api_key()


class TestDeveloperServiceClientIntegration:
    """Tests for VClient.developer property."""

    async def test_developer_property_returns_service(self, vclient):
        """Verify developer property returns DeveloperService instance."""
        # When: Accessing the developer property
        service = vclient.developer

        # Then: Returns a DeveloperService instance
        from vclient.services.developers import DeveloperService

        assert isinstance(service, DeveloperService)

    async def test_developer_property_cached(self, vclient):
        """Verify developer property returns same instance on multiple calls."""
        # When: Accessing the developer property multiple times
        service1 = vclient.developer
        service2 = vclient.developer

        # Then: Returns the same instance
        assert service1 is service2
