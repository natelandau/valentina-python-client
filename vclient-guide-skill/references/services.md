# vclient Services Reference

Complete method signatures for every service class.

## Table of Contents

- [CompaniesService](#companiesservice)
- [UsersService](#usersservice)
- [CampaignsService](#campaignsservice)
- [CharactersService](#charactersservice)
- [CharacterTraitsService](#charactertraitsservice)
- [CharacterBlueprintService](#characterblueprintservice)
- [CharacterAutogenService](#characterautogenservice)
- [BooksService](#booksservice)
- [ChaptersService](#chaptersservice)
- [DicerollService](#dicerollservice)
- [DictionaryService](#dictionaryservice)
- [UserLookupService](#userlookupservice)
- [DeveloperService](#developerservice)
- [GlobalAdminService](#globaladminservice)
- [OptionsService](#optionsservice)
- [SystemService](#systemservice)

---

## CompaniesService

**Access:** `client.companies` (property)
**Factory:** `companies_service()` / `sync_companies_service()`
**Scoping:** None

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, limit, offset` | `PaginatedResponse[Company]` |
| `list_all()` | — | `list[Company]` |
| `iter_all()` | `*, limit` | `AsyncIterator[Company]` |
| `get(company_id)` | `company_id: str` | `Company` |
| `create()` | `request: CompanyCreate \| None, **kwargs` | `NewCompanyResponse` |
| `update(company_id)` | `company_id: str, request: CompanyUpdate \| None, **kwargs` | `Company` |
| `delete(company_id)` | `company_id: str` | `None` |
| `grant_access(company_id, developer_id, permission)` | `company_id: str, developer_id: str, permission: PermissionLevel` | `CompanyPermissions` |
| `get_statistics(company_id)` | `company_id: str, *, num_top_traits: int = 5` | `RollStatistics` |

---

## UsersService

**Access:** `client.users(company_id=)`
**Factory:** `users_service(company_id=)` / `sync_users_service(company_id=)`
**Scoping:** company_id

### CRUD Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, user_role: UserRole \| None, email: str \| None, limit, offset` | `PaginatedResponse[User]` |
| `list_all()` | `*, user_role=, email=` | `list[User]` |
| `iter_all()` | `*, user_role=, email=, limit` | `AsyncIterator[User]` |
| `get(user_id)` | `user_id: str, *, include: Sequence[UserInclude] \| None` | `UserDetail` |
| `create()` | `request: UserCreate \| None, **kwargs` | `User` |
| `register()` | `request: UserRegisterDTO \| None, **kwargs` | `User` |
| `update(user_id)` | `user_id: str, request: UserUpdate \| None, **kwargs` | `User` |
| `delete(user_id)` | `user_id: str` | `None` |

**Include options for `get()`:** `"quickrolls"`, `"notes"`, `"assets"`, `"characters"`

### Unapproved User Management

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_unapproved_page(requesting_user_id)` | `requesting_user_id: str, *, limit, offset` | `PaginatedResponse[User]` |
| `list_all_unapproved(requesting_user_id)` | `requesting_user_id: str` | `list[User]` |
| `iter_all_unapproved(requesting_user_id)` | `requesting_user_id: str, *, limit` | `AsyncIterator[User]` |
| `approve_user(user_id, role, requesting_user_id)` | `user_id: str, role: UserRole, requesting_user_id: str` | `User` |
| `deny_user(user_id, requesting_user_id)` | `user_id: str, requesting_user_id: str` | `None` |
| `merge(primary_user_id, secondary_user_id, requesting_user_id)` | all `str` | `User` |

### Experience

| Method | Parameters | Returns |
|--------|-----------|---------|
| `add_experience(user_id)` | `user_id: str, request: _ExperienceAddRemove \| None, **kwargs` | `CampaignExperience` |
| `remove_experience(user_id)` | `user_id: str, request: _ExperienceAddRemove \| None, **kwargs` | `CampaignExperience` |
| `get_statistics(user_id)` | `user_id: str, *, num_top_traits: int = 5` | `RollStatistics` |

**Experience kwargs:** `amount: int, campaign_id: str, requesting_user_id: str`

### Quickrolls

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_quickrolls_page(user_id)` | `user_id: str, *, limit, offset` | `PaginatedResponse[Quickroll]` |
| `list_all_quickrolls(user_id)` | `user_id: str` | `list[Quickroll]` |
| `iter_all_quickrolls(user_id)` | `user_id: str, *, limit` | `AsyncIterator[Quickroll]` |
| `get_quickroll(user_id, quickroll_id)` | both `str` | `Quickroll` |
| `create_quickroll(user_id)` | `user_id: str, request: QuickrollCreate \| None, **kwargs` | `Quickroll` |
| `update_quickroll(user_id, quickroll_id)` | `user_id: str, quickroll_id: str, request: QuickrollUpdate \| None, **kwargs` | `Quickroll` |
| `delete_quickroll(user_id, quickroll_id)` | both `str` | `None` |

### Notes, Assets

Same pattern as other services (see CampaignsService notes/assets for the method signatures — they follow the identical pattern with `user_id` as the parent resource ID).

---

## CampaignsService

**Access:** `client.campaigns(user_id, company_id=)`
**Factory:** `campaigns_service(user_id, company_id=)` / `sync_campaigns_service(...)`
**Scoping:** company_id, user_id

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, limit, offset` | `PaginatedResponse[Campaign]` |
| `list_all()` | — | `list[Campaign]` |
| `iter_all()` | `*, limit` | `AsyncIterator[Campaign]` |
| `get(campaign_id)` | `campaign_id: str` | `Campaign` |
| `create()` | `request: CampaignCreate \| None, **kwargs` | `Campaign` |
| `update(campaign_id)` | `campaign_id: str, request: CampaignUpdate \| None, **kwargs` | `Campaign` |
| `delete(campaign_id)` | `campaign_id: str` | `None` |
| `get_statistics(campaign_id)` | `campaign_id: str, *, num_top_traits: int = 5` | `RollStatistics` |

### Assets

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_assets_page(campaign_id)` | `campaign_id: str, *, limit, offset` | `PaginatedResponse[Asset]` |
| `list_all_assets(campaign_id)` | `campaign_id: str` | `list[Asset]` |
| `iter_all_assets(campaign_id)` | `campaign_id: str, *, limit` | `AsyncIterator[Asset]` |
| `get_asset(campaign_id, asset_id)` | both `str` | `Asset` |
| `delete_asset(campaign_id, asset_id)` | both `str` | `None` |
| `upload_asset(campaign_id, filename, content)` | `campaign_id: str, filename: str, content: bytes, content_type: str \| None` | `Asset` |

### Notes

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_notes_page(campaign_id)` | `campaign_id: str, *, limit, offset` | `PaginatedResponse[Note]` |
| `list_all_notes(campaign_id)` | `campaign_id: str` | `list[Note]` |
| `iter_all_notes(campaign_id)` | `campaign_id: str, *, limit` | `AsyncIterator[Note]` |
| `get_note(campaign_id, note_id)` | both `str` | `Note` |
| `create_note(campaign_id)` | `campaign_id: str, request: NoteCreate \| None, **kwargs` | `Note` |
| `update_note(campaign_id, note_id)` | both `str`, `request: NoteUpdate \| None, **kwargs` | `Note` |
| `delete_note(campaign_id, note_id)` | both `str` | `None` |

---

## CharactersService

**Access:** `client.characters(user_id, campaign_id, company_id=)`
**Factory:** `characters_service(user_id, campaign_id, company_id=)` / `sync_characters_service(...)`
**Scoping:** company_id, user_id, campaign_id

### CRUD Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, limit, offset, user_player_id=, user_creator_id=, character_class=, character_type=, status=, is_temporary=False` | `PaginatedResponse[Character]` |
| `list_all()` | same filters (without limit/offset) | `list[Character]` |
| `iter_all()` | same filters + `limit` | `AsyncIterator[Character]` |
| `get(character_id)` | `character_id: str, *, include: Sequence[CharacterInclude] \| None` | `CharacterDetail` |
| `create()` | `request: CharacterCreate \| None, **kwargs` | `Character` |
| `update(character_id)` | `character_id: str, request: CharacterUpdate \| None, **kwargs` | `Character` |
| `delete(character_id)` | `character_id: str` | `None` |

**Include options for `get()`:** `"traits"`, `"inventory"`, `"notes"`, `"assets"`

### Statistics & Full Sheet

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_statistics(character_id)` | `character_id: str, *, num_top_traits: int = 5` | `RollStatistics` |
| `get_full_sheet(character_id)` | `character_id: str, *, include_available_traits: bool = False` | `CharacterFullSheet` |
| `get_full_sheet_category(character_id, category_id)` | both `str`, `*, include_available_traits: bool = False` | `FullSheetTraitCategory` |

### Inventory

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_inventory_page(character_id)` | `character_id: str, *, limit, offset` | `PaginatedResponse[InventoryItem]` |
| `list_all_inventory(character_id)` | `character_id: str` | `list[InventoryItem]` |
| `iter_all_inventory(character_id)` | `character_id: str, *, limit` | `AsyncIterator[InventoryItem]` |
| `get_inventory_item(character_id, item_id)` | both `str` | `InventoryItem` |
| `create_inventory_item(character_id)` | `character_id: str, request: InventoryItemCreate \| None, **kwargs` | `InventoryItem` |
| `update_inventory_item(character_id, item_id)` | both `str`, `request: InventoryItemUpdate \| None, **kwargs` | `InventoryItem` |
| `delete_inventory_item(character_id, item_id)` | both `str` | `None` |

### Assets & Notes

Same pattern as CampaignsService (with `character_id` as parent resource ID).

---

## CharacterTraitsService

**Access:** `client.character_traits(user_id, campaign_id, character_id, company_id=)`
**Factory:** `character_traits_service(user_id, campaign_id, character_id, company_id=)` / `sync_character_traits_service(...)`
**Scoping:** company_id, user_id, campaign_id, character_id

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, limit, offset, category_id: str \| None, is_rollable: bool \| None` | `PaginatedResponse[CharacterTrait]` |
| `list_all()` | `*, category_id=, is_rollable=` | `list[CharacterTrait]` |
| `iter_all()` | `*, limit, category_id=, is_rollable=` | `AsyncIterator[CharacterTrait]` |
| `get(character_trait_id)` | `character_trait_id: str` | `CharacterTrait` |
| `create()` | `request: TraitCreate \| None, **kwargs` | `CharacterTrait` |
| `delete(character_trait_id)` | `character_trait_id: str, currency: TraitModifyCurrency \| None` | `None` |
| `assign(trait_id, value, currency)` | `trait_id: str, value: int, currency: TraitModifyCurrency` | `CharacterTrait` |
| `bulk_assign(items)` | `items: list[CharacterTraitAdd]` | `BulkAssignTraitResponse` |
| `get_value_options(character_trait_id)` | `character_trait_id: str` | `CharacterTraitValueOptionsResponse` |
| `change_value(character_trait_id, new_value, currency)` | `character_trait_id: str, new_value: int, currency: TraitModifyCurrency` | `CharacterTrait` |

**TraitModifyCurrency values:** `"XP"`, `"STARTING_POINTS"`, `"NO_COST"`

---

## CharacterBlueprintService

**Access:** `client.character_blueprint(company_id=)`
**Factory:** `character_blueprint_service(company_id=)` / `sync_character_blueprint_service(...)`
**Scoping:** company_id

Provides read-only access to the character sheet template (sections, categories, subcategories, traits, concepts, clans, tribes, auspices).

### Sheet Structure Methods

Each level (sections, categories, subcategories, traits) has the standard pagination triple:

**Sections:** `get_sections_page()`, `list_all_sections()`, `iter_all_sections()`, `get_section(section_id=)`
- Filters: `game_version=`, `character_class=`

**Categories:** `get_categories_page()`, `list_all_categories()`, `iter_all_categories()`, `get_category(category_id=)`
- Filters: `game_version=`, `section_id=`, `character_class=`

**Subcategories:** `get_subcategories_page()`, `list_all_subcategories()`, `iter_all_subcategories()`, `get_subcategory(subcategory_id=)`
- Filters: `game_version=`, `category_id=`, `character_class=`

**Traits:** `get_traits_page()`, `list_all_traits()`, `iter_all_traits()`, `get_trait(trait_id=)`
- Filters: `game_version=`, `category_id=`, `subcategory_id=`, `character_class=`, `order_by: BlueprintTraitOrderBy=`

### Reference Data Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_concepts_page()` | `*, limit, offset` | `PaginatedResponse[CharacterConcept]` |
| `list_all_concepts()` | — | `list[CharacterConcept]` |
| `iter_all_concepts()` | `*, limit` | `AsyncIterator[CharacterConcept]` |
| `get_concept(concept_id=)` | `concept_id: str` | `CharacterConcept` |
| `get_vampire_clans_page()` | `*, limit, offset` | `PaginatedResponse[VampireClan]` |
| `list_all_vampire_clans()` | — | `list[VampireClan]` |
| `get_vampire_clan(clan_id=)` | `clan_id: str` | `VampireClan` |
| `get_werewolf_tribes_page()` | `*, limit, offset` | `PaginatedResponse[WerewolfTribe]` |
| `list_all_werewolf_tribes()` | — | `list[WerewolfTribe]` |
| `get_werewolf_tribe(tribe_id=)` | `tribe_id: str` | `WerewolfTribe` |
| `get_werewolf_auspices_page()` | `*, limit, offset` | `PaginatedResponse[WerewolfAuspice]` |
| `list_all_werewolf_auspices()` | — | `list[WerewolfAuspice]` |
| `get_werewolf_auspice(auspice_id=)` | `auspice_id: str` | `WerewolfAuspice` |

---

## CharacterAutogenService

**Access:** `client.character_autogen(user_id, campaign_id, company_id=)`
**Factory:** `character_autogen_service(user_id, campaign_id, company_id=)` / `sync_character_autogen_service(...)`
**Scoping:** company_id, user_id, campaign_id

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `generate_character()` | `*, character_type: CharacterType, character_class: CharacterClass \| None, experience_level: AutoGenExperienceLevel \| None, skill_focus: AbilityFocus \| None, concept_id: str \| None, vampire_clan_id: str \| None, werewolf_tribe_id: str \| None, werewolf_auspice_id: str \| None` | `Character` |
| `start_chargen_session()` | — | `ChargenSessionResponse` |
| `finalize_chargen_session(session_id, selected_character_id)` | both `str` | `Character` |
| `list_all()` | — | `list[ChargenSessionResponse]` |
| `get(session_id)` | `session_id: str` | `ChargenSessionResponse` |

---

## BooksService

**Access:** `client.books(user_id, campaign_id, company_id=)`
**Factory:** `books_service(user_id, campaign_id, company_id=)` / `sync_books_service(...)`
**Scoping:** company_id, user_id, campaign_id

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, limit, offset` | `PaginatedResponse[CampaignBook]` |
| `list_all()` | — | `list[CampaignBook]` |
| `iter_all()` | `*, limit` | `AsyncIterator[CampaignBook]` |
| `get(book_id)` | `book_id: str, *, include: Sequence[BookInclude] \| None` | `CampaignBookDetail` |
| `create()` | `request: BookCreate \| None, **kwargs` | `CampaignBook` |
| `update(book_id)` | `book_id: str, request: BookUpdate \| None, **kwargs` | `CampaignBook` |
| `delete(book_id)` | `book_id: str` | `None` |
| `renumber(book_id, number)` | `book_id: str, number: int` | `CampaignBook` |

**Include options for `get()`:** `"chapters"`, `"notes"`, `"assets"`

Plus standard notes and assets sub-resource methods (same pattern as CampaignsService).

---

## ChaptersService

**Access:** `client.chapters(user_id, campaign_id, book_id, company_id=)`
**Factory:** `chapters_service(user_id, campaign_id, book_id, company_id=)` / `sync_chapters_service(...)`
**Scoping:** company_id, user_id, campaign_id, book_id

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, limit, offset` | `PaginatedResponse[CampaignChapter]` |
| `list_all()` | — | `list[CampaignChapter]` |
| `iter_all()` | `*, limit` | `AsyncIterator[CampaignChapter]` |
| `get(chapter_id)` | `chapter_id: str, *, include: Sequence[ChapterInclude] \| None` | `CampaignChapterDetail` |
| `create()` | `request: ChapterCreate \| None, **kwargs` | `CampaignChapter` |
| `update(chapter_id)` | `chapter_id: str, request: ChapterUpdate \| None, **kwargs` | `CampaignChapter` |
| `delete(chapter_id)` | `chapter_id: str` | `None` |
| `renumber(chapter_id, number)` | `chapter_id: str, number: int` | `CampaignChapter` |

**Include options for `get()`:** `"notes"`, `"assets"`

Plus standard notes and assets sub-resource methods.

---

## DicerollService

**Access:** `client.dicerolls(user_id, company_id=)`
**Factory:** `dicerolls_service(user_id, company_id=)` / `sync_dicerolls_service(...)`
**Scoping:** company_id, user_id

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, limit, offset, userid: str \| None, characterid: str \| None, campaignid: str \| None` | `PaginatedResponse[Diceroll]` |
| `list_all()` | `*, userid=, characterid=, campaignid=` | `list[Diceroll]` |
| `iter_all()` | `*, limit, userid=, characterid=, campaignid=` | `AsyncIterator[Diceroll]` |
| `get(diceroll_id)` | `diceroll_id: str` | `Diceroll` |
| `create()` | `request: DicerollCreate \| None, **kwargs` | `Diceroll` |
| `create_from_quickroll()` | `*, quickroll_id: str, character_id: str, comment: str \| None, difficulty: int = 6, num_desperation_dice: int = 0` | `Diceroll` |

---

## DictionaryService

**Access:** `client.dictionary(company_id=)`
**Factory:** `dictionary_service(company_id=)` / `sync_dictionary_service(...)`
**Scoping:** company_id

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, limit, offset, term: str \| None` | `PaginatedResponse[DictionaryTerm]` |
| `list_all()` | `*, term=` | `list[DictionaryTerm]` |
| `iter_all()` | `*, term=, limit` | `AsyncIterator[DictionaryTerm]` |
| `get(term_id)` | `term_id: str` | `DictionaryTerm` |
| `create()` | `request: DictionaryTermCreate \| None, **kwargs` | `DictionaryTerm` |
| `update(term_id)` | `term_id: str, request: DictionaryTermUpdate \| None, **kwargs` | `DictionaryTerm` |
| `delete(term_id)` | `term_id: str` | `None` |

---

## UserLookupService

**Access:** `client.user_lookup` (property)
**Factory:** `user_lookup_service()` / `sync_user_lookup_service()`
**Scoping:** None (cross-company)

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `by_email(email)` | `email: str` | `list[UserLookupResult]` |
| `by_discord_id(discord_id)` | `discord_id: str` | `list[UserLookupResult]` |
| `by_google_id(google_id)` | `google_id: str` | `list[UserLookupResult]` |
| `by_github_id(github_id)` | `github_id: str` | `list[UserLookupResult]` |

---

## DeveloperService

**Access:** `client.developer` (property)
**Factory:** `developer_service()` / `sync_developer_service()`
**Scoping:** None

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_me()` | — | `MeDeveloper` |
| `update_me()` | `request: MeDeveloperUpdate \| None, **kwargs` | `MeDeveloper` |
| `regenerate_api_key()` | — | `MeDeveloperWithApiKey` |

---

## GlobalAdminService

**Access:** `client.global_admin` (property)
**Factory:** `global_admin_service()` / `sync_global_admin_service()`
**Scoping:** None

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, limit, offset, is_global_admin: bool \| None` | `PaginatedResponse[Developer]` |
| `list_all()` | `*, is_global_admin=` | `list[Developer]` |
| `iter_all()` | `*, limit, is_global_admin=` | `AsyncIterator[Developer]` |
| `get(developer_id)` | `developer_id: str` | `Developer` |
| `create()` | `request: DeveloperCreate \| None, **kwargs` | `Developer` |
| `update(developer_id)` | `developer_id: str, request: DeveloperUpdate \| None, **kwargs` | `Developer` |
| `delete(developer_id)` | `developer_id: str` | `None` |
| `create_api_key(developer_id)` | `developer_id: str` | `DeveloperWithApiKey` |

---

## OptionsService

**Access:** `client.options(company_id=)`
**Factory:** `options_service(company_id=)` / `sync_options_service(...)`
**Scoping:** company_id

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_options()` | — | `dict[str, dict[str, list[str] \| dict[str, str]]]` |

---

## SystemService

**Access:** `client.system` (property)
**Factory:** `system_service()` / `sync_system_service()`
**Scoping:** None

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `health()` | — | `SystemHealth` |
