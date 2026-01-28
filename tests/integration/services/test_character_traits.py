"""Integration tests for CharacterTraitsService."""

import pytest
import respx
from httpx import Response

from vclient.endpoints import Endpoints
from vclient.exceptions import NotFoundError
from vclient.models import CharacterTrait, PaginatedResponse

pytestmark = pytest.mark.anyio


@pytest.fixture
def trait_response_data() -> dict:
    """Return sample trait response data."""
    return {
        "id": "trait123",
        "name": "Strength",
        "description": "Physical power and might",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "link": None,
        "show_when_zero": True,
        "max_value": 5,
        "min_value": 0,
        "is_custom": False,
        "initial_cost": 1,
        "upgrade_cost": 2,
        "sheet_section_name": "Attributes",
        "sheet_section_id": "section123",
        "parent_category_name": "Physical",
        "parent_category_id": "cat123",
        "custom_for_character_id": None,
        "advantage_category_id": None,
        "advantage_category_name": None,
        "character_classes": ["VAMPIRE", "WEREWOLF"],
        "game_versions": ["V5"],
    }


@pytest.fixture
def character_trait_response_data(trait_response_data: dict) -> dict:
    """Return sample character trait response data."""
    return {
        "id": "ct123",
        "character_id": "char123",
        "value": 3,
        "trait": trait_response_data,
    }


@pytest.fixture
def paginated_character_trait_response(character_trait_response_data: dict) -> dict:
    """Return a paginated response with character traits."""
    return {
        "items": [character_trait_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
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
    async def test_get_page_with_parent_category_filter(
        self, vclient, base_url, paginated_character_trait_response
    ) -> None:
        """Verify get_page filters by parent_category_id."""
        # Given: A mocked endpoint expecting filter params
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "10", "offset": "0", "parent_category_id": "cat123"},
        ).mock(return_value=Response(200, json=paginated_character_trait_response))

        # When: Requesting with filter
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).get_page(parent_category_id="cat123")

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
    async def test_list_all_with_parent_category_filter(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify list_all filters by parent_category_id."""
        # Given: A mocked endpoint expecting filter params
        paginated_response = {
            "items": [character_trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "100", "offset": "0", "parent_category_id": "cat123"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Requesting with filter
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).list_all(parent_category_id="cat123")

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
        """Verify iter_all filters by parent_category_id."""
        # Given: A mocked endpoint expecting filter params
        paginated_response = {
            "items": [character_trait_response_data],
            "limit": 100,
            "offset": 0,
            "total": 1,
        }
        route = respx.get(
            f"{base_url}{Endpoints.CHARACTER_TRAITS.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}",
            params={"limit": "100", "offset": "0", "parent_category_id": "cat456"},
        ).mock(return_value=Response(200, json=paginated_response))

        # When: Iterating with filter
        traits = [
            trait
            async for trait in vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).iter_all(parent_category_id="cat456")
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
            f"{base_url}{Endpoints.CHARACTER_TRAIT_CREATE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(201, json=character_trait_response_data))

        # When: Assigning a trait
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).assign(trait_id="trait123", value=3)

        # Then: The route was called and character trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.id == "ct123"
        assert result.value == 3

        # Verify request body
        import json

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
            f"{base_url}{Endpoints.CHARACTER_TRAIT_CREATE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(201, json=response_data))

        # When: Assigning a trait with value 0
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).assign(trait_id="trait123", value=0)

        # Then: The route was called and character trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.value == 0

    @respx.mock
    async def test_assign_trait_not_found(self, vclient, base_url) -> None:
        """Verify assigning a non-existent trait raises NotFoundError."""
        # Given: A mocked 404 response
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_CREATE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123')}"
        ).mock(return_value=Response(404, json={"detail": "Trait not found", "status_code": 404}))

        # When/Then: Assigning raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).assign(trait_id="nonexistent", value=1)

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
            parent_category_id="cat123",
        )

        # Then: The route was called and character trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.trait.name == "Custom Skill"

        # Verify request body contains required fields
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["name"] == "Custom Skill"
        assert body["parent_category_id"] == "cat123"
        assert body["max_value"] == 5
        assert body["min_value"] == 0

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
            parent_category_id="backgrounds_cat",
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
        assert body["parent_category_id"] == "backgrounds_cat"
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
            parent_category_id="cat123",
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
                parent_category_id="nonexistent_cat",
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


class TestCharacterTraitsServiceIncrease:
    """Tests for CharacterTraitsService.increase method."""

    @respx.mock
    async def test_increase_trait(self, vclient, base_url, character_trait_response_data) -> None:
        """Verify increasing a character trait value."""
        # Given: A mocked increase endpoint with updated value
        response_data = {**character_trait_response_data, "value": 4}
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_INCREASE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}"
        ).mock(return_value=Response(200, json=response_data))

        # When: Increasing the trait
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).increase("ct123", num_dots=1)

        # Then: The route was called and updated trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.value == 4

        # Verify request body
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["num_dots"] == 1

    @respx.mock
    async def test_increase_trait_multiple_dots(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify increasing a trait by multiple dots."""
        # Given: A mocked increase endpoint
        response_data = {**character_trait_response_data, "value": 5}
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_INCREASE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}"
        ).mock(return_value=Response(200, json=response_data))

        # When: Increasing by 2 dots
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).increase("ct123", num_dots=2)

        # Then: Updated trait is returned
        assert route.called
        assert result.value == 5


