# Developer Experience Improvements Design

**Date:** 2026-02-04
**Status:** Approved
**Breaking Change:** Yes (clean break, new major version)

## Problem Statement

The current vclient API has DX issues:
- 40+ exports at top level, hard to discover what matters
- 90+ models exported flat, difficult to find related models
- Multiple import paths for the same functionality
- Inconsistent model naming (`CreateCharacterRequest` vs `HunterAttributesCreate`)
- Internal implementation details exposed (`BaseService`, `configure_default_client`)
- Complex nested models require many imports

## Design Goals

1. Clear, minimal top-level exports
2. Discoverable models via domain submodules
3. Consistent naming conventions
4. Flexible service API (request models or kwargs)
5. Hide internal implementation details

## Design

### 1. Top-Level Exports (`vclient/__init__.py`)

Export only essentials:

```python
from vclient import VClient, APIConfig

# Factory functions (primary access pattern)
from vclient import (
    books_service,
    campaigns_service,
    chapters_service,
    character_autogen_service,
    character_blueprint_service,
    character_traits_service,
    characters_service,
    companies_service,
    developer_service,
    dicreolls_service,
    dictionary_service,
    global_admin_service,
    options_service,
    system_service,
    users_service,
)
```

**Removed from top-level:**
- Service classes (use `vclient.services` if needed)
- Exception classes (use `vclient.exceptions`)
- All models (use `vclient.models`)
- `configure_default_client`, `default_client` (internal)

### 2. Exceptions (`vclient/exceptions.py`)

All exceptions imported from submodule:

```python
from vclient.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    RequestValidationError,
    ServerError,
    ValidationError,
)
```

### 3. Model Organization (`vclient/models/`)

#### Structure

```
vclient/models/
├── __init__.py        # Exports submodules + all public models
├── blueprint.py       # Character blueprint models
├── books.py           # Campaign book models
├── campaigns.py       # Campaign models
├── chapters.py        # Chapter models
├── characters.py      # Character models (largest)
├── companies.py       # Company models
├── developers.py      # Developer models
├── shared.py          # Cross-cutting: Note, S3Asset, PaginatedResponse
├── system.py          # System health models
├── traits.py          # Character trait models
└── users.py           # User models
```

#### Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Response | `Noun` | `Character`, `Campaign`, `User` |
| Create request | `NounCreate` | `CharacterCreate`, `CampaignCreate` |
| Update request | `NounUpdate` | `CharacterUpdate`, `CampaignUpdate` |
| Nested input | `Noun` | `HunterAttributes`, `HunterEdge` |

#### Export Rules

**Export (in `__all__`):**
- Response models developers receive
- Request models developers construct
- Nested models for complex inputs

**Don't export:**
- Internal request models built by service methods from primitives
- Examples: `RenumberChapterRequest`, `RenumberBookRequest`

#### Usage Patterns

```python
# Namespaced (recommended for complex domains)
from vclient.models import characters
request = characters.CharacterCreate(
    character_class="HUNTER",
    name_first="John",
    name_last="Doe",
    hunter_attributes=characters.HunterAttributesCreate(
        creed="Inquisitor",
        edges=[characters.HunterEdge(edge_id="123")]
    )
)

# Direct import (convenient for simple cases)
from vclient.models import Campaign, CampaignCreate, Note
```

### 4. Service Method API

Service methods accept **both** request models and kwargs:

```python
async def create(
    self,
    request: CharacterCreate | None = None,
    /,
    **kwargs,
) -> Character:
    """Create a new character.

    Args:
        request: A CharacterCreate model, OR pass fields as keyword arguments.
        **kwargs: Fields for CharacterCreate if request is not provided.
    """
    if request is None:
        request = CharacterCreate(**kwargs)
    # ... rest of method
```

**Simple case (kwargs):**
```python
campaign = await campaigns_service().create(
    name="My Campaign",
    description="A dark story"
)
```

**Complex case (request model):**
```python
from vclient.models import characters

character = await characters_service().create(
    characters.CharacterCreate(
        character_class="HUNTER",
        name_first="John",
        name_last="Doe",
        hunter_attributes=characters.HunterAttributesCreate(...)
    )
)
```

### 5. Advanced Access

For users who need direct access:

```python
# Service classes (for subclassing, testing, type hints)
from vclient.services import CharactersService, CampaignsService

# Internal utilities (for library extension)
from vclient.services import BaseService
from vclient.registry import configure_default_client, default_client
```

These are importable but not in top-level `__all__`.

## Model Renaming Reference

### characters.py

| Current | New |
|---------|-----|
| `Character` | `Character` |
| `CreateCharacterRequest` | `CharacterCreate` |
| `UpdateCharacterRequest` | `CharacterUpdate` |
| `CharacterInventoryItem` | `InventoryItem` |
| `CreateCharacterInventoryItemRequest` | `InventoryItemCreate` |
| `UpdateCharacterInventoryItemRequest` | `InventoryItemUpdate` |
| `VampireAttributes` | `VampireAttributes` |
| `VampireAttributesCreate` | `VampireAttributesCreate` |
| `VampireAttributesUpdate` | `VampireAttributesUpdate` |
| `WerewolfAttributes` | `WerewolfAttributes` |
| `WerewolfAttributesCreate` | `WerewolfAttributesCreate` |
| `WerewolfAttributesUpdate` | `WerewolfAttributesUpdate` |
| `HunterAttributes` | `HunterAttributes` |
| `HunterAttributesCreate` | `HunterAttributesCreate` |
| `HunterAttributesUpdate` | `HunterAttributesUpdate` |
| `HunterAttributesEdgeModel` | `HunterEdge` |
| `MageAttributes` | `MageAttributes` |
| `CharacterEdgeAndPerksDTO` | `EdgeAndPerks` |
| `CharacterPerkDTO` | `Perk` |

