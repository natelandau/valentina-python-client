"""Tests for vclient.validate_constants."""

import pytest

from vclient.validate_constants import (
    CONSTANT_MAP,
    ConstantMapping,
    ConstantMismatch,
    ValidationResult,
)


class TestConstantMapping:
    """Tests for ConstantMapping dataclass."""

    def test_create_mapping(self):
        """Verify creating a ConstantMapping with category and option."""
        mapping = ConstantMapping(api_category="characters", api_option="CharacterClass")
        assert mapping.api_category == "characters"
        assert mapping.api_option == "CharacterClass"

    def test_mapping_is_frozen(self):
        """Verify ConstantMapping instances are immutable."""
        mapping = ConstantMapping(api_category="characters", api_option="CharacterClass")
        with pytest.raises(AttributeError):
            mapping.api_category = "other"


class TestConstantMismatch:
    """Tests for ConstantMismatch dataclass."""

    def test_create_mismatch(self):
        """Verify creating a ConstantMismatch with all fields."""
        mismatch = ConstantMismatch(
            constant_name="CharacterClass",
            api_category="characters",
            api_option="CharacterClass",
            missing_from_client={"CHANGELING"},
            extra_in_client={"MORTAL"},
        )
        assert mismatch.constant_name == "CharacterClass"
        assert mismatch.missing_from_client == {"CHANGELING"}
        assert mismatch.extra_in_client == {"MORTAL"}


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_valid_result(self):
        """Verify creating a valid ValidationResult."""
        result = ValidationResult(is_valid=True, mismatches=[], unmapped_api_options={})
        assert result.is_valid is True
        assert result.mismatches == []
        assert result.unmapped_api_options == {}


class TestConstantMap:
    """Tests for the CONSTANT_MAP mapping table."""

    def test_all_api_constants_are_mapped(self):
        """Verify every Literal constant in constants.py has a mapping entry."""
        import typing

        from vclient import constants

        literal_names = [
            name
            for name in dir(constants)
            if not name.startswith("_")
            and hasattr(getattr(constants, name), "__origin__")
            and getattr(constants, name).__origin__ is typing.Literal
        ]
        for name in literal_names:
            assert name in CONSTANT_MAP, f"Constant '{name}' is not in CONSTANT_MAP"

    def test_map_has_no_extra_entries(self):
        """Verify CONSTANT_MAP has no entries for non-existent constants."""
        from vclient import constants

        for name in CONSTANT_MAP:
            assert hasattr(constants, name), f"CONSTANT_MAP entry '{name}' has no matching constant"
