## v1.15.1 (2026-03-14)

### Fix

- **models**: rename session_id to id in ChargenSessionResponse

## v1.15.0 (2026-03-14)

### Feat

- **chargen**: add list and get endpoints for chargen sessions (#47)

### Fix

- **user**: add lifetime experience to user model (#46)

## v1.14.0 (2026-03-10)

### Feat

- **users**: add register and merge endpoints (#45)

### Fix

- **user**: add email filter to list endpoints

## v1.13.0 (2026-03-09)

### Feat

- **users**: add google/github profiles to UserCreate and UserUpdate

## v1.12.0 (2026-03-09)

### Feat

- **users**: integrate GoogleProfile and GitHubProfile models (#44)

## v1.11.0 (2026-03-09)

### Feat

- **users**: add user approval workflow (#43)
- **testing**: add per-ID response matching (#42)

## v1.10.0 (2026-03-08)

### Feat

- **testing**: add set_response/set_error API for FakeVClient (#41)

### Fix

- **models**: make User.role a required field (#40)

## v1.9.0 (2026-03-08)

### Feat

- **character-traits**: add CharacterTraitAdd model (#39)

## v1.8.0 (2026-03-06)

### Feat

- **testing**: add vclient.testing module with fake client (#38)

### Fix

- **character-trait**: update the sync client
- **blueprint**: require sheet section id in Trait model
- **character-trait**: return full trait in value-options response
- **character_trait**: delete with currency param (#37)
- **character_trait**: add name to CharacterTraitValueOption (#36)

## v1.7.0 (2026-03-01)

### Feat

- add synchronous client (#34)

### Fix

- **models**: add id to all response models

## v1.6.0 (2026-02-28)

### Feat

- **companies**: add get_statistics method (#32)

### Fix

- **user**: support detailed name fields (#31)
- **company**: add resources_modified_at field (#30)

## v1.5.0 (2026-02-22)

### Feat

- add get_assets_page, list_all_assets, iter_all_assets to all services (#28)

### Refactor

- **models**: rename Asset to be backend agnostic

## v1.4.0 (2026-02-22)

### Feat

- **services**: infer MIME type from filename in upload_asset (#27)

### Fix

- **http**: remove hardcoded Content-Type header (#26)
- **character-trait**: fix endpoint
- **models**: use Annotated types for optional field constraints (#25)
- rename .env.secrets to .env.secret (#23)

### Refactor

- **logging**: use structured fields over formatted messages (#24)

## v1.3.0 (2026-02-20)

### Feat

- **logging**: add structured logging with loguru (#22)
- **retry**: add retry on transient 5xx and network errors (#20)
- **client**: add User-Agent header to HTTP requests (#19)

### Fix

- **client**: clear default client on close (#21)
- **models**: sync response models with API schemas (#18)
- **models**: change game_version to game_versions list (#17)

## v1.2.0 (2026-02-17)

### Feat

- **config**: add environment variable support (#16)
- add constants validation against API (#15)

### Fix

- **character_trait**: replace POST with PUT
- **endpoints**: correct dictionary path and auspice typo (#14)
- **experience**: use requesting_user_id in body (#13)
- **models**: expose _TraitAssign as public API (#12)

## v1.1.0 (2026-02-15)

### Feat

- **blueprint**: add edge_type filter to hunter edge methods (#11)
- **blueprint**: add filters to werewolf methods (#10)
- **blueprint**: add game_version filter to vampire clan methods (#9)

## v1.0.3 (2026-02-15)

### Fix

- **diceroll**: rename create_from_quickroll method (#8)

## v1.0.2 (2026-02-15)

### Refactor

- **services**: remove positional-only markers (#7)

## v1.0.1 (2026-02-14)

### Refactor

- **services**: add _build_params helper and cleanup (#5)
- remove unused code
- **client**: use argument-only configuration (#4)

## v1.0.0 (2026-02-05)

### Feat

- improve developer experience (#1)
- **character-trait**: consolidate value endpoints
- **character-trait**: add cost preview endpoints
- **character**: add mage attributes to create/update
- **characters**: add class attributes to create/update
- **company**: support updated response from create company
- add character autogeneration service
- add options service
- add diecroll service
- add dictionary
- add character blueprint service
- **character**: add hunter support
- **character**: add werewolf specials
- **character**: add character service
- **chapters**: add chapter service
- add campaign_book_service
- **campaigns**: add CampaignsService with factory pattern
- **users**: add quickroll CRUD endpoints
- **users**: add notes endpoints
- **client**: add auto idempotency key generation
- **users**: add asset upload endpoint
- **users**: add experience management methods
- **user**: add user_service
- **developers**: add developer service for self-service operations
- **exceptions**: include full API error context in exception strings
- **exceptions**: add RequestValidationError for client-side validation
- **registry**: add factory functions for individual service imports
- create package
- **exceptions**: add RFC 9457 Problem Details support
- **companies**: add Companies service with Pydantic DTOs
- **api**: add initial Valentina API client scaffold

### Fix

- **diceroll**: fix typo in public facing api
- **character**: remove id from specialties in response
- **characters**: add traits to create request, remove asset_ids
- correct method for book renumber
- export chapters_service
- remove enum from system health

### Refactor

- improve package imports
- **models**: simplify DTOs by removing bloat
- **models**: replace StrEnum classes with Literal type aliases
- **tests**: improve code standards compliance
