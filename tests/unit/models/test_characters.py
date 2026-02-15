"""Unit tests for character models."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from vclient.models import (
    Character,
    CharacterCreate,
    CharacterHunterEdge,
    CharacterUpdate,
    HunterAttributes,
    MageAttributes,
    VampireAttributes,
    WerewolfAttributes,
)


class TestCharacter:
    """Tests for Character response model."""

    def test_character_minimal_fields(self) -> None:
        """Verify Character model with minimal required fields."""
        # When: Creating a character with required fields only
        character = Character(
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
            "specialties": [{"id": "spec1", "name": "Brawl: Claws", "type": "ACTION"}],
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
            traits=traits,
        )

        # Then: All fields are set correctly
        assert request.character_class == "WEREWOLF"
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
        assert request.name_first is None
        assert request.status is None

    def test_update_request_partial(self) -> None:
        """Verify CharacterUpdate with partial fields."""
        # When: Creating an update request with some fields
        request = CharacterUpdate(
            name_first="Jane",
            status="DEAD",
        )

        # Then: Only specified fields are set
        assert request.name_first == "Jane"
        assert request.status == "DEAD"
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
            bane={"name": "Rarefied Tastes", "description": "Feeds only on specific blood"},
            compulsion={"name": "Domineering", "description": "Must be in control"},
        )

        # Then: All fields are set
        assert attrs.clan_name == "Ventrue"
        assert attrs.generation == 10
        assert attrs.bane is not None
        assert attrs.bane["name"] == "Rarefied Tastes"


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

    def test_hunter_attributes_with_edges(self) -> None:
        """Verify HunterAttributes with edges and perks."""
        # When: Creating hunter attributes with edges
        attrs = HunterAttributes(
            creed="Defender",
            edges=[CharacterHunterEdge(edge_id="edge123", perk_ids=["perk123"])],
        )

        # Then: All fields are set correctly
        assert attrs.creed == "Defender"
        assert len(attrs.edges) == 1
        assert attrs.edges[0].edge_id == "edge123"
        assert attrs.edges[0].perk_ids == ["perk123"]


class TestMageAttributes:
    """Tests for MageAttributes model."""

    def test_mage_attributes(self) -> None:
        """Verify MageAttributes model."""
        # When: Creating mage attributes
        attrs = MageAttributes(sphere="Forces")

        # Then: Field is set
        assert attrs.sphere == "Forces"
