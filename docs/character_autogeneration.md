# Character Autogeneration

The Character Autogeneration service provides methods to generate characters for a campaign.

## Usage

The character autogen service is scoped to a specific company, user, and campaign context at creation time:

```python
from vclient import VClient

async with VClient(base_url="...", api_key="...") as client:
    character_autogen = client.character_autogen(company_id="company123", user_id="user123", campaign_id="campaign123")

    character=await character_autogen.generate_character(character_type="PLAYER")
```

## Available Methods

### Generate Character

- `generate_character(character_type: CharacterType, character_class: CharacterClass | None = None, experience_level: AutoGenExperienceLevel | None = None, skill_focus: AbilityFocus | None = None, concept_id: str | None = None, vampire_clan_id: str | None = None, werewolf_tribe_id: str | None = None, werewolf_auspice_id: str | None = None) -> Character` - Generate a character

### Start Chargen Session

- `start_chargen_session() -> ChargenSessionResponse` - Start a chargen session

### Finalize Chargen Session

- `finalize_chargen_session(session_id: str, selected_character_id: str) -> Character` - Finalize a chargen session

## Response Models

### ChargenSessionResponse

| Field              | Type            | Description                                       |
| ------------------ | --------------- | ------------------------------------------------- |
| session_id         | str             | The ID of the chargen session.                    |
| expires_at         | datetime        | The date and time the chargen session expires.    |
| requires_selection | bool            | Whether the chargen session requires a selection. |
| characters         | list[Character] | The characters available in the chargen session.  |
