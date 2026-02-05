# DX Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Improve developer experience by reorganizing exports, renaming models consistently, and adding hybrid service method API.

**Architecture:** Reorganize `vclient.models` into domain submodules with consistent `Noun`/`NounCreate`/`NounUpdate` naming. Update `vclient/__init__.py` to export only essentials. Modify service methods to accept both request models and kwargs.

**Tech Stack:** Python 3.13, Pydantic v2, pytest

---

## Phase 1: Model Reorganization

### Task 1: Rename models in characters.py

**Files:**
- Modify: `src/vclient/models/characters.py`

**Step 1: Rename request models**

Change class names:
- `CreateCharacterRequest` → `CharacterCreate`
- `UpdateCharacterRequest` → `CharacterUpdate`
- `CharacterInventoryItem` → `InventoryItem`
- `CreateCharacterInventoryItemRequest` → `InventoryItemCreate`
- `UpdateCharacterInventoryItemRequest` → `InventoryItemUpdate`
- `HunterAttributesEdgeModel` → `HunterEdge`
- `CharacterEdgeAndPerksDTO` → `EdgeAndPerks`
- `CharacterPerkDTO` → `Perk`

**Step 2: Add `__all__` to characters.py**

```python
__all__ = [
    "Character",
    "CharacterCreate",
    "CharacterUpdate",
    "EdgeAndPerks",
    "HunterAttributes",
    "HunterAttributesCreate",
    "HunterAttributesUpdate",
    "HunterEdge",
    "InventoryItem",
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "MageAttributes",
    "Perk",
    "VampireAttributes",
    "VampireAttributesCreate",
    "VampireAttributesUpdate",
    "WerewolfAttributes",
    "WerewolfAttributesCreate",
    "WerewolfAttributesUpdate",
]
```

**Step 3: Run tests to verify nothing broke**

Run: `uv run pytest tests/ -v --tb=short -q`
Expected: All tests pass (will fail due to import changes - fix in Task 2)

**Step 4: Commit**

```bash
git add src/vclient/models/characters.py
git commit -m "refactor(models): rename character models to NounCreate/NounUpdate pattern"
```

---

### Task 2: Update character service imports

**Files:**
- Modify: `src/vclient/services/characters.py`

**Step 1: Update imports to use new names**

Change:
```python
from vclient.models import (
    AssignCharacterTraitRequest,
    Character,
    CharacterEdgeAndPerksDTO,
    CharacterInventoryItem,
    CharacterPerkDTO,
    CreateCharacterInventoryItemRequest,
    CreateCharacterRequest,
    ...
)
```

To:
```python
from vclient.models import (
    Character,
    CharacterCreate,
    CharacterUpdate,
    EdgeAndPerks,
    HunterAttributesCreate,
    HunterAttributesUpdate,
    InventoryItem,
    InventoryItemCreate,
    InventoryItemUpdate,
    MageAttributes,
    Perk,
    VampireAttributesCreate,
    VampireAttributesUpdate,
    WerewolfAttributesCreate,
    WerewolfAttributesUpdate,
)
from vclient.models.traits import TraitAssign
```

**Step 2: Update all references in method bodies**

Replace all occurrences:
- `CreateCharacterRequest` → `CharacterCreate`
- `UpdateCharacterRequest` → `CharacterUpdate`
- `CharacterInventoryItem` → `InventoryItem`
- `CreateCharacterInventoryItemRequest` → `InventoryItemCreate`
- `UpdateCharacterInventoryItemRequest` → `InventoryItemUpdate`
- `CharacterEdgeAndPerksDTO` → `EdgeAndPerks`
- `CharacterPerkDTO` → `Perk`

**Step 3: Run tests**

Run: `uv run pytest tests/test_characters.py -v --tb=short`
Expected: All character tests pass

**Step 4: Commit**

```bash
git add src/vclient/services/characters.py
git commit -m "refactor(services): update character service to use renamed models"
```

---

### Task 3: Rename models in campaigns.py

**Files:**
- Modify: `src/vclient/models/campaigns.py`

**Step 1: Rename request models**

Change class names:
- `CreateCampaignRequest` → `CampaignCreate`
- `UpdateCampaignRequest` → `CampaignUpdate`

**Step 2: Add `__all__`**

```python
__all__ = [
    "Campaign",
    "CampaignCreate",
    "CampaignUpdate",
]
```

**Step 3: Commit**

