"""Tests for vclient.services.users."""

import pytest
import respx

from vclient.endpoints import Endpoints
from vclient.exceptions import NotFoundError, RequestValidationError
from vclient.models import (
    CampaignExperience,
    DiscordProfile,
    Note,
    PaginatedResponse,
    Quickroll,
    RollStatistics,
    S3Asset,
    User,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def user_response_data() -> dict:
    """Return sample user response data."""
    return {
        "id": "507f1f77bcf86cd799439011",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "name": "Test User",
        "email": "test@example.com",
        "role": "PLAYER",
        "company_id": "company123",
        "discord_profile": {
            "id": "discord123",
            "username": "testuser",
        },
        "campaign_experience": [
            {"campaign_id": "campaign1", "xp_current": 50, "xp_total": 100, "cool_points": 5}
        ],
        "asset_ids": ["asset1"],
    }


@pytest.fixture
def paginated_users_response(user_response_data) -> dict:
    """Return sample paginated users response."""
    return {
        "items": [user_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def statistics_response_data() -> dict:
    """Return sample statistics response data."""
    return {
        "botches": 5,
        "successes": 50,
        "failures": 30,
        "criticals": 15,
        "total_rolls": 100,
        "average_difficulty": 6.5,
        "average_pool": 4.2,
        "top_traits": [{"name": "Strength", "count": 20}],
        "criticals_percentage": 15.0,
        "success_percentage": 50.0,
        "failure_percentage": 30.0,
        "botch_percentage": 5.0,
    }


@pytest.fixture
def asset_response_data() -> dict:
    """Return sample asset response data."""
    return {
        "id": "asset123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "file_type": "image",
        "original_filename": "avatar.png",
        "public_url": "https://example.com/avatar.png",
        "uploaded_by": "user123",
        "parent_type": "user",
    }


@pytest.fixture
def experience_response_data() -> dict:
    """Return sample experience response data."""
    return {
        "campaign_id": "campaign123",
        "xp_current": 50,
        "xp_total": 100,
        "cool_points": 5,
    }


@pytest.fixture
def note_response_data() -> dict:
    """Return sample note response data."""
    return {
        "id": "note123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "title": "Test Note",
        "content": "This is test content",
    }


@pytest.fixture
def quickroll_response_data() -> dict:
    """Return sample quickroll response data."""
    return {
        "id": "quickroll123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "name": "Test Quickroll",
        "description": "A test quickroll",
        "user_id": "user123",
        "trait_ids": ["trait1", "trait2"],
    }


class TestUsersServiceGetPage:
    """Tests for UsersService.get_page method."""

    @respx.mock
    async def test_get_page_users(self, vclient, base_url, paginated_users_response):
        """Verify get_page returns paginated User objects."""
        # Given: A mocked users list endpoint
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.USERS.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0"},
        ).respond(200, json=paginated_users_response)

        # When: Getting a page of users
        result = await vclient.users(company_id).get_page()

        # Then: Returns PaginatedResponse with User objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], User)
        assert result.items[0].name == "Test User"
        assert result.total == 1

    @respx.mock
    async def test_get_page_with_role_filter(self, vclient, base_url, paginated_users_response):
        """Verify get_page accepts role filter parameter."""
        # Given: A mocked endpoint expecting role filter
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.USERS.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0", "user_role": "STORYTELLER"},
        ).respond(200, json=paginated_users_response)

        # When: Getting a page with role filter
        result = await vclient.users(company_id).get_page(user_role="STORYTELLER")

        # Then: Request was made with correct params
        assert route.called
        assert isinstance(result, PaginatedResponse)

    @respx.mock
    async def test_get_page_with_pagination(self, vclient, base_url, user_response_data):
        """Verify get_page accepts pagination parameters."""
        # Given: A mocked endpoint expecting custom pagination
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.USERS.format(company_id=company_id)}",
            params={"limit": "25", "offset": "50"},
        ).respond(
            200,
            json={
                "items": [user_response_data],
                "limit": 25,
                "offset": 50,
                "total": 100,
            },
        )

        # When: Getting a page with custom pagination
        result = await vclient.users(company_id).get_page(limit=25, offset=50)

        # Then: Request was made with correct params
        assert route.called
        assert result.limit == 25
        assert result.offset == 50


