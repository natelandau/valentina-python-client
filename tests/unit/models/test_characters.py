"""Unit tests for character models."""

from __future__ import annotations

from typing import get_args

import pytest
from pydantic import ValidationError as PydanticValidationError

from vclient.models import (
    Character,
    CharacterCreate,
    CharacterDetail,
    CharacterUpdate,
    HunterAttributes,
    MageAttributes,
    NameDescriptionSubDocument,
    VampireAttributes,
    WerewolfAttributes,
)


class TestCharacter:
    """Tests for Character response model."""

    def test_character_minimal_fields(self) -> None:
        """Verify Character model with minimal required fields."""
        # When: Creating a character with required fields only
        character = Character(
            id="char123",
            character_class="VAMPIRE",
            game_version="V5",
            name_first="John",
            name_last="Doe",
            name="Johnny",
            name_full="John Doe",
            user_creator_id="user123",
            user_player_id="user456",
            company_id="company123",
            campaign_id="campaign123",
        )

        # Then: Character is created with defaults
        assert character.character_class == "VAMPIRE"
        assert character.game_version == "V5"
        assert character.name_first == "John"
        assert character.name_last == "Doe"
        assert character.type == "PLAYER"
        assert character.status == "ALIVE"
        assert character.starting_points == 0
        assert character.is_temporary is False
        assert character.asset_ids == []
        assert character.character_trait_ids == []
        assert character.specialties == []

    def test_character_all_fields(self) -> None:
        """Verify Character model with all fields populated."""
        # Given: Complete character data
        data = {
            "id": "char123",
            "date_created": "2024-01-15T10:30:00Z",
            "date_modified": "2024-01-15T10:30:00Z",
            "date_killed": None,
            "character_class": "WEREWOLF",
            "type": "NPC",
            "game_version": "V4",
            "status": "ALIVE",
            "starting_points": 15,
            "name_first": "Jane",
            "name_last": "Smith",
            "name_nick": "Wolf",
            "name": "Wolf",
            "name_full": "Jane Smith",
            "age": 28,
            "biography": "A fierce warrior of the pack.",
            "demeanor": "Aggressive",
            "nature": "Protector",
            "concept_id": "concept456",
            "user_creator_id": "user123",
            "user_player_id": "user789",
            "company_id": "company123",
            "campaign_id": "campaign123",
            "asset_ids": ["asset1", "asset2"],
            "character_trait_ids": ["trait1"],
            "specialties": [
                {
                    "id": "spec1",
                    "name": "Brawl: Claws",
                    "type": "ACTION",
                    "description": "Skilled with claws",
                }
            ],
            "is_temporary": True,
            "vampire_attributes": None,
            "werewolf_attributes": {
                "tribe_id": "tribe123",
                "tribe_name": "Glass Walkers",
                "auspice_id": "auspice123",
                "auspice_name": "Ahroun",
                "pack_name": "Urban Hunters",
            },
            "mage_attributes": None,
            "hunter_attributes": None,
        }

        # When: Creating a character from data
        character = Character.model_validate(data)

        # Then: All fields are correctly parsed
        assert character.id == "char123"
        assert character.character_class == "WEREWOLF"
        assert character.type == "NPC"
        assert character.game_version == "V4"
        assert character.name_first == "Jane"
        assert character.age == 28
        assert character.is_temporary is True
        assert character.werewolf_attributes is not None
        assert character.werewolf_attributes.tribe_name == "Glass Walkers"
        assert len(character.specialties) == 1
        assert character.specialties[0].name == "Brawl: Claws"

    def test_character_class_validation(self) -> None:
        """Verify character_class only accepts valid values."""
        # When/Then: Invalid character class is rejected
        with pytest.raises(PydanticValidationError) as exc_info:
            Character(
                character_class="INVALID",  # type: ignore[arg-type]
                game_version="V5",
                name_first="John",
                name_last="Doe",
                name="Johnny",
                name_full="John Doe",
                user_creator_id="user123",
                user_player_id="user456",
                company_id="company123",
                campaign_id="campaign123",
            )

        assert "character_class" in str(exc_info.value)

    def test_character_type_validation(self) -> None:
        """Verify type only accepts valid values."""
        # When/Then: Invalid type is rejected
        with pytest.raises(PydanticValidationError) as exc_info:
            Character(
                character_class="VAMPIRE",
                type="INVALID",  # type: ignore[arg-type]
                game_version="V5",
                name_first="John",
                name_last="Doe",
                name="Johnny",
                name_full="John Doe",
                user_creator_id="user123",
                user_player_id="user456",
                company_id="company123",
                campaign_id="campaign123",
            )

        assert "type" in str(exc_info.value)

    def test_character_game_version_validation(self) -> None:
        """Verify game_version only accepts V4 or V5."""
        # When/Then: Invalid game version is rejected
        with pytest.raises(PydanticValidationError) as exc_info:
            Character(
                character_class="VAMPIRE",
                game_version="V3",  # type: ignore[arg-type]
                name_first="John",
                name_last="Doe",
                name="Johnny",
                name_full="John Doe",
                user_creator_id="user123",
                user_player_id="user456",
                company_id="company123",
                campaign_id="campaign123",
            )

        assert "game_version" in str(exc_info.value)

    def test_character_status_validation(self) -> None:
        """Verify status only accepts ALIVE or DEAD."""
        # When/Then: Invalid status is rejected
        with pytest.raises(PydanticValidationError) as exc_info:
            Character(
                character_class="VAMPIRE",
                game_version="V5",
                status="UNDEAD",  # type: ignore[arg-type]
                name_first="John",
                name_last="Doe",
                name="Johnny",
                name_full="John Doe",
                user_creator_id="user123",
                user_player_id="user456",
                company_id="company123",
                campaign_id="campaign123",
            )

        assert "status" in str(exc_info.value)