### campaigns.py

| Current | New |
|---------|-----|
| `Campaign` | `Campaign` |
| `CreateCampaignRequest` | `CampaignCreate` |
| `UpdateCampaignRequest` | `CampaignUpdate` |

### companies.py

| Current | New |
|---------|-----|
| `Company` | `Company` |
| `CreateCompanyRequest` | `CompanyCreate` |
| `UpdateCompanyRequest` | `CompanyUpdate` |
| `CompanyPermissions` | `Permissions` |
| `CompanySettings` | `Settings` |
| `NewCompanyResponse` | `CompanyWithApiKey` |
| `GrantAccessRequest` | *internal* |

### users.py

| Current | New |
|---------|-----|
| `User` | `User` |
| `CreateUserRequest` | `UserCreate` |
| `UpdateUserRequest` | `UserUpdate` |
| `DiscordProfile` | `DiscordProfile` |
| `CampaignExperience` | `CampaignExperience` |
| `Quickroll` | `Quickroll` |
| `CreateQuickrollRequest` | `QuickrollCreate` |
| `UpdateQuickrollRequest` | `QuickrollUpdate` |
| `ExperienceAddRemoveRequest` | *internal* |

### shared.py

| Current | New |
|---------|-----|
| `Note` | `Note` |
| `CreateNoteRequest` | `NoteCreate` |
| `UpdateNoteRequest` | `NoteUpdate` |
| `S3Asset` | `S3Asset` |
| `PaginatedResponse` | `PaginatedResponse` |
| `Trait` | `Trait` |
| `CharacterSpecialty` | `Specialty` |
| `RollStatistics` | `RollStatistics` |
| `NameDescriptionSubDocument` | *internal* |
| `WerewolfGift` | `WerewolfGift` |
| `WerewolfRite` | `WerewolfRite` |

### books.py

| Current | New |
|---------|-----|
| `CampaignBook` | `Book` |
| `CreateBookRequest` | `BookCreate` |
| `UpdateBookRequest` | `BookUpdate` |
| `RenumberBookRequest` | *internal* |

### chapters.py

| Current | New |
|---------|-----|
| `CampaignChapter` | `Chapter` |
| `CreateChapterRequest` | `ChapterCreate` |
| `UpdateChapterRequest` | `ChapterUpdate` |
| `RenumberChapterRequest` | *internal* |

### traits.py (character_trait.py)

| Current | New |
|---------|-----|
| `CharacterTrait` | `Trait` |
| `CreateCharacterTraitRequest` | `TraitCreate` |
| `CharacterTraitModifyRequest` | `TraitModify` |
| `AssignCharacterTraitRequest` | `TraitAssign` |
| `CharacterTraitValueOptionsResponse` | `TraitValueOptions` |

### developers.py

| Current | New |
|---------|-----|
| `MeDeveloper` | `Developer` |
| `MeDeveloperCompanyPermission` | `CompanyPermission` |
| `MeDeveloperWithApiKey` | `DeveloperWithApiKey` |
| `UpdateMeDeveloperRequest` | `DeveloperUpdate` |

### global_admin.py → admin.py

| Current | New |
|---------|-----|
| `Developer` | `Developer` |
| `DeveloperCompanyPermission` | `CompanyPermission` |
| `DeveloperWithApiKey` | `DeveloperWithApiKey` |
| `CreateDeveloperRequest` | `DeveloperCreate` |
| `UpdateDeveloperRequest` | `DeveloperUpdate` |

### blueprint.py (character_blueprint.py)

| Current | New |
|---------|-----|
| `SheetSection` | `Section` |
| `TraitCategory` | `Category` |
| `CharacterConcept` | `Concept` |
| `VampireClan` | `VampireClan` |
| `WerewolfTribe` | `WerewolfTribe` |
| `WerewolfAuspice` | `WerewolfAuspice` |
| `HunterEdge` | `HunterEdge` |
| `HunterEdgePerk` | `HunterEdgePerk` |

### system.py

| Current | New |
|---------|-----|
| `SystemHealth` | `Health` |

### diceroll.py → dicerolls.py

| Current | New |
|---------|-----|
| `Dicreoll` | `Diceroll` |
| `CreateDicreollRequest` | `DicerollCreate` |
| `CreateDicreollQuickrollRequest` | *internal* |

### dictionary.py

| Current | New |
|---------|-----|
| `DictionaryTerm` | `Term` |
| `CreateDictionaryTermRequest` | `TermCreate` |
| `UpdateDictionaryTermRequest` | `TermUpdate` |

### character_autogen.py → autogen.py

| Current | New |
|---------|-----|
| `ChargenSessionResponse` | `Session` |
| `ChargenSessionFinalizeDTO` | `SessionFinalize` |
| `CreateAutogenerateDTO` | `AutogenCreate` |

## Implementation Tasks

1. Create domain submodule files with renamed models
2. Update `vclient/models/__init__.py` exports
3. Update `vclient/__init__.py` exports
4. Update service methods to accept request model or kwargs
5. Update all internal imports in services
6. Update tests
7. Update documentation
8. Bump to v1.0.0

## Migration Notes

This is a breaking change. Users upgrading must:
1. Update imports from `vclient` to `vclient.exceptions` for exceptions
2. Update imports from `vclient` or `vclient.models` using new names
3. Service method signatures unchanged (kwargs still work)
