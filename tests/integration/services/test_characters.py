"""Integration tests for CharactersService."""

import copy
from datetime import UTC, datetime

import pytest
import respx
from httpx import Response

from vclient.endpoints import Endpoints
from vclient.exceptions import NotFoundError
from vclient.models import (
    Asset,
    Character,
    CharacterFullSheet,
    FullSheetTraitCategory,
    HunterAttributesCreate,
    HunterAttributesUpdate,
    InventoryItem,
    NameDescriptionSubDocument,
    Note,
    PaginatedResponse,
    RollStatistics,
    VampireAttributesCreate,
    VampireAttributesUpdate,
    WerewolfAttributesCreate,
    WerewolfAttributesUpdate,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def paginated_character_response(character_response_data: dict) -> dict:
    """Return a paginated response with characters."""
    return {
        "items": [character_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def statistics_response_data() -> dict:
    """Return sample statistics response data."""
    return {
        "botches": 5,
        "successes": 50,
        "failures": 30,
        "criticals": 15,
        "total_rolls": 100,
        "average_difficulty": 6.5,
        "average_pool": 4.2,
        "top_traits": [{"name": "Strength", "count": 20}],
        "criticals_percentage": 15.0,
        "success_percentage": 50.0,
        "failure_percentage": 30.0,
        "botch_percentage": 5.0,
    }


@pytest.fixture
def full_sheet_response_data() -> dict:
    """Return sample full sheet response data."""
    return {
        "character": {
            "id": "char123",
            "character_class": "VAMPIRE",
            "game_version": "V5",
            "name_first": "Marcus",
            "name_last": "Blackwood",
            "name": "Marcus",
            "name_full": "Marcus Blackwood",
            "user_creator_id": "user123",
            "user_player_id": "user123",
            "company_id": "company123",
            "campaign_id": "507f1f77bcf86cd799439011",
        },
        "sections": [
            {
                "id": "sec1",
                "name": "Physical",
                "order": 1,
                "show_when_empty": True,
                "categories": [
                    {
                        "id": "cat1",
                        "name": "Attributes",
                        "initial_cost": 1,
                        "upgrade_cost": 2,
                        "show_when_empty": True,
                        "order": 1,
                        "subcategories": [],
                        "character_traits": [
                            {
                                "id": "ct1",
                                "character_id": "char123",
                                "value": 3,
                                "trait": {
                                    "id": "t1",
                                    "name": "Strength",
                                    "date_created": "2024-01-01T00:00:00Z",
                                    "date_modified": "2024-01-01T00:00:00Z",
                                    "sheet_section_id": "sec1",
                                    "parent_category_id": "cat1",
                                },
                            }
                        ],
                    }
                ],
            }
        ],
    }


@pytest.fixture
def full_sheet_category_response_data() -> dict:
    """Return sample full sheet category response data."""
    return {
        "id": "cat1",
        "name": "Attributes",
        "initial_cost": 1,
        "upgrade_cost": 2,
        "show_when_empty": True,
        "order": 1,
        "subcategories": [],
        "character_traits": [
            {
                "id": "ct1",
                "character_id": "char123",
                "value": 3,
                "trait": {
                    "id": "t1",
                    "name": "Strength",
                    "date_created": "2024-01-01T00:00:00Z",
                    "date_modified": "2024-01-01T00:00:00Z",
                    "sheet_section_id": "sec1",
                    "parent_category_id": "cat1",
                },
            }
        ],
        "available_traits": [],
    }


@pytest.fixture
def full_sheet_category_response_data_with_available_traits(
    full_sheet_category_response_data: dict,
) -> dict:
    """Return sample full sheet category response data with available traits."""
    data = copy.deepcopy(full_sheet_category_response_data)
    data["character_traits"] = []
    data["available_traits"] = [
        {
            "id": "t2",
            "name": "Dexterity",
            "date_created": "2024-01-01T00:00:00Z",
            "date_modified": "2024-01-01T00:00:00Z",
            "sheet_section_id": "sec1",
            "parent_category_id": "cat1",
        }
    ]
    return data


@pytest.fixture
def full_sheet_response_data_with_available_traits(
    full_sheet_response_data: dict,
    full_sheet_category_response_data_with_available_traits: dict,
) -> dict:
    """Return sample full sheet response data with available traits."""
    data = copy.deepcopy(full_sheet_response_data)
    data["sections"][0]["categories"][0] = full_sheet_category_response_data_with_available_traits
    return data


@pytest.fixture
def asset_response_data() -> dict:
    """Return sample asset response data."""
    return {
        "id": "asset123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "asset_type": "image",
        "mime_type": "image/png",
        "original_filename": "character.png",
        "public_url": "https://example.com/character.png",
        "uploaded_by": "user123",
        "company_id": "company123",
        "parent_type": "character",
    }


@pytest.fixture
def note_response_data() -> dict:
    """Return sample note response data."""
    return {
        "id": "note123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "title": "Test Note",
        "content": "This is test content",
    }


@pytest.fixture
def inventory_item_response_data() -> dict:
    """Return sample inventory item response data."""
    return {
        "id": "item123",
        "character_id": "char123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "name": "Test Item",
        "type": "BOOK",
        "description": "This is test content",
    }


@pytest.fixture
def werewolf_character_response_data() -> dict:
    """Return sample werewolf character response data."""
    return {
        "id": "char456",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "date_killed": None,
        "character_class": "WEREWOLF",
        "type": "PLAYER",
        "game_version": "V5",
        "status": "ALIVE",
        "starting_points": 0,
        "name_first": "Wolf",
        "name_last": "Runner",
        "name_nick": "Howler",
        "name": "Howler",
        "name_full": "Wolf Runner",
        "age": 28,
        "biography": "A fierce werewolf.",
        "demeanor": "Aggressive",
        "nature": "Survivor",
        "concept_id": "concept456",
        "user_creator_id": "user123",
        "user_player_id": "user456",
        "company_id": "company123",
        "campaign_id": "campaign123",
        "asset_ids": [],
        "character_trait_ids": [],
        "specialties": [],
        "vampire_attributes": None,
        "werewolf_attributes": {
            "tribe_id": "tribe123",
            "tribe_name": "Shadow Lords",
            "auspice_id": "auspice123",
            "auspice_name": "Ahroun",
            "pack_name": "Moon Runners",
        },
        "mage_attributes": None,
        "hunter_attributes": None,
    }


@pytest.fixture
def hunter_character_response_data() -> dict:
    """Return sample hunter character response data."""
    return {
        "id": "char789",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "date_killed": None,
        "character_class": "HUNTER",
        "type": "PLAYER",
        "game_version": "V5",
        "status": "ALIVE",
        "starting_points": 0,
        "name_first": "John",
        "name_last": "Hunter",
        "name_nick": "Slayer",
        "name": "Slayer",
        "name_full": "John Hunter",
        "age": 40,
        "biography": "A veteran hunter.",
        "demeanor": "Determined",
        "nature": "Avenger",
        "concept_id": "concept789",
        "user_creator_id": "user123",
        "user_player_id": "user456",
        "company_id": "company123",
        "campaign_id": "campaign123",
        "asset_ids": [],
        "character_trait_ids": [],
        "specialties": [],
        "vampire_attributes": None,
        "werewolf_attributes": None,
        "mage_attributes": None,
        "hunter_attributes": {
            "creed": "Avenger",
        },
    }


class TestCharactersServiceGetPage:
    """Tests for CharactersService.get_page method."""

    @respx.mock
    async def test_get_page(self, vclient, base_url, paginated_character_response) -> None:
        """Verify getting a page of characters returns paginated response."""
        # Given: A mocked characters list endpoint
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTERS.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(200, json=paginated_character_response))

        # When: Requesting a page of characters
        result = await vclient.characters(
            "user123", "campaign123", company_id="company123"
        ).get_page()

        # Then: The route was called and response is paginated
        assert route.called
        assert len(result.items) == 1
        assert isinstance(result.items[0], Character)
        assert result.items[0].name_first == "John"
        assert result.total == 1

    @respx.mock
    async def test_get_page_with_filters(
        self, vclient, base_url, paginated_character_response
    ) -> None:
        """Verify get_page passes filter parameters correctly."""
        # Given: A mocked endpoint expecting filter params
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTERS.format(company_id='company123', user_id='user123', campaign_id='campaign123')}",
            params={
                "limit": "10",
                "offset": "0",
                "character_class": "VAMPIRE",
                "status": "ALIVE",
                "is_temporary": "true",
            },
        ).mock(return_value=Response(200, json=paginated_character_response))

        # When: Requesting with filters
        result = await vclient.characters(
            "user123", "campaign123", company_id="company123"
        ).get_page(character_class="VAMPIRE", status="ALIVE", is_temporary=True)

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1