class TestCharacterCreate:
    """Tests for CharacterCreate model."""

    def test_create_request_minimal(self) -> None:
        """Verify CharacterCreate with required fields only."""
        # When: Creating a request with required fields
        request = CharacterCreate(
            character_class="VAMPIRE",
            game_version="V5",
            name_first="John",
            name_last="Doe",
        )

        # Then: Request is created with correct values
        assert request.character_class == "VAMPIRE"
        assert request.game_version == "V5"
        assert request.name_first == "John"
        assert request.name_last == "Doe"
        assert request.is_temporary is False
        assert request.type is None
        assert request.age is None

    def test_create_request_all_fields(self) -> None:
        """Verify CharacterCreate with all fields."""
        # Given: Traits to assign
        from vclient.models.character_trait import CharacterCreateTraitAssign

        traits = [CharacterCreateTraitAssign(trait_id="trait123", value=3)]

        # When: Creating a request with all fields
        request = CharacterCreate(
            character_class="WEREWOLF",
            game_version="V4",
            name_first="Jane",
            name_last="Smith",
            type="NPC",
            name_nick="Wolf",
            age=28,
            biography="A fierce warrior.",
            demeanor="Aggressive",
            nature="Protector",
            concept_id="concept123",
            user_player_id="user456",
            is_temporary=True,
            traits=traits,
        )

        # Then: All fields are set correctly
        assert request.character_class == "WEREWOLF"
        assert request.is_temporary is True
        assert request.type == "NPC"
        assert request.name_nick == "Wolf"
        assert request.age == 28
        assert request.traits == traits

    def test_create_request_name_first_min_length(self) -> None:
        """Verify name_first requires minimum 3 characters."""
        # When/Then: Short first name is rejected
        with pytest.raises(PydanticValidationError) as exc_info:
            CharacterCreate(
                character_class="VAMPIRE",
                game_version="V5",
                name_first="Jo",  # Too short
                name_last="Doe",
            )

        assert "name_first" in str(exc_info.value)

    def test_create_request_name_last_min_length(self) -> None:
        """Verify name_last requires minimum 3 characters."""
        # When/Then: Short last name is rejected
        with pytest.raises(PydanticValidationError) as exc_info:
            CharacterCreate(
                character_class="VAMPIRE",
                game_version="V5",
                name_first="John",
                name_last="Do",  # Too short
            )

        assert "name_last" in str(exc_info.value)

    def test_create_request_model_dump_excludes_none(self) -> None:
        """Verify model_dump with exclude_none excludes unset optional fields."""
        # Given: A request with only required fields
        request = CharacterCreate(
            character_class="VAMPIRE",
            game_version="V5",
            name_first="John",
            name_last="Doe",
        )

        # When: Dumping with exclude_none
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Only required fields are in the output
        assert data == {
            "character_class": "VAMPIRE",
            "game_version": "V5",
            "name_first": "John",
            "name_last": "Doe",
        }


