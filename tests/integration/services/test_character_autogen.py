"""Integration tests for CharacterAutogenService."""

import pytest
import respx
from httpx import Response

from vclient.endpoints import Endpoints
from vclient.models import Character, ChargenSessionResponse

pytestmark = pytest.mark.anyio


@pytest.fixture
def character_autogen_response_data(character_response_data: dict) -> dict:
    """Return sample character autogen response data."""
    return {
        "session_id": "session123",
        "expires_at": "2024-01-15T10:30:00Z",
        "requires_selection": True,
        "characters": [character_response_data, character_response_data],
    }


class TestCharacterAutogenService:
    """Tests for CharacterAutogenService."""

    @respx.mock
    async def test_start_chargen_session(
        self, vclient, base_url, character_autogen_response_data
    ) -> None:
        """Verify starting a chargen session returns ChargenSessionResponse."""
        # Given: A mocked endpoint returning ChargenSessionResponse
        route = respx.post(
            f"{base_url}{Endpoints.CHARGEN_START.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(200, json=character_autogen_response_data))

        # When: Starting a chargen session
        result = await vclient.character_autogen(
            "company123", "user123", "campaign123"
        ).start_chargen_session()

        # Then: The route was called with correct params
        assert route.called
        assert isinstance(result, ChargenSessionResponse)
        assert result.session_id == "session123"


class TestCharacterAutogenServiceFinalizeChargenSession:
    """Tests for CharacterAutogenService finalize_chargen_session."""

    @respx.mock
    async def test_finalize_chargen_session(
        self, vclient, base_url, character_response_data: dict
    ) -> None:
        """Verify finalizing a chargen session returns Character."""
        # Given: A mocked endpoint returning Character
        route = respx.post(
            f"{base_url}{Endpoints.CHARGEN_FINALIZE.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(200, json=character_response_data))

        # When: Finalizing a chargen session
        result = await vclient.character_autogen(
            "company123", "user123", "campaign123"
        ).finalize_chargen_session("session123", "char123")

        # Then: The route was called with correct params
        assert route.called
        assert isinstance(result, Character)
        assert result.id == "char123"
        assert result.name_first == "John"
        assert result.name_last == "Doe"
        assert result.character_class == "VAMPIRE"
        assert result.game_version == "V5"


class TestCharacterAutogenerateCharacter:
    """Tests for CharacterAutogenService generate_character."""

    @respx.mock
    async def test_generate_character(
        self, vclient, base_url, character_response_data: dict
    ) -> None:
        """Verify generating a character returns Character."""
        # Given: A mocked endpoint returning Character
        route = respx.post(
            f"{base_url}{Endpoints.AUTOGENERATE.format(company_id='company123', user_id='user123', campaign_id='campaign123')}"
        ).mock(return_value=Response(200, json=character_response_data))

        # When: Generating a character
        result = await vclient.character_autogen(
            "company123", "user123", "campaign123"
        ).generate_character(character_type="PLAYER")

        # Then: The route was called with correct params
        assert route.called
        assert isinstance(result, Character)
        assert result.id == "char123"
        assert result.name_first == "John"
