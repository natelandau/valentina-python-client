"""Tests for vclient.models.shared."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from vclient.models.shared import (
    Asset,
    Note,
    NoteCreate,
    NoteUpdate,
    RollStatistics,
)


class TestAsset:
    """Tests for Asset model."""

    def test_valid_asset(self):
        """Verify valid asset creation."""
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

        assert asset.id == "asset123"
        assert asset.asset_type == "image"
        assert asset.mime_type == "image/png"
        assert asset.original_filename == "avatar.png"
        assert asset.public_url == "https://example.com/avatar.png"
        assert asset.uploaded_by == "user123"
        assert asset.company_id == "company123"
        assert asset.parent_type == "user"

    def test_parent_type_defaults_to_none(self):
        """Verify parent_type defaults to None."""
        asset = Asset(
            id="asset123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            asset_type="document",
            mime_type="application/pdf",
            original_filename="doc.pdf",
            public_url="https://example.com/doc.pdf",
            uploaded_by="user123",
            company_id="company123",
        )

        assert asset.parent_type is None

    def test_all_asset_types(self):
        """Verify all asset types are valid."""
        asset_types = ["image", "text", "audio", "video", "document", "archive", "other"]

        for asset_type in asset_types:
            asset = Asset(
                id="asset123",
                date_created="2024-01-15T10:30:00Z",
                date_modified="2024-01-15T10:30:00Z",
                asset_type=asset_type,
                mime_type="application/octet-stream",
                original_filename="file.bin",
                public_url="https://example.com/file.bin",
                uploaded_by="user123",
                company_id="company123",
            )
            assert asset.asset_type == asset_type

    def test_all_parent_types(self):
        """Verify all parent types are valid."""
        parent_types = [
            "character",
            "campaign",
            "campaignbook",
            "campaignchapter",
            "user",
            "company",
            "unknown",
        ]

        for parent_type in parent_types:
            asset = Asset(
                id="asset123",
                date_created="2024-01-15T10:30:00Z",
                date_modified="2024-01-15T10:30:00Z",
                asset_type="image",
                mime_type="image/png",
                original_filename="file.png",
                public_url="https://example.com/file.png",
                uploaded_by="user123",
                company_id="company123",
                parent_type=parent_type,
            )
            assert asset.parent_type == parent_type


class TestNote:
    """Tests for Note model."""

    def test_valid_note(self):
        """Verify valid note creation."""
        note = Note(
            id="note123",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            title="Test Note",
            content="This is a test note.",
        )

        assert note.id == "note123"
        assert note.title == "Test Note"
        assert note.content == "This is a test note."


class TestNoteCreate:
    """Tests for NoteCreate model."""

    def test_valid_request(self):
        """Verify valid request creation."""
        request = NoteCreate(
            title="Test Note",
            content="This is a test note.",
        )

        assert request.title == "Test Note"
        assert request.content == "This is a test note."

    def test_title_min_length(self):
        """Verify title minimum length validation."""
        with pytest.raises(PydanticValidationError):
            NoteCreate(title="ab", content="Valid content")

    def test_title_max_length(self):
        """Verify title maximum length validation."""
        with pytest.raises(PydanticValidationError):
            NoteCreate(title="a" * 51, content="Valid content")

    def test_content_min_length(self):
        """Verify content minimum length validation."""
        with pytest.raises(PydanticValidationError):
            NoteCreate(title="Valid title", content="ab")


class TestNoteUpdate:
    """Tests for NoteUpdate model."""

    def test_all_fields_optional(self):
        """Verify all fields default to None."""
        request = NoteUpdate()

        assert request.title is None
        assert request.content is None

    def test_partial_update(self):
        """Verify partial update works."""
        request = NoteUpdate(title="New Title")

        assert request.title == "New Title"
        assert request.content is None

    def test_model_dump_excludes_none(self):
        """Verify model_dump with exclude_none works correctly."""
        request = NoteUpdate(title="New Title")

        data = request.model_dump(exclude_none=True)

        assert data == {"title": "New Title"}

    def test_update_explicit_none_for_constrained_fields(self):
        """Verify explicitly passing None for constrained optional fields does not raise."""
        # When: Creating an update request with None for constrained fields
        request = NoteUpdate(title=None, content=None)

        # Then: Fields are None without validation errors
        assert request.title is None
        assert request.content is None

    def test_update_constrained_fields_still_validate_non_none(self):
        """Verify constraints still apply when a non-None value is provided."""
        with pytest.raises(PydanticValidationError):
            NoteUpdate(title="ab")

        with pytest.raises(PydanticValidationError):
            NoteUpdate(content="ab")


class TestRollStatistics:
    """Tests for RollStatistics model."""

    def test_valid_statistics(self):
        """Verify valid statistics creation."""
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

        assert stats.botches == 5
        assert stats.successes == 50
        assert stats.failures == 30
        assert stats.criticals == 15
        assert stats.total_rolls == 100
        assert stats.average_difficulty == 6.5
        assert stats.average_pool == 4.2
        assert len(stats.top_traits) == 1
        assert stats.criticals_percentage == 15.0

    def test_optional_fields_default_to_none(self):
        """Verify optional fields default correctly."""
        stats = RollStatistics(
            botches=5,
            successes=50,
            failures=30,
            criticals=15,
            total_rolls=100,
            criticals_percentage=15.0,
            success_percentage=50.0,
            failure_percentage=30.0,
            botch_percentage=5.0,
        )

        assert stats.average_difficulty is None
        assert stats.average_pool is None
        assert stats.top_traits == []
