"""Integration tests for CharacterTraitsService."""

import json

import pytest
import respx
from httpx import Response

from vclient.endpoints import Endpoints
from vclient.exceptions import NotFoundError, ValidationError
from vclient.models import (
    BulkAssignTraitResponse,
    CharacterTrait,
    CharacterTraitAdd,
    CharacterTraitValueOptionsResponse,
    PaginatedResponse,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def paginated_character_trait_response(character_trait_response_data: dict) -> dict:
    """Return a paginated response with character traits."""
    return {
        "items": [character_trait_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def character_trait_value_options_response_data(trait_response_data: dict) -> dict:
    """Return a response data for the value options for a character trait."""
    return {
        "name": "Strength",
        "current_value": 2,
        "trait": trait_response_data,
        "xp_current": 0,
        "starting_points_current": 0,
        "options": {
            "1": {
                "direction": "decrease",
                "point_change": 10,
                "can_use_xp": True,
                "xp_after": 10,
                "can_use_starting_points": True,
                "starting_points_after": 10,
            },
            "3": {
                "direction": "increase",
                "point_change": 15,
                "can_use_xp": False,
                "xp_after": -15,
                "can_use_starting_points": False,
                "starting_points_after": -15,
            },
            "4": {
                "direction": "increase",
                "point_change": 35,
                "can_use_xp": False,
                "xp_after": -35,
                "can_use_starting_points": False,
                "starting_points_after": -35,
            },
            "5": {
                "direction": "increase",
                "point_change": 60,
                "can_use_xp": False,
                "xp_after": -60,
                "can_use_starting_points": False,
                "starting_points_after": -60,
            },
        },
    }


class TestCharacterTraitsServiceGetPage:
    """Tests for CharacterTraitsService.get_page method."""

    @respx.mock
    async def test_get_page(self, vclient, base_url, paginated_character_trait_response) -> None:
        """Verify getting a page of character traits returns paginated response."""
        # Given: A mocked character traits list endpoint
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json=paginated_character_trait_response))

        # When: Requesting a page of character traits
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).get_page()

        # Then: The route was called and response is paginated
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], CharacterTrait)
        assert result.items[0].trait.name == "Strength"
        assert result.items[0].value == 3
        assert result.total == 1

    @respx.mock
    async def test_get_page_with_pagination_params(
        self, vclient, base_url, paginated_character_trait_response
    ) -> None:
        """Verify get_page passes pagination parameters correctly."""
        # Given: A mocked endpoint expecting pagination params
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "20", "offset": "10"},
        ).mock(return_value=Response(200, json=paginated_character_trait_response))

        # When: Requesting with pagination
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).get_page(limit=20, offset=10)

        # Then: The route was called with correct params
        assert route.called
        assert isinstance(result, PaginatedResponse)

    @respx.mock
    async def test_get_page_with_category_filter(
        self, vclient, base_url, paginated_character_trait_response
    ) -> None:
        """Verify get_page filters by category_id."""
        # Given: A mocked endpoint expecting filter params
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "10", "offset": "0", "category_id": "cat123"},
        ).mock(return_value=Response(200, json=paginated_character_trait_response))

        # When: Requesting with filter
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).get_page(category_id="cat123")

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_get_page_with_is_rollable_true(
        self, vclient, base_url, paginated_character_trait_response
    ) -> None:
        """Verify get_page passes is_rollable=True filter correctly."""
        # Given: A mocked endpoint expecting is_rollable param
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "10", "offset": "0", "is_rollable": "true"},
        ).mock(return_value=Response(200, json=paginated_character_trait_response))

        # When: Requesting with is_rollable filter
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).get_page(is_rollable=True)

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1

    @respx.mock
    async def test_get_page_with_is_rollable_false(
        self, vclient, base_url, paginated_character_trait_response
    ) -> None:
        """Verify get_page passes is_rollable=False filter correctly."""
        # Given: A mocked endpoint expecting is_rollable=False param
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "10", "offset": "0", "is_rollable": "false"},
        ).mock(return_value=Response(200, json=paginated_character_trait_response))

        # When: Requesting with is_rollable=False filter
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).get_page(is_rollable=False)

        # Then: The route was called with correct params
        assert route.called
        assert len(result.items) == 1


