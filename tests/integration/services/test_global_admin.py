"""Tests for vclient.api.services.global_admin."""

import json

import pytest
import respx

from vclient.api.endpoints import Endpoints
from vclient.api.exceptions import AuthorizationError, NotFoundError
from vclient.api.models.global_admin import Developer, DeveloperWithApiKey
from vclient.api.models.pagination import PaginatedResponse

pytestmark = pytest.mark.anyio


@pytest.fixture
def developer_response_data() -> dict:
    """Return sample developer response data."""
    return {
        "id": "507f1f77bcf86cd799439011",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "username": "testuser",
        "email": "test@example.com",
        "key_generated": "2024-01-15T10:30:00Z",
        "is_global_admin": False,
        "companies": [
            {
                "company_id": "company123",
                "name": "Test Company",
                "permission": "USER",
            }
        ],
    }


@pytest.fixture
def paginated_developers_response(developer_response_data) -> dict:
    """Return sample paginated developers response."""
    return {
        "items": [developer_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


class TestGlobalAdminServiceGetPage:
    """Tests for GlobalAdminService.get_page method."""

    @respx.mock
    async def test_get_page_developers(self, vclient, base_url, paginated_developers_response):
        """Verify get_page returns paginated Developer objects."""
        # Given: A mocked developers list endpoint
        route = respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPERS}",
            params={"limit": "10", "offset": "0"},
        ).respond(200, json=paginated_developers_response)

        # When: Getting a page of developers
        result = await vclient.global_admin.get_page()

        # Then: Returns PaginatedResponse with Developer objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Developer)
        assert result.items[0].username == "testuser"
        assert result.total == 1

    @respx.mock
    async def test_get_page_with_pagination(self, vclient, base_url, developer_response_data):
        """Verify get_page accepts pagination parameters."""
        # Given: A mocked endpoint expecting custom pagination
        route = respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPERS}",
            params={"limit": "25", "offset": "50"},
        ).respond(
            200,
            json={
                "items": [developer_response_data],
                "limit": 25,
                "offset": 50,
                "total": 100,
            },
        )

        # When: Getting a page with custom pagination
        result = await vclient.global_admin.get_page(limit=25, offset=50)

        # Then: Request was made with correct params
        assert route.called
        assert result.limit == 25
        assert result.offset == 50

    @respx.mock
    async def test_get_page_with_global_admin_filter(
        self, vclient, base_url, paginated_developers_response
    ):
        """Verify get_page accepts is_global_admin filter."""
        # Given: A mocked endpoint expecting global admin filter
        route = respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPERS}",
            params={"limit": "10", "offset": "0", "is_global_admin": "true"},
        ).respond(200, json=paginated_developers_response)

        # When: Getting a page filtered by global admin status
        result = await vclient.global_admin.get_page(is_global_admin=True)

        # Then: Request was made with filter param
        assert route.called
        assert isinstance(result, PaginatedResponse)


class TestGlobalAdminServiceListAll:
    """Tests for GlobalAdminService.list_all method."""

    @respx.mock
    async def test_list_all_developers(self, vclient, base_url, developer_response_data):
        """Verify list_all returns all developers across pages."""
        # Given: Mocked endpoints for a single page
        respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPERS}",
            params={"limit": "100", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [developer_response_data],
                "limit": 100,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Calling list_all
        result = await vclient.global_admin.list_all()

        # Then: Returns list of Developer objects
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Developer)

    @respx.mock
    async def test_list_all_with_filter(self, vclient, base_url, developer_response_data):
        """Verify list_all accepts is_global_admin filter."""
        # Given: Mocked endpoint with filter
        respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPERS}",
            params={"limit": "100", "offset": "0", "is_global_admin": "false"},
        ).respond(
            200,
            json={
                "items": [developer_response_data],
                "limit": 100,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Calling list_all with filter
        result = await vclient.global_admin.list_all(is_global_admin=False)

        # Then: Returns filtered list
        assert len(result) == 1


class TestGlobalAdminServiceIterAll:
    """Tests for GlobalAdminService.iter_all method."""

    @respx.mock
    async def test_iter_all_developers(self, vclient, base_url, developer_response_data):
        """Verify iter_all yields Developer objects across pages."""
        # Given: Mocked endpoints for multiple pages
        developer2 = {
            **developer_response_data,
            "id": "507f1f77bcf86cd799439012",
            "username": "user2",
        }
        respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPERS}",
            params={"limit": "1", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [developer_response_data],
                "limit": 1,
                "offset": 0,
                "total": 2,
            },
        )
        respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPERS}",
            params={"limit": "1", "offset": "1"},
        ).respond(
            200,
            json={
                "items": [developer2],
                "limit": 1,
                "offset": 1,
                "total": 2,
            },
        )

        # When: Iterating through all developers
        developers = [dev async for dev in vclient.global_admin.iter_all(limit=1)]

        # Then: All developers are yielded as Developer objects
        assert len(developers) == 2
        assert all(isinstance(d, Developer) for d in developers)
        assert developers[0].username == "testuser"
        assert developers[1].username == "user2"