class TestCharacterUpdate:
    """Tests for CharacterUpdate model."""

    def test_update_request_empty(self) -> None:
        """Verify CharacterUpdate with no fields."""
        # When: Creating an empty update request
        request = CharacterUpdate()

        # Then: All fields are None
        assert request.character_class is None
        assert request.is_temporary is None
        assert request.name_first is None
        assert request.status is None

    def test_update_request_partial(self) -> None:
        """Verify CharacterUpdate with partial fields."""
        # When: Creating an update request with some fields
        request = CharacterUpdate(
            name_first="Jane",
            status="DEAD",
            is_temporary=True,
        )

        # Then: Only specified fields are set
        assert request.name_first == "Jane"
        assert request.status == "DEAD"
        assert request.is_temporary is True
        assert request.name_last is None
        assert request.character_class is None

    def test_update_request_model_dump_excludes_unset(self) -> None:
        """Verify model_dump with exclude_unset only includes set fields."""
        # Given: An update request with partial fields
        request = CharacterUpdate(
            name_first="Jane",
        )

        # When: Dumping with exclude_none and exclude_unset
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Only the set field is in the output
        assert data == {"name_first": "Jane"}

    def test_update_request_name_first_min_length(self) -> None:
        """Verify name_first requires minimum 3 characters when provided."""
        # When/Then: Short first name is rejected
        with pytest.raises(PydanticValidationError) as exc_info:
            CharacterUpdate(name_first="Jo")  # Too short

        assert "name_first" in str(exc_info.value)

    def test_update_explicit_none_for_constrained_fields(self) -> None:
        """Verify explicitly passing None for constrained optional fields does not raise."""
        # When: Creating an update request with None for all constrained string fields
        request = CharacterUpdate(
            name_first=None,
            name_last=None,
            name_nick=None,
            biography=None,
            demeanor=None,
            nature=None,
        )

        # Then: All fields are None without validation errors
        assert request.name_first is None
        assert request.name_last is None
        assert request.name_nick is None
        assert request.biography is None
        assert request.demeanor is None
        assert request.nature is None

    def test_update_constrained_fields_still_validate_non_none(self) -> None:
        """Verify constraints still apply when a non-None value is provided."""
        # When/Then: Short values are rejected for each constrained field
        with pytest.raises(PydanticValidationError):
            CharacterUpdate(name_last="ab")

        with pytest.raises(PydanticValidationError):
            CharacterUpdate(name_nick="ab")

        with pytest.raises(PydanticValidationError):
            CharacterUpdate(biography="ab")

        with pytest.raises(PydanticValidationError):
            CharacterUpdate(demeanor="ab")

        with pytest.raises(PydanticValidationError):
            CharacterUpdate(nature="ab")


class TestCharacterCreateConstraints:
    """Tests for CharacterCreate optional field constraint handling."""

    def test_create_explicit_none_for_optional_constrained_fields(self) -> None:
        """Verify explicitly passing None for optional constrained fields does not raise."""
        # When: Creating a request with None for optional constrained fields
        request = CharacterCreate(
            character_class="VAMPIRE",
            game_version="V5",
            name_first="John",
            name_last="Doe",
            name_nick=None,
            biography=None,
            demeanor=None,
            nature=None,
        )

        # Then: Optional fields are None without validation errors
        assert request.name_nick is None
        assert request.biography is None
        assert request.demeanor is None
        assert request.nature is None


class TestVampireAttributes:
    """Tests for VampireAttributes model."""

    def test_vampire_attributes_empty(self) -> None:
        """Verify VampireAttributes with no fields."""
        # When: Creating empty vampire attributes
        attrs = VampireAttributes()

        # Then: All fields are None
        assert attrs.clan_id is None
        assert attrs.clan_name is None
        assert attrs.generation is None
        assert attrs.sire is None

    def test_vampire_attributes_full(self) -> None:
        """Verify VampireAttributes with all fields."""
        # When: Creating full vampire attributes
        attrs = VampireAttributes(
            clan_id="clan123",
            clan_name="Ventrue",
            generation=10,
            sire="Ancient One",
            bane=NameDescriptionSubDocument(
                name="Rarefied Tastes", description="Feeds only on specific blood"
            ),
            compulsion=NameDescriptionSubDocument(
                name="Domineering", description="Must be in control"
            ),
        )

        # Then: All fields are set
        assert attrs.clan_name == "Ventrue"
        assert attrs.generation == 10
        assert attrs.bane is not None
        assert attrs.bane.name == "Rarefied Tastes"


class TestWerewolfAttributes:
    """Tests for WerewolfAttributes model."""

    def test_werewolf_attributes_full(self) -> None:
        """Verify WerewolfAttributes with all fields."""
        # When: Creating full werewolf attributes
        attrs = WerewolfAttributes(
            tribe_id="tribe123",
            tribe_name="Glass Walkers",
            auspice_id="auspice123",
            auspice_name="Ahroun",
            pack_name="Urban Hunters",
        )

        # Then: All fields are set
        assert attrs.tribe_name == "Glass Walkers"
        assert attrs.auspice_name == "Ahroun"
        assert attrs.pack_name == "Urban Hunters"


class TestHunterAttributes:
    """Tests for HunterAttributes model."""

    def test_hunter_attributes_with_creed(self) -> None:
        """Verify HunterAttributes with creed."""
        # When: Creating hunter attributes with creed
        attrs = HunterAttributes(creed="Defender")

        # Then: Creed is set correctly
        assert attrs.creed == "Defender"


