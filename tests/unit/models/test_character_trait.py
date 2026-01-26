"""Unit tests for character trait models."""

from datetime import UTC, datetime

from vclient.models.character_trait import (
    AssignCharacterTraitRequest,
    CharacterTrait,
    CharacterTraitValueChangeRequest,
    CreateCharacterTraitRequest,
)
from vclient.models.shared import Trait


class TestCharacterTrait:
    """Tests for CharacterTrait response model."""

    def test_character_trait_minimal_fields(self) -> None:
        """Verify CharacterTrait model with required fields."""
        # Given: A trait object
        trait = Trait(
            id="trait123",
            name="Strength",
            date_created=datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
            date_modified=datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
            parent_category_id="cat123",
        )

        # When: Creating a character trait
        character_trait = CharacterTrait(
            id="ct123",
            character_id="char123",
            value=3,
            trait=trait,
        )

        # Then: All fields are set correctly
        assert character_trait.id == "ct123"
        assert character_trait.character_id == "char123"
        assert character_trait.value == 3
        assert character_trait.trait.name == "Strength"

    def test_character_trait_from_api_response(self) -> None:
        """Verify CharacterTrait model validates from API response format."""
        # Given: API response data
        data = {
            "id": "ct456",
            "character_id": "char789",
            "value": 5,
            "trait": {
                "id": "trait456",
                "name": "Dexterity",
                "description": "Physical agility and coordination",
                "date_created": "2024-01-15T10:30:00Z",
                "date_modified": "2024-01-15T10:30:00Z",
                "parent_category_id": "cat456",
                "show_when_zero": True,
                "max_value": 5,
                "min_value": 0,
                "is_custom": False,
                "initial_cost": 1,
                "upgrade_cost": 2,
            },
        }

        # When: Validating the response
        character_trait = CharacterTrait.model_validate(data)

        # Then: All fields are correctly parsed
        assert character_trait.id == "ct456"
        assert character_trait.character_id == "char789"
        assert character_trait.value == 5
        assert character_trait.trait.id == "trait456"
        assert character_trait.trait.name == "Dexterity"
        assert character_trait.trait.description == "Physical agility and coordination"
        assert character_trait.trait.max_value == 5

    def test_character_trait_with_full_trait_data(self) -> None:
        """Verify CharacterTrait with complete trait information."""
        # Given: Complete API response data
        data = {
            "id": "ct789",
            "character_id": "char111",
            "value": 2,
            "trait": {
                "id": "trait789",
                "name": "Firearms",
                "description": "Skill with ranged weapons",
                "date_created": "2024-01-15T10:30:00Z",
                "date_modified": "2024-01-15T10:30:00Z",
                "link": "https://wiki.example.com/firearms",
                "show_when_zero": False,
                "max_value": 5,
                "min_value": 0,
                "is_custom": False,
                "initial_cost": 3,
                "upgrade_cost": 3,
                "sheet_section_name": "Skills",
                "sheet_section_id": "section123",
                "parent_category_name": "Physical Skills",
                "parent_category_id": "cat789",
                "character_classes": ["VAMPIRE", "HUNTER"],
                "game_versions": ["V5"],
            },
        }

        # When: Validating the response
        character_trait = CharacterTrait.model_validate(data)

        # Then: All trait details are accessible
        assert character_trait.trait.link == "https://wiki.example.com/firearms"
        assert character_trait.trait.sheet_section_name == "Skills"
        assert character_trait.trait.parent_category_name == "Physical Skills"
        assert character_trait.trait.character_classes == ["VAMPIRE", "HUNTER"]
        assert character_trait.trait.game_versions == ["V5"]


class TestAssignCharacterTraitRequest:
    """Tests for AssignCharacterTraitRequest model."""

    def test_assign_request_required_fields(self) -> None:
        """Verify AssignCharacterTraitRequest with required fields."""
        # When: Creating a request
        request = AssignCharacterTraitRequest(
            trait_id="trait123",
            value=3,
        )

        # Then: Fields are set correctly
        assert request.trait_id == "trait123"
        assert request.value == 3

    def test_assign_request_model_dump(self) -> None:
        """Verify model_dump produces correct JSON payload."""
        # Given: An assign request
        request = AssignCharacterTraitRequest(
            trait_id="trait456",
            value=5,
        )

        # When: Dumping to JSON
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Correct JSON structure is produced
        assert data == {
            "trait_id": "trait456",
            "value": 5,
        }

    def test_assign_request_zero_value(self) -> None:
        """Verify AssignCharacterTraitRequest accepts zero value."""
        # When: Creating a request with value 0
        request = AssignCharacterTraitRequest(
            trait_id="trait789",
            value=0,
        )

        # Then: Value is set correctly
        assert request.value == 0