class TestGlobalAdminServiceGet:
    """Tests for GlobalAdminService.get method."""

    @respx.mock
    async def test_get_developer(self, vclient, base_url, developer_response_data):
        """Verify getting a developer returns Developer object."""
        # Given: A mocked developer endpoint
        developer_id = "507f1f77bcf86cd799439011"
        route = respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id)}"
        ).respond(200, json=developer_response_data)

        # When: Getting the developer
        result = await vclient.global_admin.get(developer_id)

        # Then: Returns Developer object with correct data
        assert route.called
        assert isinstance(result, Developer)
        assert result.id == developer_id
        assert result.username == "testuser"
        assert result.email == "test@example.com"

    @respx.mock
    async def test_get_developer_not_found(self, vclient, base_url):
        """Verify getting non-existent developer raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        developer_id = "nonexistent"
        respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id)}"
        ).respond(404, json={"detail": "Developer not found"})

        # When/Then: Getting the developer raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.global_admin.get(developer_id)

    @respx.mock
    async def test_get_developer_unauthorized(self, vclient, base_url):
        """Verify getting developer without admin access raises AuthorizationError."""
        # Given: A mocked endpoint returning 403
        developer_id = "507f1f77bcf86cd799439011"
        respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id)}"
        ).respond(403, json={"detail": "Global admin access required"})

        # When/Then: Getting the developer raises AuthorizationError
        with pytest.raises(AuthorizationError):
            await vclient.global_admin.get(developer_id)


class TestGlobalAdminServiceCreate:
    """Tests for GlobalAdminService.create method."""

    @respx.mock
    async def test_create_developer_minimal(self, vclient, base_url, developer_response_data):
        """Verify creating developer with minimal data."""
        # Given: A mocked create endpoint
        route = respx.post(f"{base_url}{Endpoints.ADMIN_DEVELOPERS}").respond(
            201, json=developer_response_data
        )

        # When: Creating a developer with minimal data
        result = await vclient.global_admin.create(
            username="testuser",
            email="test@example.com",
        )

        # Then: Returns created Developer object
        assert route.called
        assert isinstance(result, Developer)
        assert result.username == "testuser"

        # Verify request body
        request = route.calls.last.request
        body = json.loads(request.content)
        assert body["username"] == "testuser"
        assert body["email"] == "test@example.com"
        assert body["is_global_admin"] is False

    @respx.mock
    async def test_create_developer_as_global_admin(
        self, vclient, base_url, developer_response_data
    ):
        """Verify creating developer with global admin privileges."""
        # Given: A mocked create endpoint
        admin_response = {**developer_response_data, "is_global_admin": True}
        route = respx.post(f"{base_url}{Endpoints.ADMIN_DEVELOPERS}").respond(
            201, json=admin_response
        )

        # When: Creating a developer with global admin
        result = await vclient.global_admin.create(
            username="adminuser",
            email="admin@example.com",
            is_global_admin=True,
        )

        # Then: Returns created Developer object with admin status
        assert route.called
        assert isinstance(result, Developer)
        assert result.is_global_admin is True

        # Verify request body includes is_global_admin
        request = route.calls.last.request
        body = json.loads(request.content)
        assert body["is_global_admin"] is True


class TestGlobalAdminServiceUpdate:
    """Tests for GlobalAdminService.update method."""

    @respx.mock
    async def test_update_developer_username(self, vclient, base_url, developer_response_data):
        """Verify updating developer username."""
        # Given: A mocked update endpoint
        developer_id = "507f1f77bcf86cd799439011"
        updated_data = {**developer_response_data, "username": "newusername"}
        route = respx.patch(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id)}"
        ).respond(200, json=updated_data)

        # When: Updating the developer username
        result = await vclient.global_admin.update(developer_id, username="newusername")

        # Then: Returns updated Developer object
        assert route.called
        assert isinstance(result, Developer)
        assert result.username == "newusername"

        # Verify only username is in request body
        request = route.calls.last.request
        body = json.loads(request.content)
        assert body == {"username": "newusername"}

    @respx.mock
    async def test_update_developer_multiple_fields(
        self, vclient, base_url, developer_response_data
    ):
        """Verify updating developer with multiple fields."""
        # Given: A mocked update endpoint
        developer_id = "507f1f77bcf86cd799439011"
        updated_data = {
            **developer_response_data,
            "email": "new@example.com",
            "is_global_admin": True,
        }
        route = respx.patch(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id)}"
        ).respond(200, json=updated_data)

        # When: Updating multiple fields
        result = await vclient.global_admin.update(
            developer_id,
            email="new@example.com",
            is_global_admin=True,
        )

        # Then: Returns updated Developer object
        assert route.called
        assert isinstance(result, Developer)

        # Verify request body has both fields
        request = route.calls.last.request
        body = json.loads(request.content)
        assert body == {"email": "new@example.com", "is_global_admin": True}

    @respx.mock
    async def test_update_developer_not_found(self, vclient, base_url):
        """Verify updating non-existent developer raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        developer_id = "nonexistent"
        respx.patch(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id)}"
        ).respond(404, json={"detail": "Developer not found"})

        # When/Then: Updating raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.global_admin.update(developer_id, username="newname")


