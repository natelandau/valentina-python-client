"""Integration tests for CharacterBlueprintService."""

import pytest
import respx
from httpx import Response

from vclient.endpoints import Endpoints
from vclient.exceptions import NotFoundError
from vclient.models import (
    CharacterConcept,
    PaginatedResponse,
    SheetSection,
    Trait,
    TraitCategory,
    TraitSubcategory,
    VampireClan,
    WerewolfAuspice,
    WerewolfTribe,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def section_response_data() -> dict:
    """Return sample character blueprint section response data."""
    return {
        "id": "section123",
        "name": "Attributes",
        "description": "Physical, Social, and Mental attributes",
        "character_classes": ["VAMPIRE", "WEREWOLF"],
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "game_versions": ["V5"],
        "show_when_empty": True,
        "order": 1,
    }


@pytest.fixture
def paginated_section_response(section_response_data: dict) -> dict:
    """Return a paginated response with sections."""
    return {
        "items": [section_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def category_response_data() -> dict:
    """Return sample character blueprint category response data."""
    return {
        "id": "category123",
        "name": "Physical",
        "description": "Physical attributes",
        "character_classes": ["VAMPIRE", "WEREWOLF"],
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "game_versions": ["V5"],
        "parent_sheet_section_id": "section123",
        "initial_cost": 1,
        "upgrade_cost": 5,
        "order": 1,
        "show_when_empty": True,
    }


@pytest.fixture
def paginated_category_response(category_response_data: dict) -> dict:
    """Return a paginated response with categories."""
    return {
        "items": [category_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def subcategory_response_data() -> dict:
    """Return sample character blueprint subcategory response data."""
    return {
        "id": "subcat123",
        "name": "Allies",
        "description": "People who support the character",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "game_versions": ["V5"],
        "character_classes": ["VAMPIRE", "WEREWOLF"],
        "show_when_empty": True,
        "initial_cost": 1,
        "upgrade_cost": 2,
        "requires_parent": False,
        "pool": None,
        "system": None,
        "parent_category_id": "category123",
        "parent_category_name": "Backgrounds",
    }


@pytest.fixture
def paginated_subcategory_response(subcategory_response_data: dict) -> dict:
    """Return a paginated response with subcategories."""
    return {
        "items": [subcategory_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def trait_response_data() -> dict:
    """Return sample trait response data."""
    return {
        "id": "trait123",
        "name": "Strength",
        "description": "Physical power and might",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "link": "https://example.com/strength",
        "show_when_zero": True,
        "max_value": 5,
        "min_value": 0,
        "is_custom": False,
        "initial_cost": 1,
        "upgrade_cost": 5,
        "sheet_section_name": "Attributes",
        "sheet_section_id": "section123",
        "parent_category_name": "Physical",
        "parent_category_id": "category123",
        "custom_for_character_id": None,
        "trait_subcategory_id": None,
        "trait_subcategory_name": None,
        "pool": None,
        "system": None,
        "character_classes": ["VAMPIRE", "WEREWOLF"],
        "game_versions": ["V5"],
    }


@pytest.fixture
def paginated_trait_response(trait_response_data: dict) -> dict:
    """Return a paginated response with traits."""
    return {
        "items": [trait_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def character_concept_response_data() -> dict:
    """Return sample character concept response data."""
    return {
        "id": "concept123",
        "name": "Physical",
        "description": "Physical attributes",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "examples": ["Example 1", "Example 2"],
        "max_specialties": 1,
        "specialties": [
            {
                "id": "spec1",
                "name": "Brawl: Kindred",
                "type": "ACTION",
                "description": "Skilled in fighting other Kindred",
            }
        ],
        "favored_ability_names": ["Ability 1", "Ability 2"],
    }


@pytest.fixture
def paginated_character_concept_response(character_concept_response_data: dict) -> dict:
    """Return a paginated response with character concepts."""
    return {
        "items": [character_concept_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def vampire_clan_response_data() -> dict:
    """Return sample vampire clan response data."""
    return {
        "id": "clan123",
        "name": "Clan Name",
        "description": "Clan description",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "game_versions": ["V5"],
        "discipline_ids": ["discipline123", "discipline456"],
        "bane": {"name": "Rarefied Tastes", "description": "Feeds only on specific blood"},
        "variant_bane": {"name": "Rarefied Tastes", "description": "Feeds only on specific blood"},
        "compulsion": {"name": "Rarefied Tastes", "description": "Feeds only on specific blood"},
        "link": "https://example.com/clan123",
    }


@pytest.fixture
def paginated_vampire_clan_response(vampire_clan_response_data: dict) -> dict:
    """Return a paginated response with vampire clans."""
    return {
        "items": [vampire_clan_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def werewolf_auspice_response_data() -> dict:
    """Return sample werewolf auspice response data."""
    return {
        "id": "auspice123",
        "name": "Auspice Name",
        "description": "Auspice description",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "game_versions": ["V5"],
        "gift_trait_ids": ["gift123", "gift456"],
        "link": "https://example.com/auspice123",
    }


@pytest.fixture
def paginated_werewolf_auspice_response(werewolf_auspice_response_data: dict) -> dict:
    """Return a paginated response with werewolf auspices."""
    return {
        "items": [werewolf_auspice_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def werewolf_tribe_response_data() -> dict:
    """Return sample werewolf tribe response data."""
    return {
        "id": "tribe123",
        "name": "Tribe Name",
        "description": "Tribe description",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "game_versions": ["V5"],
        "renown": "HONOR",
        "patron_spirit": "Spirit Name",
        "favor": "Favor Name",
        "ban": "Ban Name",
        "gift_trait_ids": ["gift123", "gift456"],
        "link": "https://example.com/tribe123",
    }


@pytest.fixture
def paginated_werewolf_tribe_response(werewolf_tribe_response_data: dict) -> dict:
    """Return a paginated response with werewolf tribes."""
    return {
        "items": [werewolf_tribe_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


class TestCharacterBlueprintServiceSections:
    """Tests for CharacterBlueprintService section methods."""

    @respx.mock
    async def test_get_sections_page(self, vclient, base_url, paginated_section_response) -> None:
        """Verify getting a page of character blueprint sections."""
        # Given: A mocked sections endpoint
        company_id = "company123"
        game_version = "V5"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SECTIONS.format(company_id=company_id, game_version=game_version)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_section_response))

        # When: Requesting a page of sections
        result = await vclient.character_blueprint(company_id).get_sections_page(game_version)

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], SheetSection)
        assert result.items[0].name == "Attributes"
        assert result.total == 1

    @respx.mock
    async def test_get_sections_page_with_character_class_filter(
        self, vclient, base_url, paginated_section_response
    ) -> None:
        """Verify get_sections_page passes character_class filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        game_version = "V5"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SECTIONS.format(company_id=company_id, game_version=game_version)}",
            params={"limit": "10", "offset": "0", "character_class": "VAMPIRE"},
        ).mock(return_value=Response(200, json=paginated_section_response))

        # When: Requesting with character_class filter
        result = await vclient.character_blueprint(company_id).get_sections_page(
            game_version, character_class="VAMPIRE"
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_list_all_sections(self, vclient, base_url, section_response_data) -> None:
        """Verify list_all_sections returns all sections across pages."""
        # Given: A mocked endpoint that returns paginated results
        company_id = "company123"
        game_version = "V5"
        paginated_response = {
            "items": [section_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SECTIONS.format(company_id=company_id, game_version=game_version)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all sections
        result = await vclient.character_blueprint(company_id).list_all_sections(
            game_version=game_version
        )

        # Then: All sections are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], SheetSection)
        assert result[0].name == "Attributes"

    @respx.mock
    async def test_iter_all_sections(self, vclient, base_url, section_response_data) -> None:
        """Verify iter_all_sections yields sections across pages."""
        # Given: A mocked endpoint
        company_id = "company123"
        game_version = "V5"
        paginated_response = {
            "items": [section_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SECTIONS.format(company_id=company_id, game_version=game_version)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all sections
        sections = [
            section
            async for section in vclient.character_blueprint(company_id).iter_all_sections(
                game_version=game_version
            )
        ]

        # Then: All sections are yielded
        assert route.called
        assert len(sections) == 1
        assert isinstance(sections[0], SheetSection)

    @respx.mock
    async def test_get_section(self, vclient, base_url, section_response_data) -> None:
        """Verify getting a section by ID returns SheetSection object."""
        # Given: A mocked section endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SECTION_DETAIL.format(company_id=company_id, game_version=game_version, section_id=section_id)}"
        ).mock(return_value=Response(200, json=section_response_data))

        # When: Requesting a section
        result = await vclient.character_blueprint(company_id).get_section(
            game_version=game_version, section_id=section_id
        )

        # Then: The route was called and section is returned
        assert route.called
        assert isinstance(result, SheetSection)
        assert result.id == "section123"
        assert result.name == "Attributes"
        assert result.game_versions == ["V5"]
        assert result.order == 1

    @respx.mock
    async def test_get_section_not_found(self, vclient, base_url) -> None:
        """Verify getting a non-existent section raises NotFoundError."""
        # Given: A mocked 404 response
        company_id = "company123"
        game_version = "V5"
        section_id = "nonexistent"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SECTION_DETAIL.format(company_id=company_id, game_version=game_version, section_id=section_id)}"
        ).mock(return_value=Response(404, json={"detail": "Section not found", "status_code": 404}))

        # When/Then: Requesting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_blueprint(company_id).get_section(
                game_version=game_version, section_id=section_id
            )

        assert route.called


class TestCharacterBlueprintServiceCategories:
    """Tests for CharacterBlueprintService category methods."""

    @respx.mock
    async def test_get_categories_page(
        self, vclient, base_url, paginated_category_response
    ) -> None:
        """Verify getting a page of character blueprint categories."""
        # Given: A mocked categories endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORIES.format(company_id=company_id, game_version=game_version, section_id=section_id)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_category_response))

        # When: Requesting a page of categories
        result = await vclient.character_blueprint(company_id).get_categories_page(
            game_version=game_version, section_id=section_id
        )

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], TraitCategory)
        assert result.items[0].name == "Physical"
        assert result.total == 1

    @respx.mock
    async def test_get_categories_page_with_character_class_filter(
        self, vclient, base_url, paginated_category_response
    ) -> None:
        """Verify get_categories_page passes character_class filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORIES.format(company_id=company_id, game_version=game_version, section_id=section_id)}",
            params={"limit": "10", "offset": "0", "character_class": "VAMPIRE"},
        ).mock(return_value=Response(200, json=paginated_category_response))

        # When: Requesting with character_class filter
        result = await vclient.character_blueprint(company_id).get_categories_page(
            game_version=game_version, section_id=section_id, character_class="VAMPIRE"
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_list_all_categories(self, vclient, base_url, category_response_data) -> None:
        """Verify list_all_categories returns all categories across pages."""
        # Given: A mocked endpoint that returns paginated results
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        paginated_response = {
            "items": [category_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORIES.format(company_id=company_id, game_version=game_version, section_id=section_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all categories
        result = await vclient.character_blueprint(company_id).list_all_categories(
            game_version=game_version, section_id=section_id
        )

        # Then: All categories are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], TraitCategory)
        assert result[0].name == "Physical"

    @respx.mock
    async def test_iter_all_categories(self, vclient, base_url, category_response_data) -> None:
        """Verify iter_all_categories yields categories across pages."""
        # Given: A mocked endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        paginated_response = {
            "items": [category_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORIES.format(company_id=company_id, game_version=game_version, section_id=section_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all categories
        categories = [
            category
            async for category in vclient.character_blueprint(company_id).iter_all_categories(
                game_version=game_version, section_id=section_id
            )
        ]

        # Then: All categories are yielded
        assert route.called
        assert len(categories) == 1
        assert isinstance(categories[0], TraitCategory)

    @respx.mock
    async def test_get_category(self, vclient, base_url, category_response_data) -> None:
        """Verify getting a category by ID returns TraitCategory object."""
        # Given: A mocked category endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_DETAIL.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}"
        ).mock(return_value=Response(200, json=category_response_data))

        # When: Requesting a category
        result = await vclient.character_blueprint(company_id).get_category(
            game_version=game_version, section_id=section_id, category_id=category_id
        )

        # Then: The route was called and category is returned
        assert route.called
        assert isinstance(result, TraitCategory)
        assert result.id == "category123"
        assert result.name == "Physical"
        assert result.parent_sheet_section_id == "section123"
        assert result.initial_cost == 1
        assert result.upgrade_cost == 5

    @respx.mock
    async def test_get_category_not_found(self, vclient, base_url) -> None:
        """Verify getting a non-existent category raises NotFoundError."""
        # Given: A mocked 404 response
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "nonexistent"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_DETAIL.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}"
        ).mock(
            return_value=Response(404, json={"detail": "Category not found", "status_code": 404})
        )

        # When/Then: Requesting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_blueprint(company_id).get_category(
                game_version=game_version, section_id=section_id, category_id=category_id
            )

        assert route.called


class TestCharacterBlueprintServiceCategoryTraits:
    """Tests for CharacterBlueprintService trait methods."""

    @respx.mock
    async def test_get_category_traits_page(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify getting a page of character blueprint category traits."""
        # Given: A mocked traits endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting a page of traits
        result = await vclient.character_blueprint(company_id).get_category_traits_page(
            game_version=game_version, section_id=section_id, category_id=category_id
        )

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Trait)
        assert result.items[0].name == "Strength"
        assert result.total == 1

    @respx.mock
    async def test_get_category_traits_page_with_filters(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify get_category_traits_page passes filter parameters correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}",
            params={
                "limit": "10",
                "offset": "0",
                "character_class": "VAMPIRE",
                "character_id": "char123",
            },
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting with filters
        result = await vclient.character_blueprint(company_id).get_category_traits_page(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
            character_class="VAMPIRE",
            character_id="char123",
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_list_all_category_traits(self, vclient, base_url, trait_response_data) -> None:
        """Verify list_all_category_traits returns all category traits across pages."""
        # Given: A mocked endpoint that returns paginated results
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        paginated_response = {
            "items": [trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all traits
        result = await vclient.character_blueprint(company_id).list_all_category_traits(
            game_version=game_version, section_id=section_id, category_id=category_id
        )

        # Then: All traits are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], Trait)
        assert result[0].name == "Strength"

    @respx.mock
    async def test_iter_all_category_traits(self, vclient, base_url, trait_response_data) -> None:
        """Verify iter_all_category_traits yields category traits across pages."""
        # Given: A mocked endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        paginated_response = {
            "items": [trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all traits
        traits = [
            trait
            async for trait in vclient.character_blueprint(company_id).iter_all_category_traits(
                game_version=game_version, section_id=section_id, category_id=category_id
            )
        ]

        # Then: All traits are yielded
        assert route.called
        assert len(traits) == 1
        assert isinstance(traits[0], Trait)

    @respx.mock
    async def test_get_category_traits_page_with_is_rollable_filter(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify get_category_traits_page passes is_rollable filter correctly."""
        # Given: A mocked endpoint expecting is_rollable param
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}",
            params={"limit": "10", "offset": "0", "is_rollable": "true"},
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting with is_rollable filter
        result = await vclient.character_blueprint(company_id).get_category_traits_page(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
            is_rollable=True,
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_get_category_traits_page_with_is_rollable_false(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify get_category_traits_page passes is_rollable=False filter correctly."""
        # Given: A mocked endpoint expecting is_rollable=False param
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}",
            params={"limit": "10", "offset": "0", "is_rollable": "false"},
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting with is_rollable=False filter
        result = await vclient.character_blueprint(company_id).get_category_traits_page(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
            is_rollable=False,
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_get_category_traits_page_exclude_subcategory_traits(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify exclude_subcategory_traits=True sends the query parameter."""
        # Given: A mocked endpoint expecting the exclude param
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}",
            params={"limit": "10", "offset": "0", "exclude_subcategory_traits": "true"},
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting with exclude_subcategory_traits=True
        result = await vclient.character_blueprint(company_id).get_category_traits_page(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
            exclude_subcategory_traits=True,
        )

        # Then: The route was called with the parameter
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_get_category_traits_page_exclude_subcategory_traits_default(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify exclude_subcategory_traits=False does not send the query parameter."""
        # Given: A mocked endpoint expecting no exclude param
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting with default exclude_subcategory_traits (False)
        result = await vclient.character_blueprint(company_id).get_category_traits_page(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
        )

        # Then: The route was called without the exclude parameter
        assert route.called
        assert len(result.items) == 1


class TestCharacterBlueprintServiceSubcategories:
    """Tests for CharacterBlueprintService subcategory methods."""

    @respx.mock
    async def test_get_subcategories_page(
        self, vclient, base_url, paginated_subcategory_response
    ) -> None:
        """Verify getting a page of character blueprint subcategories."""
        # Given: A mocked subcategories endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_SUBCATEGORIES.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_subcategory_response))

        # When: Requesting a page of subcategories
        result = await vclient.character_blueprint(company_id).get_subcategories_page(
            game_version=game_version, section_id=section_id, category_id=category_id
        )

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], TraitSubcategory)
        assert result.items[0].name == "Allies"
        assert result.total == 1

    @respx.mock
    async def test_get_subcategories_page_with_character_class_filter(
        self, vclient, base_url, paginated_subcategory_response
    ) -> None:
        """Verify get_subcategories_page passes character_class filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_SUBCATEGORIES.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}",
            params={"limit": "10", "offset": "0", "character_class": "VAMPIRE"},
        ).mock(return_value=Response(200, json=paginated_subcategory_response))

        # When: Requesting with character_class filter
        result = await vclient.character_blueprint(company_id).get_subcategories_page(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
            character_class="VAMPIRE",
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_list_all_subcategories(
        self, vclient, base_url, subcategory_response_data
    ) -> None:
        """Verify list_all_subcategories returns all subcategories across pages."""
        # Given: A mocked endpoint that returns paginated results
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        paginated_response = {
            "items": [subcategory_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_SUBCATEGORIES.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all subcategories
        result = await vclient.character_blueprint(company_id).list_all_subcategories(
            game_version=game_version, section_id=section_id, category_id=category_id
        )

        # Then: All subcategories are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], TraitSubcategory)
        assert result[0].name == "Allies"

    @respx.mock
    async def test_iter_all_subcategories(
        self, vclient, base_url, subcategory_response_data
    ) -> None:
        """Verify iter_all_subcategories yields subcategories across pages."""
        # Given: A mocked endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        paginated_response = {
            "items": [subcategory_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_SUBCATEGORIES.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all subcategories
        subcategories = [
            subcategory
            async for subcategory in vclient.character_blueprint(company_id).iter_all_subcategories(
                game_version=game_version, section_id=section_id, category_id=category_id
            )
        ]

        # Then: All subcategories are yielded
        assert route.called
        assert len(subcategories) == 1
        assert isinstance(subcategories[0], TraitSubcategory)

    @respx.mock
    async def test_get_subcategory(self, vclient, base_url, subcategory_response_data) -> None:
        """Verify getting a single subcategory by ID."""
        # Given: A mocked subcategory detail endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        subcategory_id = "subcat123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_SUBCATEGORY_DETAIL.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id, subcategory_id=subcategory_id)}"
        ).mock(return_value=Response(200, json=subcategory_response_data))

        # When: Requesting a single subcategory
        result = await vclient.character_blueprint(company_id).get_subcategory(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
            subcategory_id=subcategory_id,
        )

        # Then: The correct subcategory is returned
        assert route.called
        assert isinstance(result, TraitSubcategory)
        assert result.id == "subcat123"
        assert result.name == "Allies"
        assert result.parent_category_id == "category123"
        assert result.initial_cost == 1
        assert result.upgrade_cost == 2

    @respx.mock
    async def test_get_subcategory_not_found(self, vclient, base_url) -> None:
        """Verify getting a non-existent subcategory raises NotFoundError."""
        # Given: A mocked 404 response
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        subcategory_id = "nonexistent"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_CATEGORY_SUBCATEGORY_DETAIL.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id, subcategory_id=subcategory_id)}"
        ).mock(
            return_value=Response(404, json={"detail": "Subcategory not found", "status_code": 404})
        )

        # When/Then: Requesting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_blueprint(company_id).get_subcategory(
                game_version=game_version,
                section_id=section_id,
                category_id=category_id,
                subcategory_id=subcategory_id,
            )

        assert route.called


class TestCharacterBlueprintServiceSubcategoryTraits:
    """Tests for CharacterBlueprintService subcategory trait methods."""

    @respx.mock
    async def test_get_subcategory_traits_page(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify getting a page of character blueprint subcategory traits."""
        # Given: A mocked subcategory traits endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        subcategory_id = "subcat123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SUBCATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id, subcategory_id=subcategory_id)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting a page of subcategory traits
        result = await vclient.character_blueprint(company_id).get_subcategory_traits_page(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
            subcategory_id=subcategory_id,
        )

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Trait)
        assert result.items[0].name == "Strength"
        assert result.total == 1

    @respx.mock
    async def test_get_subcategory_traits_page_with_character_class_filter(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify get_subcategory_traits_page passes character_class filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        subcategory_id = "subcat123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SUBCATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id, subcategory_id=subcategory_id)}",
            params={"limit": "10", "offset": "0", "character_class": "VAMPIRE"},
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting with character_class filter
        result = await vclient.character_blueprint(company_id).get_subcategory_traits_page(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
            subcategory_id=subcategory_id,
            character_class="VAMPIRE",
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_get_subcategory_traits_page_with_is_rollable_filter(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify get_subcategory_traits_page passes is_rollable filter correctly."""
        # Given: A mocked endpoint expecting is_rollable param
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        subcategory_id = "subcat123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SUBCATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id, subcategory_id=subcategory_id)}",
            params={"limit": "10", "offset": "0", "is_rollable": "true"},
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting with is_rollable filter
        result = await vclient.character_blueprint(company_id).get_subcategory_traits_page(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
            subcategory_id=subcategory_id,
            is_rollable=True,
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_list_all_subcategory_traits(
        self, vclient, base_url, trait_response_data
    ) -> None:
        """Verify list_all_subcategory_traits returns all traits across pages."""
        # Given: A mocked endpoint that returns paginated results
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        subcategory_id = "subcat123"
        paginated_response = {
            "items": [trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SUBCATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id, subcategory_id=subcategory_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all subcategory traits
        result = await vclient.character_blueprint(company_id).list_all_subcategory_traits(
            game_version=game_version,
            section_id=section_id,
            category_id=category_id,
            subcategory_id=subcategory_id,
        )

        # Then: All traits are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], Trait)
        assert result[0].name == "Strength"

    @respx.mock
    async def test_iter_all_subcategory_traits(
        self, vclient, base_url, trait_response_data
    ) -> None:
        """Verify iter_all_subcategory_traits yields traits across pages."""
        # Given: A mocked endpoint
        company_id = "company123"
        game_version = "V5"
        section_id = "section123"
        category_id = "category123"
        subcategory_id = "subcat123"
        paginated_response = {
            "items": [trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SUBCATEGORY_TRAITS.format(company_id=company_id, game_version=game_version, section_id=section_id, category_id=category_id, subcategory_id=subcategory_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all subcategory traits
        traits = [
            trait
            async for trait in vclient.character_blueprint(company_id).iter_all_subcategory_traits(
                game_version=game_version,
                section_id=section_id,
                category_id=category_id,
                subcategory_id=subcategory_id,
            )
        ]

        # Then: All traits are yielded
        assert route.called
        assert len(traits) == 1
        assert isinstance(traits[0], Trait)


class TestCharacterBlueprintServiceTraits:
    """Tests for CharacterBlueprintService trait methods."""

    @respx.mock
    async def test_get_traits_page(self, vclient, base_url, paginated_trait_response) -> None:
        """Verify getting a page of character blueprint traits."""
        # Given: A mocked traits endpoint
        company_id = "company123"

        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_TRAITS.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting a page of traits
        result = await vclient.character_blueprint(company_id).get_traits_page()

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Trait)
        assert result.items[0].name == "Strength"
        assert result.total == 1

    @respx.mock
    async def test_get_traits_page_with_filters(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify get_traits_page passes filter parameters correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_TRAITS.format(company_id=company_id)}",
            params={
                "limit": "10",
                "offset": "0",
                "character_class": "VAMPIRE",
                "parent_category_id": "category123",
            },
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting with filters
        result = await vclient.character_blueprint(company_id).get_traits_page(
            character_class="VAMPIRE",
            parent_category_id="category123",
            order_by=None,
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_get_traits_page_with_is_rollable_filter(
        self, vclient, base_url, paginated_trait_response
    ) -> None:
        """Verify get_traits_page passes is_rollable filter correctly."""
        # Given: A mocked endpoint expecting is_rollable param
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_TRAITS.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0", "is_rollable": "true"},
        ).mock(return_value=Response(200, json=paginated_trait_response))

        # When: Requesting with is_rollable filter
        result = await vclient.character_blueprint(company_id).get_traits_page(
            is_rollable=True,
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_list_all_traits(self, vclient, base_url, trait_response_data) -> None:
        """Verify list_all_traits returns all traits across pages."""
        # Given: A mocked endpoint that returns paginated results
        company_id = "company123"
        paginated_response = {
            "items": [trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_TRAITS.format(company_id=company_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all traits
        result = await vclient.character_blueprint(company_id).list_all_traits()

        # Then: All traits are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], Trait)
        assert result[0].name == "Strength"

    @respx.mock
    async def test_iter_all_traits(self, vclient, base_url, trait_response_data) -> None:
        """Verify iter_all_traits yields traits across pages."""
        # Given: A mocked endpoint
        company_id = "company123"

        paginated_response = {
            "items": [trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_TRAITS.format(company_id=company_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all traits
        traits = [
            trait async for trait in vclient.character_blueprint(company_id).iter_all_traits()
        ]

        # Then: All traits are yielded
        assert route.called
        assert len(traits) == 1
        assert isinstance(traits[0], Trait)

    @respx.mock
    async def test_get_trait(self, vclient, base_url, trait_response_data) -> None:
        """Verify getting a trait by ID returns Trait object."""
        # Given: A mocked trait endpoint
        company_id = "company123"
        trait_id = "trait123"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_TRAIT_DETAIL.format(company_id=company_id, trait_id=trait_id)}"
        ).mock(return_value=Response(200, json=trait_response_data))

        # When: Requesting a trait
        result = await vclient.character_blueprint(company_id).get_trait(
            trait_id=trait_id,
        )

        # Then: The route was called and trait is returned
        assert route.called
        assert isinstance(result, Trait)
        assert result.id == "trait123"
        assert result.name == "Strength"
        assert result.max_value == 5
        assert result.parent_category_id == "category123"

    @respx.mock
    async def test_get_trait_not_found(self, vclient, base_url) -> None:
        """Verify getting a non-existent trait raises NotFoundError."""
        # Given: A mocked 404 response
        company_id = "company123"
        trait_id = "nonexistent"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_TRAIT_DETAIL.format(company_id=company_id, trait_id=trait_id)}"
        ).mock(return_value=Response(404, json={"detail": "Trait not found", "status_code": 404}))

        # When/Then: Requesting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_blueprint(company_id).get_trait(trait_id=trait_id)

        assert route.called


class TestCharacterBlueprintServicePagination:
    """Tests for pagination behavior in CharacterBlueprintService."""

    @respx.mock
    async def test_get_sections_page_with_custom_pagination(
        self, vclient, base_url, section_response_data
    ) -> None:
        """Verify custom limit and offset are passed correctly."""
        # Given: A mocked endpoint expecting custom pagination params
        company_id = "company123"
        game_version = "V5"
        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SECTIONS.format(company_id=company_id, game_version=game_version)}",
            params={"limit": "50", "offset": "100"},
        ).mock(
            return_value=Response(
                200,
                json={
                    "items": [section_response_data],
                    "limit": 50,
                    "offset": 100,
                    "total": 150,
                },
            )
        )

        # When: Requesting with custom pagination
        result = await vclient.character_blueprint(company_id).get_sections_page(
            game_version, limit=50, offset=100
        )

        # Then: The route was called with correct params
        assert route.called
        assert result.limit == 50
        assert result.offset == 100
        assert result.total == 150

    @respx.mock
    async def test_iter_all_sections_multiple_pages(
        self, vclient, base_url, section_response_data
    ) -> None:
        """Verify iter_all_sections handles multiple pages correctly."""
        # Given: A mocked endpoint that returns two pages of results
        company_id = "company123"
        game_version = "V5"
        section2 = {**section_response_data, "id": "section456", "name": "Skills"}

        # First page
        first_page = {
            "items": [section_response_data],
            "limit": 1,
            "offset": 0,
            "total": 2,
        }
        # Second page
        second_page = {
            "items": [section2],
            "limit": 1,
            "offset": 1,
            "total": 2,
        }

        route = respx.get(
            f"{base_url}{Endpoints.BLUEPRINT_SECTIONS.format(company_id=company_id, game_version=game_version)}"
        ).mock(side_effect=[Response(200, json=first_page), Response(200, json=second_page)])

        # When: Iterating through all sections
        sections = [
            section
            async for section in vclient.character_blueprint(company_id).iter_all_sections(
                game_version=game_version
            )
        ]

        # Then: All sections from both pages are yielded
        assert route.call_count == 2
        assert len(sections) == 2
        assert sections[0].name == "Attributes"
        assert sections[1].name == "Skills"


class TestCharacterBlueprintServiceConcepts:
    """Tests for CharacterBlueprintService concept methods."""

    @respx.mock
    async def test_get_concepts_page(
        self, vclient, base_url, paginated_character_concept_response
    ) -> None:
        """Verify getting a page of character concepts."""
        # Given: A mocked concepts endpoint
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.CONCEPTS.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_character_concept_response))

        # When: Requesting a page of concepts
        result = await vclient.character_blueprint(company_id).get_concepts_page()

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], CharacterConcept)
        assert result.items[0].name == "Physical"
        assert result.total == 1

    @respx.mock
    async def test_list_all_concepts(
        self, vclient, base_url, character_concept_response_data
    ) -> None:
        """Verify list_all_concepts returns all concepts across pages."""
        # Given: A mocked endpoint that returns paginated results
        company_id = "company123"
        paginated_response = {
            "items": [character_concept_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(f"{base_url}{Endpoints.CONCEPTS.format(company_id=company_id)}").mock(
            return_value=Response(200, json=paginated_response)
        )

        # When: Requesting all concepts
        result = await vclient.character_blueprint(company_id).list_all_concepts()

        # Then: All concepts are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], CharacterConcept)
        assert result[0].name == "Physical"

    @respx.mock
    async def test_iter_all_concepts(
        self, vclient, base_url, character_concept_response_data
    ) -> None:
        """Verify iter_all_concepts yields concepts across pages."""
        # Given: A mocked endpoint
        company_id = "company123"
        paginated_response = {
            "items": [character_concept_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(f"{base_url}{Endpoints.CONCEPTS.format(company_id=company_id)}").mock(
            return_value=Response(200, json=paginated_response)
        )

        # When: Iterating through all concepts
        concepts = [
            concept async for concept in vclient.character_blueprint(company_id).iter_all_concepts()
        ]

        # Then: All concepts are yielded
        assert route.called
        assert len(concepts) == 1
        assert isinstance(concepts[0], CharacterConcept)
        assert concepts[0].name == "Physical"

    @respx.mock
    async def test_get_concept(self, vclient, base_url, character_concept_response_data) -> None:
        """Verify getting a concept by ID returns Concept object."""
        # Given: A mocked concept endpoint
        company_id = "company123"
        concept_id = "concept123"
        route = respx.get(
            f"{base_url}{Endpoints.CONCEPT_DETAIL.format(company_id=company_id, concept_id=concept_id)}"
        ).mock(return_value=Response(200, json=character_concept_response_data))

        # When: Requesting a concept
        result = await vclient.character_blueprint(company_id).get_concept(concept_id=concept_id)

        # Then: The route was called and concept is returned
        assert route.called
        assert isinstance(result, CharacterConcept)
        assert result.id == "concept123"
        assert result.name == "Physical"
        assert result.max_specialties == 1
        assert result.specialties[0].name == "Brawl: Kindred"
        assert result.specialties[0].type == "ACTION"
        assert result.favored_ability_names == ["Ability 1", "Ability 2"]

    @respx.mock
    async def test_get_concept_not_found(self, vclient, base_url) -> None:
        """Verify getting a non-existent concept raises NotFoundError."""
        # Given: A mocked 404 response
        company_id = "company123"
        concept_id = "nonexistent"
        route = respx.get(
            f"{base_url}{Endpoints.CONCEPT_DETAIL.format(company_id=company_id, concept_id=concept_id)}"
        ).mock(return_value=Response(404, json={"detail": "Concept not found", "status_code": 404}))

        # When/Then: Requesting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_blueprint(company_id).get_concept(concept_id=concept_id)

        assert route.called


class TestCharacterBlueprintServiceVampireClans:
    """Tests for CharacterBlueprintService vampire clan methods."""

    @respx.mock
    async def test_get_vampire_clans_page(
        self, vclient, base_url, paginated_vampire_clan_response
    ) -> None:
        """Verify getting a page of vampire clans."""
        # Given: A mocked vampire clans endpoint
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.VAMPIRE_CLANS.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_vampire_clan_response))

        # When: Requesting a page of vampire clans
        result = await vclient.character_blueprint(company_id).get_vampire_clans_page()

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], VampireClan)
        assert result.items[0].name == "Clan Name"
        assert result.total == 1

    @respx.mock
    async def test_get_vampire_clans_page_with_game_version_filter(
        self, vclient, base_url, paginated_vampire_clan_response
    ) -> None:
        """Verify get_vampire_clans_page passes game_version filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.VAMPIRE_CLANS.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0", "game_version": "V5"},
        ).mock(return_value=Response(200, json=paginated_vampire_clan_response))

        # When: Requesting with game_version filter
        result = await vclient.character_blueprint(company_id).get_vampire_clans_page(
            game_version="V5"
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_list_all_vampire_clans(
        self, vclient, base_url, vampire_clan_response_data
    ) -> None:
        """Verify list_all_vampire_clans returns all vampire clans across pages."""
        # Given: A mocked endpoint that returns paginated results
        company_id = "company123"
        paginated_response = {
            "items": [vampire_clan_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.VAMPIRE_CLANS.format(company_id=company_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all vampire clans
        result = await vclient.character_blueprint(company_id).list_all_vampire_clans()

        # Then: All vampire clans are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], VampireClan)
        assert result[0].name == "Clan Name"

    @respx.mock
    async def test_list_all_vampire_clans_with_game_version_filter(
        self, vclient, base_url, vampire_clan_response_data
    ) -> None:
        """Verify list_all_vampire_clans passes game_version filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        paginated_response = {
            "items": [vampire_clan_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.VAMPIRE_CLANS.format(company_id=company_id)}",
            params__contains={"game_version": "V5"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all vampire clans with game_version filter
        result = await vclient.character_blueprint(company_id).list_all_vampire_clans(
            game_version="V5"
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], VampireClan)

    @respx.mock
    async def test_iter_all_vampire_clans(
        self, vclient, base_url, vampire_clan_response_data
    ) -> None:
        """Verify iter_all_vampire_clans yields vampire clans across pages."""
        # Given: A mocked endpoint
        company_id = "company123"
        paginated_response = {
            "items": [vampire_clan_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.VAMPIRE_CLANS.format(company_id=company_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all vampire clans
        clans = [
            clan async for clan in vclient.character_blueprint(company_id).iter_all_vampire_clans()
        ]

        # Then: All vampire clans are yielded
        assert route.called
        assert len(clans) == 1
        assert isinstance(clans[0], VampireClan)

    @respx.mock
    async def test_iter_all_vampire_clans_with_game_version_filter(
        self, vclient, base_url, vampire_clan_response_data
    ) -> None:
        """Verify iter_all_vampire_clans passes game_version filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        paginated_response = {
            "items": [vampire_clan_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.VAMPIRE_CLANS.format(company_id=company_id)}",
            params__contains={"game_version": "V5"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating with game_version filter
        clans = [
            clan
            async for clan in vclient.character_blueprint(company_id).iter_all_vampire_clans(
                game_version="V5"
            )
        ]

        # Then: The route was called with correct params
        assert route.called
        assert len(clans) == 1
        assert isinstance(clans[0], VampireClan)

    @respx.mock
    async def test_get_vampire_clan(self, vclient, base_url, vampire_clan_response_data) -> None:
        """Verify getting a vampire clan by ID returns VampireClan object."""
        # Given: A mocked vampire clan endpoint
        company_id = "company123"
        vampire_clan_id = "clan123"
        route = respx.get(
            f"{base_url}{Endpoints.VAMPIRE_CLAN_DETAIL.format(company_id=company_id, vampire_clan_id=vampire_clan_id)}"
        ).mock(return_value=Response(200, json=vampire_clan_response_data))

        # When: Requesting a vampire clan
        result = await vclient.character_blueprint(company_id).get_vampire_clan(
            vampire_clan_id=vampire_clan_id
        )

        # Then: The route was called and vampire clan is returned
        assert route.called
        assert isinstance(result, VampireClan)
        assert result.id == "clan123"
        assert result.name == "Clan Name"
        assert result.description == "Clan description"

    @respx.mock
    async def test_get_vampire_clan_not_found(self, vclient, base_url) -> None:
        """Verify getting a non-existent vampire clan raises NotFoundError."""
        # Given: A mocked 404 response
        company_id = "company123"
        vampire_clan_id = "nonexistent"
        route = respx.get(
            f"{base_url}{Endpoints.VAMPIRE_CLAN_DETAIL.format(company_id=company_id, vampire_clan_id=vampire_clan_id)}"
        ).mock(
            return_value=Response(
                404, json={"detail": "Vampire clan not found", "status_code": 404}
            )
        )

        # When/Then: Requesting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_blueprint(company_id).get_vampire_clan(
                vampire_clan_id=vampire_clan_id
            )

        assert route.called


class TestCharacterBlueprintServiceWerewolfAuspices:
    """Tests for CharacterBlueprintService werewolf auspice methods."""

    @respx.mock
    async def test_get_werewolf_auspices_page(
        self, vclient, base_url, paginated_werewolf_auspice_response
    ) -> None:
        """Verify getting a page of werewolf auspices."""
        # Given: A mocked werewolf auspices endpoint
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_AUSPICES.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_werewolf_auspice_response))

        # When: Requesting a page of werewolf auspices
        result = await vclient.character_blueprint(company_id).get_werewolf_auspices_page()

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], WerewolfAuspice)
        assert result.items[0].name == "Auspice Name"

    @respx.mock
    async def test_get_werewolf_auspices_page_with_game_version_filter(
        self, vclient, base_url, paginated_werewolf_auspice_response
    ) -> None:
        """Verify get_werewolf_auspices_page passes game_version filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_AUSPICES.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0", "game_version": "V5"},
        ).mock(return_value=Response(200, json=paginated_werewolf_auspice_response))

        # When: Requesting with game_version filter
        result = await vclient.character_blueprint(company_id).get_werewolf_auspices_page(
            game_version="V5"
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_list_all_werewolf_auspices(
        self, vclient, base_url, werewolf_auspice_response_data
    ) -> None:
        """Verify list_all_werewolf_auspices returns all werewolf auspices across pages."""
        # Given: A mocked endpoint that returns paginated results
        company_id = "company123"
        paginated_response = {
            "items": [werewolf_auspice_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_AUSPICES.format(company_id=company_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all werewolf auspices
        result = await vclient.character_blueprint(company_id).list_all_werewolf_auspices()

        # Then: All werewolf auspices are returned as a list
        assert route.called
        assert len(result) == 1

    @respx.mock
    async def test_iter_all_werewolf_auspices(
        self, vclient, base_url, werewolf_auspice_response_data
    ) -> None:
        """Verify iter_all_werewolf_auspices yields werewolf auspices across pages."""
        # Given: A mocked endpoint
        company_id = "company123"
        paginated_response = {
            "items": [werewolf_auspice_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_AUSPICES.format(company_id=company_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all werewolf auspices
        auspices = [
            auspice
            async for auspice in vclient.character_blueprint(
                company_id
            ).iter_all_werewolf_auspices()
        ]

        # Then: All werewolf auspices are yielded
        assert route.called
        assert len(auspices) == 1
        assert isinstance(auspices[0], WerewolfAuspice)

    @respx.mock
    async def test_list_all_werewolf_auspices_with_game_version_filter(
        self, vclient, base_url, werewolf_auspice_response_data
    ) -> None:
        """Verify list_all_werewolf_auspices passes game_version filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        paginated_response = {
            "items": [werewolf_auspice_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_AUSPICES.format(company_id=company_id)}",
            params__contains={"game_version": "V5"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all werewolf auspices with game_version filter
        result = await vclient.character_blueprint(company_id).list_all_werewolf_auspices(
            game_version="V5"
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], WerewolfAuspice)

    @respx.mock
    async def test_iter_all_werewolf_auspices_with_game_version_filter(
        self, vclient, base_url, werewolf_auspice_response_data
    ) -> None:
        """Verify iter_all_werewolf_auspices passes game_version filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        paginated_response = {
            "items": [werewolf_auspice_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_AUSPICES.format(company_id=company_id)}",
            params__contains={"game_version": "V5"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating with game_version filter
        auspices = [
            auspice
            async for auspice in vclient.character_blueprint(company_id).iter_all_werewolf_auspices(
                game_version="V5"
            )
        ]

        # Then: The route was called with correct params
        assert route.called
        assert len(auspices) == 1
        assert isinstance(auspices[0], WerewolfAuspice)

    @respx.mock
    async def test_get_werewolf_auspice(
        self, vclient, base_url, werewolf_auspice_response_data
    ) -> None:
        """Verify getting a werewolf auspice by ID returns WerewolfAuspice object."""
        # Given: A mocked werewolf auspice endpoint
        company_id = "company123"
        werewolf_auspice_id = "auspice123"
        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_AUSPICE_DETAIL.format(company_id=company_id, werewolf_auspice_id=werewolf_auspice_id)}"
        ).mock(return_value=Response(200, json=werewolf_auspice_response_data))

        # When: Requesting a werewolf auspice
        result = await vclient.character_blueprint(company_id).get_werewolf_auspice(
            werewolf_auspice_id=werewolf_auspice_id
        )

        # Then: The route was called and werewolf auspice is returned
        assert route.called
        assert isinstance(result, WerewolfAuspice)

    @respx.mock
    async def test_get_werewolf_auspice_not_found(self, vclient, base_url) -> None:
        """Verify getting a non-existent werewolf auspice raises NotFoundError."""
        # Given: A mocked 404 response
        company_id = "company123"
        werewolf_auspice_id = "nonexistent"
        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_AUSPICE_DETAIL.format(company_id=company_id, werewolf_auspice_id=werewolf_auspice_id)}"
        ).mock(
            return_value=Response(
                404, json={"detail": "Werewolf auspice not found", "status_code": 404}
            )
        )

        # When/Then: Requesting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_blueprint(company_id).get_werewolf_auspice(
                werewolf_auspice_id=werewolf_auspice_id
            )

        assert route.called


class TestCharacterBlueprintServiceWerewolfTribes:
    """Tests for CharacterBlueprintService werewolf tribe methods."""

    @respx.mock
    async def test_get_werewolf_tribes_page(
        self, vclient, base_url, paginated_werewolf_tribe_response
    ) -> None:
        """Verify getting a page of werewolf tribes."""
        # Given: A mocked werewolf tribes endpoint
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_TRIBES.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0"},
        ).mock(return_value=Response(200, json=paginated_werewolf_tribe_response))

        # When: Requesting a page of werewolf tribes
        result = await vclient.character_blueprint(company_id).get_werewolf_tribes_page()

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], WerewolfTribe)

    @respx.mock
    async def test_get_werewolf_tribes_page_with_game_version_filter(
        self, vclient, base_url, paginated_werewolf_tribe_response
    ) -> None:
        """Verify get_werewolf_tribes_page passes game_version filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_TRIBES.format(company_id=company_id)}",
            params={"limit": "10", "offset": "0", "game_version": "V5"},
        ).mock(return_value=Response(200, json=paginated_werewolf_tribe_response))

        # When: Requesting with game_version filter
        result = await vclient.character_blueprint(company_id).get_werewolf_tribes_page(
            game_version="V5"
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_list_all_werewolf_tribes(
        self, vclient, base_url, werewolf_tribe_response_data
    ) -> None:
        """Verify list_all_werewolf_tribes returns all werewolf tribes across pages."""
        # Given: A mocked endpoint that returns paginated results
        company_id = "company123"
        paginated_response = {
            "items": [werewolf_tribe_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_TRIBES.format(company_id=company_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all werewolf tribes
        result = await vclient.character_blueprint(company_id).list_all_werewolf_tribes()

        # Then: All werewolf tribes are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], WerewolfTribe)
        assert result[0].name == "Tribe Name"

    @respx.mock
    async def test_list_all_werewolf_tribes_with_game_version_filter(
        self, vclient, base_url, werewolf_tribe_response_data
    ) -> None:
        """Verify list_all_werewolf_tribes passes game_version filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        paginated_response = {
            "items": [werewolf_tribe_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_TRIBES.format(company_id=company_id)}",
            params__contains={"game_version": "V5"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all werewolf tribes with game_version filter
        result = await vclient.character_blueprint(company_id).list_all_werewolf_tribes(
            game_version="V5"
        )

        # Then: The route was called with correct params
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], WerewolfTribe)

    @respx.mock
    async def test_iter_all_werewolf_tribes(
        self, vclient, base_url, werewolf_tribe_response_data
    ) -> None:
        """Verify iter_all_werewolf_tribes yields werewolf tribes across pages."""
        # Given: A mocked endpoint
        company_id = "company123"
        paginated_response = {
            "items": [werewolf_tribe_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_TRIBES.format(company_id=company_id)}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all werewolf tribes
        tribes = [
            tribe
            async for tribe in vclient.character_blueprint(company_id).iter_all_werewolf_tribes()
        ]

        # Then: All werewolf tribes are yielded
        assert route.called
        assert len(tribes) == 1
        assert isinstance(tribes[0], WerewolfTribe)

    @respx.mock
    async def test_iter_all_werewolf_tribes_with_game_version_filter(
        self, vclient, base_url, werewolf_tribe_response_data
    ) -> None:
        """Verify iter_all_werewolf_tribes passes game_version filter correctly."""
        # Given: A mocked endpoint expecting filter params
        company_id = "company123"
        paginated_response = {
            "items": [werewolf_tribe_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }

        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_TRIBES.format(company_id=company_id)}",
            params__contains={"game_version": "V5"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating with game_version filter
        tribes = [
            tribe
            async for tribe in vclient.character_blueprint(company_id).iter_all_werewolf_tribes(
                game_version="V5"
            )
        ]

        # Then: The route was called with correct params
        assert route.called
        assert len(tribes) == 1
        assert isinstance(tribes[0], WerewolfTribe)

    @respx.mock
    async def test_get_werewolf_tribe(
        self, vclient, base_url, werewolf_tribe_response_data
    ) -> None:
        """Verify getting a werewolf tribe by ID returns WerewolfTribe object."""
        # Given: A mocked werewolf tribe endpoint
        company_id = "company123"
        werewolf_tribe_id = "tribe123"
        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_TRIBE_DETAIL.format(company_id=company_id, werewolf_tribe_id=werewolf_tribe_id)}"
        ).mock(return_value=Response(200, json=werewolf_tribe_response_data))

        # When: Requesting a werewolf tribe
        result = await vclient.character_blueprint(company_id).get_werewolf_tribe(
            werewolf_tribe_id=werewolf_tribe_id
        )

        # Then: The route was called and werewolf tribe is returned
        assert route.called
        assert isinstance(result, WerewolfTribe)
        assert result.id == "tribe123"
        assert result.name == "Tribe Name"
        assert result.description == "Tribe description"

    @respx.mock
    async def test_get_werewolf_tribe_not_found(self, vclient, base_url) -> None:
        """Verify getting a non-existent werewolf tribe raises NotFoundError."""
        # Given: A mocked 404 response
        company_id = "company123"
        werewolf_tribe_id = "nonexistent"
        route = respx.get(
            f"{base_url}{Endpoints.WEREWOLF_TRIBE_DETAIL.format(company_id=company_id, werewolf_tribe_id=werewolf_tribe_id)}"
        ).mock(
            return_value=Response(
                404, json={"detail": "Werewolf tribe not found", "status_code": 404}
            )
        )

        # When/Then: Requesting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_blueprint(company_id).get_werewolf_tribe(
                werewolf_tribe_id=werewolf_tribe_id
            )

        assert route.called
