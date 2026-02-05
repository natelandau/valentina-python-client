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
        assert campaign.asset_ids == []
        assert campaign.desperation == 0
        assert campaign.danger == 0


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
        assert request.desperation == 0
        assert request.danger == 0

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