```bash
git add src/vclient/models/campaigns.py
git commit -m "refactor(models): rename campaign models to NounCreate/NounUpdate pattern"
```

---

### Task 4: Update campaign service imports

**Files:**
- Modify: `src/vclient/services/campaigns.py`

**Step 1: Update imports and references**

Replace:
- `CreateCampaignRequest` → `CampaignCreate`
- `UpdateCampaignRequest` → `CampaignUpdate`

**Step 2: Run tests**

Run: `uv run pytest tests/test_campaigns.py -v --tb=short`

**Step 3: Commit**

```bash
git add src/vclient/services/campaigns.py
git commit -m "refactor(services): update campaign service to use renamed models"
```

---

### Task 5: Rename models in books.py

**Files:**
- Modify: `src/vclient/models/books.py`

**Step 1: Rename models**

- `CampaignBook` → `Book`
- `CreateBookRequest` → `BookCreate`
- `UpdateBookRequest` → `BookUpdate`
- `RenumberBookRequest` → `_RenumberBookRequest` (internal)

**Step 2: Add `__all__`**

```python
__all__ = [
    "Book",
    "BookCreate",
    "BookUpdate",
]
```

**Step 3: Commit**

```bash
git add src/vclient/models/books.py
git commit -m "refactor(models): rename book models to NounCreate/NounUpdate pattern"
```

---

### Task 6: Update books service imports

**Files:**
- Modify: `src/vclient/services/campaign_books.py`

**Step 1: Update imports and references**

**Step 2: Run tests and commit**

---

### Task 7: Rename models in chapters.py

**Files:**
- Modify: `src/vclient/models/chapters.py`

**Step 1: Rename models**

- `CampaignChapter` → `Chapter`
- `CreateChapterRequest` → `ChapterCreate`
- `UpdateChapterRequest` → `ChapterUpdate`
- `RenumberChapterRequest` → `_RenumberChapterRequest` (internal)

**Step 2: Add `__all__`**

```python
__all__ = [
    "Chapter",
    "ChapterCreate",
    "ChapterUpdate",
]
```

**Step 3: Commit**

---

### Task 8: Update chapters service imports

**Files:**
- Modify: `src/vclient/services/campaign_book_chapters.py`

---

### Task 9: Rename models in companies.py

**Files:**
- Modify: `src/vclient/models/companies.py`

**Step 1: Rename models**

- `CreateCompanyRequest` → `CompanyCreate`
- `UpdateCompanyRequest` → `CompanyUpdate`
- `CompanyPermissions` → `Permissions`
- `CompanySettings` → `Settings`
- `NewCompanyResponse` → `CompanyWithApiKey`
- `GrantAccessRequest` → `_GrantAccessRequest` (internal)

**Step 2: Add `__all__`**

```python
__all__ = [
    "Company",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyWithApiKey",
    "Permissions",
    "Settings",
]
```

**Step 3: Commit**

---

### Task 10: Update companies service imports

**Files:**
- Modify: `src/vclient/services/companies.py`

---

### Task 11: Rename models in users.py

**Files:**
- Modify: `src/vclient/models/users.py`

**Step 1: Rename models**

- `CreateUserRequest` → `UserCreate`
- `UpdateUserRequest` → `UserUpdate`
- `CreateQuickrollRequest` → `QuickrollCreate`
- `UpdateQuickrollRequest` → `QuickrollUpdate`
- `ExperienceAddRemoveRequest` → `_ExperienceAddRemoveRequest` (internal)

**Step 2: Add `__all__`**

```python
__all__ = [
    "CampaignExperience",
    "DiscordProfile",
    "Quickroll",
    "QuickrollCreate",
    "QuickrollUpdate",
    "User",
    "UserCreate",
    "UserUpdate",
]
```

**Step 3: Commit**

---

### Task 12: Update users service imports

**Files:**
- Modify: `src/vclient/services/users.py`

---

### Task 13: Rename models in shared.py

**Files:**
- Modify: `src/vclient/models/shared.py`

**Step 1: Rename models**

- `CreateNoteRequest` → `NoteCreate`
- `UpdateNoteRequest` → `NoteUpdate`
- `CharacterSpecialty` → `Specialty`
- `NameDescriptionSubDocument` → `_NameDescriptionSubDocument` (internal)

**Step 2: Add `__all__`**

