"""Integration tests for DicreollService."""

import json

import pytest
import respx

from vclient.endpoints import Endpoints
from vclient.exceptions import NotFoundError
from vclient.models import Dicreoll, PaginatedResponse

pytestmark = pytest.mark.anyio


@pytest.fixture
def dicreoll_response_data() -> dict:
    """Return sample dicreoll response data."""
    return {
        "id": "dicreoll123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "dice_size": 10,
        "difficulty": 6,
        "num_dice": 1,
        "num_desperation_dice": 0,
        "comment": "A test comment",
        "trait_ids": ["trait1", "trait2"],
        "user_id": "user123",
        "character_id": "character123",
        "campaign_id": "campaign123",
        "company_id": "company123",
        "quickroll_id": "quickroll123",
        "result": {
            "total_result": 1,
            "total_result_type": "SUCCESS",
            "total_result_humanized": "Success",
            "total_dice_roll": [1],
            "player_roll": [1],
            "desperation_roll": [0],
            "player_roll_emoji": "🎲",
            "player_roll_shortcode": ":one:",
            "desperation_roll_emoji": "💥",
            "desperation_roll_shortcode": ":one:",
            "total_dice_roll_emoji": "🎲",
            "total_dice_roll_shortcode": ":one:",
            "total_result_emoji": "🎉",
            "total_result_shortcode": "1",
        },
    }