class TestMageAttributes:
    """Tests for MageAttributes model."""

    def test_mage_attributes(self) -> None:
        """Verify MageAttributes model."""
        # When: Creating mage attributes
        attrs = MageAttributes(sphere="Forces")

        # Then: Field is set
        assert attrs.sphere == "Forces"


class TestCharacterDetail:
    """Tests for CharacterDetail response model."""

    def test_character_detail_without_includes(self) -> None:
        """Verify CharacterDetail works identically to Character when no includes are present."""
        # Given: Standard character data with no embedded resources
        detail = CharacterDetail(
            id="char123",
            character_class="VAMPIRE",
            game_version="V5",
            name_first="John",
            name_last="Doe",
            name="Johnny",
            name_full="John Doe",
            user_creator_id="user123",
            user_player_id="user456",
            company_id="company123",
            campaign_id="campaign123",
        )

        # Then: Embedded fields default to None
        assert detail.traits is None
        assert detail.inventory is None
        assert detail.notes is None
        assert detail.assets is None

        # Then: It is a subclass of Character
        assert isinstance(detail, Character)

    def test_character_detail_with_all_includes(self) -> None:
        """Verify CharacterDetail accepts embedded child resources."""
        # Given: Character data with all embedded resources
        detail = CharacterDetail(
            id="char123",
            character_class="VAMPIRE",
            game_version="V5",
            name_first="John",
            name_last="Doe",
            name="Johnny",
            name_full="John Doe",
            user_creator_id="user123",
            user_player_id="user456",
            company_id="company123",
            campaign_id="campaign123",
            traits=[
                {
                    "id": "ct1",
                    "character_id": "char123",
                    "value": 3,
                    "trait": {
                        "id": "t1",
                        "name": "Strength",
                        "date_created": "2024-01-15T10:30:00Z",
                        "date_modified": "2024-01-15T10:30:00Z",
                        "max_value": 5,
                        "min_value": 0,
                        "is_custom": False,
                        "show_when_zero": True,
                        "sheet_section_id": "sec1",
                        "category_id": "cat1",
                        "is_rollable": True,
                        "character_classes": ["VAMPIRE"],
                        "game_versions": ["V5"],
                    },
                }
            ],
            inventory=[
                {
                    "id": "item1",
                    "character_id": "char123",
                    "name": "Silver Knife",
                    "type": "WEAPON",
                    "date_created": "2024-01-15T10:30:00Z",
                    "date_modified": "2024-01-15T10:30:00Z",
                }
            ],
            notes=[
                {
                    "id": "note1",
                    "date_created": "2024-01-15T10:30:00Z",
                    "date_modified": "2024-01-15T10:30:00Z",
                    "title": "Session Log",
                    "content": "Met the prince.",
                }
            ],
            assets=[
                {
                    "id": "asset1",
                    "date_created": "2024-01-15T10:30:00Z",
                    "date_modified": "2024-01-15T10:30:00Z",
                    "asset_type": "image",
                    "mime_type": "image/png",
                    "original_filename": "portrait.png",
                    "public_url": "https://example.com/portrait.png",
                    "uploaded_by": "user123",
                    "company_id": "company123",
                }
            ],
        )

        # Then: Embedded resources are populated
        assert len(detail.traits) == 1
        assert detail.traits[0].trait.name == "Strength"
        assert len(detail.inventory) == 1
        assert detail.inventory[0].name == "Silver Knife"
        assert len(detail.notes) == 1
        assert detail.notes[0].title == "Session Log"
        assert len(detail.assets) == 1
        assert detail.assets[0].original_filename == "portrait.png"

    def test_character_detail_from_json_missing_keys(self) -> None:
        """Verify CharacterDetail handles absent embedded keys from JSON."""
        # Given: JSON response with no embedded resource keys
        data = {
            "id": "char123",
            "character_class": "VAMPIRE",
            "game_version": "V5",
            "name_first": "John",
            "name_last": "Doe",
            "name": "Johnny",
            "name_full": "John Doe",
            "user_creator_id": "user123",
            "user_player_id": "user456",
            "company_id": "company123",
            "campaign_id": "campaign123",
        }

        # When: Validating from raw JSON
        detail = CharacterDetail.model_validate(data)

        # Then: Embedded fields are None
        assert detail.traits is None
        assert detail.inventory is None
        assert detail.notes is None
        assert detail.assets is None


class TestCharacterInclude:
    """Tests for CharacterInclude Literal type."""

    def test_character_include_valid_values(self) -> None:
        """Verify CharacterInclude contains the expected literal values."""
        # Given: The expected include values
        from vclient.constants import CharacterInclude

        expected = {"traits", "inventory", "notes", "assets"}

        # When: Extracting the Literal args
        actual = set(get_args(CharacterInclude))

        # Then: They match exactly
        assert actual == expected
