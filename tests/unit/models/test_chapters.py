"""Tests for vclient.models.chapters."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from vclient.models.chapters import (
    CampaignChapter,
    ChapterCreate,
    ChapterUpdate,
    _ChapterRenumber,
)


class TestCampaignChapter:
    """Tests for CampaignChapter model."""

    def test_valid_chapter(self):
        """Verify valid chapter creation."""
        chapter = CampaignChapter(
            id="chapter123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test Chapter",
            description="A test chapter",
            asset_ids=["asset1", "asset2"],
            number=1,
            book_id="book123",
        )

        assert chapter.id == "chapter123"
        assert chapter.name == "Test Chapter"
        assert chapter.description == "A test chapter"
        assert chapter.asset_ids == ["asset1", "asset2"]
        assert chapter.number == 1
        assert chapter.book_id == "book123"

    def test_defaults(self):
        """Verify default values."""
        chapter = CampaignChapter(
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test Chapter",
            number=1,
            book_id="book123",
        )

        assert chapter.id is None
        assert chapter.description is None
        assert chapter.asset_ids == []

    def test_required_fields(self):
        """Verify required fields raise error when missing."""
        with pytest.raises(PydanticValidationError):
            CampaignChapter(
                date_created="2024-01-15T10:30:00Z",
                date_modified="2024-01-15T10:30:00Z",
                name="Test Chapter",
                number=1,
                # Missing book_id
            )


class TestChapterCreate:
    """Tests for ChapterCreate model."""

    def test_valid_request(self):
        """Verify valid request creation."""
        request = ChapterCreate(
            name="Test Chapter",
            description="A test chapter",
        )

        assert request.name == "Test Chapter"
        assert request.description == "A test chapter"

    def test_minimal_request(self):
        """Verify minimal valid request with defaults."""
        request = ChapterCreate(name="Test")

        assert request.name == "Test"
        assert request.description is None

    def test_name_required(self):
        """Verify name is required."""
        with pytest.raises(PydanticValidationError):
            ChapterCreate()


class TestChapterUpdate:
    """Tests for ChapterUpdate model."""

    def test_all_fields_optional(self):
        """Verify all fields default to None."""
        request = ChapterUpdate()

        assert request.name is None
        assert request.description is None

    def test_partial_update(self):
        """Verify partial update works."""
        request = ChapterUpdate(name="New Name")

        assert request.name == "New Name"
        assert request.description is None

    def test_model_dump_excludes_none(self):
        """Verify model_dump with exclude_none works correctly."""
        request = ChapterUpdate(name="New Name")

        data = request.model_dump(exclude_none=True)

        assert data == {"name": "New Name"}

    def test_full_update(self):
        """Verify full update with all fields."""
        request = ChapterUpdate(name="New Name", description="New Description")

        assert request.name == "New Name"
        assert request.description == "New Description"


class TestChapterRenumber:
    """Tests for _ChapterRenumber model."""

    def test_valid_request(self):
        """Verify valid request creation."""
        request = _ChapterRenumber(number=5)

        assert request.number == 5

    def test_number_min_value(self):
        """Verify number minimum value validation."""
        with pytest.raises(PydanticValidationError):
            _ChapterRenumber(number=0)

    def test_number_negative_value(self):
        """Verify negative number validation."""
        with pytest.raises(PydanticValidationError):
            _ChapterRenumber(number=-1)

    def test_number_required(self):
        """Verify number is required."""
        with pytest.raises(PydanticValidationError):
            _ChapterRenumber()
