# vclient Services Reference

Complete method signatures for every service class.

## Table of Contents

- [CompaniesService](#companiesservice)
- [UsersService](#usersservice)
- [IdentityService](#identityservice)
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
| `get_audit_log_page(company_id)` | `company_id: str, *, limit, offset, acting_user_id=, user_id=, campaign_id=, book_id=, chapter_id=, character_id=, entity_type=, operation=, date_from=, date_to=, include=` | `PaginatedResponse[AuditLog \| AuditLogDetail]` |
| `list_all_audit_logs(company_id)` | `company_id: str, *, (same filters)` | `list[AuditLog \| AuditLogDetail]` |
| `iter_all_audit_logs(company_id)` | `company_id: str, *, limit, (same filters)` | `AsyncIterator[AuditLog \| AuditLogDetail]` |

---

## UsersService

**Access:** `client.users(on_behalf_of, company_id=)`
**Factory:** `users_service(on_behalf_of, company_id=)` / `sync_users_service(on_behalf_of, company_id=)`
**Scoping:** on_behalf_of, company_id

### CRUD Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, user_role: UserRole \| None, email: str \| None, limit, offset` | `PaginatedResponse[User]` |
| `list_all()` | `*, user_role=, email=` | `list[User]` |
| `iter_all()` | `*, user_role=, email=, limit` | `AsyncIterator[User]` |
| `get(user_id)` | `user_id: str, *, include: Sequence[UserInclude] \| None` | `UserDetail` |
| `create()` | `request: UserCreate \| None, **kwargs` | `User` |
| `update(user_id)` | `user_id: str, request: UserUpdate \| None, **kwargs` | `User` |
| `delete(user_id)` | `user_id: str` | `None` |

**Include options for `get()`:** `"quickrolls"`, `"notes"`, `"assets"`, `"characters"`

### Identity Linking

| Method | Parameters | Returns |
|--------|-----------|---------|
| `link_identity(user_id, *, provider, token)` | `user_id: str, provider: IdentityProvider, token: str` | `User` |
| `unlink_identity(user_id, *, provider)` | `user_id: str, provider: IdentityProvider` | `User` |

**Auth:** `on_behalf_of` is required. Only the acting user themselves or a company ADMIN may call these.
**Semantics:** `link_identity` verifies the provider credential and attaches the identity (re-linking the same identity is idempotent and refreshes the stored profile). `unlink_identity` removes a single provider identity; the matching `*_profile` field on the returned `User` is cleared to `None`.
**Error codes:** `link_identity` raises `ConflictError` (409, code `IDENTITY_ALREADY_LINKED`) when the identity belongs to another user or the user already has a different identity from this provider, and `UnprocessableEntityError` (422, code `TOKEN_VERIFICATION_FAILED`) when token verification fails. `unlink_identity` raises `NotFoundError` (404, code `IDENTITY_NOT_LINKED`) when the user has no identity from that provider, and `ConflictError` (409, code `LAST_IDENTITY`) when the provider is the user's only linked identity (the last one cannot be removed).

**Testing:** Use `Routes.USERS_IDENTITY_LINK` and `Routes.USERS_IDENTITY_UNLINK` with `FakeVClient.set_response()` or `set_error()` (e.g. `set_error(Routes.USERS_IDENTITY_UNLINK, status_code=409, code="LAST_IDENTITY")` to test branching on `APIError.code`).

### Unapproved User Management

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_unapproved_page()` | `*, limit, offset` | `PaginatedResponse[User]` |
| `list_all_unapproved()` | — | `list[User]` |
| `iter_all_unapproved()` | `*, limit` | `AsyncIterator[User]` |
| `approve_user(user_id, role)` | `user_id: str, role: UserRole` | `User` |
| `merge(primary_user_id, secondary_user_id)` | both `str` | `User` |

### Experience

| Method | Parameters | Returns |
|--------|-----------|---------|
| `add_xp(user_id, campaign_id, amount)` | `user_id: str, campaign_id: str, amount: int` | `CampaignExperience` |
| `remove_xp(user_id, campaign_id, amount)` | `user_id: str, campaign_id: str, amount: int` | `CampaignExperience` |
| `add_cool_points(user_id, campaign_id, amount)` | `user_id: str, campaign_id: str, amount: int` | `CampaignExperience` |
| `get_experience(user_id, campaign_id)` | `user_id: str, campaign_id: str` | `CampaignExperience` |
| `get_statistics(user_id)` | `user_id: str, *, num_top_traits: int = 5` | `RollStatistics` |

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

## IdentityService

**Access:** `client.identity(company_id=)`
**Factory:** `identity_service(company_id=)` / `sync_identity_service(company_id=)`
**Scoping:** company_id (no on_behalf_of, API key auth only)

Resolves verified provider credentials to canonical users. Forward the credential obtained from a provider's own login flow: an OIDC ID token for `apple`/`google`, or an OAuth access token for `discord`/`github`. The API verifies the credential with the provider, then resolves the user through:

1. **matched** - an existing user already holds this provider identity
2. **linked** - the identity was auto-linked to an existing user by provider-verified email
3. **created** - a new UNAPPROVED user was registered (username/email in the request body apply only on this path)

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `identify(request=None, **kwargs)` | `request: UserIdentifyDTO \| None, **kwargs` | `IdentityResolution` |

**Identify kwargs:** `provider: IdentityProvider` (required), `token: str` (required, min length 1), `username: str \| None`, `email: str \| None`

**Note:** `username` and `email` are used only when the API creates a new user; `email` is required on create only if the provider did not supply one.

**Error codes raised by `identify()`:**

| Exception | HTTP | Code | Cause |
|-----------|------|------|-------|
| `UnprocessableEntityError` | 422 | `TOKEN_VERIFICATION_FAILED` | Provider rejected the credential |
| `UnprocessableEntityError` | 422 | `EMAIL_REQUIRED` | Creating a user but provider supplied no email and none was passed |
| `ServerError` | 503 | `PROVIDER_UNAVAILABLE` | Provider is unreachable (HTTP 503; `ServerError` covers all 5xx) |

**Apple/Google audience requirement:** Token verification for `apple` and `google` checks whether the token's audience (bundle ID or OAuth client ID) appears in the union of the server's environment allowlists and the audiences registered on the calling developer's profile. If both are empty for a given app, `TOKEN_VERIFICATION_FAILED` is raised. Register audiences via `client.developer.update_me(provider_audiences={"apple": [...], "google": [...]})`.

**Testing:** Use `Routes.IDENTITY_IDENTIFY` with `FakeVClient.set_response()` or `set_error()` (e.g. `set_error(Routes.IDENTITY_IDENTIFY, status_code=422, code="TOKEN_VERIFICATION_FAILED")` to test branching on `APIError.code`).

---

## CampaignsService

**Access:** `client.campaigns(on_behalf_of, company_id=)`
**Factory:** `campaigns_service(on_behalf_of, company_id=)` / `sync_campaigns_service(...)`
**Scoping:** on_behalf_of, company_id

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

**Access:** `client.characters(on_behalf_of, company_id=)`
**Factory:** `characters_service(on_behalf_of, company_id=)` / `sync_characters_service(...)`
**Scoping:** on_behalf_of, company_id

**Access control:** `on_behalf_of` is required and sent on every request, including reads. `STORYTELLER` characters are visible only to `STORYTELLER`/`ADMIN` roles. For a `PLAYER`: list results omit `STORYTELLER` characters (filtering `character_type="STORYTELLER"` yields an empty page), and fetching a `STORYTELLER` character or any of its sub-resources (traits, inventory, notes, assets, statistics) raises `AuthorizationError` (403). Only `STORYTELLER`/`ADMIN` may create or convert a character to `type="STORYTELLER"`; a `PLAYER` attempting it raises `AuthorizationError` (403).

**Player/creator assignment:** `Character.user_player_id` and `Character.user_creator_id` are both nullable. `PLAYER` characters always have a non-null `user_player_id`; `NPC`/`STORYTELLER` characters always have `user_player_id = null`. `user_creator_id` may be `null` if the creator was deleted. These rules are server-enforced and surface as `ValidationError` (400): creating a `PLAYER` without `user_player_id` defaults it to the acting user; creating an `NPC`/`STORYTELLER` with a non-null `user_player_id`, or assigning one to an existing `NPC`/`STORYTELLER`, is rejected; converting `PLAYER` → `NPC`/`STORYTELLER` auto-clears `user_player_id` (no explicit `None` needed); converting `NPC`/`STORYTELLER` → `PLAYER` requires a `user_player_id` in the same `update()`.

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

**Access:** `client.character_traits(on_behalf_of, character_id, company_id=)`
**Factory:** `character_traits_service(on_behalf_of, character_id, company_id=)` / `sync_character_traits_service(...)`
**Scoping:** on_behalf_of, character_id, company_id

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

**NPC/STORYTELLER currency restriction:** On `NPC` and `STORYTELLER` characters, every method taking a `currency` (`assign`, `bulk_assign`, `create`, `change_value`, `delete`) accepts only `"NO_COST"`. Passing `"XP"` or `"STARTING_POINTS"` raises `ValidationError` (400). `PLAYER` characters accept all three.

---

## CharacterBlueprintService

**Access:** `client.character_blueprint(on_behalf_of=, company_id=)` — `on_behalf_of` is optional (not required by API)
**Factory:** `character_blueprint_service(on_behalf_of=, company_id=)` / `sync_character_blueprint_service(...)`
**Scoping:** company_id

Provides read-only access to the character sheet template (sections, categories, subcategories, traits, concepts, clans, tribes, auspices).

**Higher page limit:** As a reference/catalog service, every `get_*_page()` method accepts `limit` up to **1000** (other services cap at 100). `list_all_*()`/`iter_all_*()` fetch 1000 per page automatically.

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

**Access:** `client.character_autogen(on_behalf_of, company_id=)`
**Factory:** `character_autogen_service(on_behalf_of, company_id=)` / `sync_character_autogen_service(...)`
**Scoping:** on_behalf_of, company_id

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `generate_character()` | `*, campaign_id: str, character_type: CharacterType, character_class: CharacterClass \| None, experience_level: AutoGenExperienceLevel \| None, skill_focus: AbilityFocus \| None, concept_id: str \| None, vampire_clan_id: str \| None, werewolf_tribe_id: str \| None, werewolf_auspice_id: str \| None` | `Character` |
| `start_chargen_session()` | `*, campaign_id: str` | `ChargenSessionResponse` |
| `finalize_chargen_session(session_id, selected_character_id)` | both `str` | `Character` |
| `list_all()` | — | `list[ChargenSessionResponse]` |
| `get(session_id)` | `session_id: str` | `ChargenSessionResponse` |

---

## BooksService

**Access:** `client.books(campaign_id, on_behalf_of, company_id=)`
**Factory:** `books_service(campaign_id, on_behalf_of, company_id=)` / `sync_books_service(...)`
**Scoping:** campaign_id, on_behalf_of, company_id

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

**Access:** `client.chapters(campaign_id, book_id, on_behalf_of, company_id=)`
**Factory:** `chapters_service(campaign_id, book_id, on_behalf_of, company_id=)` / `sync_chapters_service(...)`
**Scoping:** campaign_id, book_id, on_behalf_of, company_id

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

**Access:** `client.dicerolls(on_behalf_of, company_id=)`
**Factory:** `dicerolls_service(on_behalf_of, company_id=)` / `sync_dicerolls_service(...)`
**Scoping:** on_behalf_of, company_id

**Access control:** `on_behalf_of` is required and sent on every request, including reads. For a `PLAYER`, list results omit rolls tied to `STORYTELLER` characters (rolls with no character are unaffected), and fetching such a roll by ID raises `AuthorizationError` (403).

### Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_page()` | `*, limit, offset, userid: str \| None, characterid: str \| None, campaignid: str \| None, character_type: CharacterType \| None` | `PaginatedResponse[Diceroll]` |
| `list_all()` | `*, userid=, characterid=, campaignid=, character_type: CharacterType \| None` | `list[Diceroll]` |
| `iter_all()` | `*, limit, userid=, characterid=, campaignid=, character_type: CharacterType \| None` | `AsyncIterator[Diceroll]` |
| `get(diceroll_id)` | `diceroll_id: str` | `Diceroll` |
| `create()` | `request: DicerollCreate \| None, **kwargs` | `Diceroll` |
| `create_from_quickroll()` | `*, quickroll_id: str, character_id: str, comment: str \| None, difficulty: int = 6, num_desperation_dice: int = 0` | `Diceroll` |

---

## DictionaryService

**Access:** `client.dictionary(on_behalf_of=, company_id=)` — `on_behalf_of` is optional (not required by API)
**Factory:** `dictionary_service(on_behalf_of=, company_id=)` / `sync_dictionary_service(...)`
**Scoping:** company_id

**Higher page limit:** As a reference/catalog service, `get_page()` accepts `limit` up to **1000** (other services cap at 100). `list_all()`/`iter_all()` fetch 1000 per page automatically.

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
| `by_apple_id(apple_id)` | `apple_id: str` | `list[UserLookupResult]` |

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

Requires a global-admin API key. No `on_behalf_of` parameter on any method. User methods also surface archived users and bypass normal role-hierarchy restrictions.

### Developer Methods

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_developer_page()` | `*, limit, offset, is_global_admin: bool \| None` | `PaginatedResponse[Developer]` |
| `list_all_developers()` | `*, is_global_admin=` | `list[Developer]` |
| `iter_all_developers()` | `*, limit, is_global_admin=` | `AsyncIterator[Developer]` |
| `get_developer(developer_id)` | `developer_id: str` | `Developer` |
| `create_developer()` | `request: DeveloperCreate \| None, **kwargs` | `Developer` |
| `update_developer(developer_id)` | `developer_id: str, request: DeveloperUpdate \| None, **kwargs` | `Developer` |
| `delete_developer(developer_id)` | `developer_id: str` | `None` |
| `create_api_key(developer_id)` | `developer_id: str` | `DeveloperWithApiKey` |
| `get_audit_log_page(developer_id)` | `developer_id: str, *, limit, offset, company_id=, acting_user_id=, user_id=, campaign_id=, book_id=, chapter_id=, character_id=, entity_type=, operation=, date_from=, date_to=, include=` | `PaginatedResponse[AuditLog \| AuditLogDetail]` |
| `list_all_audit_logs(developer_id)` | `developer_id: str, *, company_id=, (same filters)` | `list[AuditLog \| AuditLogDetail]` |
| `iter_all_audit_logs(developer_id)` | `developer_id: str, *, limit, company_id=, (same filters)` | `AsyncIterator[AuditLog \| AuditLogDetail]` |

### User Methods

Cross-company user management. Archived users are included in results and can be restored via `update_user`. Role hierarchy is bypassed (all roles assignable regardless of the acting developer's own role).

| Method | Parameters | Returns |
|--------|-----------|---------|
| `get_user_page()` | `*, company_id: str \| None, role: UserRole \| None, email: str \| None, is_archived: bool \| None, limit, offset` | `PaginatedResponse[AdminUser]` |
| `list_all_users()` | `*, company_id=, role=, email=, is_archived=` | `list[AdminUser]` |
| `iter_all_users()` | `*, limit, company_id=, role=, email=, is_archived=` | `AsyncIterator[AdminUser]` |
| `get_user(user_id)` | `user_id: str` | `AdminUser` |
| `create_user()` | `request: AdminUserCreate \| None, **kwargs` | `AdminUser` |
| `update_user(user_id)` | `user_id: str, request: AdminUserUpdate \| None, **kwargs` | `AdminUser` |
| `delete_user(user_id)` | `user_id: str` | `None` |

### Server Logs

Requires global admin. Raises `AuthorizationError` (403) for non-admins and `ConflictError` (409) when file logging is disabled on the server.

| Method | Parameters | Returns |
|--------|-----------|---------|
| `tail_logs()` | `*, level: LogLevel \| None = None, limit: int = 100` | `list[ServerLogEntry]` |
| `download_logs()` | None | `ServerLogArchive` |

`tail_logs()` returns the most recent entries, newest first. `level` filters by minimum severity (omitted = server default). `limit` is clamped to 1-500. `download_logs()` returns a zip archive of the server logs.

---

## OptionsService

**Access:** `client.options(on_behalf_of=, company_id=)` — `on_behalf_of` is optional (not required by API)
**Factory:** `options_service(on_behalf_of=, company_id=)` / `sync_options_service(...)`
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
