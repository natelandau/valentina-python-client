"""Tests for vclient.api.models.users."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from vclient.models import (
    Asset,
    CampaignExperience,
    DiscordProfile,
    Note,
    NoteCreate,
    NoteUpdate,
    Quickroll,
    QuickrollCreate,
    QuickrollUpdate,
    RollStatistics,
    User,
    UserCreate,
    UserUpdate,
)


class TestDiscordProfile:
    """Tests for DiscordProfile model."""

    def test_all_fields_default_to_none(self):
        """Verify all fields default to None."""
        # When: Creating profile with no arguments
        profile = DiscordProfile()

        # Then: All values are None
        assert profile.id is None
        assert profile.username is None
        assert profile.global_name is None
        assert profile.avatar_id is None
        assert profile.avatar_url is None
        assert profile.discriminator is None
        assert profile.email is None
        assert profile.verified is None

    def test_partial_profile(self):
        """Verify partial profile creation."""
        # When: Creating profile with some values
        profile = DiscordProfile(
            id="123456789",
            username="testuser",
            verified=True,
        )

        # Then: Specified values are set, others are None
        assert profile.id == "123456789"
        assert profile.username == "testuser"
        assert profile.verified is True
        assert profile.global_name is None

    def test_model_dump_excludes_none(self):
        """Verify model_dump with exclude_none works correctly."""
        # Given: Profile with some values set
        profile = DiscordProfile(
            id="123456789",
            username="testuser",
        )

        # When: Dumping with exclude_none
        data = profile.model_dump(exclude_none=True)

        # Then: Only non-None values are included
        assert data == {
            "id": "123456789",
            "username": "testuser",
        }


class TestCampaignExperience:
    """Tests for CampaignExperience model."""

    def test_defaults(self):
        """Verify default values for experience fields."""
        # When: Creating experience with only campaign_id
        exp = CampaignExperience(campaign_id="campaign123")

        # Then: Defaults are set correctly
        assert exp.campaign_id == "campaign123"
        assert exp.xp_current == 0
        assert exp.xp_total == 0
        assert exp.cool_points == 0

    def test_full_experience(self):
        """Verify creating experience with all fields."""
        # When: Creating experience with all fields
        exp = CampaignExperience(
            campaign_id="campaign123",
            xp_current=50,
            xp_total=100,
            cool_points=5,
        )

        # Then: All fields are set correctly
        assert exp.campaign_id == "campaign123"
        assert exp.xp_current == 50
        assert exp.xp_total == 100
        assert exp.cool_points == 5


class TestUser:
    """Tests for User model."""

    def test_minimal_user(self):
        """Verify creating user with required fields only."""
        # When: Creating user with required fields
        user = User(
            id="user123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test User",
            email="test@example.com",
            company_id="company123",
        )

        # Then: User is created correctly with defaults
        assert user.id == "user123"
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.company_id == "company123"
        assert user.role is None
        assert user.discord_profile is None
        assert user.campaign_experience == []
        assert user.asset_ids == []

    def test_full_user(self):
        """Verify creating user with all fields populated."""
        # Given: Nested objects
        discord = DiscordProfile(id="discord123", username="testuser")
        experience = CampaignExperience(campaign_id="campaign1", xp_current=50)

        # When: Creating user with all fields
        user = User(
            id="user123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Full User",
            email="full@example.com",
            role="PLAYER",
            company_id="company123",
            discord_profile=discord,
            campaign_experience=[experience],
            asset_ids=["asset1", "asset2"],
        )

        # Then: All fields are set correctly
        assert user.role == "PLAYER"
        assert user.discord_profile.id == "discord123"
        assert len(user.campaign_experience) == 1
        assert user.campaign_experience[0].xp_current == 50
        assert user.asset_ids == ["asset1", "asset2"]

    def test_user_from_api_response(self):
        """Verify creating user from API response dict."""
        # Given: API response data
        data = {
            "id": "507f1f77bcf86cd799439011",
            "date_created": "2024-01-15T10:30:00Z",
            "date_modified": "2024-01-15T10:30:00Z",
            "name": "API User",
            "email": "api@example.com",
            "role": "STORYTELLER",
            "company_id": "company123",
            "discord_profile": {
                "id": "discord123",
                "username": "apiuser",
            },
            "campaign_experience": [
                {"campaign_id": "campaign1", "xp_current": 100, "xp_total": 200, "cool_points": 10}
            ],
            "asset_ids": ["a1", "a2"],
        }

        # When: Creating user from dict
        user = User.model_validate(data)

        # Then: User is created correctly
        assert user.id == "507f1f77bcf86cd799439011"
        assert user.name == "API User"
        assert user.role == "STORYTELLER"
        assert user.discord_profile.username == "apiuser"
        assert user.campaign_experience[0].xp_current == 100

    def test_invalid_role_rejected(self):
        """Verify invalid role values are rejected by Pydantic."""
        # When/Then: Creating user with invalid role raises error
        with pytest.raises(PydanticValidationError):
            User(
                id="user123",
                date_created="2024-01-15T10:30:00Z",
                date_modified="2024-01-15T10:30:00Z",
                name="Test",
                email="test@example.com",
                role="INVALID",
                company_id="company123",
            )


class TestUserCreate:
    """Tests for UserCreate model."""

    def test_minimal_request(self):
        """Verify creating request with required fields only."""
        # When: Creating request with required fields
        request = UserCreate(
            name="Test User",
            email="test@example.com",
            role="PLAYER",
            requesting_user_id="requester123",
        )

        # Then: Request is created correctly
        assert request.name == "Test User"
        assert request.email == "test@example.com"
        assert request.role == "PLAYER"
        assert request.requesting_user_id == "requester123"
        assert request.discord_profile is None

    def test_full_request(self):
        """Verify creating request with all fields."""
        # Given: Discord profile
        discord = DiscordProfile(id="discord123", username="testuser")

        # When: Creating request with all fields
        request = UserCreate(
            name="Full User",
            email="full@example.com",
            role="ADMIN",
            requesting_user_id="requester123",
            discord_profile=discord,
        )

        # Then: All fields are set correctly
        assert request.name == "Full User"
        assert request.discord_profile.id == "discord123"

    def test_name_validation_min_length(self):
        """Verify name minimum length validation."""
        # When/Then: Creating request with name too short raises error
        with pytest.raises(PydanticValidationError):
            UserCreate(
                name="AB",
                email="test@example.com",
                role="PLAYER",
                requesting_user_id="requester123",
            )

    def test_name_validation_max_length(self):
        """Verify name maximum length validation."""
        # When/Then: Creating request with name too long raises error
        with pytest.raises(PydanticValidationError):
            UserCreate(
                name="A" * 51,
                email="test@example.com",
                role="PLAYER",
                requesting_user_id="requester123",
            )

    def test_model_dump_excludes_unset(self):
        """Verify model_dump with exclude_unset excludes unset fields."""
        # Given: Request with required fields only
        request = UserCreate(
            name="Test",
            email="test@example.com",
            role="PLAYER",
            requesting_user_id="requester123",
        )

        # When: Dumping with exclude_none and exclude_unset
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Only set fields are included
        assert data == {
            "name": "Test",
            "email": "test@example.com",
            "role": "PLAYER",
            "requesting_user_id": "requester123",
        }


class TestUserUpdate:
    """Tests for UserUpdate model."""

    def test_only_requesting_user_id_required(self):
        """Verify only requesting_user_id is required."""
        # When: Creating request with only requesting_user_id
        request = UserUpdate(requesting_user_id="requester123")

        # Then: All other fields are None
        assert request.requesting_user_id == "requester123"
        assert request.name is None
        assert request.email is None
        assert request.role is None
        assert request.discord_profile is None

    def test_partial_update(self):
        """Verify creating request with some fields."""
        # When: Creating request with name and role
        request = UserUpdate(
            name="Updated Name",
            role="STORYTELLER",
            requesting_user_id="requester123",
        )

        # Then: Only specified fields are set
        assert request.name == "Updated Name"
        assert request.role == "STORYTELLER"
        assert request.email is None

    def test_model_dump_excludes_unset(self):
        """Verify model_dump with exclude_unset only includes set fields."""
        # Given: Request with only some fields set
        request = UserUpdate(
            name="Updated Name",
            requesting_user_id="requester123",
        )

        # When: Dumping with exclude_none and exclude_unset
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Only set fields are in the output
        assert data == {
            "name": "Updated Name",
            "requesting_user_id": "requester123",
        }

    def test_update_explicit_none_for_constrained_fields(self):
        """Verify explicitly passing None for constrained optional fields does not raise."""
        # When: Creating an update request with None for constrained name field
        request = UserUpdate(name=None, requesting_user_id="requester123")

        # Then: Name is None without validation errors
        assert request.name is None

    def test_update_constrained_fields_still_validate_non_none(self):
        """Verify constraints still apply when a non-None value is provided."""
        with pytest.raises(PydanticValidationError):
            UserUpdate(name="ab", requesting_user_id="requester123")


class TestRollStatistics:
    """Tests for RollStatistics model."""

    def test_all_fields(self):
        """Verify creating statistics with all fields."""
        # When: Creating statistics
        stats = RollStatistics(
            botches=5,
            successes=50,
            failures=30,
            criticals=15,
            total_rolls=100,
            average_difficulty=6.5,
            average_pool=4.2,
            top_traits=[{"name": "Strength", "count": 20}],
            criticals_percentage=15.0,
            success_percentage=50.0,
            failure_percentage=30.0,
            botch_percentage=5.0,
        )

        # Then: All fields are set correctly
        assert stats.botches == 5
        assert stats.successes == 50
        assert stats.failures == 30
        assert stats.criticals == 15
        assert stats.total_rolls == 100
        assert stats.average_difficulty == 6.5
        assert stats.average_pool == 4.2
        assert len(stats.top_traits) == 1
        assert stats.criticals_percentage == 15.0
        assert stats.success_percentage == 50.0
        assert stats.failure_percentage == 30.0
        assert stats.botch_percentage == 5.0

    def test_statistics_from_api_response(self):
        """Verify creating statistics from API response dict."""
        # Given: API response data
        data = {
            "botches": 2,
            "successes": 80,
            "failures": 15,
            "criticals": 3,
            "total_rolls": 100,
            "average_difficulty": 6.0,
            "average_pool": 5.0,
            "top_traits": [{"name": "Dexterity", "count": 30}, {"name": "Wits", "count": 25}],
            "criticals_percentage": 3.0,
            "success_percentage": 80.0,
            "failure_percentage": 15.0,
            "botch_percentage": 2.0,
        }

        # When: Creating statistics from dict
        stats = RollStatistics.model_validate(data)

        # Then: Statistics are created correctly
        assert stats.total_rolls == 100
        assert len(stats.top_traits) == 2


class TestAsset:
    """Tests for Asset model."""

    def test_all_fields(self):
        """Verify creating asset with all fields."""
        # When: Creating asset
        asset = Asset(
            id="asset123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            asset_type="image",
            mime_type="image/png",
            original_filename="avatar.png",
            public_url="https://example.com/avatar.png",
            uploaded_by="user123",
            company_id="company123",
            parent_type="user",
        )

        # Then: All fields are set correctly
        assert asset.id == "asset123"
        assert asset.asset_type == "image"
        assert asset.mime_type == "image/png"
        assert asset.original_filename == "avatar.png"
        assert asset.public_url == "https://example.com/avatar.png"
        assert asset.uploaded_by == "user123"
        assert asset.company_id == "company123"
        assert asset.parent_type == "user"

    def test_invalid_asset_type_rejected(self):
        """Verify invalid asset type is rejected."""
        # When/Then: Creating asset with invalid asset type raises error
        with pytest.raises(PydanticValidationError):
            Asset(
                id="asset123",
                date_created="2024-01-15T10:30:00Z",
                date_modified="2024-01-15T10:30:00Z",
                asset_type="invalid",
                mime_type="application/octet-stream",
                original_filename="file.txt",
                public_url="https://example.com/file.txt",
                uploaded_by="user123",
                company_id="company123",
            )


class TestNote:
    """Tests for Note model."""

    def test_all_fields(self):
        """Verify creating note with all fields."""
        # When: Creating note
        note = Note(
            id="note123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            title="My Note",
            content="This is the content of my note.",
        )

        # Then: All fields are set correctly
        assert note.id == "note123"
        assert note.title == "My Note"
        assert note.content == "This is the content of my note."


class TestNoteCreate:
    """Tests for NoteCreate model."""

    def test_required_fields(self):
        """Verify creating request with required fields."""
        # When: Creating request
        request = NoteCreate(
            title="Note Title",
            content="Note content here",
        )

        # Then: Fields are set correctly
        assert request.title == "Note Title"
        assert request.content == "Note content here"

    def test_title_min_length_validation(self):
        """Verify title minimum length validation."""
        # When/Then: Creating request with title too short raises error
        with pytest.raises(PydanticValidationError):
            NoteCreate(title="AB", content="Valid content")

    def test_content_min_length_validation(self):
        """Verify content minimum length validation."""
        # When/Then: Creating request with content too short raises error
        with pytest.raises(PydanticValidationError):
            NoteCreate(title="Valid Title", content="AB")


class TestNoteUpdate:
    """Tests for NoteUpdate model."""

    def test_empty_request(self):
        """Verify creating empty update request."""
        # When: Creating request with no fields
        request = NoteUpdate()

        # Then: All fields are None
        assert request.title is None
        assert request.content is None

    def test_partial_update(self):
        """Verify creating request with some fields."""
        # When: Creating request with only title
        request = NoteUpdate(title="Updated Title")

        # Then: Only title is set
        assert request.title == "Updated Title"
        assert request.content is None

    def test_model_dump_excludes_unset(self):
        """Verify model_dump with exclude_unset only includes set fields."""
        # Given: Request with only title set
        request = NoteUpdate(title="Updated Title")

        # When: Dumping with exclude_none and exclude_unset
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Only title is in the output
        assert data == {"title": "Updated Title"}


class TestQuickroll:
    """Tests for Quickroll model."""

    def test_minimal_quickroll(self):
        """Verify creating quickroll with required fields."""
        # When: Creating quickroll with required fields
        quickroll = Quickroll(
            id="qr123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Quick Attack",
            user_id="user123",
        )

        # Then: Quickroll is created with defaults
        assert quickroll.id == "qr123"
        assert quickroll.name == "Quick Attack"
        assert quickroll.user_id == "user123"
        assert quickroll.description is None
        assert quickroll.trait_ids == []

    def test_full_quickroll(self):
        """Verify creating quickroll with all fields."""
        # When: Creating quickroll with all fields
        quickroll = Quickroll(
            id="qr123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Quick Attack",
            description="A quick attack roll",
            user_id="user123",
            trait_ids=["trait1", "trait2"],
        )

        # Then: All fields are set correctly
        assert quickroll.description == "A quick attack roll"
        assert quickroll.trait_ids == ["trait1", "trait2"]


class TestQuickrollCreate:
    """Tests for QuickrollCreate model."""

    def test_minimal_request(self):
        """Verify creating request with required fields only."""
        # When: Creating request with name only
        request = QuickrollCreate(name="Quick Roll")

        # Then: Request is created with defaults
        assert request.name == "Quick Roll"
        assert request.description is None
        assert request.trait_ids == []

    def test_full_request(self):
        """Verify creating request with all fields."""
        # When: Creating request with all fields
        request = QuickrollCreate(
            name="Full Roll",
            description="A complete roll",
            trait_ids=["trait1", "trait2"],
        )

        # Then: All fields are set correctly
        assert request.name == "Full Roll"
        assert request.description == "A complete roll"
        assert request.trait_ids == ["trait1", "trait2"]

    def test_name_min_length_validation(self):
        """Verify name minimum length validation."""
        # When/Then: Creating request with name too short raises error
        with pytest.raises(PydanticValidationError):
            QuickrollCreate(name="AB")


class TestQuickrollUpdate:
    """Tests for QuickrollUpdate model."""

    def test_empty_request(self):
        """Verify creating empty update request."""
        # When: Creating request with no fields
        request = QuickrollUpdate()

        # Then: All fields are None
        assert request.name is None
        assert request.description is None
        assert request.trait_ids is None

    def test_partial_update(self):
        """Verify creating request with some fields."""
        # When: Creating request with name only
        request = QuickrollUpdate(name="Updated Name")

        # Then: Only name is set
        assert request.name == "Updated Name"
        assert request.description is None
        assert request.trait_ids is None

    def test_update_explicit_none_for_constrained_fields(self):
        """Verify explicitly passing None for constrained optional fields does not raise."""
        # When: Creating an update request with None for constrained fields
        request = QuickrollUpdate(name=None, description=None)

        # Then: Fields are None without validation errors
        assert request.name is None
        assert request.description is None

    def test_update_constrained_fields_still_validate_non_none(self):
        """Verify constraints still apply when a non-None value is provided."""
        with pytest.raises(PydanticValidationError):
            QuickrollUpdate(name="ab")

        with pytest.raises(PydanticValidationError):
            QuickrollUpdate(description="ab")


class TestQuickrollCreateConstraints:
    """Tests for QuickrollCreate optional field constraint handling."""

    def test_create_explicit_none_for_optional_constrained_fields(self):
        """Verify explicitly passing None for optional constrained fields does not raise."""
        # When: Creating a request with None for optional description
        request = QuickrollCreate(name="Test Roll", description=None)

        # Then: Description is None without validation errors
        assert request.description is None