class TestCharactersServiceGet:
    """Tests for CharactersService.get method."""

    @respx.mock
    async def test_get_character(self, vclient, base_url, character_response_data) -> None:
        """Verify getting a character returns Character object."""
        # Given: A mocked character endpoint
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json=character_response_data))

        # When: Requesting a character
        result = await vclient.characters("user123", "campaign123", company_id="company123").get(
            "char123"
        )

        # Then: The route was called and character is returned
        assert route.called
        assert isinstance(result, Character)
        assert result.id == "char123"
        assert result.name_first == "John"
        assert result.name_last == "Doe"
        assert result.character_class == "VAMPIRE"
        assert result.game_version == "V5"

    @respx.mock
    async def test_get_character_not_found(self, vclient, base_url) -> None:
        """Verify getting a non-existent character raises NotFoundError."""
        # Given: A mocked 404 response
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='nonexistent')}"
        ).mock(
            return_value=Response(404, json={"detail": "Character not found", "status_code": 404})
        )

        # When/Then: Requesting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.characters("user123", "campaign123", company_id="company123").get(
                "nonexistent"
            )

        assert route.called


class TestCharactersServiceCreate:
    """Tests for CharactersService.create method."""

    @respx.mock
    async def test_create_character_minimal(
        self, vclient, base_url, character_response_data
    ) -> None:
        """Verify creating a character with minimal fields."""
        # Given: A mocked create endpoint
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTERS.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(201, json=character_response_data))

        # When: Creating a character with required fields only
        result = await vclient.characters("user123", "campaign123", company_id="company123").create(
            character_class="VAMPIRE",
            game_version="V5",
            name_first="John",
            name_last="Doe",
        )

        # Then: The route was called and character is returned
        assert route.called
        assert isinstance(result, Character)
        assert result.name_first == "John"

        # Verify request body
        request = route.calls[0].request
        import json

        body = json.loads(request.content)
        assert body["character_class"] == "VAMPIRE"
        assert body["game_version"] == "V5"
        assert body["name_first"] == "John"
        assert body["name_last"] == "Doe"

    @respx.mock
    async def test_create_character_with_all_options(
        self, vclient, base_url, character_response_data
    ) -> None:
        """Verify creating a character with all optional fields."""
        # Given: A mocked create endpoint
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTERS.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(201, json=character_response_data))

        # When: Creating a character with all fields
        result = await vclient.characters("user123", "campaign123", company_id="company123").create(
            character_class="VAMPIRE",
            game_version="V5",
            name_first="John",
            name_last="Doe",
            type="NPC",
            name_nick="Johnny",
            age=35,
            biography="A mysterious vampire.",
            demeanor="Friendly",
            nature="Warrior",
            concept_id="concept123",
            user_player_id="user456",
        )

        # Then: The route was called and character is returned
        assert route.called
        assert isinstance(result, Character)

        # Verify request body includes optional fields
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["type"] == "NPC"  # explicitly set
        assert body["name_nick"] == "Johnny"
        assert body["age"] == 35
        assert body["biography"] == "A mysterious vampire."

    @respx.mock
    async def test_create_character_with_vampire_attributes(
        self, vclient, base_url, character_response_data
    ) -> None:
        """Verify creating a character with vampire attributes."""
        # Given: A mocked create endpoint
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTERS.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(201, json=character_response_data))

        # Given: Vampire attributes to create
        vampire_attrs = VampireAttributesCreate(
            clan_id="clan123",
            generation=10,
            sire="Ancient One",
            bane=NameDescriptionSubDocument(
                name="Rarefied Tastes",
                description="Feeds only on specific blood",
            ),
        )

        # When: Creating a character with vampire attributes
        result = await vclient.characters("user123", "campaign123", company_id="company123").create(
            character_class="VAMPIRE",
            game_version="V5",
            name_first="John",
            name_last="Doe",
            vampire_attributes=vampire_attrs,
        )

        # Then: The route was called and character is returned
        assert route.called
        assert isinstance(result, Character)
        assert result.vampire_attributes is not None
        assert result.vampire_attributes.clan_name == "Ventrue"

        # Verify request body includes vampire_attributes
        import json

        body = json.loads(route.calls[0].request.content)
        assert "vampire_attributes" in body
        assert body["vampire_attributes"]["clan_id"] == "clan123"
        assert body["vampire_attributes"]["generation"] == 10
        assert body["vampire_attributes"]["sire"] == "Ancient One"
        assert body["vampire_attributes"]["bane"]["name"] == "Rarefied Tastes"

    @respx.mock
    async def test_create_character_with_werewolf_attributes(
        self, vclient, base_url, werewolf_character_response_data
    ) -> None:
        """Verify creating a character with werewolf attributes."""
        # Given: A mocked create endpoint
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTERS.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(201, json=werewolf_character_response_data))

        # Given: Werewolf attributes to create
        werewolf_attrs = WerewolfAttributesCreate(
            tribe_id="tribe123",
            auspice_id="auspice123",
            pack_name="Moon Runners",
        )

        # When: Creating a character with werewolf attributes
        result = await vclient.characters("user123", "campaign123", company_id="company123").create(
            character_class="WEREWOLF",
            game_version="V5",
            name_first="Wolf",
            name_last="Runner",
            werewolf_attributes=werewolf_attrs,
        )

        # Then: The route was called and character is returned
        assert route.called
        assert isinstance(result, Character)
        assert result.werewolf_attributes is not None
        assert result.werewolf_attributes.tribe_name == "Shadow Lords"
        assert result.werewolf_attributes.auspice_name == "Ahroun"

        # Verify request body includes werewolf_attributes
        import json

        body = json.loads(route.calls[0].request.content)
        assert "werewolf_attributes" in body
        assert body["werewolf_attributes"]["tribe_id"] == "tribe123"
        assert body["werewolf_attributes"]["auspice_id"] == "auspice123"
        assert body["werewolf_attributes"]["pack_name"] == "Moon Runners"

    @respx.mock
    async def test_create_character_with_hunter_attributes(
        self, vclient, base_url, hunter_character_response_data
    ) -> None:
        """Verify creating a character with hunter attributes."""
        # Given: A mocked create endpoint
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTERS.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(201, json=hunter_character_response_data))

        # Given: Hunter attributes to create
        hunter_attrs = HunterAttributesCreate(
            creed="Avenger",
        )

        # When: Creating a character with hunter attributes
        result = await vclient.characters("user123", "campaign123", company_id="company123").create(
            character_class="HUNTER",
            game_version="V5",
            name_first="John",
            name_last="Hunter",
            hunter_attributes=hunter_attrs,
        )

        # Then: The route was called and character is returned
        assert route.called
        assert isinstance(result, Character)
        assert result.hunter_attributes is not None
        assert result.hunter_attributes.creed == "Avenger"

        # Verify request body includes hunter_attributes
        import json

        body = json.loads(route.calls[0].request.content)
        assert "hunter_attributes" in body
        assert body["hunter_attributes"]["creed"] == "Avenger"

    @respx.mock
    async def test_create_character_with_traits(
        self, vclient, base_url, character_response_data
    ) -> None:
        """Verify creating a character with traits."""
        # Given: A mocked create endpoint
        response_data = {
            **character_response_data,
            "character_trait_ids": ["trait123", "trait456"],
        }
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTERS.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(201, json=response_data))

        # Given: Traits to assign
        from vclient.models.character_trait import CharacterCreateTraitAssign

        traits = [
            CharacterCreateTraitAssign(trait_id="trait123", value=3),
            CharacterCreateTraitAssign(trait_id="trait456", value=2),
        ]

        # When: Creating a character with traits
        result = await vclient.characters("user123", "campaign123", company_id="company123").create(
            character_class="VAMPIRE",
            game_version="V5",
            name_first="John",
            name_last="Doe",
            traits=traits,
        )

        # Then: The route was called and character is returned
        assert route.called
        assert isinstance(result, Character)
        assert len(result.character_trait_ids) == 2

        # Verify request body includes traits
        import json

        body = json.loads(route.calls[0].request.content)
        assert "traits" in body
        assert len(body["traits"]) == 2
        assert body["traits"][0]["trait_id"] == "trait123"
        assert body["traits"][0]["value"] == 3
        assert body["traits"][1]["trait_id"] == "trait456"
        assert body["traits"][1]["value"] == 2