class TestUsersServiceListAll:
    """Tests for UsersService.list_all method."""

    @respx.mock
    async def test_list_all_users(self, vclient, base_url, user_response_data):
        """Verify list_all returns all users across pages."""
        # Given: Mocked endpoint
        company_id = "company123"
        respx.get(
            f"{base_url}{Endpoints.USERS.format(company_id=company_id)}",
            params={"limit": "100", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [user_response_data],
                "limit": 100,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Calling list_all
        result = await vclient.users(company_id).list_all()

        # Then: Returns list of User objects
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], User)


class TestUsersServiceIterAll:
    """Tests for UsersService.iter_all method."""

    @respx.mock
    async def test_iter_all_users(self, vclient, base_url, user_response_data):
        """Verify iter_all yields User objects across pages."""
        # Given: Mocked endpoints for multiple pages
        company_id = "company123"
        user2 = {**user_response_data, "id": "507f1f77bcf86cd799439012", "name": "User 2"}
        respx.get(
            f"{base_url}{Endpoints.USERS.format(company_id=company_id)}",
            params={"limit": "1", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [user_response_data],
                "limit": 1,
                "offset": 0,
                "total": 2,
            },
        )
        respx.get(
            f"{base_url}{Endpoints.USERS.format(company_id=company_id)}",
            params={"limit": "1", "offset": "1"},
        ).respond(
            200,
            json={
                "items": [user2],
                "limit": 1,
                "offset": 1,
                "total": 2,
            },
        )

        # When: Iterating through all users
        users = [user async for user in vclient.users(company_id).iter_all(limit=1)]

        # Then: All users are yielded as User objects
        assert len(users) == 2
        assert all(isinstance(u, User) for u in users)
        assert users[0].name == "Test User"
        assert users[1].name == "User 2"


class TestUsersServiceGet:
    """Tests for UsersService.get method."""

    @respx.mock
    async def test_get_user(self, vclient, base_url, user_response_data):
        """Verify getting a user returns User object."""
        # Given: A mocked user endpoint
        company_id = "company123"
        user_id = "507f1f77bcf86cd799439011"
        route = respx.get(
            f"{base_url}{Endpoints.USER.format(company_id=company_id, user_id=user_id)}"
        ).respond(200, json=user_response_data)

        # When: Getting the user
        result = await vclient.users(company_id).get(user_id)

        # Then: Returns User object with correct data
        assert route.called
        assert isinstance(result, User)
        assert result.id == user_id
        assert result.name == "Test User"
        assert result.email == "test@example.com"

    @respx.mock
    async def test_get_user_not_found(self, vclient, base_url):
        """Verify getting non-existent user raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        company_id = "company123"
        user_id = "nonexistent"
        respx.get(
            f"{base_url}{Endpoints.USER.format(company_id=company_id, user_id=user_id)}"
        ).respond(404, json={"detail": "User not found"})

        # When/Then: Getting the user raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.users(company_id).get(user_id)


class TestUsersServiceCreate:
    """Tests for UsersService.create method."""

    @respx.mock
    async def test_create_user_minimal(self, vclient, base_url, user_response_data):
        """Verify creating user with minimal data."""
        # Given: A mocked create endpoint
        company_id = "company123"
        route = respx.post(f"{base_url}{Endpoints.USERS.format(company_id=company_id)}").respond(
            201, json=user_response_data
        )

        # When: Creating a user with minimal data
        result = await vclient.users(company_id).create(
            name="Test User",
            email="test@example.com",
            role="PLAYER",
            requesting_user_id="requester123",
        )

        # Then: Returns created User object
        assert route.called
        assert isinstance(result, User)
        assert result.name == "Test User"

        # Verify request body
        request = route.calls.last.request
        import json

        body = json.loads(request.content)
        assert body["name"] == "Test User"
        assert body["email"] == "test@example.com"
        assert body["role"] == "PLAYER"
        assert body["requesting_user_id"] == "requester123"

    @respx.mock
    async def test_create_user_with_discord_profile(self, vclient, base_url, user_response_data):
        """Verify creating user with Discord profile."""
        # Given: A mocked create endpoint
        company_id = "company123"
        route = respx.post(f"{base_url}{Endpoints.USERS.format(company_id=company_id)}").respond(
            201, json=user_response_data
        )

        # When: Creating a user with Discord profile
        discord = DiscordProfile(id="discord123", username="testuser")
        result = await vclient.users(company_id).create(
            name="Test User",
            email="test@example.com",
            role="PLAYER",
            requesting_user_id="requester123",
            discord_profile=discord,
        )

        # Then: Returns created User object
        assert route.called
        assert isinstance(result, User)

        # Verify request body includes discord profile
        request = route.calls.last.request
        import json

        body = json.loads(request.content)
        assert body["discord_profile"]["id"] == "discord123"
        assert body["discord_profile"]["username"] == "testuser"

    async def test_create_user_validation_error(self, vclient):
        """Verify validation error on invalid data raises RequestValidationError."""
        # When/Then: Creating with invalid data raises RequestValidationError
        with pytest.raises(RequestValidationError) as exc_info:
            await vclient.users("company123").create(
                name="AB",
                email="test@example.com",
                role="PLAYER",
                requesting_user_id="requester123",
            )

        # Verify error details are accessible
        assert len(exc_info.value.errors) == 1
        assert exc_info.value.errors[0]["loc"] == ("name",)


class TestUsersServiceUpdate:
    """Tests for UsersService.update method."""

    @respx.mock
    async def test_update_user_name(self, vclient, base_url, user_response_data):
        """Verify updating user name."""
        # Given: A mocked update endpoint
        company_id = "company123"
        user_id = "507f1f77bcf86cd799439011"
        updated_data = {**user_response_data, "name": "Updated Name"}
        route = respx.patch(
            f"{base_url}{Endpoints.USER.format(company_id=company_id, user_id=user_id)}"
        ).respond(200, json=updated_data)

        # When: Updating the user name
        result = await vclient.users(company_id).update(
            user_id,
            requesting_user_id="requester123",
            name="Updated Name",
        )

        # Then: Returns updated User object
        assert route.called
        assert isinstance(result, User)
        assert result.name == "Updated Name"

        # Verify request body
        request = route.calls.last.request
        import json

        body = json.loads(request.content)
        assert body == {"name": "Updated Name", "requesting_user_id": "requester123"}

    @respx.mock
    async def test_update_user_not_found(self, vclient, base_url):
        """Verify updating non-existent user raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        company_id = "company123"
        user_id = "nonexistent"
        respx.patch(
            f"{base_url}{Endpoints.USER.format(company_id=company_id, user_id=user_id)}"
        ).respond(404, json={"detail": "User not found"})

        # When/Then: Updating raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.users(company_id).update(
                user_id,
                requesting_user_id="requester123",
                name="New Name",
            )