class TestGlobalAdminServiceDelete:
    """Tests for GlobalAdminService.delete method."""

    @respx.mock
    async def test_delete_developer(self, vclient, base_url):
        """Verify deleting a developer."""
        # Given: A mocked delete endpoint
        developer_id = "507f1f77bcf86cd799439011"
        route = respx.delete(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id)}"
        ).respond(204)

        # When: Deleting the developer
        result = await vclient.global_admin.delete(developer_id)

        # Then: Request was made and returns None
        assert route.called
        assert result is None

    @respx.mock
    async def test_delete_developer_not_found(self, vclient, base_url):
        """Verify deleting non-existent developer raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        developer_id = "nonexistent"
        respx.delete(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id)}"
        ).respond(404, json={"detail": "Developer not found"})

        # When/Then: Deleting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.global_admin.delete(developer_id)

    @respx.mock
    async def test_delete_developer_unauthorized(self, vclient, base_url):
        """Verify deleting without permission raises AuthorizationError."""
        # Given: A mocked endpoint returning 403
        developer_id = "507f1f77bcf86cd799439011"
        respx.delete(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER.format(developer_id=developer_id)}"
        ).respond(403, json={"detail": "Global admin access required"})

        # When/Then: Deleting raises AuthorizationError
        with pytest.raises(AuthorizationError):
            await vclient.global_admin.delete(developer_id)


class TestGlobalAdminServiceCreateApiKey:
    """Tests for GlobalAdminService.create_api_key method."""

    @respx.mock
    async def test_create_api_key(self, vclient, base_url, developer_response_data):
        """Verify creating a new API key."""
        # Given: A mocked create key endpoint
        developer_id = "507f1f77bcf86cd799439011"
        response_data = {**developer_response_data, "api_key": "vapi_newkey123"}
        route = respx.post(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER_NEW_KEY.format(developer_id=developer_id)}"
        ).respond(201, json=response_data)

        # When: Creating a new API key
        result = await vclient.global_admin.create_api_key(developer_id)

        # Then: Returns DeveloperWithApiKey object with the new key
        assert route.called
        assert isinstance(result, DeveloperWithApiKey)
        assert result.api_key == "vapi_newkey123"
        assert result.username == "testuser"

    @respx.mock
    async def test_create_api_key_not_found(self, vclient, base_url):
        """Verify creating key for non-existent developer raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        developer_id = "nonexistent"
        respx.post(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER_NEW_KEY.format(developer_id=developer_id)}"
        ).respond(404, json={"detail": "Developer not found"})

        # When/Then: Creating key raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.global_admin.create_api_key(developer_id)

    @respx.mock
    async def test_create_api_key_unauthorized(self, vclient, base_url):
        """Verify creating key without permission raises AuthorizationError."""
        # Given: A mocked endpoint returning 403
        developer_id = "507f1f77bcf86cd799439011"
        respx.post(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER_NEW_KEY.format(developer_id=developer_id)}"
        ).respond(403, json={"detail": "Global admin access required"})

        # When/Then: Creating key raises AuthorizationError
        with pytest.raises(AuthorizationError):
            await vclient.global_admin.create_api_key(developer_id)


class TestGlobalAdminServiceClientIntegration:
    """Tests for VClient.global_admin property."""

    async def test_global_admin_property_returns_service(self, vclient):
        """Verify global_admin property returns GlobalAdminService instance."""
        # When: Accessing the global_admin property
        service = vclient.global_admin

        # Then: Returns a GlobalAdminService instance
        from vclient.api.services.global_admin import GlobalAdminService

        assert isinstance(service, GlobalAdminService)

    async def test_global_admin_property_cached(self, vclient):
        """Verify global_admin property returns same instance on multiple calls."""
        # When: Accessing the global_admin property multiple times
        service1 = vclient.global_admin
        service2 = vclient.global_admin

        # Then: Returns the same instance
        assert service1 is service2