class TestCharactersServiceUpdate:
    """Tests for CharactersService.update method."""

    @respx.mock
    async def test_update_character_name(self, vclient, base_url, character_response_data) -> None:
        """Verify updating a character's name."""
        # Given: A mocked update endpoint
        updated_data = {**character_response_data, "name_first": "Jane"}
        route = respx.patch(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json=updated_data))

        # When: Updating the character's name
        result = await vclient.characters("user123", "campaign123", company_id="company123").update(
            "char123", name_first="Jane"
        )

        # Then: The route was called and updated character is returned
        assert route.called
        assert isinstance(result, Character)
        assert result.name_first == "Jane"

        # Verify only name_first was in request body
        import json

        body = json.loads(route.calls[0].request.content)
        assert body == {"name_first": "Jane"}

    @respx.mock
    async def test_update_character_status(
        self, vclient, base_url, character_response_data
    ) -> None:
        """Verify updating a character's status to dead."""
        # Given: A mocked update endpoint
        updated_data = {
            **character_response_data,
            "status": "DEAD",
            "date_killed": "2024-06-15T10:00:00Z",
        }
        route = respx.patch(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json=updated_data))

        # When: Updating the character's status
        result = await vclient.characters("user123", "campaign123", company_id="company123").update(
            "char123", status="DEAD"
        )

        # Then: The route was called and updated character is returned
        assert route.called
        assert result.status == "DEAD"

    @respx.mock
    async def test_update_character_not_found(self, vclient, base_url) -> None:
        """Verify updating a non-existent character raises NotFoundError."""
        # Given: A mocked 404 response
        route = respx.patch(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='nonexistent')}"
        ).mock(
            return_value=Response(404, json={"detail": "Character not found", "status_code": 404})
        )

        # When/Then: Updating raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.characters("user123", "campaign123", company_id="company123").update(
                "nonexistent", name_first="Jane"
            )

        assert route.called

    @respx.mock
    async def test_update_character_vampire_attributes(
        self, vclient, base_url, character_response_data
    ) -> None:
        """Verify updating a character's vampire attributes."""
        # Given: A mocked update endpoint with updated vampire attributes
        updated_data = {
            **character_response_data,
            "vampire_attributes": {
                "clan_id": "clan456",
                "clan_name": "Toreador",
                "generation": 9,
                "sire": "New Sire",
                "bane": None,
                "compulsion": {"name": "Obsession", "description": "Cannot resist beauty"},
            },
        }
        route = respx.patch(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json=updated_data))

        # Given: Vampire attributes to update
        vampire_attrs = VampireAttributesUpdate(
            clan_id="clan456",
            generation=9,
            sire="New Sire",
            compulsion=NameDescriptionSubDocument(
                name="Obsession",
                description="Cannot resist beauty",
            ),
        )

        # When: Updating the character's vampire attributes
        result = await vclient.characters("user123", "campaign123", company_id="company123").update(
            "char123", vampire_attributes=vampire_attrs
        )

        # Then: The route was called and updated character is returned
        assert route.called
        assert isinstance(result, Character)
        assert result.vampire_attributes is not None
        assert result.vampire_attributes.clan_name == "Toreador"
        assert result.vampire_attributes.generation == 9
        assert result.vampire_attributes.sire == "New Sire"

        # Verify request body includes vampire_attributes
        import json

        body = json.loads(route.calls[0].request.content)
        assert "vampire_attributes" in body
        assert body["vampire_attributes"]["clan_id"] == "clan456"
        assert body["vampire_attributes"]["generation"] == 9
        assert body["vampire_attributes"]["sire"] == "New Sire"
        assert body["vampire_attributes"]["compulsion"]["name"] == "Obsession"

    @respx.mock
    async def test_update_character_werewolf_attributes(
        self, vclient, base_url, werewolf_character_response_data
    ) -> None:
        """Verify updating a character's werewolf attributes."""
        # Given: A mocked update endpoint with updated werewolf attributes
        updated_data = {
            **werewolf_character_response_data,
            "werewolf_attributes": {
                "tribe_id": "tribe456",
                "tribe_name": "Silver Fangs",
                "auspice_id": "auspice456",
                "auspice_name": "Galliard",
                "pack_name": "Star Gazers",
            },
        }
        route = respx.patch(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char456')}"
        ).mock(return_value=Response(200, json=updated_data))

        # Given: Werewolf attributes to update
        werewolf_attrs = WerewolfAttributesUpdate(
            tribe_id="tribe456",
            auspice_id="auspice456",
            pack_name="Star Gazers",
        )

        # When: Updating the character's werewolf attributes
        result = await vclient.characters("user123", "campaign123", company_id="company123").update(
            "char456", werewolf_attributes=werewolf_attrs
        )

        # Then: The route was called and updated character is returned
        assert route.called
        assert isinstance(result, Character)
        assert result.werewolf_attributes is not None
        assert result.werewolf_attributes.tribe_name == "Silver Fangs"
        assert result.werewolf_attributes.auspice_name == "Galliard"
        assert result.werewolf_attributes.pack_name == "Star Gazers"

        # Verify request body includes werewolf_attributes
        import json

        body = json.loads(route.calls[0].request.content)
        assert "werewolf_attributes" in body
        assert body["werewolf_attributes"]["tribe_id"] == "tribe456"
        assert body["werewolf_attributes"]["auspice_id"] == "auspice456"
        assert body["werewolf_attributes"]["pack_name"] == "Star Gazers"

    @respx.mock
    async def test_update_character_hunter_attributes(
        self, vclient, base_url, hunter_character_response_data
    ) -> None:
        """Verify updating a character's hunter attributes."""
        # Given: A mocked update endpoint with updated hunter attributes
        updated_data = {
            **hunter_character_response_data,
            "hunter_attributes": {
                "creed": "Defender",
            },
        }
        route = respx.patch(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char789')}"
        ).mock(return_value=Response(200, json=updated_data))

        # Given: Hunter attributes to update
        hunter_attrs = HunterAttributesUpdate(
            creed="Defender",
        )

        # When: Updating the character's hunter attributes
        result = await vclient.characters("user123", "campaign123", company_id="company123").update(
            "char789", hunter_attributes=hunter_attrs
        )

        # Then: The route was called and updated character is returned
        assert route.called
        assert isinstance(result, Character)
        assert result.hunter_attributes is not None
        assert result.hunter_attributes.creed == "Defender"

        # Verify request body includes hunter_attributes
        import json

        body = json.loads(route.calls[0].request.content)
        assert "hunter_attributes" in body
        assert body["hunter_attributes"]["creed"] == "Defender"