@pytest.fixture
def paginated_dicreolls_response(dicreoll_response_data) -> dict:
    """Return sample paginated dicreolls response."""
    return {
        "items": [dicreoll_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


class TestDicreollServiceGetPage:
    """Tests for DicreollService.get_page method."""

    @respx.mock
    async def test_get_page(self, vclient, base_url, paginated_dicreolls_response):
        """Verify getting a page of dicreolls."""
        # Given: A mocked dicreoll endpoint
        route = respx.get(
            f"{base_url}{Endpoints.DICREOLLS.format(company_id='company123', user_id='user123')}",
            params={"limit": "10", "offset": "0"},
        ).respond(200, json=paginated_dicreolls_response)

        # When: Getting a page of dicreolls
        result = await vclient.dicreolls(company_id="company123", user_id="user123").get_page()

        # Then: Returns paginated Dicreoll objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Dicreoll)
        assert result.items[0].id == "dicreoll123"
        assert result.total == 1
        assert result.items[0].result is not None
        assert result.items[0].result.total_result == 1
        assert result.items[0].result.total_result_type == "SUCCESS"
        assert result.items[0].result.total_result_humanized == "Success"
        assert result.items[0].result.total_dice_roll == [1]
        assert result.items[0].result.player_roll == [1]
        assert result.items[0].result.desperation_roll == [0]
        assert result.items[0].result.player_roll_emoji == "🎲"
        assert result.items[0].result.player_roll_shortcode == ":one:"
        assert result.items[0].result.desperation_roll_emoji == "💥"

    @respx.mock
    async def test_get_page_with_filters(self, vclient, base_url, paginated_dicreolls_response):
        """Verify get_page accepts filter parameters."""
        # Given: A mocked dicreoll endpoint
        route = respx.get(
            f"{base_url}{Endpoints.DICREOLLS.format(company_id='company123', user_id='user123')}",
            params={
                "limit": "10",
                "offset": "0",
                "userid": "user123",
                "characterid": "character123",
                "campaignid": "campaign123",
            },
        ).respond(200, json=paginated_dicreolls_response)

        # When: Getting a page of dicreolls with filters
        result = await vclient.dicreolls(company_id="company123", user_id="user123").get_page(
            userid="user123", characterid="character123", campaignid="campaign123"
        )

        # Then: Returns paginated Dicreoll objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Dicreoll)
        assert result.items[0].id == "dicreoll123"
        assert result.total == 1
        assert result.items[0].result is not None
        assert result.items[0].result.total_result == 1
        assert result.items[0].result.total_result_type == "SUCCESS"
        assert result.items[0].result.total_result_humanized == "Success"

    @respx.mock
    async def test_get_page_with_pagination(self, vclient, base_url, paginated_dicreolls_response):
        """Verify get_page accepts pagination parameters."""
        # Given: A mocked dicreoll endpoint
        route = respx.get(
            f"{base_url}{Endpoints.DICREOLLS.format(company_id='company123', user_id='user123')}",
            params={"limit": "25", "offset": "50"},
        ).respond(200, json=paginated_dicreolls_response)

        # When: Getting a page of dicreolls with pagination
        result = await vclient.dicreolls(company_id="company123", user_id="user123").get_page(
            limit=25, offset=50
        )

        # Then: Returns paginated Dicreoll objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Dicreoll)
        assert result.items[0].id == "dicreoll123"
        assert result.total == 1
        assert result.items[0].result is not None
        assert result.items[0].result.total_result == 1
        assert result.items[0].result.total_result_type == "SUCCESS"
        assert result.items[0].result.total_result_humanized == "Success"


class TestDicreollServiceListAll:
    """Tests for DicreollService.list_all method."""

    @respx.mock
    async def test_list_all(self, vclient, base_url, paginated_dicreolls_response):
        """Verify getting all dicreolls."""
        # Given: A mocked dicreoll endpoint
        route = respx.get(
            f"{base_url}{Endpoints.DICREOLLS.format(company_id='company123', user_id='user123')}",
        ).respond(200, json=paginated_dicreolls_response)

        # When: Getting all dicreolls
        result = await vclient.dicreolls(company_id="company123", user_id="user123").list_all()

        # Then: Returns list of Dicreoll objects
        assert route.called
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Dicreoll)
        assert result[0].id == "dicreoll123"
        assert result[0].result is not None
        assert result[0].result.total_result == 1

    @respx.mock
    async def test_list_all_with_filters(self, vclient, base_url, paginated_dicreolls_response):
        """Verify list_all accepts filter parameters."""
        # Given: A mocked dicreoll endpoint
        route = respx.get(
            f"{base_url}{Endpoints.DICREOLLS.format(company_id='company123', user_id='user123')}",
            params={
                "userid": "user123",
                "characterid": "character123",
                "campaignid": "campaign123",
            },
        ).respond(200, json=paginated_dicreolls_response)

        # When: Getting all dicreolls with filters
        result = await vclient.dicreolls(company_id="company123", user_id="user123").list_all(
            userid="user123", characterid="character123", campaignid="campaign123"
        )

        # Then: Returns list of Dicreoll objects
        assert route.called
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Dicreoll)
        assert result[0].id == "dicreoll123"
        assert result[0].result is not None
        assert result[0].result.total_result == 1


class TestDicreollServiceIterAll:
    """Tests for DicreollService.iter_all method."""

    @respx.mock
    async def test_iter_all(self, vclient, base_url, paginated_dicreolls_response):
        """Verify iterating through all dicreolls."""
        # Given: A mocked dicreoll endpoint
        route = respx.get(
            f"{base_url}{Endpoints.DICREOLLS.format(company_id='company123', user_id='user123')}",
        ).respond(200, json=paginated_dicreolls_response)

        # When: Iterating through all dicreolls
        result = [
            dicreoll
            async for dicreoll in vclient.dicreolls(
                company_id="company123", user_id="user123"
            ).iter_all()
        ]

        # Then: Returns list of Dicreoll objects
        assert route.called
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Dicreoll)
        assert result[0].id == "dicreoll123"
        assert result[0].result is not None
        assert result[0].result.total_result == 1


