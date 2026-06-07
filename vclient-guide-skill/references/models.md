# vclient Models Reference

All Pydantic v2 models with fields, types, and validation constraints. Import from `vclient.models`.

## Table of Contents

- [Shared Models](#shared-models)
- [Companies](#companies)
- [Users](#users)
  - [Identity Resolution](#identity-resolution)
- [Campaigns](#campaigns)
- [Characters](#characters)
- [Character Traits](#character-traits)
- [Character Blueprint](#character-blueprint)
- [Character Autogen](#character-autogen)
- [Books & Chapters](#books--chapters)
- [Dice Rolls](#dice-rolls)
- [Dictionary](#dictionary)
- [Full Sheet](#full-sheet)
- [Developers](#developers)
- [Global Admin](#global-admin)
- [Pagination](#pagination)
- [System](#system)
- [User Lookup](#user-lookup)
- [Audit Logs](#audit-logs)

---

## Shared Models

### Asset

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| asset_type | AssetType | yes |
| mime_type | str | yes |
| original_filename | str | yes |
| public_url | str | yes |
| uploaded_by_id | str | yes |
| company_id | str | yes |
| character_id | str \| None | no |
| campaign_id | str \| None | no |
| book_id | str \| None | no |
| chapter_id | str \| None | no |
| user_parent_id | str \| None | no |

### Note / NoteCreate / NoteUpdate

**Note** (response):

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| title | str | yes |
| content | str | yes |

**NoteCreate:** `title` (str, 3-50 chars), `content` (str, min 3 chars) — both required.
**NoteUpdate:** `title` (str \| None, 3-50 chars), `content` (str \| None, min 3 chars) — both optional.

### NameDescriptionSubDocument

| Field | Type | Required |
|-------|------|----------|
| name | str \| None | no |
| description | str \| None | no |

### RollStatistics

| Field | Type | Required |
|-------|------|----------|
| botches | int | yes |
| successes | int | yes |
| failures | int | yes |
| criticals | int | yes |
| total_rolls | int | yes |
| average_difficulty | float \| None | no |
| average_pool | float \| None | no |
| top_traits | list[dict[str, Any]] | no (default=[]) |
| criticals_percentage | float | yes |
| success_percentage | float | yes |
| failure_percentage | float | yes |
| botch_percentage | float | yes |

### Trait

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str \| None | no |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| link | str \| None | no |
| show_when_zero | bool | no (default=True) |
| max_value | int | no (default=5) |
| min_value | int | no (default=0) |
| is_custom | bool | no (default=False) |
| initial_cost | int | no (default=1) |
| upgrade_cost | int | no (default=2) |
| count_based_cost_multiplier | int \| None | no |
| is_rollable | bool | no (default=True) |
| sheet_section_name | str \| None | no |
| sheet_section_id | str | yes |
| category_name | str \| None | no |
| category_id | str | yes |
| custom_for_character_id | str \| None | no |
| subcategory_id | str \| None | no |
| subcategory_name | str \| None | no |
| pool | str \| None | no |
| opposing_pool | str \| None | no |
| system | str \| None | no |
| gift_attributes | GiftAttributes \| None | no |
| character_classes | list[CharacterClass] | no (default=[]) |
| game_versions | list[GameVersion] | no (default=[]) |

### GiftAttributes

| Field | Type | Required |
|-------|------|----------|
| renown | WerewolfRenown | yes |
| cost | str \| None | no |
| duration | str \| None | no |
| minimum_renown | int \| None | no |
| is_native_gift | bool | no (default=False) |
| tribe_id | str \| None | no |
| tribe_name | str \| None | no |
| auspice_id | str \| None | no |
| auspice_name | str \| None | no |

### CharacterSpecialty

| Field | Type | Required |
|-------|------|----------|
| name | str | yes |
| type | SpecialtyType | yes |
| description | str | yes |

---

## Companies

### Company

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| name | str | yes |
| description | str \| None | no |
| email | str | yes |
| resources_modified_at | datetime | yes |
| num_campaigns | int | no (default=0) |
| num_player_characters | int | no (default=0) |
| num_storyteller_characters | int | no (default=0) |
| num_npc_characters | int | no (default=0) |
| num_users | int | no (default=0) |
| settings | CompanySettings | yes |

### CompanySettings

Strict response model — all fields always populated by the server.

| Field | Type | Required |
|-------|------|----------|
| character_autogen_xp_cost | int | yes |
| character_autogen_num_choices | int | yes |
| character_autogen_starting_points | int | yes |
| permission_manage_campaign | ManageCampaignPermission | yes |
| permission_manage_npc | ManageNPCPermission | yes |
| permission_grant_xp | GrantXPPermission | yes |
| permission_free_trait_changes | FreeTraitChangesPermission | yes |
| permission_recoup_xp | RecoupXPPermission | yes |

### CompanySettingsCreate

Request payload for `POST /companies`. All fields optional.

| Field | Type | Required |
|-------|------|----------|
| character_autogen_xp_cost | int \| None | no |
| character_autogen_num_choices | int \| None | no |
| character_autogen_starting_points | int \| None | no |
| permission_manage_campaign | ManageCampaignPermission \| None | no |
| permission_manage_npc | ManageNPCPermission \| None | no |
| permission_grant_xp | GrantXPPermission \| None | no |
| permission_free_trait_changes | FreeTraitChangesPermission \| None | no |
| permission_recoup_xp | RecoupXPPermission \| None | no |

### CompanySettingsUpdate

Request payload for `PATCH /companies/{id}`. All fields optional.

| Field | Type | Required |
|-------|------|----------|
| character_autogen_xp_cost | int \| None | no |
| character_autogen_num_choices | int \| None | no |
| character_autogen_starting_points | int \| None | no |
| permission_manage_campaign | ManageCampaignPermission \| None | no |
| permission_manage_npc | ManageNPCPermission \| None | no |
| permission_grant_xp | GrantXPPermission \| None | no |
| permission_free_trait_changes | FreeTraitChangesPermission \| None | no |
| permission_recoup_xp | RecoupXPPermission \| None | no |

### CompanyCreate

| Field | Type | Constraints |
|-------|------|------------|
| name | str | 3-50 chars, required |
| email | str | required |
| description | str \| None | min 3 chars |
| settings | CompanySettingsCreate \| None | optional |

### CompanyUpdate

| Field | Type | Constraints |
|-------|------|------------|
| name | str \| None | 3-50 chars |
| email | str \| None | — |
| description | str \| None | min 3 chars |
| settings | CompanySettingsUpdate \| None | — |

### NewCompanyResponse

| Field | Type | Required |
|-------|------|----------|
| company | Company | yes |
| admin_user | User | yes |

### CompanyPermissions

| Field | Type | Required |
|-------|------|----------|
| company_id | str | yes |
| name | str \| None | no |
| permission | PermissionLevel | yes |

---

## Users

### User

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| name_first | str \| None | no |
| name_last | str \| None | no |
| username | str | yes |
| email | str | yes |
| role | UserRole | yes |
| company_id | str | yes |
| discord_profile | DiscordProfile \| None | no |
| google_profile | GoogleProfile \| None | no |
| github_profile | GitHubProfile \| None | no |
| apple_profile | AppleProfile \| None | no |
| campaign_experience | list[CampaignExperience] | no (default=[]) |
| asset_ids | list[str] | no (default=[]) |
| lifetime_xp | int | no (default=0) |
| lifetime_cool_points | int | no (default=0) |
| num_quickrolls | int | no (default=0) |
| num_notes | int | no (default=0) |
| num_assets | int | no (default=0) |
| num_characters | int | no (default=0) |

### UserDetail (extends User)

| Field | Type | Required |
|-------|------|----------|
| quickrolls | list[Quickroll] \| None | no |
| notes | list[Note] \| None | no |
| assets | list[Asset] \| None | no |
| characters | list[Character] \| None | no |

### UserCreate

| Field | Type | Constraints |
|-------|------|------------|
| name_first | str \| None | 3-50 chars |
| name_last | str \| None | 3-50 chars |
| username | str | 3-50 chars, required |
| email | str | required |
| role | UserRole | required |
| discord_profile | DiscordProfileUpdate \| None | — |
| google_profile | GoogleProfile \| None | — |
| github_profile | GitHubProfile \| None | — |
| apple_profile | AppleProfile \| None | — |

### UserUpdate

All fields optional. Same fields as UserCreate, with `role` becoming optional.

### UserRegisterDTO

| Field | Type | Required |
|-------|------|----------|
| name_first | str \| None | no |
| name_last | str \| None | no |
| username | str | yes |
| email | str | yes |
| discord_profile | DiscordProfileUpdate \| None | no |
| google_profile | GoogleProfile \| None | no |
| github_profile | GitHubProfile \| None | no |
| apple_profile | AppleProfile \| None | no |

### UserMergeDTO

| Field | Type | Required |
|-------|------|----------|
| primary_user_id | str | yes |
| secondary_user_id | str | yes |

### Identity Resolution

#### UserIdentifyDTO

Request body for `IdentityService.identify()`. Fields `username` and `email` apply only when a new user is created.

| Field | Type | Constraints |
|-------|------|------------|
| provider | IdentityProvider | required |
| token | str | required, min length 1 |
| username | str \| None | optional |
| email | str \| None | optional |

#### UserIdentityLinkDTO

Request body for `UsersService.link_identity()`.

| Field | Type | Constraints |
|-------|------|------------|
| provider | IdentityProvider | required |
| token | str | required, min length 1 |

#### IdentityResolution

Response model from `IdentityService.identify()`. Reports how the API resolved the credential.

| Field | Type | Required |
|-------|------|----------|
| resolution | IdentityResolutionType | yes |
| user | User | yes |

**Resolution values:** `"matched"` (existing provider identity found), `"linked"` (auto-linked by provider-verified email), `"created"` (new UNAPPROVED user registered).

### CampaignExperience

| Field | Type | Required |
|-------|------|----------|
| campaign_id | str | yes |
| xp_current | int | no (default=0) |
| xp_total | int | no (default=0) |
| cool_points | int | no (default=0) |

### Quickroll / QuickrollCreate / QuickrollUpdate

**Quickroll:**

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| name | str | yes |
| description | str \| None | no |
| user_id | str | yes |
| trait_ids | list[str] | no (default=[]) |

**QuickrollCreate:** `name` (str, 3-50 chars, required), `description` (str \| None, min 3), `trait_ids` (list[str], default=[]).
**QuickrollUpdate:** All optional.

### Social Profiles

**DiscordProfile:** `id`, `username`, `global_name`, `avatar_id`, `avatar_url`, `discriminator`, `email`, `verified` — all optional.
**GoogleProfile:** `id`, `email`, `verified_email`, `username`, `name_first`, `name_last`, `avatar_url`, `locale` — all optional.
**GitHubProfile:** `id`, `login`, `username`, `avatar_url`, `email`, `profile_url` — all optional.
**AppleProfile:** `id`, `email`, `fullname` — all optional.
**DiscordProfileUpdate:** Same fields as DiscordProfile minus `avatar_url`.

---

## Campaigns

### Campaign

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| name | str | yes |
| description | str \| None | no |
| asset_ids | list[str] | no (default=[]) |
| desperation | int | no (default=0) |
| danger | int | no (default=0) |
| company_id | str | yes |
| num_books | int | no (default=0) |
| num_chapters | int | no (default=0) |
| num_notes | int | no (default=0) |
| num_player_characters | int | no (default=0) |
| num_storyteller_characters | int | no (default=0) |
| num_npc_characters | int | no (default=0) |

### CampaignCreate

| Field | Type | Constraints |
|-------|------|------------|
| name | str | 3-50 chars, required |
| description | str \| None | min 3 chars |
| desperation | int | 0-5, default=0 |
| danger | int | 0-5, default=0 |

### CampaignUpdate

All fields optional. Same constraints as CampaignCreate.

---

## Characters

### Character

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| date_killed | datetime \| None | no |
| character_class | CharacterClass | yes |
| type | CharacterType | no (default="PLAYER") |
| game_version | GameVersion | yes |
| status | CharacterStatus | no (default="ALIVE") |
| starting_points | int | no (default=0) |
| is_temporary | bool | no (default=False) |
| name_first | str | yes (min 3) |
| name_last | str | yes (min 3) |
| name_nick | str \| None | no (3-50 chars) |
| name | str | yes |
| name_full | str | yes |
| age | int \| None | no |
| biography | str \| None | no (min 3) |
| demeanor | str \| None | no (3-50 chars) |
| nature | str \| None | no (3-50 chars) |
| concept_id | str \| None | no |
| concept_name | str \| None | no |
| user_creator_id | str \| None | no |
| user_player_id | str \| None | no |
| company_id | str | yes |
| campaign_id | str | yes |
| asset_ids | list[str] | no (default=[]) |
| character_trait_ids | list[str] | no (default=[]) |
| specialties | list[CharacterSpecialty] | no (default=[]) |
| vampire_attributes | VampireAttributes \| None | no |
| werewolf_attributes | WerewolfAttributes \| None | no |
| mage_attributes | MageAttributes \| None | no |
| hunter_attributes | HunterAttributes \| None | no |
| num_inventory_items | int | no (default=0) |
| num_notes | int | no (default=0) |
| num_assets | int | no (default=0) |

### CharacterDetail (extends Character)

| Field | Type | Required |
|-------|------|----------|
| traits | list[CharacterTrait] \| None | no |
| inventory | list[InventoryItem] \| None | no |
| notes | list[Note] \| None | no |
| assets | list[Asset] \| None | no |

### CharacterCreate

| Field | Type | Constraints |
|-------|------|------------|
| character_class | CharacterClass | required |
| game_version | GameVersion | required |
| campaign_id | str | required |
| name_first | str | min 3, required |
| name_last | str | min 3, required |
| type | CharacterType \| None | optional |
| is_temporary | bool | default=False |
| name_nick | str \| None | 3-50 chars |
| age | int \| None | — |
| biography | str \| None | min 3 |
| demeanor | str \| None | 3-50 chars |
| nature | str \| None | 3-50 chars |
| concept_id | str \| None | — |
| user_player_id | str \| None | — |
| traits | list[CharacterCreateTraitAssign] \| None | — |
| vampire_attributes | VampireAttributesCreate \| None | — |
| werewolf_attributes | WerewolfAttributesCreate \| None | — |
| hunter_attributes | HunterAttributesCreate \| None | — |
| mage_attributes | MageAttributes \| None | — |

### CharacterUpdate

All fields optional. Same field set as CharacterCreate plus `status`, `date_killed`.

### Class-Specific Attributes

**VampireAttributes:** `clan_id`, `clan_name`, `generation`, `sire`, `bane` (NameDescriptionSubDocument), `compulsion` (NameDescriptionSubDocument) — all optional.
**VampireAttributesCreate:** `clan_id` (required), rest optional.

**WerewolfAttributes:** `tribe_id`, `tribe_name`, `auspice_id`, `auspice_name`, `pack_name`, `total_renown` (default=0) — all optional.
**WerewolfAttributesCreate:** `tribe_id` (required), rest optional.

**MageAttributes:** `sphere`, `tradition` — both optional.

**HunterAttributes:** `creed` — optional.
**HunterAttributesCreate/Update:** `creed` — optional.

### InventoryItem / InventoryItemCreate / InventoryItemUpdate

**InventoryItem:**

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| character_id | str | yes |
| name | str | yes |
| type | CharacterInventoryType | yes |
| description | str \| None | no |
| date_created | datetime | yes |
| date_modified | datetime | yes |

**InventoryItemCreate:** `name` (str, required), `type` (CharacterInventoryType, required), `description` (str \| None).
**InventoryItemUpdate:** All optional.

---

## Character Traits

### CharacterTrait

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| character_id | str | yes |
| value | int | yes |
| trait | Trait | yes |

### CharacterCreateTraitAssign

Used during character creation to assign initial traits.

| Field | Type | Required |
|-------|------|----------|
| trait_id | str | yes |
| value | int | yes |

### CharacterTraitAdd

Used for assigning traits to existing characters (single or bulk).

| Field | Type | Required |
|-------|------|----------|
| trait_id | str | yes |
| value | int | yes |
| currency | TraitModifyCurrency | yes |

### TraitCreate

For creating custom traits on a character.

| Field | Type | Required |
|-------|------|----------|
| name | str | yes |
| category_id | str | yes |
| description | str \| None | no |
| max_value | int | no (default=5, 0-100) |
| min_value | int | no (default=0, 0-100) |
| show_when_zero | bool \| None | no (default=True) |
| initial_cost | int \| None | no |
| upgrade_cost | int \| None | no |
| count_based_cost_multiplier | int \| None | no |
| value | int \| None | no |

### CharacterTraitValueOptionsResponse

| Field | Type | Required |
|-------|------|----------|
| name | str | yes |
| current_value | int | yes |
| trait | Trait | yes |
| xp_current | int | yes |
| starting_points_current | int | yes |
| options | dict[str, CharacterTraitValueOption] | yes |

### CharacterTraitValueOption

| Field | Type | Required |
|-------|------|----------|
| direction | str | yes |
| point_change | int | yes |
| can_use_xp | bool | yes |
| xp_after | int | yes |
| can_use_starting_points | bool | yes |
| starting_points_after | int | yes |

### BulkAssignTraitResponse

| Field | Type | Required |
|-------|------|----------|
| succeeded | list[BulkAssignTraitSuccess] | yes |
| failed | list[BulkAssignTraitFailure] | yes |

**BulkAssignTraitSuccess:** `trait_id` (str), `character_trait` (CharacterTrait).
**BulkAssignTraitFailure:** `trait_id` (str), `error` (str).

---

## Character Blueprint

### SheetSection

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str \| None | no |
| character_classes | list[CharacterClass] | no (default=[]) |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| game_versions | list[GameVersion] | no (default=[]) |
| show_when_empty | bool | yes |
| order | int | yes |

### TraitCategory

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str \| None | no |
| character_classes | list[CharacterClass] | no (default=[]) |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| game_versions | list[GameVersion] | no (default=[]) |
| sheet_section_id | str | yes |
| sheet_section_name | str | yes |
| initial_cost | int | yes |
| upgrade_cost | int | yes |
| count_based_cost_multiplier | int \| None | no |
| order | int | yes |
| show_when_empty | bool | yes |

### TraitSubcategory

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str \| None | no |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| game_versions | list[GameVersion] | no (default=[]) |
| character_classes | list[CharacterClass] | no (default=[]) |
| show_when_empty | bool | yes |
| initial_cost | int | yes |
| upgrade_cost | int | yes |
| count_based_cost_multiplier | int \| None | no |
| requires_parent | bool | yes |
| pool | str \| None | no |
| system | str \| None | no |
| category_id | str | yes |
| category_name | str | yes |
| sheet_section_id | str | yes |
| sheet_section_name | str | yes |
| hunter_edge_type | str \| None | no |

### VampireClan

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str \| None | no |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| game_versions | list[GameVersion] | no (default=[]) |
| discipline_ids | list[str] | no (default=[]) |
| bane | NameDescriptionSubDocument \| None | no |
| variant_bane | NameDescriptionSubDocument \| None | no |
| compulsion | NameDescriptionSubDocument \| None | no |
| link | str \| None | no |

### WerewolfTribe

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str \| None | no |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| game_versions | list[GameVersion] | no (default=[]) |
| renown | WerewolfRenown | yes |
| patron_spirit | str \| None | no |
| favor | str \| None | no |
| ban | str \| None | no |
| gift_trait_ids | list[str] | no (default=[]) |
| link | str \| None | no |

### WerewolfAuspice

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str \| None | no |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| game_versions | list[GameVersion] | no (default=[]) |
| gift_trait_ids | list[str] | no (default=[]) |
| link | str \| None | no |

### CharacterConcept

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| examples | list[str] | yes |
| max_specialties | int | no (default=1) |
| specialties | list[CharacterSpecialty] | no (default=[]) |
| favored_ability_names | list[str] | no (default=[]) |

---

## Character Autogen

### ChargenSessionResponse

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| expires_at | datetime | yes |
| requires_selection | bool | yes |
| characters | list[Character] | yes |
| user_id | str | yes |
| campaign_id | str | yes |

### CreateAutogenerateDTO

| Field | Type | Required |
|-------|------|----------|
| character_type | CharacterType | yes |
| character_class | CharacterClass \| None | no |
| experience_level | AutoGenExperienceLevel \| None | no |
| skill_focus | AbilityFocus \| None | no |
| concept_id | str \| None | no |
| vampire_clan_id | str \| None | no |
| werewolf_tribe_id | str \| None | no |
| werewolf_auspice_id | str \| None | no |

### ChargenSessionFinalizeDTO

| Field | Type | Required |
|-------|------|----------|
| session_id | str | yes |
| selected_character_id | str | yes |

---

## Books & Chapters

### CampaignBook

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| name | str | yes |
| description | str \| None | no |
| asset_ids | list[str] | no (default=[]) |
| number | int | yes |
| campaign_id | str | yes |
| num_chapters | int | no (default=0) |
| num_notes | int | no (default=0) |
| num_assets | int | no (default=0) |

### CampaignBookDetail (extends CampaignBook)

| Field | Type | Required |
|-------|------|----------|
| chapters | list[CampaignChapter] \| None | no |
| notes | list[Note] \| None | no |
| assets | list[Asset] \| None | no |

**BookCreate:** `name` (str, 3-50 chars, required), `description` (str \| None, min 3).
**BookUpdate:** All optional, same constraints.

### CampaignChapter

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| name | str | yes (3-50 chars) |
| description | str \| None | no |
| asset_ids | list[str] | no (default=[]) |
| number | int | yes |
| book_id | str | yes |
| num_notes | int | no (default=0) |
| num_assets | int | no (default=0) |

### CampaignChapterDetail (extends CampaignChapter)

| Field | Type | Required |
|-------|------|----------|
| notes | list[Note] \| None | no |
| assets | list[Asset] \| None | no |

**ChapterCreate:** `name` (str, 3-50 chars, required), `description` (str \| None).
**ChapterUpdate:** All optional.

---

## Dice Rolls

### Diceroll

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| dice_size | DiceSize | yes |
| difficulty | int \| None | no |
| num_dice | int | yes |
| num_desperation_dice | int | no (default=0) |
| comment | str \| None | no |
| trait_ids | list[str] | no (default=[]) |
| user_id | str \| None | no |
| character_id | str \| None | no |
| campaign_id | str \| None | no |
| company_id | str | yes |
| result | DiceRollResultSchema \| None | no |

### DiceRollResultSchema

| Field | Type | Required |
|-------|------|----------|
| total_result | int \| None | no |
| total_result_type | RollResultType | yes |
| total_result_humanized | str | yes |
| total_dice_roll | list[int] | no (default=[]) |
| player_roll | list[int] | no (default=[]) |
| desperation_roll | list[int] | no (default=[]) |
| total_dice_roll_emoji | str | yes |
| total_dice_roll_shortcode | str | yes |
| player_roll_emoji | str | yes |
| player_roll_shortcode | str | yes |
| desperation_roll_emoji | str | yes |
| desperation_roll_shortcode | str | yes |

### DicerollCreate

| Field | Type | Constraints |
|-------|------|------------|
| dice_size | DiceSize | required |
| difficulty | int \| None | — |
| num_dice | int | required |
| num_desperation_dice | int | default=0 |
| comment | str \| None | — |
| trait_ids | list[str] | default=[] |
| character_id | str \| None | — |
| campaign_id | str \| None | — |

---

## Dictionary

### DictionaryTerm

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| term | str | yes |
| definition | str \| None | no |
| link | str \| None | no |
| synonyms | list[str] | no (default=[]) |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| company_id | str \| None | no |
| source_type | str \| None | no |
| source_id | str \| None | no |

**DictionaryTermCreate:** `term` (str, required), `definition` (str \| None), `link` (str \| None), `synonyms` (list[str], default=[]).
**DictionaryTermUpdate:** All optional.

---

## Full Sheet

### CharacterFullSheet

| Field | Type | Required |
|-------|------|----------|
| character | Character | yes |
| sections | list[FullSheetTraitSection] | yes |

### FullSheetTraitSection

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str \| None | no |
| order | int | yes |
| show_when_empty | bool | yes |
| categories | list[FullSheetTraitCategory] | yes |

### FullSheetTraitCategory

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str \| None | no |
| initial_cost | int | yes |
| upgrade_cost | int | yes |
| show_when_empty | bool | yes |
| order | int | yes |
| subcategories | list[FullSheetTraitSubcategory] | yes |
| character_traits | list[CharacterTrait] | yes |
| available_traits | list[Trait] | no (default=[]) |

### FullSheetTraitSubcategory

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| name | str | yes |
| description | str \| None | no |
| initial_cost | int | yes |
| upgrade_cost | int | yes |
| show_when_empty | bool | yes |
| requires_parent | bool | yes |
| pool | str \| None | no |
| system | str \| None | no |
| hunter_edge_type | HunterEdgeType \| None | no |
| character_traits | list[CharacterTrait] | yes |
| available_traits | list[Trait] | no (default=[]) |

---

## Developers

### MeDeveloper

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| username | str | yes |
| email | str | yes |
| key_generated | datetime \| None | no |
| companies | list[MeDeveloperCompanyPermission] | yes |

### MeDeveloperWithApiKey (extends MeDeveloper)

| Field | Type | Required |
|-------|------|----------|
| api_key | str | yes |

### MeDeveloperUpdate

`username` (str \| None), `email` (str \| None) — both optional.

### MeDeveloperCompanyPermission

| Field | Type | Required |
|-------|------|----------|
| company_id | str | yes |
| name | str \| None | no |
| permission | PermissionLevel | yes |

---

## Global Admin

### Developer

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| date_modified | datetime | yes |
| username | str | yes |
| email | str | yes |
| key_generated | datetime \| None | no |
| is_global_admin | bool | yes |
| companies | list[DeveloperCompanyPermission] | yes |

### DeveloperWithApiKey (extends Developer)

| Field | Type | Required |
|-------|------|----------|
| api_key | str \| None | no |

### DeveloperCreate

| Field | Type | Constraints |
|-------|------|------------|
| username | str | required |
| email | str | required |
| is_global_admin | bool | default=False |

### DeveloperUpdate

All optional: `username`, `email`, `is_global_admin`.

### DeveloperCompanyPermission

| Field | Type | Required |
|-------|------|----------|
| company_id | str | yes |
| name | str \| None | no |
| permission | PermissionLevel | yes |

### AdminUser (extends User)

Returned by `GlobalAdminService` user methods. Adds archival state to the standard `User` fields. Archived users are not visible through the regular `UsersService`.

| Field | Type | Required |
|-------|------|----------|
| is_archived | bool | yes |

### AdminUserCreate

Request payload for `GlobalAdminService.create_user()`. Creates a user in any company regardless of role hierarchy.

| Field | Type | Constraints |
|-------|------|------------|
| company_id | str | required |
| username | str | required |
| email | str | required |
| role | UserRole | required |
| name_first | str \| None | optional |
| name_last | str \| None | optional |
| discord_profile | DiscordProfileUpdate \| None | optional |
| google_profile | GoogleProfile \| None | optional |
| github_profile | GitHubProfile \| None | optional |
| apple_profile | AppleProfile \| None | optional |

### AdminUserUpdate

Request payload for `GlobalAdminService.update_user()`. All fields optional. Setting `is_archived=False` restores an archived user.

| Field | Type | Constraints |
|-------|------|------------|
| name_first | str \| None | optional |
| name_last | str \| None | optional |
| username | str \| None | optional |
| email | str \| None | optional |
| role | UserRole \| None | optional |
| discord_profile | DiscordProfileUpdate \| None | optional |
| google_profile | GoogleProfile \| None | optional |
| github_profile | GitHubProfile \| None | optional |
| apple_profile | AppleProfile \| None | optional |
| is_archived | bool \| None | optional |

### ServerLogEntry

A single parsed server log line. All fields nullable to tolerate partial or malformed lines.

| Field | Type | Required |
|-------|------|----------|
| timestamp | str \| None | no |
| level | str \| None | no |
| name | str \| None | no |
| message | str \| None | no |
| exception | str \| None | no |
| extra | dict[str, Any] | no (default={}) |
| raw | str \| None | no |

### ServerLogArchive

Frozen dataclass (not a Pydantic model) returned by `download_logs()`.

| Field | Type | Required |
|-------|------|----------|
| filename | str | yes |
| content | bytes | yes |

---

## Pagination

### PaginatedResponse[T]

| Field | Type | Required |
|-------|------|----------|
| items | list[T] | yes |
| limit | int | yes |
| offset | int | yes |
| total | int | yes |

**Computed properties:** `has_more` (bool), `next_offset` (int), `total_pages` (int), `current_page` (int).

---

## System

### SystemHealth

| Field | Type | Required |
|-------|------|----------|
| database_status | str | yes |
| cache_status | str | yes |
| database_latency_ms | float \| None | yes |
| cache_latency_ms | float \| None | yes |
| uptime | str | yes |
| version | str | yes |

---

## User Lookup

### UserLookupResult

| Field | Type | Required |
|-------|------|----------|
| company_id | str | yes |
| company_name | str | yes |
| user_id | str | yes |
| role | UserRole | yes |

---

## Audit Logs

### AuditLog

| Field | Type | Required |
|-------|------|----------|
| id | str | yes |
| date_created | datetime | yes |
| entity_type | AuditEntityType | yes |
| operation | AuditOperation | yes |
| target_entity_id | str | yes |
| description | str | yes |
| changes | dict[str, Any] \| None | no |
| company_id | str | yes |
| acting_user_id | str \| None | no |
| user_id | str \| None | no |
| campaign_id | str \| None | no |
| book_id | str \| None | no |
| chapter_id | str \| None | no |
| character_id | str \| None | no |
| request_id | str \| None | no |
| summary | str \| None | no |

### AuditLogDetail

Inherits all `AuditLog` fields plus:

| Field | Type | Required |
|-------|------|----------|
| method | str \| None | no |
| url | str \| None | no |
| request_json | dict[str, Any] \| None | no |
| request_body | str \| None | no |
| path_params | dict[str, str] \| None | no |
| query_params | dict[str, str] \| None | no |
| operation_id | str \| None | no |
| handler_name | str \| None | no |