class TestCharactersServiceDelete:
    """Tests for CharactersService.delete method."""

    @respx.mock
    async def test_delete_character(self, vclient, base_url) -> None:
        """Verify deleting a character."""
        # Given: A mocked delete endpoint
        route = respx.delete(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(204))

        # When: Deleting the character
        result = await vclient.characters("user123", "campaign123", company_id="company123").delete(
            "char123"
        )

        # Then: The route was called and None is returned
        assert route.called
        assert result is None

    @respx.mock
    async def test_delete_character_not_found(self, vclient, base_url) -> None:
        """Verify deleting a non-existent character raises NotFoundError."""
        # Given: A mocked 404 response
        route = respx.delete(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='nonexistent')}"
        ).mock(
            return_value=Response(404, json={"detail": "Character not found", "status_code": 404})
        )

        # When/Then: Deleting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.characters("user123", "campaign123", company_id="company123").delete(
                "nonexistent"
            )

        assert route.called


class TestCharactersServiceListAll:
    """Tests for CharactersService.list_all method."""

    @respx.mock
    async def test_list_all_characters(self, vclient, base_url, character_response_data) -> None:
        """Verify list_all returns all characters across pages."""
        # Given: A mocked endpoint that returns paginated results
        paginated_response = {
            "items": [character_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTERS.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all characters
        result = await vclient.characters(
            "user123", "campaign123", company_id="company123"
        ).list_all()

        # Then: All characters are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], Character)
        assert result[0].name_first == "John"


class TestCharactersServiceIterAll:
    """Tests for CharactersService.iter_all method."""

    @respx.mock
    async def test_iter_all_characters(self, vclient, base_url, character_response_data) -> None:
        """Verify iter_all yields characters across pages."""
        # Given: A mocked endpoint
        paginated_response = {
            "items": [character_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTERS.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all characters
        characters = [
            character
            async for character in vclient.characters(
                "user123", "campaign123", company_id="company123"
            ).iter_all()
        ]

        # Then: All characters are yielded
        assert route.called
        assert len(characters) == 1
        assert isinstance(characters[0], Character)


class TestCharactersServiceVampireAttributes:
    """Tests for character vampire attributes handling."""

    @respx.mock
    async def test_get_character_with_vampire_attributes(
        self, vclient, base_url, character_response_data
    ) -> None:
        """Verify vampire attributes are properly parsed."""
        # Given: A mocked character endpoint
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json=character_response_data))

        # When: Requesting the character
        result = await vclient.characters("user123", "campaign123", company_id="company123").get(
            "char123"
        )

        # Then: Vampire attributes are properly parsed
        assert route.called
        assert result.vampire_attributes is not None
        assert result.vampire_attributes.clan_name == "Ventrue"
        assert result.vampire_attributes.generation == 10
        assert result.vampire_attributes.sire == "Ancient One"


class TestCharactersServiceAssets:
    """Tests for CharactersService asset methods."""

    @respx.mock
    async def test_get_assets_page(self, vclient, base_url, asset_response_data):
        """Verify getting a page of character assets."""
        # Given: A mocked assets endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_ASSETS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id='char123')}",
            params={"limit": "10", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [asset_response_data],
                "limit": 10,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Getting a page of assets
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).get_assets_page("char123")

        # Then: Returns paginated Asset objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Asset)

    @respx.mock
    async def test_list_all_assets(self, vclient, base_url, asset_response_data):
        """Verify list_all_assets returns all assets."""
        # Given: A mocked assets endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        character_id = "character123"
        respx.get(
            f"{base_url}{Endpoints.CHARACTER_ASSETS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id)}",
            params={"limit": "100", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [asset_response_data],
                "limit": 100,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Calling list_all_assets
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).list_all_assets(character_id)

        # Then: Returns list of Asset objects
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Asset)

    @respx.mock
    async def test_get_asset(self, vclient, base_url, asset_response_data):
        """Verify getting a specific asset."""
        # Given: A mocked asset endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        asset_id = "asset123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_ASSET.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id='char123', asset_id=asset_id)}"
        ).respond(200, json=asset_response_data)

        # When: Getting the asset
        result = await vclient.characters(user_id, campaign_id, company_id=company_id).get_asset(
            "char123", asset_id
        )

        # Then: Returns Asset object
        assert route.called
        assert isinstance(result, Asset)
        assert result.id == "asset123"

    @respx.mock
    async def test_delete_asset(self, vclient, base_url):
        """Verify deleting an asset."""
        # Given: A mocked delete endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        asset_id = "asset123"
        route = respx.delete(
            f"{base_url}{Endpoints.CHARACTER_ASSET.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id='char123', asset_id=asset_id)}"
        ).respond(204)

        # When: Deleting the asset
        await vclient.characters(user_id, campaign_id, company_id=company_id).delete_asset(
            "char123", asset_id
        )

        # Then: Request was made
        assert route.called

    @respx.mock
    async def test_upload_asset(self, vclient, base_url, asset_response_data):
        """Verify uploading an asset."""
        # Given: A mocked upload endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_ASSET_UPLOAD.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id='char123')}"
        ).respond(201, json=asset_response_data)

        # When: Uploading an asset
        result = await vclient.characters(user_id, campaign_id, company_id=company_id).upload_asset(
            "char123",
            filename="test.png",
            content=b"test content",
            content_type="image/png",
        )

        # Then: Returns Asset object
        assert route.called
        assert isinstance(result, Asset)
        assert result.id == "asset123"


