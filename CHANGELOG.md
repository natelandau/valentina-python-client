## v1.7.0 (2026-03-01)

### Feat

- add synchronous client (#34)

## v1.6.1 (2026-02-28)

### Fix

- **models**: add id to all response models

## v1.6.0 (2026-02-28)

### Feat

- **companies**: add get_statistics method (#32)

## v1.5.2 (2026-02-27)

### Fix

- **user**: support detailed name fields (#31)

## v1.5.1 (2026-02-24)

### Fix

- **company**: add resources_modified_at field (#30)

## v1.5.0 (2026-02-22)

### Feat

- add get_assets_page, list_all_assets, iter_all_assets to all services (#28)

## v1.4.1 (2026-02-22)

### Refactor

- **models**: rename Asset to be backend agnostic

## v1.4.0 (2026-02-22)

### Feat

- **services**: infer MIME type from filename in upload_asset (#27)

### Fix

- **http**: remove hardcoded Content-Type header (#26)

## v1.3.2 (2026-02-21)

### Fix

- **character-trait**: fix endpoint

## v1.3.1 (2026-02-21)

### Fix

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

## v1.2.1 (2026-02-18)

### Fix

- **models**: change game_version to game_versions list (#17)

## v1.2.0 (2026-02-17)

### Feat

- **config**: add environment variable support (#16)
- add constants validation against API (#15)

### Fix

- **character_trait**: replace POST with PUT

## v1.1.2 (2026-02-15)

### Fix

- **endpoints**: correct dictionary path and auspice typo (#14)
- **experience**: use requesting_user_id in body (#13)

## v1.1.1 (2026-02-15)

### Fix

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