class TestCharacterTraitsServiceDecrease:
    """Tests for CharacterTraitsService.decrease method."""

    @respx.mock
    async def test_decrease_trait(self, vclient, base_url, character_trait_response_data) -> None:
        """Verify decreasing a character trait value."""
        # Given: A mocked decrease endpoint with updated value
        response_data = {**character_trait_response_data, "value": 2}
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_DECREASE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}"
        ).mock(return_value=Response(200, json=response_data))

        # When: Decreasing the trait
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).decrease("ct123", num_dots=1)

        # Then: The route was called and updated trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.value == 2

        # Verify request body
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["num_dots"] == 1


class TestCharacterTraitsServicePurchaseXp:
    """Tests for CharacterTraitsService.purchase_xp method."""

    @respx.mock
    async def test_purchase_xp(self, vclient, base_url, character_trait_response_data) -> None:
        """Verify purchasing trait dots with XP."""
        # Given: A mocked purchase endpoint with updated value
        response_data = {**character_trait_response_data, "value": 4}
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_XP_PURCHASE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}"
        ).mock(return_value=Response(200, json=response_data))

        # When: Purchasing with XP
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).purchase_xp("ct123", num_dots=1)

        # Then: The route was called and updated trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.value == 4

        # Verify request body
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["num_dots"] == 1

    @respx.mock
    async def test_purchase_xp_not_found(self, vclient, base_url) -> None:
        """Verify purchasing XP for non-existent trait raises NotFoundError."""
        # Given: A mocked 404 response
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_XP_PURCHASE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='nonexistent')}"
        ).mock(return_value=Response(404, json={"detail": "Trait not found", "status_code": 404}))

        # When/Then: Purchasing raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.character_traits(
                user_id="user123",
                campaign_id="campaign123",
                character_id="char123",
                company_id="company123",
            ).purchase_xp("nonexistent", num_dots=1)

        assert route.called


class TestCharacterTraitsServiceRefundXp:
    """Tests for CharacterTraitsService.refund_xp method."""

    @respx.mock
    async def test_refund_xp(self, vclient, base_url, character_trait_response_data) -> None:
        """Verify refunding trait dots for XP."""
        # Given: A mocked refund endpoint with updated value
        response_data = {**character_trait_response_data, "value": 2}
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_XP_REFUND.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}"
        ).mock(return_value=Response(200, json=response_data))

        # When: Refunding XP
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).refund_xp("ct123", num_dots=1)

        # Then: The route was called and updated trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.value == 2

        # Verify request body
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["num_dots"] == 1


class TestCharacterTraitsServicePurchaseStartingPoints:
    """Tests for CharacterTraitsService.purchase_starting_points method."""

    @respx.mock
    async def test_purchase_starting_points(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify purchasing trait dots with starting points."""
        # Given: A mocked purchase endpoint with updated value
        response_data = {**character_trait_response_data, "value": 4}
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_STARTINGPOINTS_PURCHASE.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}"
        ).mock(return_value=Response(200, json=response_data))

        # When: Purchasing with starting points
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).purchase_starting_points("ct123", num_dots=1)

        # Then: The route was called and updated trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.value == 4

        # Verify request body
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["num_dots"] == 1


class TestCharacterTraitsServiceRefundStartingPoints:
    """Tests for CharacterTraitsService.refund_starting_points method."""

    @respx.mock
    async def test_refund_starting_points(
        self, vclient, base_url, character_trait_response_data
    ) -> None:
        """Verify refunding trait dots for starting points."""
        # Given: A mocked refund endpoint with updated value
        response_data = {**character_trait_response_data, "value": 2}
        route = respx.post(
            f"{base_url}{Endpoints.CHARACTER_TRAIT_STARTINGPOINTS_REFUND.format(company_id='company123', user_id='user123', campaign_id='campaign123', character_id='char123', character_trait_id='ct123')}"
        ).mock(return_value=Response(200, json=response_data))

        # When: Refunding starting points
        result = await vclient.character_traits(
            user_id="user123",
            campaign_id="campaign123",
            character_id="char123",
            company_id="company123",
        ).refund_starting_points("ct123", num_dots=1)

        # Then: The route was called and updated trait is returned
        assert route.called
        assert isinstance(result, CharacterTrait)
        assert result.value == 2

        # Verify request body
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["num_dots"] == 1


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