class TestCharacterTraitsServiceGet:
    """Tests for CharacterTraitsService.get method."""

    @respx.mock
    async def test_get_character_trait(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify getting a character trait returns CharacterTrait object."""
        # Given: A mocked character trait endpoint
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAIT.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}"
        ).mock(return_value=Response(200, json=character_trait_response_data))

        # When: Requesting a character trait
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).get("ct123")

        # Then: The route was called and character trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.id == "ct123"
        assert result.character_id == "char123"
        assert result.value == 3
        assert result.trait.name == "Strength"

    @respx.mock
    async def test_get_character_trait_not_found(self, vclient, base_url) -> None:
        """Verify getting a non-existent character trait raises NotFoundError."""
        # Given: A mocked 404 response
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAIT.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='nonexistent')}"
        ).mock(
            return_value=Response(
                404, json={"detail": "Character trait not found", "status_code": 404}
            )
        )

        # When/Then: Requesting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_traits(
                "user123", "campaign123", "char123", company_id="company123"
            ).get("nonexistent")

        assert route.called


class TestCharacterTraitsServiceListAll:
    """Tests for CharacterTraitsService.list_all method."""

    @respx.mock
    async def test_list_all_character_traits(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify list_all returns all character traits across pages."""
        # Given: A mocked endpoint that returns paginated results
        paginated_response = {
            "items": [character_trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting all character traits
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).list_all()

        # Then: All character traits are returned as a list
        assert route.called
        assert len(result) == 1
        assert isinstance(result[0], CharacterTrait)
        assert result[0].trait.name == "Strength"

    @respx.mock
    async def test_list_all_with_category_filter(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify list_all filters by category_id."""
        # Given: A mocked endpoint expecting filter params
        paginated_response = {
            "items": [character_trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "100", "offset": "0", "category_id": "cat123"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting with filter
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).list_all(category_id="cat123")

        # Then: Filtered results are returned
        assert route.called
        assert len(result) == 1

    @respx.mock
    async def test_list_all_with_is_rollable_filter(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify list_all filters by is_rollable."""
        # Given: A mocked endpoint expecting is_rollable param
        paginated_response = {
            "items": [character_trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "100", "offset": "0", "is_rollable": "true"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting with is_rollable filter
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).list_all(is_rollable=True)

        # Then: Filtered results are returned
        assert route.called
        assert len(result) == 1


class TestCharacterTraitsServiceIterAll:
    """Tests for CharacterTraitsService.iter_all method."""

    @respx.mock
    async def test_iter_all_character_traits(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify iter_all yields character traits across pages."""
        # Given: A mocked endpoint
        paginated_response = {
            "items": [character_trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating through all character traits
        traits = [
            trait
            async for trait in vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).iter_all()
        ]

        # Then: All character traits are yielded
        assert route.called
        assert len(traits) == 1
        assert isinstance(traits[0], CharacterTrait)

    @respx.mock
    async def test_iter_all_with_filter(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify iter_all filters by category_id."""
        # Given: A mocked endpoint expecting filter params
        paginated_response = {
            "items": [character_trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "100", "offset": "0", "category_id": "cat456"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating with filter
        traits = [
            trait
            async for trait in vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).iter_all(category_id="cat456")
        ]

        # Then: Filtered results are yielded
        assert route.called
        assert len(traits) == 1

    @respx.mock
    async def test_iter_all_with_is_rollable_filter(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify iter_all filters by is_rollable."""
        # Given: A mocked endpoint expecting is_rollable param
        paginated_response = {
            "items": [character_trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "100", "offset": "0", "is_rollable": "false"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating with is_rollable filter
        traits = [
            trait
            async for trait in vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).iter_all(is_rollable=False)
        ]

        # Then: Filtered results are yielded
        assert route.called
        assert len(traits) == 1


class TestCharacterTraitsServiceAssign:
    """Tests for CharacterTraitsService.assign method."""

    @respx.mock
    async def test_assign_trait(self, vclient, base_url, character_trait_response_data) -> None:
        """Verify assigning an existing trait to a character."""
        # Given: A mocked create endpoint
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_ASSIGN.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(201, json=character_trait_response_data))

        # When: Assigning a trait
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).assign(trait_id="trait123", value=3, currency="XP")

        # Then: The route was called and character trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.id == "ct123"
        assert result.value == 3

        # Verify request body
        body = json.loads(route.calls[0].request.content)
        assert body["trait_id"] == "trait123"
        assert body["value"] == 3

    @respx.mock
    async def test_assign_trait_zero_value(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify assigning a trait with value zero."""
        # Given: A mocked create endpoint with zero value response
        response_data = {**character_trait_response_data, "value": 0}
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_ASSIGN.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(201, json=response_data))

        # When: Assigning a trait with value 0
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).assign(trait_id="trait123", value=0, currency="XP")

        # Then: The route was called and character trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.value == 0

    @respx.mock
    async def test_assign_trait_not_found(self, vclient, base_url) -> None:
        """Verify assigning a non-existent trait raises NotFoundError."""
        # Given: A mocked 404 response
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_ASSIGN.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(404, json={"detail": "Trait not found", "status_code": 404}))

        # When/Then: Assigning raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).assign(trait_id="nonexistent", value=1, currency="XP")

        assert route.called


class TestCharacterTraitsServiceCreate:
    """Tests for CharacterTraitsService.create method."""

    @respx.mock
    async def test_create_trait_minimal(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify creating a custom trait with minimal fields."""
        # Given: A mocked create endpoint
        response_data = {
            **character_trait_response_data,
            "trait": {
                **character_trait_response_data["trait"],
                "name": "Custom Skill",
                "is_custom": True,
            },
        }
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_CREATE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(201, json=response_data))

        # When: Creating a custom trait with required fields only
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).create(
            name="Custom Skill",
            category_id="cat123",
        )

        # Then: The route was called and character trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.trait.name == "Custom Skill"

        # Verify request body contains required fields
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["name"] == "Custom Skill"
        assert body["category_id"] == "cat123"
        # max_value and min_value have defaults but are not sent when not explicitly set

    @respx.mock
    async def test_create_trait_all_options(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify creating a custom trait with all optional fields."""
        # Given: A mocked create endpoint
        response_data = {
            **character_trait_response_data,
            "value": 3,
            "trait": {
                **character_trait_response_data["trait"],
                "name": "Custom Background",
                "description": "A custom background trait",
                "max_value": 10,
                "min_value": 1,
                "show_when_zero": False,
                "initial_cost": 3,
                "upgrade_cost": 2,
                "is_custom": True,
            },
        }
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_CREATE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(201, json=response_data))

        # When: Creating a custom trait with all fields
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).create(
            name="Custom Background",
            category_id="backgrounds_cat",
            description="A custom background trait",
            max_value=10,
            min_value=1,
            show_when_zero=False,
            initial_cost=3,
            upgrade_cost=2,
            value=3,
        )

        # Then: The route was called and character trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.trait.name == "Custom Background"
        assert result.value == 3

        # Verify request body contains all fields
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["name"] == "Custom Background"
        assert body["category_id"] == "backgrounds_cat"
        assert body["description"] == "A custom background trait"
        assert body["max_value"] == 10
        assert body["min_value"] == 1
        assert body["show_when_zero"] is False
        assert body["initial_cost"] == 3
        assert body["upgrade_cost"] == 2
        assert body["value"] == 3

    @respx.mock
    async def test_create_trait_with_value(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify creating a custom trait with an initial value."""
        # Given: A mocked create endpoint
        response_data = {**character_trait_response_data, "value": 2}
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_CREATE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(201, json=response_data))

        # When: Creating a custom trait with initial value
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).create(
            name="Custom Trait",
            category_id="cat123",
            value=2,
        )

        # Then: The character trait is returned with the value
        assert route.called
        assert result.value == 2

    @respx.mock
    async def test_create_trait_not_found_category(self, vclient, base_url) -> None:
        """Verify creating a trait with invalid category raises NotFoundError."""
        # Given: A mocked 404 response
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_CREATE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(
            return_value=Response(
                404, json={"detail": "Parent category not found", "status_code": 404}
            )
        )

        # When/Then: Creating raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).create(
                name="Custom Trait",
                category_id="nonexistent_cat",
            )

        assert route.called


class TestCharacterTraitsServiceDelete:
    """Tests for CharacterTraitsService.delete method."""

    @respx.mock
    async def test_delete_trait(self, vclient, base_url) -> None:
        """Verify deleting a character trait."""
        # Given: A mocked delete endpoint
        route = respx.delete(
            f"{base_url}{Endpoints.CHARACTER_TRAIT.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}"
        ).mock(return_value=Response(204))

        # When: Deleting the trait
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).delete("ct123")

        # Then: The route was called and None is returned
        assert route.called
        assert result is None

    @respx.mock
    async def test_delete_trait_with_currency(self, vclient, base_url) -> None:
        """Verify deleting a character trait with a currency parameter."""
        # Given: A mocked delete endpoint expecting currency param
        route = respx.delete(
            f"{base_url}{Endpoints.CHARACTER_TRAIT.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}",
            params={"currency": "XP"},
        ).mock(return_value=Response(204))

        # When: Deleting the trait with currency
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).delete("ct123", currency="XP")

        # Then: The route was called with currency param and None is returned
        assert route.called
        assert result is None

    @respx.mock
    async def test_delete_trait_not_found(self, vclient, base_url) -> None:
        """Verify deleting a non-existent trait raises NotFoundError."""
        # Given: A mocked 404 response
        route = respx.delete(
            f"{base_url}{Endpoints.CHARACTER_TRAIT.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='nonexistent')}"
        ).mock(return_value=Response(404, json={"detail": "Trait not found", "status_code": 404}))

        # When/Then: Deleting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).delete("nonexistent")

        assert route.called


class TestCharacterTraitsServiceMultiplePages:
    """Tests for CharacterTraitsService pagination across multiple pages."""

    @respx.mock
    async def test_iter_all_multiple_pages(self, vclient, base_url, trait_response_data) -> None:
        """Verify iter_all handles multiple pages correctly."""
        # Given: Two pages of character traits
        trait1 = {
            "id": "ct1",
            "character_id": "char123",
            "value": 1,
            "trait": {**trait_response_data, "id": "trait1", "name": "Strength"},
        }
        trait2 = {
            "id": "ct2",
            "character_id": "char123",
            "value": 2,
            "trait": {**trait_response_data, "id": "trait2", "name": "Dexterity"},
        }

        page1_response = {
            "items": [trait1],
            "limit": 1,
            "offset": 0,
            "total": 2,
        }
        page2_response = {
            "items": [trait2],
            "limit": 1,
            "offset": 1,
            "total": 2,
        }

        route1 = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "1", "offset": "0"},
        ).mock(return_value=Response(200, json=page1_response))

        route2 = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "1", "offset": "1"},
        ).mock(return_value=Response(200, json=page2_response))

        # When: Iterating through all character traits with limit=1
        traits = [
            trait
            async for trait in vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).iter_all(limit=1)
        ]

        # Then: All character traits from both pages are yielded
        assert route1.called
        assert route2.called
        assert len(traits) == 2
        assert traits[0].trait.name == "Strength"
        assert traits[1].trait.name == "Dexterity"


class TestCharacterTraitsServiceGetValueOptions:
    """Tests for CharacterTraitsService.get_value_options method."""

    @respx.mock
    async def test_get_value_options(
        self, vclient, base_url, character_trait_value_options_response_data
    ) -> None:
        """Verify getting the value options for a character trait."""
        # Given: A mocked get value options endpoint
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_VALUE_OPTIONS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}",
        ).mock(return_value=Response(200, json=character_trait_value_options_response_data))

        # When: Getting the value options for a character trait
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).get_value_options("ct123")

        # Then: The route was called and the value options are returned
        assert route.called
        assert result == CharacterTraitValueOptionsResponse.model_validate(
            character_trait_value_options_response_data
        )


class TestCharacterTraitsServiceChangeValue:
    """Tests for CharacterTraitsService.change_value method."""

    @respx.mock
    async def test_change_value(self, vclient, base_url, character_trait_response_data) -> None:
        """Verify changing the value of a character trait."""
        # Given: A mocked change value endpoint
        route = respx.put(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_VALUE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}",
        ).mock(return_value=Response(200, json=character_trait_response_data))

        # When: Changing the value of a character trait
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).change_value("ct123", new_value=4, currency="XP")

        # Then: The route was called and character trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.trait.name == "Strength"


@pytest.fixture
def bulk_assign_response_data(character_trait_response_data: dict) -> dict:
    """Return sample bulk assign response data with mixed results."""
    return {
        "succeeded": [
            {"trait_id": "trait1", "character_trait": character_trait_response_data},
        ],
        "failed": [
            {"trait_id": "trait2", "error": "Not enough XP to add trait"},
        ],
    }


@pytest.fixture
def bulk_assign_all_success_response_data(character_trait_response_data: dict) -> dict:
    """Return sample bulk assign response with all successes."""
    return {
        "succeeded": [
            {"trait_id": "trait1", "character_trait": character_trait_response_data},
            {
                "trait_id": "trait2",
                "character_trait": {**character_trait_response_data, "id": "ct456"},
            },
        ],
        "failed": [],
    }


class TestCharacterTraitsServiceBulkAssign:
    """Tests for CharacterTraitsService.bulk_assign method."""

    @respx.mock
    async def test_bulk_assign_success(
        self, vclient, base_url, bulk_assign_all_success_response_data
    ) -> None:
        """Verify bulk assigning traits returns BulkAssignTraitResponse with all successes."""
        # Given: A mocked bulk-assign endpoint
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_BULK_ASSIGN.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json=bulk_assign_all_success_response_data))

        # When: Bulk assigning traits
        items = [
            CharacterTraitAdd(trait_id="trait1", value=2, currency="NO_COST"),
            CharacterTraitAdd(trait_id="trait2", value=1, currency="XP"),
        ]
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).bulk_assign(items)

        # Then: The route was called and response is parsed correctly
        assert route.called
        assert isinstance(result, BulkAssignTraitResponse)
        assert len(result.succeeded) == 2
        assert len(result.failed) == 0
        assert result.succeeded[0].trait_id == "trait1"
        assert isinstance(result.succeeded[0].character_trait, CharacterTrait)

        # Verify request body is a JSON list
        body = json.loads(route.calls[0].request.content)
        assert isinstance(body, list)
        assert len(body) == 2
        assert body[0]["trait_id"] == "trait1"
        assert body[0]["value"] == 2
        assert body[0]["currency"] == "NO_COST"

    @respx.mock
    async def test_bulk_assign_mixed_results(
        self, vclient, base_url, bulk_assign_response_data
    ) -> None:
        """Verify bulk assign with mixed succeeded and failed items."""
        # Given: A mocked endpoint returning mixed results
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_BULK_ASSIGN.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json=bulk_assign_response_data))

        # When: Bulk assigning traits
        items = [
            CharacterTraitAdd(trait_id="trait1", value=2, currency="NO_COST"),
            CharacterTraitAdd(trait_id="trait2", value=1, currency="XP"),
        ]
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).bulk_assign(items)

        # Then: Both succeeded and failed lists are populated
        assert route.called
        assert len(result.succeeded) == 1
        assert len(result.failed) == 1
        assert result.failed[0].trait_id == "trait2"
        assert result.failed[0].error == "Not enough XP to add trait"

    @respx.mock
    async def test_bulk_assign_empty_list(self, vclient, base_url) -> None:
        """Verify bulk assign with empty list returns empty response."""
        # Given: A mocked endpoint returning empty results
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_BULK_ASSIGN.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(200, json={"succeeded": [], "failed": []}))

        # When: Bulk assigning an empty list
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).bulk_assign([])

        # Then: Both lists are empty
        assert route.called
        assert result.succeeded == []
        assert result.failed == []

    @respx.mock
    async def test_bulk_assign_validation_error(self, vclient, base_url) -> None:
        """Verify bulk assign over batch limit raises ValidationError."""
        # Given: A mocked 400 response for exceeding batch limit
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_BULK_ASSIGN.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(
            return_value=Response(
                400,
                json={"detail": "Batch size must not exceed 200 items", "status_code": 400},
            )
        )

        # When/Then: Bulk assigning raises ValidationError
        items = [CharacterTraitAdd(trait_id="t1", value=1, currency="NO_COST")]
        with pytest.raises(ValidationError):
            await vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).bulk_assign(items)

        assert route.called
