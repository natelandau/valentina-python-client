"""Tests for vclient.models.campaigns."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from vclient.models.campaigns import (
    Campaign,
    CampaignCreate,
    CampaignUpdate,
)


class TestCampaign:
    """Tests for Campaign model."""

    def test_valid_campaign(self):
        """Verify valid campaign creation."""
        campaign = Campaign(
            id="campaign123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test Campaign",
            description="A test campaign",
            asset_ids=["asset1", "asset2"],
            desperation=2,
            danger=3,
            company_id="company123",
        )

        assert campaign.id == "campaign123"
        assert campaign.name == "Test Campaign"
        assert campaign.description == "A test campaign"
        assert campaign.asset_ids == ["asset1", "asset2"]
        assert campaign.desperation == 2
        assert campaign.danger == 3
        assert campaign.company_id == "company123"

    def test_defaults(self):
        """Verify default values."""
        campaign = Campaign(
            id="campaign123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test Campaign",
            company_id="company123",
        )

        assert campaign.description is None
        assert campaign.year is None
        assert campaign.asset_ids == []
        assert campaign.desperation == 0
        assert campaign.danger == 0

    def test_year_field(self):
        """Verify the year field accepts free-form text."""
        campaign = Campaign(
            id="campaign123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test Campaign",
            company_id="company123",
            year="Third Age, 2941",
        )

        assert campaign.year == "Third Age, 2941"

    def test_child_resource_counts(self):
        """Verify child-resource count fields default to 0 and accept values."""
        defaults = Campaign(
            id="campaign123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test Campaign",
            company_id="company123",
        )
        assert defaults.num_books == 0
        assert defaults.num_chapters == 0
        assert defaults.num_notes == 0
        assert defaults.num_player_characters == 0
        assert defaults.num_storyteller_characters == 0
        assert defaults.num_npc_characters == 0

        populated = Campaign(
            id="campaign123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test Campaign",
            company_id="company123",
            num_books=2,
            num_chapters=5,
            num_notes=3,
            num_player_characters=4,
            num_storyteller_characters=1,
            num_npc_characters=7,
        )
        assert populated.num_books == 2
        assert populated.num_chapters == 5
        assert populated.num_notes == 3
        assert populated.num_player_characters == 4
        assert populated.num_storyteller_characters == 1
        assert populated.num_npc_characters == 7


class TestCampaignCreate:
    """Tests for CampaignCreate model."""

    def test_valid_request(self):
        """Verify valid request creation."""
        request = CampaignCreate(
            name="Test Campaign",
            description="A test campaign",
            desperation=2,
            danger=3,
        )

        assert request.name == "Test Campaign"
        assert request.description == "A test campaign"
        assert request.desperation == 2
        assert request.danger == 3

    def test_minimal_request(self):
        """Verify minimal valid request with defaults."""
        request = CampaignCreate(name="Test")

        assert request.name == "Test"
        assert request.description is None
        assert request.year is None
        assert request.desperation == 0
        assert request.danger == 0

    def test_year_accepts_text(self):
        """Verify year accepts free-form text up to 50 chars."""
        request = CampaignCreate(name="Valid", year="1924")

        assert request.year == "1924"

    def test_year_max_length(self):
        """Verify year maximum length validation."""
        with pytest.raises(PydanticValidationError):
            CampaignCreate(name="Valid", year="a" * 51)

    def test_name_min_length(self):
        """Verify name minimum length validation."""
        with pytest.raises(PydanticValidationError):
            CampaignCreate(name="ab")

    def test_name_max_length(self):
        """Verify name maximum length validation."""
        with pytest.raises(PydanticValidationError):
            CampaignCreate(name="a" * 51)

    def test_description_min_length(self):
        """Verify description minimum length validation."""
        with pytest.raises(PydanticValidationError):
            CampaignCreate(name="Valid", description="ab")

    def test_desperation_max_value(self):
        """Verify desperation maximum value validation."""
        with pytest.raises(PydanticValidationError):
            CampaignCreate(name="Valid", desperation=6)

    def test_desperation_min_value(self):
        """Verify desperation minimum value validation."""
        with pytest.raises(PydanticValidationError):
            CampaignCreate(name="Valid", desperation=-1)

    def test_danger_max_value(self):
        """Verify danger maximum value validation."""
        with pytest.raises(PydanticValidationError):
            CampaignCreate(name="Valid", danger=6)

    def test_danger_min_value(self):
        """Verify danger minimum value validation."""
        with pytest.raises(PydanticValidationError):
            CampaignCreate(name="Valid", danger=-1)


class TestCampaignUpdate:
    """Tests for CampaignUpdate model."""

    def test_all_fields_optional(self):
        """Verify all fields default to None."""
        request = CampaignUpdate()

        assert request.name is None
        assert request.description is None
        assert request.desperation is None
        assert request.danger is None

    def test_partial_update(self):
        """Verify partial update works."""
        request = CampaignUpdate(name="New Name", desperation=3)

        assert request.name == "New Name"
        assert request.description is None
        assert request.desperation == 3
        assert request.danger is None

    def test_model_dump_excludes_none(self):
        """Verify model_dump with exclude_none works correctly."""
        request = CampaignUpdate(name="New Name", danger=4)

        data = request.model_dump(exclude_none=True)

        assert data == {"name": "New Name", "danger": 4}

    def test_year_clear_via_empty_string(self):
        """Verify an empty-string year survives exclude_none so the server can clear it."""
        # Empty string (not None) must reach the API to clear the year; None is dropped by exclude_none.
        request = CampaignUpdate(year="")

        data = request.model_dump(exclude_none=True, exclude_unset=True)

        assert data == {"year": ""}

    def test_year_max_length_when_provided(self):
        """Verify year maximum length validation still applies on update."""
        with pytest.raises(PydanticValidationError):
            CampaignUpdate(year="a" * 51)

    def test_name_validation_when_provided(self):
        """Verify name validation still applies when value is provided."""
        with pytest.raises(PydanticValidationError):
            CampaignUpdate(name="ab")

    def test_desperation_validation_when_provided(self):
        """Verify desperation validation still applies when value is provided."""
        with pytest.raises(PydanticValidationError):
            CampaignUpdate(desperation=6)

    def test_danger_validation_when_provided(self):
        """Verify danger validation still applies when value is provided."""
        with pytest.raises(PydanticValidationError):
            CampaignUpdate(danger=6)

    def test_update_explicit_none_for_constrained_fields(self):
        """Verify explicitly passing None for constrained optional fields does not raise."""
        # When: Creating an update request with None for all constrained fields
        request = CampaignUpdate(
            name=None,
            description=None,
            desperation=None,
            danger=None,
        )

        # Then: All fields are None without validation errors
        assert request.name is None
        assert request.description is None
        assert request.desperation is None
        assert request.danger is None


class TestCampaignCreateConstraints:
    """Tests for CampaignCreate optional field constraint handling."""

    def test_create_explicit_none_for_optional_constrained_fields(self):
        """Verify explicitly passing None for optional constrained fields does not raise."""
        # When: Creating a request with None for optional description
        request = CampaignCreate(name="Test", description=None)

        # Then: Description is None without validation errors
        assert request.description is None