class TestDicreollServiceGet:
    """Tests for DicreollService.get method."""

    @respx.mock
    async def test_get(self, vclient, base_url, dicreoll_response_data):
        """Verify getting a dicreoll."""
        # Given: A mocked dicreoll endpoint
        route = respx.get(
            f"{base_url}{Endpoints.DICREOLL.format(company_id='company123', user_id='user123', dicreoll_id='dicreoll123')}",
        ).respond(200, json=dicreoll_response_data)

        # When: Getting a dicreoll
        result = await vclient.dicreolls(company_id="company123", user_id="user123").get(
            "dicreoll123"
        )

        # Then: Returns Dicreoll object
        assert route.called
        assert isinstance(result, Dicreoll)
        assert result.id == "dicreoll123"
        assert result.result is not None
        assert result.result.total_result == 1
        assert result.result.total_result_type == "SUCCESS"
        assert result.result.total_result_humanized == "Success"
        assert result.result.total_dice_roll == [1]
        assert result.result.player_roll == [1]
        assert result.result.desperation_roll == [0]

    @respx.mock
    async def test_get_not_found(self, vclient, base_url):
        """Verify getting a non-existent dicreoll raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        route = respx.get(
            f"{base_url}{Endpoints.DICREOLL.format(company_id='company123', user_id='user123', dicreoll_id='nonexistent')}",
        ).respond(404, json={"detail": "Dicreoll not found"})

        # When/Then: Getting the dicreoll raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.dicreolls(company_id="company123", user_id="user123").get("nonexistent")

        assert route.called


class TestDicreollServiceCreate:
    """Tests for DicreollService.create method."""

    @respx.mock
    async def test_create(self, vclient, base_url, dicreoll_response_data):
        """Verify creating a dicreoll."""
        # Given: A mocked dicreoll endpoint
        route = respx.post(
            f"{base_url}{Endpoints.DICREOLLS.format(company_id='company123', user_id='user123')}",
        ).respond(200, json=dicreoll_response_data)

        # When: Creating a dicreoll
        result = await vclient.dicreolls(company_id="company123", user_id="user123").create(
            dice_size=10,
            difficulty=6,
            num_dice=1,
            num_desperation_dice=0,
            comment="A test comment",
            trait_ids=["trait1", "trait2"],
            character_id="character123",
            campaign_id="campaign123",
        )

        # Then: Returns Dicreoll object
        assert route.called
        assert isinstance(result, Dicreoll)
        assert result.id == "dicreoll123"
        assert result.result is not None
        assert result.result.total_result == 1
        assert result.result.total_result_type == "SUCCESS"
        assert result.result.total_result_humanized == "Success"

        # Verify request body
        request = route.calls.last.request
        body = json.loads(request.content)
        assert body == {
            "dice_size": 10,
            "difficulty": 6,
            "num_dice": 1,
            "num_desperation_dice": 0,
            "comment": "A test comment",
            "trait_ids": ["trait1", "trait2"],
            "character_id": "character123",
            "campaign_id": "campaign123",
        }


class TestDicreollServiceCreateQuickroll:
    """Tests for DicreollService.create_quickroll method."""

    @respx.mock
    async def test_create_quickroll(self, vclient, base_url, dicreoll_response_data):
        """Verify creating a dicreoll quickroll."""
        # Given: A mocked dicreoll endpoint
        route = respx.post(
            f"{base_url}{Endpoints.DICEROLL_QUICKROLL.format(company_id='company123', user_id='user123')}",
        ).respond(200, json=dicreoll_response_data)

        # When: Creating a dicreoll quickroll
        result = await vclient.dicreolls(
            company_id="company123", user_id="user123"
        ).create_quickroll(
            quickroll_id="quickroll123",
            character_id="character123",
            comment="A test comment",
            difficulty=6,
            num_desperation_dice=0,
        )

        # Then: Returns Dicreoll object
        assert route.called
        assert isinstance(result, Dicreoll)

        # Verify request body
        request = route.calls.last.request
        body = json.loads(request.content)
        assert body == {
            "quickroll_id": "quickroll123",
            "character_id": "character123",
            "comment": "A test comment",
            "difficulty": 6,
            "num_desperation_dice": 0,
        }