class TestUsersServiceDelete:
    """Tests for UsersService.delete method."""

    @respx.mock
    async def test_delete_user(self, vclient, base_url):
        """Verify deleting a user."""
        # Given: A mocked delete endpoint
        company_id = "company123"
        user_id = "507f1f77bcf86cd799439011"
        route = respx.delete(
            f"{base_url}{Endpoints.USER.format(company_id=company_id, user_id=user_id)}",
            params={"requesting_user_id": "requester123"},
        ).respond(204)

        # When: Deleting the user
        result = await vclient.users(company_id).delete(user_id, "requester123")

        # Then: Request was made and returns None
        assert route.called
        assert result is None

    @respx.mock
    async def test_delete_user_not_found(self, vclient, base_url):
        """Verify deleting non-existent user raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        company_id = "company123"
        user_id = "nonexistent"
        respx.delete(
            f"{base_url}{Endpoints.USER.format(company_id=company_id, user_id=user_id)}",
            params={"requesting_user_id": "requester123"},
        ).respond(404, json={"detail": "User not found"})

        # When/Then: Deleting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.users(company_id).delete(user_id, "requester123")


class TestUsersServiceGetStatistics:
    """Tests for UsersService.get_statistics method."""

    @respx.mock
    async def test_get_statistics(self, vclient, base_url, statistics_response_data):
        """Verify getting user statistics."""
        # Given: A mocked statistics endpoint
        company_id = "company123"
        user_id = "user123"
        route = respx.get(
            f"{base_url}{Endpoints.USER_STATISTICS.format(company_id=company_id, user_id=user_id)}",
            params={"num_top_traits": "5"},
        ).respond(200, json=statistics_response_data)

        # When: Getting statistics
        result = await vclient.users(company_id).get_statistics(user_id)

        # Then: Returns RollStatistics object
        assert route.called
        assert isinstance(result, RollStatistics)
        assert result.total_rolls == 100
        assert result.success_percentage == 50.0


class TestUsersServiceAssets:
    """Tests for UsersService asset methods."""

    @respx.mock
    async def test_list_assets(self, vclient, base_url, asset_response_data):
        """Verify listing user assets."""
        # Given: A mocked assets endpoint
        company_id = "company123"
        user_id = "user123"
        route = respx.get(
            f"{base_url}{Endpoints.USER_ASSETS.format(company_id=company_id, user_id=user_id)}",
            params={"limit": "10", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [asset_response_data],
                "limit": 10,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Listing assets
        result = await vclient.users(company_id).list_assets(user_id)

        # Then: Returns PaginatedResponse with S3Asset objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], S3Asset)

    @respx.mock
    async def test_get_asset(self, vclient, base_url, asset_response_data):
        """Verify getting a specific asset."""
        # Given: A mocked asset endpoint
        company_id = "company123"
        user_id = "user123"
        asset_id = "asset123"
        route = respx.get(
            f"{base_url}{Endpoints.USER_ASSET.format(company_id=company_id, user_id=user_id, asset_id=asset_id)}"
        ).respond(200, json=asset_response_data)

        # When: Getting the asset
        result = await vclient.users(company_id).get_asset(user_id, asset_id)

        # Then: Returns S3Asset object
        assert route.called
        assert isinstance(result, S3Asset)
        assert result.id == "asset123"

    @respx.mock
    async def test_delete_asset(self, vclient, base_url):
        """Verify deleting an asset."""
        # Given: A mocked delete endpoint
        company_id = "company123"
        user_id = "user123"
        asset_id = "asset123"
        route = respx.delete(
            f"{base_url}{Endpoints.USER_ASSET.format(company_id=company_id, user_id=user_id, asset_id=asset_id)}"
        ).respond(204)

        # When: Deleting the asset
        await vclient.users(company_id).delete_asset(user_id, asset_id)

        # Then: Request was made
        assert route.called

    @respx.mock
    async def test_upload_asset(self, vclient, base_url, asset_response_data):
        """Verify uploading an asset."""
        # Given: A mocked upload endpoint
        company_id = "company123"
        user_id = "user123"
        route = respx.post(
            f"{base_url}{Endpoints.USER_ASSET_UPLOAD.format(company_id=company_id, user_id=user_id)}"
        ).respond(201, json=asset_response_data)

        # When: Uploading an asset
        result = await vclient.users(company_id).upload_asset(
            user_id,
            filename="test.png",
            content=b"fake image content",
            content_type="image/png",
        )

        # Then: Returns S3Asset object
        assert route.called
        assert isinstance(result, S3Asset)
        assert result.id == "asset123"


class TestUsersServiceExperience:
    """Tests for UsersService experience methods."""

    @respx.mock
    async def test_get_experience(self, vclient, base_url, experience_response_data):
        """Verify getting user experience for a campaign."""
        # Given: A mocked experience endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        route = respx.get(
            f"{base_url}{Endpoints.USER_EXPERIENCE_CAMPAIGN.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id)}"
        ).respond(200, json=experience_response_data)

        # When: Getting experience
        result = await vclient.users(company_id).get_experience(user_id, campaign_id)

        # Then: Returns CampaignExperience object
        assert route.called
        assert isinstance(result, CampaignExperience)
        assert result.campaign_id == "campaign123"

    @respx.mock
    async def test_add_xp(self, vclient, base_url, experience_response_data):
        """Verify adding XP to a user."""
        # Given: A mocked add XP endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        updated_data = {**experience_response_data, "xp_current": 150, "xp_total": 200}
        route = respx.post(
            f"{base_url}{Endpoints.USER_EXPERIENCE_XP_ADD.format(company_id=company_id, user_id=user_id)}"
        ).respond(201, json=updated_data)

        # When: Adding XP
        result = await vclient.users(company_id).add_xp(user_id, campaign_id, amount=100)

        # Then: Returns updated CampaignExperience object
        assert route.called
        assert isinstance(result, CampaignExperience)
        assert result.xp_current == 150

    @respx.mock
    async def test_remove_xp(self, vclient, base_url, experience_response_data):
        """Verify removing XP from a user."""
        # Given: A mocked remove XP endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        updated_data = {**experience_response_data, "xp_current": 25}
        route = respx.post(
            f"{base_url}{Endpoints.USER_EXPERIENCE_XP_REMOVE.format(company_id=company_id, user_id=user_id)}"
        ).respond(201, json=updated_data)

        # When: Removing XP
        result = await vclient.users(company_id).remove_xp(user_id, campaign_id, amount=25)

        # Then: Returns updated CampaignExperience object
        assert route.called
        assert isinstance(result, CampaignExperience)
        assert result.xp_current == 25

    @respx.mock
    async def test_add_cool_points(self, vclient, base_url, experience_response_data):
        """Verify adding cool points to a user."""
        # Given: A mocked add CP endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        updated_data = {**experience_response_data, "cool_points": 10}
        route = respx.post(
            f"{base_url}{Endpoints.USER_EXPERIENCE_CP_ADD.format(company_id=company_id, user_id=user_id)}"
        ).respond(201, json=updated_data)

        # When: Adding cool points
        result = await vclient.users(company_id).add_cool_points(user_id, campaign_id, amount=5)

        # Then: Returns updated CampaignExperience object
        assert route.called
        assert isinstance(result, CampaignExperience)
        assert result.cool_points == 10


class TestUsersServiceNotes:
    """Tests for UsersService note methods."""

    @respx.mock
    async def test_get_notes_page(self, vclient, base_url, note_response_data):
        """Verify get_notes_page returns paginated Note objects."""
        # Given: A mocked notes list endpoint
        company_id = "company123"
        user_id = "user123"
        route = respx.get(
            f"{base_url}{Endpoints.USER_NOTES.format(company_id=company_id, user_id=user_id)}",
            params={"limit": "10", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [note_response_data],
                "limit": 10,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Getting a page of notes
        result = await vclient.users(company_id).get_notes_page(user_id)

        # Then: Returns PaginatedResponse with Note objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Note)

    @respx.mock
    async def test_get_note(self, vclient, base_url, note_response_data):
        """Verify getting a specific note returns Note object."""
        # Given: A mocked note endpoint
        company_id = "company123"
        user_id = "user123"
        note_id = "note123"
        route = respx.get(
            f"{base_url}{Endpoints.USER_NOTE.format(company_id=company_id, user_id=user_id, note_id=note_id)}"
        ).respond(200, json=note_response_data)

        # When: Getting the note
        result = await vclient.users(company_id).get_note(user_id, note_id)

        # Then: Returns Note object
        assert route.called
        assert isinstance(result, Note)
        assert result.id == "note123"

    @respx.mock
    async def test_create_note(self, vclient, base_url, note_response_data):
        """Verify creating a note returns Note object."""
        # Given: A mocked create endpoint
        company_id = "company123"
        user_id = "user123"
        route = respx.post(
            f"{base_url}{Endpoints.USER_NOTES.format(company_id=company_id, user_id=user_id)}"
        ).respond(201, json=note_response_data)

        # When: Creating a note
        result = await vclient.users(company_id).create_note(
            user_id,
            title="Test Note",
            content="This is test content",
        )

        # Then: Returns created Note object
        assert route.called
        assert isinstance(result, Note)
        assert result.title == "Test Note"

    @respx.mock
    async def test_update_note(self, vclient, base_url, note_response_data):
        """Verify updating a note returns Note object."""
        # Given: A mocked update endpoint
        company_id = "company123"
        user_id = "user123"
        note_id = "note123"
        updated_data = {**note_response_data, "title": "Updated Title"}
        route = respx.patch(
            f"{base_url}{Endpoints.USER_NOTE.format(company_id=company_id, user_id=user_id, note_id=note_id)}"
        ).respond(200, json=updated_data)

        # When: Updating the note
        result = await vclient.users(company_id).update_note(
            user_id,
            note_id,
            title="Updated Title",
        )

        # Then: Returns updated Note object
        assert route.called
        assert isinstance(result, Note)
        assert result.title == "Updated Title"

    @respx.mock
    async def test_delete_note(self, vclient, base_url):
        """Verify deleting a note."""
        # Given: A mocked delete endpoint
        company_id = "company123"
        user_id = "user123"
        note_id = "note123"
        route = respx.delete(
            f"{base_url}{Endpoints.USER_NOTE.format(company_id=company_id, user_id=user_id, note_id=note_id)}"
        ).respond(204)

        # When: Deleting the note
        await vclient.users(company_id).delete_note(user_id, note_id)

        # Then: Request was made
        assert route.called


class TestUsersServiceQuickrolls:
    """Tests for UsersService quickroll methods."""

    @respx.mock
    async def test_get_quickrolls_page(self, vclient, base_url, quickroll_response_data):
        """Verify get_quickrolls_page returns paginated Quickroll objects."""
        # Given: A mocked quickrolls list endpoint
        company_id = "company123"
        user_id = "user123"
        route = respx.get(
            f"{base_url}{Endpoints.USER_QUICKROLLS.format(company_id=company_id, user_id=user_id)}",
            params={"limit": "10", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [quickroll_response_data],
                "limit": 10,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Getting a page of quickrolls
        result = await vclient.users(company_id).get_quickrolls_page(user_id)

        # Then: Returns PaginatedResponse with Quickroll objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Quickroll)

    @respx.mock
    async def test_get_quickroll(self, vclient, base_url, quickroll_response_data):
        """Verify getting a specific quickroll returns Quickroll object."""
        # Given: A mocked quickroll endpoint
        company_id = "company123"
        user_id = "user123"
        quickroll_id = "quickroll123"
        route = respx.get(
            f"{base_url}{Endpoints.USER_QUICKROLL.format(company_id=company_id, user_id=user_id, quickroll_id=quickroll_id)}"
        ).respond(200, json=quickroll_response_data)

        # When: Getting the quickroll
        result = await vclient.users(company_id).get_quickroll(user_id, quickroll_id)

        # Then: Returns Quickroll object
        assert route.called
        assert isinstance(result, Quickroll)
        assert result.id == "quickroll123"

    @respx.mock
    async def test_create_quickroll(self, vclient, base_url, quickroll_response_data):
        """Verify creating a quickroll returns Quickroll object."""
        # Given: A mocked create endpoint
        company_id = "company123"
        user_id = "user123"
        route = respx.post(
            f"{base_url}{Endpoints.USER_QUICKROLLS.format(company_id=company_id, user_id=user_id)}"
        ).respond(201, json=quickroll_response_data)

        # When: Creating a quickroll
        result = await vclient.users(company_id).create_quickroll(
            user_id,
            name="Test Quickroll",
            description="A test quickroll",
            trait_ids=["trait1", "trait2"],
        )

        # Then: Returns created Quickroll object
        assert route.called
        assert isinstance(result, Quickroll)
        assert result.name == "Test Quickroll"

    @respx.mock
    async def test_update_quickroll(self, vclient, base_url, quickroll_response_data):
        """Verify updating a quickroll returns Quickroll object."""
        # Given: A mocked update endpoint
        company_id = "company123"
        user_id = "user123"
        quickroll_id = "quickroll123"
        updated_data = {**quickroll_response_data, "name": "Updated Name"}
        route = respx.patch(
            f"{base_url}{Endpoints.USER_QUICKROLL.format(company_id=company_id, user_id=user_id, quickroll_id=quickroll_id)}"
        ).respond(200, json=updated_data)

        # When: Updating the quickroll
        result = await vclient.users(company_id).update_quickroll(
            user_id,
            quickroll_id,
            name="Updated Name",
        )

        # Then: Returns updated Quickroll object
        assert route.called
        assert isinstance(result, Quickroll)
        assert result.name == "Updated Name"

    @respx.mock
    async def test_delete_quickroll(self, vclient, base_url):
        """Verify deleting a quickroll."""
        # Given: A mocked delete endpoint
        company_id = "company123"
        user_id = "user123"
        quickroll_id = "quickroll123"
        route = respx.delete(
            f"{base_url}{Endpoints.USER_QUICKROLL.format(company_id=company_id, user_id=user_id, quickroll_id=quickroll_id)}"
        ).respond(204)

        # When: Deleting the quickroll
        await vclient.users(company_id).delete_quickroll(user_id, quickroll_id)

        # Then: Request was made
        assert route.called


class TestUsersServiceFactoryMethod:
    """Tests for VClient.users factory method."""

    async def test_users_method_returns_service(self, vclient):
        """Verify users method returns UsersService instance."""
        # When: Calling the users method
        service = vclient.users("company123")

        # Then: Returns a UsersService instance
        from vclient.services.users import UsersService

        assert isinstance(service, UsersService)

    async def test_users_method_creates_new_instance(self, vclient):
        """Verify users method creates new instance each call."""
        # When: Calling the users method multiple times
        service1 = vclient.users("company123")
        service2 = vclient.users("company123")

        # Then: Returns different instances (not cached)
        assert service1 is not service2

    async def test_users_method_stores_company_id(self, vclient):
        """Verify users method stores company_id on the service."""
        # When: Calling the users method with a company_id
        service = vclient.users("company123")

        # Then: The service has the company_id stored
        assert service._company_id == "company123"