class TestCharactersServiceNotes:
    """Tests for CharactersService note methods."""

    @respx.mock
    async def test_get_notes_page(self, vclient, base_url, note_response_data):
        """Verify getting a page of notes."""
        # Given: A mocked notes endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_NOTES.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id='char123')}",
            params={"limit": "10", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [note_response_data],
                "limit": 10,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Getting a page of notes
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).get_notes_page("char123")

        # Then: Returns paginated Note objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Note)

    @respx.mock
    async def test_get_note(self, vclient, base_url, note_response_data):
        """Verify getting a specific note."""
        # Given: A mocked note endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        note_id = "note123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_NOTE.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id='char123', note_id=note_id)}"
        ).respond(200, json=note_response_data)

        # When: Getting the note
        result = await vclient.characters(user_id, campaign_id, company_id=company_id).get_note(
            "char123", note_id
        )

        # Then: Returns Note object
        assert route.called
        assert isinstance(result, Note)
        assert result.id == "note123"
        assert result.title == "Test Note"

    @respx.mock
    async def test_create_note(self, vclient, base_url, note_response_data):
        """Verify creating a note."""
        # Given: A mocked create endpoint
        company_id = "company123"
        user_id = "user123"
        character_id = "char123"
        campaign_id = "campaign123"
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_NOTES.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id)}"
        ).respond(201, json=note_response_data)

        # When: Creating a note
        result = await vclient.characters(user_id, campaign_id, company_id=company_id).create_note(
            character_id, title="Test Note", content="This is test content"
        )

        # Then: Returns Note object
        assert route.called
        assert isinstance(result, Note)
        assert result.title == "Test Note"

    @respx.mock
    async def test_update_note(self, vclient, base_url, note_response_data):
        """Verify updating a note."""
        # Given: A mocked update endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        character_id = "char123"
        note_id = "note123"
        updated_data = {**note_response_data, "title": "Updated Title"}
        route = respx.patch(
            f"{base_url}{Endpoints.CHARACTER_NOTE.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id, note_id=note_id)}"
        ).respond(200, json=updated_data)

        # When: Updating the note
        result = await vclient.characters(user_id, campaign_id, company_id=company_id).update_note(
            character_id, note_id, title="Updated Title"
        )

        # Then: Returns updated Note object
        assert route.called
        assert isinstance(result, Note)
        assert result.title == "Updated Title"

    @respx.mock
    async def test_delete_note(self, vclient, base_url):
        """Verify deleting a note."""
        # Given: A mocked delete endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        note_id = "note123"
        route = respx.delete(
            f"{base_url}{Endpoints.CHARACTER_NOTE.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id='char123', note_id=note_id)}"
        ).respond(204)

        # When: Deleting the note
        await vclient.characters(user_id, campaign_id, company_id=company_id).delete_note(
            "char123", note_id
        )

        # Then: Request was made
        assert route.called


