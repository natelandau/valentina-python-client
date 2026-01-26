"""Tests for vclient.models.books."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from vclient.models.books import (
    CampaignBook,
    CreateBookRequest,
    RenumberBookRequest,
    UpdateBookRequest,
)


class TestCampaignBook:
    """Tests for CampaignBook model."""

    def test_valid_book(self):
        """Verify valid book creation."""
        book = CampaignBook(
            id="book123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test Book",
            description="A test book",
            asset_ids=["asset1", "asset2"],
            number=1,
            campaign_id="campaign123",
        )

        assert book.id == "book123"
        assert book.name == "Test Book"
        assert book.description == "A test book"
        assert book.asset_ids == ["asset1", "asset2"]
        assert book.number == 1
        assert book.campaign_id == "campaign123"

    def test_defaults(self):
        """Verify default values."""
        book = CampaignBook(
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test Book",
            number=1,
            campaign_id="campaign123",
        )

        assert book.id is None
        assert book.description is None
        assert book.asset_ids == []


class TestCreateBookRequest:
    """Tests for CreateBookRequest model."""

    def test_valid_request(self):
        """Verify valid request creation."""
        request = CreateBookRequest(
            name="Test Book",
            description="A test book",
        )

        assert request.name == "Test Book"
        assert request.description == "A test book"

    def test_minimal_request(self):
        """Verify minimal valid request with defaults."""
        request = CreateBookRequest(name="Test")

        assert request.name == "Test"
        assert request.description is None

    def test_name_min_length(self):
        """Verify name minimum length validation."""
        with pytest.raises(PydanticValidationError):
            CreateBookRequest(name="ab")

    def test_name_max_length(self):
        """Verify name maximum length validation."""
        with pytest.raises(PydanticValidationError):
            CreateBookRequest(name="a" * 51)

    def test_description_min_length(self):
        """Verify description minimum length validation."""
        with pytest.raises(PydanticValidationError):
            CreateBookRequest(name="Valid", description="ab")


class TestUpdateBookRequest:
    """Tests for UpdateBookRequest model."""

    def test_all_fields_optional(self):
        """Verify all fields default to None."""
        request = UpdateBookRequest()

        assert request.name is None
        assert request.description is None

    def test_partial_update(self):
        """Verify partial update works."""
        request = UpdateBookRequest(name="New Name")

        assert request.name == "New Name"
        assert request.description is None

    def test_model_dump_excludes_none(self):
        """Verify model_dump with exclude_none works correctly."""
        request = UpdateBookRequest(name="New Name")

        data = request.model_dump(exclude_none=True)

        assert data == {"name": "New Name"}

    def test_name_validation_when_provided(self):
        """Verify name validation still applies when value is provided."""
        with pytest.raises(PydanticValidationError):
            UpdateBookRequest(name="ab")

    def test_description_validation_when_provided(self):
        """Verify description validation still applies when value is provided."""
        with pytest.raises(PydanticValidationError):
            UpdateBookRequest(description="ab")


class TestRenumberBookRequest:
    """Tests for RenumberBookRequest model."""

    def test_valid_request(self):
        """Verify valid request creation."""
        request = RenumberBookRequest(number=5)

        assert request.number == 5

    def test_number_min_value(self):
        """Verify number minimum value validation."""
        with pytest.raises(PydanticValidationError):
            RenumberBookRequest(number=0)

    def test_number_negative_value(self):
        """Verify negative number validation."""
        with pytest.raises(PydanticValidationError):
            RenumberBookRequest(number=-1)

    def test_number_required(self):
        """Verify number is required."""
        with pytest.raises(PydanticValidationError):
            RenumberBookRequest()