```python
__all__ = [
    "Note",
    "NoteCreate",
    "NoteUpdate",
    "PaginatedResponse",
    "RollStatistics",
    "S3Asset",
    "Specialty",
    "Trait",
    "WerewolfGift",
    "WerewolfRite",
]
```

**Step 3: Commit**

---

### Task 14: Rename models in character_trait.py → traits.py

**Files:**
- Rename: `src/vclient/models/character_trait.py` → `src/vclient/models/traits.py`

**Step 1: Rename file and models**

- `CharacterTrait` → `Trait`
- `CreateCharacterTraitRequest` → `TraitCreate`
- `CharacterTraitModifyRequest` → `TraitModify`
- `AssignCharacterTraitRequest` → `TraitAssign`
- `CharacterTraitValueOptionsResponse` → `TraitValueOptions`

**Step 2: Add `__all__`**

```python
__all__ = [
    "Trait",
    "TraitAssign",
    "TraitCreate",
    "TraitModify",
    "TraitValueOptions",
]
```

**Step 3: Update imports in character_traits service**

**Step 4: Commit**

---

### Task 15: Rename models in developers.py

**Files:**
- Modify: `src/vclient/models/developers.py`

**Step 1: Rename models**

- `MeDeveloper` → `Developer`
- `MeDeveloperCompanyPermission` → `CompanyPermission`
- `MeDeveloperWithApiKey` → `DeveloperWithApiKey`
- `UpdateMeDeveloperRequest` → `DeveloperUpdate`

**Step 2: Add `__all__`**

**Step 3: Update developers service**

**Step 4: Commit**

---

### Task 16: Rename models in global_admin.py → admin.py

**Files:**
- Rename: `src/vclient/models/global_admin.py` → `src/vclient/models/admin.py`

**Step 1: Rename models**

- `CreateDeveloperRequest` → `DeveloperCreate`
- `UpdateDeveloperRequest` → `DeveloperUpdate`

Note: `Developer`, `DeveloperCompanyPermission`, `DeveloperWithApiKey` stay same but may conflict with developers.py - need to namespace or use different approach.

**Step 2: Add `__all__`**

**Step 3: Update global_admin service**

**Step 4: Commit**

---

### Task 17: Rename models in character_blueprint.py → blueprint.py

**Files:**
- Rename: `src/vclient/models/character_blueprint.py` → `src/vclient/models/blueprint.py`

**Step 1: Rename models**

- `SheetSection` → `Section`
- `TraitCategory` → `Category`
- `CharacterConcept` → `Concept`

**Step 2: Add `__all__`**

**Step 3: Update character_blueprint service**

**Step 4: Commit**

---

### Task 18: Rename models in system.py

**Files:**
- Modify: `src/vclient/models/system.py`

**Step 1: Rename models**

- `SystemHealth` → `Health`

**Step 2: Add `__all__`**

**Step 3: Commit**

---

### Task 19: Rename models in diceroll.py → dicerolls.py

**Files:**
- Rename: `src/vclient/models/diceroll.py` → `src/vclient/models/dicerolls.py`

**Step 1: Rename models**

- `Dicreoll` → `Diceroll`
- `CreateDicreollRequest` → `DicerollCreate`
- `CreateDicreollQuickrollRequest` → `_QuickrollCreate` (internal)

**Step 2: Add `__all__`**

**Step 3: Update diecrolls service**

**Step 4: Commit**

---

### Task 20: Rename models in dictionary.py

**Files:**
- Modify: `src/vclient/models/dictionary.py`

**Step 1: Rename models**

- `DictionaryTerm` → `Term`
- `CreateDictionaryTermRequest` → `TermCreate`
- `UpdateDictionaryTermRequest` → `TermUpdate`

**Step 2: Add `__all__`**

**Step 3: Update dictionary service**

**Step 4: Commit**

---

### Task 21: Rename models in character_autogen.py → autogen.py

**Files:**
- Rename: `src/vclient/models/character_autogen.py` → `src/vclient/models/autogen.py`

**Step 1: Rename models**

- `ChargenSessionResponse` → `Session`
- `ChargenSessionFinalizeDTO` → `SessionFinalize`
- `CreateAutogenerateDTO` → `AutogenCreate`

**Step 2: Add `__all__`**

**Step 3: Update character_autogen service**

**Step 4: Commit**

---

## Phase 2: Update models/__init__.py

### Task 22: Rewrite models/__init__.py