class TestCharactersServiceGetStatistics:
    """Tests for CharactersService.get_statistics method."""

    @respx.mock
    async def test_get_statistics(self, vclient, base_url, statistics_response_data):
        """Verify getting character statistics."""
        # Given: A mocked statistics endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "507f1f77bcf86cd799439011"
        character_id = "char123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_STATISTICS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id)}",
            params={"num_top_traits": "5"},
        ).respond(200, json=statistics_response_data)

        # When: Getting statistics
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).get_statistics(character_id)

        # Then: Returns RollStatistics object
        assert route.called
        assert isinstance(result, RollStatistics)
        assert result.total_rolls == 100
        assert result.success_percentage == 50.0


class TestCharactersServiceGetFullSheet:
    """Tests for CharactersService.get_full_sheet method."""

    @respx.mock
    async def test_get_full_sheet(self, vclient, base_url, full_sheet_response_data):
        """Verify getting character full sheet."""
        # Given: A mocked full sheet endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "507f1f77bcf86cd799439011"
        character_id = "char123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_FULL_SHEET.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id)}",
        ).respond(200, json=full_sheet_response_data)

        # When: Getting the full sheet
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).get_full_sheet(character_id)

        # Then: Returns CharacterFullSheet with correct hierarchy
        assert route.called
        assert isinstance(result, CharacterFullSheet)
        assert result.character.name_first == "Marcus"
        assert len(result.sections) == 1
        assert result.sections[0].name == "Physical"
        assert result.sections[0].categories[0].character_traits[0].value == 3

    @respx.mock
    async def test_get_full_sheet_with_available_traits(
        self, vclient, base_url, full_sheet_response_data_with_available_traits
    ):
        """Verify getting full sheet with include_available_traits param."""
        # Given: A mocked full sheet endpoint expecting the query param
        company_id = "company123"
        user_id = "user123"
        campaign_id = "507f1f77bcf86cd799439011"
        character_id = "char123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_FULL_SHEET.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id)}",
            params={"include_available_traits": "true"},
        ).respond(200, json=full_sheet_response_data_with_available_traits)

        # When: Getting the full sheet with include_available_traits=True
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).get_full_sheet(character_id, include_available_traits=True)

        # Then: Returns CharacterFullSheet with available_traits populated
        assert route.called
        assert isinstance(result, CharacterFullSheet)
        assert len(result.sections[0].categories[0].available_traits) == 1
        assert result.sections[0].categories[0].available_traits[0].name == "Dexterity"