class TestCreateCharacterTraitRequest:
    """Tests for CreateCharacterTraitRequest model."""

    def test_create_request_required_fields(self) -> None:
        """Verify CreateCharacterTraitRequest with required fields only."""
        # When: Creating a request with required fields
        request = CreateCharacterTraitRequest(
            name="Custom Skill",
            parent_category_id="cat123",
        )

        # Then: Required fields are set, defaults applied
        assert request.name == "Custom Skill"
        assert request.parent_category_id == "cat123"
        assert request.max_value == 5
        assert request.min_value == 0
        assert request.show_when_zero is True
        assert request.description is None
        assert request.initial_cost is None
        assert request.upgrade_cost is None
        assert request.value is None

    def test_create_request_all_fields(self) -> None:
        """Verify CreateCharacterTraitRequest with all fields."""
        # When: Creating a request with all fields
        request = CreateCharacterTraitRequest(
            name="Custom Background",
            parent_category_id="backgrounds_cat",
            description="A custom background trait",
            max_value=10,
            min_value=1,
            show_when_zero=False,
            initial_cost=3,
            upgrade_cost=2,
            value=5,
        )

        # Then: All fields are set correctly
        assert request.name == "Custom Background"
        assert request.parent_category_id == "backgrounds_cat"
        assert request.description == "A custom background trait"
        assert request.max_value == 10
        assert request.min_value == 1
        assert request.show_when_zero is False
        assert request.initial_cost == 3
        assert request.upgrade_cost == 2
        assert request.value == 5

    def test_create_request_model_dump(self) -> None:
        """Verify model_dump produces correct JSON payload."""
        # Given: A create request with required fields only
        request = CreateCharacterTraitRequest(
            name="Stealth",
            parent_category_id="skills_cat",
        )

        # When: Dumping to JSON with exclude_none and exclude_unset
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Required fields and unset fields without defaults are in the output
        assert data["name"] == "Stealth"
        assert data["parent_category_id"] == "skills_cat"
        assert "description" not in data
        assert "initial_cost" not in data
        assert "upgrade_cost" not in data
        assert "value" not in data

    def test_create_request_model_dump_with_optionals(self) -> None:
        """Verify model_dump includes optional fields when set."""
        # Given: A create request with optional fields
        request = CreateCharacterTraitRequest(
            name="Lore",
            parent_category_id="knowledge_cat",
            description="Knowledge of ancient texts",
            initial_cost=2,
            value=3,
        )

        # When: Dumping to JSON
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Optional fields are included
        assert data["name"] == "Lore"
        assert data["description"] == "Knowledge of ancient texts"
        assert data["initial_cost"] == 2
        assert data["value"] == 3

    def test_create_request_max_value_validation(self) -> None:
        """Verify max_value has valid range constraint."""
        # When: Creating a request with valid max_value
        request = CreateCharacterTraitRequest(
            name="Test Trait",
            parent_category_id="cat123",
            max_value=100,
        )

        # Then: Value is accepted
        assert request.max_value == 100

    def test_create_request_min_value_validation(self) -> None:
        """Verify min_value has valid range constraint."""
        # When: Creating a request with valid min_value
        request = CreateCharacterTraitRequest(
            name="Test Trait",
            parent_category_id="cat123",
            min_value=0,
        )

        # Then: Value is accepted
        assert request.min_value == 0


class TestCharacterTraitValueChangeRequest:
    """Tests for CharacterTraitValueChangeRequest model."""

    def test_value_change_request_required_field(self) -> None:
        """Verify CharacterTraitValueChangeRequest with required field."""
        # When: Creating a request
        request = CharacterTraitValueChangeRequest(num_dots=2)

        # Then: Field is set correctly
        assert request.num_dots == 2

    def test_value_change_request_model_dump(self) -> None:
        """Verify model_dump produces correct JSON payload."""
        # Given: A value change request
        request = CharacterTraitValueChangeRequest(num_dots=3)

        # When: Dumping to JSON
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Correct JSON structure is produced
        assert data == {"num_dots": 3}

    def test_value_change_request_single_dot(self) -> None:
        """Verify CharacterTraitValueChangeRequest accepts single dot."""
        # When: Creating a request with 1 dot
        request = CharacterTraitValueChangeRequest(num_dots=1)

        # Then: Value is set correctly
        assert request.num_dots == 1

    def test_value_change_request_negative_value(self) -> None:
        """Verify CharacterTraitValueChangeRequest accepts negative values for decreases."""
        # When: Creating a request with negative value
        request = CharacterTraitValueChangeRequest(num_dots=-1)

        # Then: Value is set correctly
        assert request.num_dots == -1