**Files:**
- Modify: `src/vclient/models/__init__.py`

**Step 1: Import submodules**

```python
"""Data models for API responses."""

from . import (
    admin,
    autogen,
    blueprint,
    books,
    campaigns,
    chapters,
    characters,
    companies,
    developers,
    dicerolls,
    dictionary,
    shared,
    system,
    traits,
    users,
)
```

**Step 2: Import all public models for direct access**

```python
from .admin import (
    CompanyPermission as AdminCompanyPermission,
    Developer as AdminDeveloper,
    DeveloperCreate as AdminDeveloperCreate,
    DeveloperUpdate as AdminDeveloperUpdate,
    DeveloperWithApiKey as AdminDeveloperWithApiKey,
)
from .autogen import AutogenCreate, Session, SessionFinalize
from .blueprint import (
    Category,
    Concept,
    HunterEdge as BlueprintHunterEdge,
    HunterEdgePerk,
    Section,
    VampireClan,
    WerewolfAuspice,
    WerewolfTribe,
)
from .books import Book, BookCreate, BookUpdate
from .campaigns import Campaign, CampaignCreate, CampaignUpdate
from .chapters import Chapter, ChapterCreate, ChapterUpdate
from .characters import (
    Character,
    CharacterCreate,
    CharacterUpdate,
    EdgeAndPerks,
    HunterAttributes,
    HunterAttributesCreate,
    HunterAttributesUpdate,
    HunterEdge,
    InventoryItem,
    InventoryItemCreate,
    InventoryItemUpdate,
    MageAttributes,
    Perk,
    VampireAttributes,
    VampireAttributesCreate,
    VampireAttributesUpdate,
    WerewolfAttributes,
    WerewolfAttributesCreate,
    WerewolfAttributesUpdate,
)
from .companies import (
    Company,
    CompanyCreate,
    CompanyUpdate,
    CompanyWithApiKey,
    Permissions,
    Settings,
)
from .developers import (
    CompanyPermission,
    Developer,
    DeveloperUpdate,
    DeveloperWithApiKey,
)
from .dicerolls import Diceroll, DicerollCreate
from .dictionary import Term, TermCreate, TermUpdate
from .shared import (
    Note,
    NoteCreate,
    NoteUpdate,
    PaginatedResponse,
    RollStatistics,
    S3Asset,
    Specialty,
    Trait,
    WerewolfGift,
    WerewolfRite,
)
from .system import Health
from .traits import (
    Trait as CharacterTrait,
    TraitAssign,
    TraitCreate,
    TraitModify,
    TraitValueOptions,
)
from .users import (
    CampaignExperience,
    DiscordProfile,
    Quickroll,
    QuickrollCreate,
    QuickrollUpdate,
    User,
    UserCreate,
    UserUpdate,
)
```

**Step 3: Define `__all__`**

```python
__all__ = [
    # Submodules
    "admin",
    "autogen",
    "blueprint",
    "books",
    "campaigns",
    "chapters",
    "characters",
    "companies",
    "developers",
    "dicerolls",
    "dictionary",
    "shared",
    "system",
    "traits",
    "users",
    # Individual models (alphabetical)
    "AdminCompanyPermission",
    "AdminDeveloper",
    "AdminDeveloperCreate",
    "AdminDeveloperUpdate",
    "AdminDeveloperWithApiKey",
    "AutogenCreate",
    "BlueprintHunterEdge",
    "Book",
    "BookCreate",
    "BookUpdate",
    "Campaign",
    "CampaignCreate",
    "CampaignExperience",
    "CampaignUpdate",
    "Category",
    "Chapter",
    "ChapterCreate",
    "ChapterUpdate",
    "Character",
    "CharacterCreate",
    "CharacterTrait",
    "CharacterUpdate",
    "Company",
    "CompanyCreate",
    "CompanyPermission",
    "CompanyUpdate",
    "CompanyWithApiKey",
    "Concept",
    "Developer",
    "DeveloperUpdate",
    "DeveloperWithApiKey",
    "Diceroll",
    "DicerollCreate",
    "DiscordProfile",
    "EdgeAndPerks",
    "Health",
    "HunterAttributes",
    "HunterAttributesCreate",
    "HunterAttributesUpdate",
    "HunterEdge",
    "HunterEdgePerk",
    "InventoryItem",
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "MageAttributes",
    "Note",
    "NoteCreate",
    "NoteUpdate",
    "PaginatedResponse",
    "Perk",
    "Permissions",
    "Quickroll",
    "QuickrollCreate",
    "QuickrollUpdate",
    "RollStatistics",
    "S3Asset",
    "Section",
    "Session",
    "SessionFinalize",
    "Settings",
    "Specialty",
    "Term",
    "TermCreate",
    "TermUpdate",
    "Trait",
    "TraitAssign",
    "TraitCreate",
    "TraitModify",
    "TraitValueOptions",
    "User",
    "UserCreate",
    "UserUpdate",
    "VampireAttributes",
    "VampireAttributesCreate",
    "VampireAttributesUpdate",
    "VampireClan",
    "WerewolfAttributes",
    "WerewolfAttributesCreate",
    "WerewolfAttributesUpdate",
    "WerewolfAuspice",
    "WerewolfGift",
    "WerewolfRite",
    "WerewolfTribe",
]
```