class TestCharactersServiceGetFullSheetCategory:
    """Tests for CharactersService.get_full_sheet_category method."""

    @respx.mock
    async def test_get_full_sheet_category(
        self, vclient, base_url, full_sheet_category_response_data
    ):
        """Verify getting a single category from the full sheet."""
        # Given: A mocked category endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "507f1f77bcf86cd799439011"
        character_id = "char123"
        category_id = "cat1"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_FULL_SHEET_CATEGORY.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id, category_id=category_id)}",
        ).respond(200, json=full_sheet_category_response_data)

        # When: Getting a single category
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).get_full_sheet_category(character_id, category_id)

        # Then: Returns FullSheetTraitCategory with correct data
        assert route.called
        assert isinstance(result, FullSheetTraitCategory)
        assert result.id == "cat1"
        assert result.name == "Attributes"
        assert len(result.character_traits) == 1
        assert result.character_traits[0].value == 3

    @respx.mock
    async def test_get_full_sheet_category_with_available_traits(
        self, vclient, base_url, full_sheet_category_response_data_with_available_traits
    ):
        """Verify getting a category with available traits."""
        # Given: A mocked category endpoint expecting the query param
        company_id = "company123"
        user_id = "user123"
        campaign_id = "507f1f77bcf86cd799439011"
        character_id = "char123"
        category_id = "cat1"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_FULL_SHEET_CATEGORY.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id, category_id=category_id)}",
            params={"include_available_traits": "true"},
        ).respond(200, json=full_sheet_category_response_data_with_available_traits)

        # When: Getting a category with available traits
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).get_full_sheet_category(character_id, category_id, include_available_traits=True)

        # Then: Returns category with available_traits populated
        assert route.called
        assert isinstance(result, FullSheetTraitCategory)
        assert len(result.available_traits) == 1
        assert result.available_traits[0].name == "Dexterity"


class TestCharactersServiceInventory:
    """Tests for CharactersService inventory methods."""

    @respx.mock
    async def test_get_inventory_page(self, vclient, base_url, inventory_item_response_data):
        """Verify getting a page of inventory items."""
        # Given: A mocked inventory endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        character_id = "char123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_INVENTORY.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id)}",
            params={"limit": "10", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [inventory_item_response_data],
                "limit": 10,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Getting a page of inventory items
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).get_inventory_page(character_id)

        # Then: Returns paginated InventoryItem objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], InventoryItem)
        assert result.items[0].name == "Test Item"
        assert result.items[0].type == "BOOK"
        assert result.items[0].description == "This is test content"
        assert result.items[0].character_id == "char123"
        assert result.items[0].date_created == datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        assert result.items[0].date_modified == datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)

    @respx.mock
    async def test_list_all_inventory(self, vclient, base_url, inventory_item_response_data):
        """Verify listing all inventory items."""
        # Given: A mocked inventory endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        character_id = "char123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_INVENTORY.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id)}",
        ).respond(
            200,
            json={"items": [inventory_item_response_data], "total": 1, "limit": 100, "offset": 0},
        )

        # When: Listing all inventory items
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).list_all_inventory(character_id)

        # Then: Returns list of InventoryItem objects
        assert route.called
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], InventoryItem)
        assert result[0].name == "Test Item"

    @respx.mock
    async def test_iter_all_inventory(self, vclient, base_url, inventory_item_response_data):
        """Verify iterating through all inventory items."""
        # Given: A mocked inventory endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        character_id = "char123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_INVENTORY.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id)}",
        ).respond(
            200,
            json={"items": [inventory_item_response_data], "total": 1, "limit": 100, "offset": 0},
        )
        # When: Iterating through all inventory items
        result = [
            item
            async for item in vclient.characters(
                user_id=user_id, campaign_id=campaign_id, company_id=company_id
            ).iter_all_inventory(character_id)
        ]

        # Then: Returns list of InventoryItem objects
        assert route.called
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], InventoryItem)
        assert result[0].name == "Test Item"

    @respx.mock
    async def test_get_inventory_item(self, vclient, base_url, inventory_item_response_data):
        """Verify getting a specific inventory item."""
        # Given: A mocked inventory item endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        character_id = "char123"
        item_id = "item123"
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_INVENTORY_ITEM.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id, item_id=item_id)}"
        ).respond(200, json=inventory_item_response_data)
        # When: Getting the inventory item
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).get_inventory_item(character_id, item_id)

        # Then: Returns InventoryItem object
        assert route.called
        assert isinstance(result, InventoryItem)
        assert result.name == "Test Item"
        assert result.type == "BOOK"
        assert result.description == "This is test content"
        assert result.character_id == "char123"

    @respx.mock
    async def test_create_inventory_item(self, vclient, base_url, inventory_item_response_data):
        """Verify creating a new inventory item."""
        # Given: A mocked create endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        character_id = "char123"
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_INVENTORY.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id)}"
        ).respond(201, json=inventory_item_response_data)
        # When: Creating the inventory item
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).create_inventory_item(
            character_id, name="Test Item", type="BOOK", description="This is test content"
        )

        # Then: Returns InventoryItem object
        assert route.called
        assert isinstance(result, InventoryItem)
        assert result.name == "Test Item"
        assert result.type == "BOOK"
        assert result.description == "This is test content"
        assert result.character_id == "char123"

    @respx.mock
    async def test_update_inventory_item(self, vclient, base_url, inventory_item_response_data):
        """Verify updating an inventory item."""
        # Given: A mocked update endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        character_id = "char123"
        item_id = "item123"
        updated_data = {**inventory_item_response_data, "name": "Updated Item"}
        route = respx.patch(
            f"{base_url}{Endpoints.CHARACTER_INVENTORY_ITEM.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id, item_id=item_id)}"
        ).respond(200, json=updated_data)

        # When: Updating the inventory item
        result = await vclient.characters(
            user_id, campaign_id, company_id=company_id
        ).update_inventory_item(character_id, item_id, name="Updated Item")

        # Then: Returns InventoryItem object
        assert route.called
        assert isinstance(result, InventoryItem)
        assert result.name == "Updated Item"
        assert result.type == "BOOK"
        assert result.description == "This is test content"
        assert result.character_id == "char123"

    @respx.mock
    async def test_delete_inventory_item(self, vclient, base_url):
        """Verify deleting an inventory item."""
        # Given: A mocked delete endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        character_id = "char123"
        item_id = "item123"
        route = respx.delete(
            f"{base_url}{Endpoints.CHARACTER_INVENTORY_ITEM.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, character_id=character_id, item_id=item_id)}"
        ).respond(204)

        # When: Deleting the inventory item
        await vclient.characters(user_id, campaign_id, company_id=company_id).delete_inventory_item(
            character_id, item_id
        )

        # Then: Request was made
        assert route.called