**Step 4: Run all tests**

Run: `uv run pytest tests/ -v --tb=short -q`

**Step 5: Commit**

```bash
git add src/vclient/models/__init__.py
git commit -m "refactor(models): reorganize models/__init__.py with submodules and direct imports"
```

---

## Phase 3: Update vclient/__init__.py

### Task 23: Simplify vclient/__init__.py

**Files:**
- Modify: `src/vclient/__init__.py`

**Step 1: Remove model and exception exports, keep only essentials**

```python
"""API client for the vclient service."""

from vclient.client import VClient
from vclient.config import APIConfig
from vclient.registry import (
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

__all__ = (
    "APIConfig",
    "VClient",
    "books_service",
    "campaigns_service",
    "chapters_service",
    "character_autogen_service",
    "character_blueprint_service",
    "character_traits_service",
    "characters_service",
    "companies_service",
    "developer_service",
    "dicreolls_service",
    "dictionary_service",
    "global_admin_service",
    "options_service",
    "system_service",
    "users_service",
)
```

**Step 2: Run tests**

**Step 3: Commit**

```bash
git add src/vclient/__init__.py
git commit -m "refactor: simplify vclient exports to essentials only"
```

---

## Phase 4: Add Hybrid Service API

### Task 24: Update CharactersService.create() to accept request model or kwargs

**Files:**
- Modify: `src/vclient/services/characters.py`

**Step 1: Modify create() signature**

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

    Returns:
        The newly created Character object.
    """
    if request is None:
        request = self._validate_request(CharacterCreate, **kwargs)

    response = await self._post(
        self._format_endpoint(Endpoints.CHARACTERS),
        json=request.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
    )
    return Character.model_validate(response.json())
```

**Step 2: Add test for request model usage**

```python
async def test_create_character_with_request_model(mock_client, characters_service):
    from vclient.models import characters

    request = characters.CharacterCreate(
        character_class="VAMPIRE",
        game_version="V5",
        name_first="Test",
        name_last="Character",
    )

    character = await characters_service.create(request)
    assert character.name_first == "Test"
```

**Step 3: Run tests**

**Step 4: Commit**

---

### Task 25: Update CharactersService.update() similarly

**Files:**
- Modify: `src/vclient/services/characters.py`

---

### Task 26-35: Repeat for other services

Apply same pattern to:
- CampaignsService
- CompaniesService
- UsersService
- BooksService
- ChaptersService
- DictionaryService
- etc.

---

## Phase 5: Update Tests

### Task 36: Update test imports

**Files:**
- Modify: All files in `tests/`

**Step 1: Update imports to use new model names**

Search and replace:
- `from vclient.models import CreateCharacterRequest` → `from vclient.models import CharacterCreate`
- etc.

**Step 2: Run all tests**

**Step 3: Commit**

---

## Phase 6: Update Documentation

### Task 37: Update README.md examples

**Files:**
- Modify: `README.md`

**Step 1: Update import examples**

**Step 2: Commit**

---

### Task 38: Update service documentation

**Files:**
- Modify: All files in `docs/`

---

## Phase 7: Final Verification

### Task 39: Run full test suite

Run: `uv run pytest tests/ -v`
Expected: All tests pass

### Task 40: Run linting

Run: `uv run duty lint`
Expected: No errors

### Task 41: Final commit and merge preparation

```bash
git log --oneline feature/dx-improvements ^main
```

Review all commits, squash if needed, prepare PR.
