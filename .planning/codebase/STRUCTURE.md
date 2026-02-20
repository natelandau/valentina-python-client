# Codebase Structure

**Analysis Date:** 2026-02-20

## Directory Layout

```
valentina-python-client/
├── src/vclient/                    # Main package
│   ├── models/                     # Pydantic v2 data models
│   │   ├── __init__.py             # Central export of all models
│   │   ├── books.py                # Campaign book models
│   │   ├── campaigns.py            # Campaign models
│   │   ├── chapters.py             # Campaign chapter models
│   │   ├── character_*.py          # Character and trait models
│   │   ├── characters.py           # Character detail models
│   │   ├── companies.py            # Company and permission models
│   │   ├── developers.py           # Developer account models
│   │   ├── diceroll.py             # Dice roll models
│   │   ├── dictionary.py           # Dictionary term models
│   │   ├── global_admin.py         # Admin user management models
│   │   ├── pagination.py           # PaginatedResponse[T] generic
│   │   ├── shared.py               # Shared subdocuments (Note, Trait, Asset, etc.)
│   │   └── system.py               # System health check models
│   ├── services/                   # Service layer implementations
│   │   ├── __init__.py             # Export all service classes
│   │   ├── base.py                 # BaseService with HTTP operations
│   │   ├── campaign_book_chapters.py
│   │   ├── campaign_books.py
│   │   ├── campaigns.py
│   │   ├── character_*.py          # Character-related services
│   │   ├── characters.py
│   │   ├── character_traits.py
│   │   ├── companies.py
│   │   ├── developers.py
│   │   ├── dicerolls.py
│   │   ├── dictionary.py
│   │   ├── global_admin.py
│   │   ├── options.py
│   │   ├── system.py
│   │   └── users.py
│   ├── __init__.py                 # Package entry point, exports VClient and factory functions
│   ├── client.py                   # Main VClient class
│   ├── config.py                   # Internal _APIConfig dataclass
│   ├── constants.py                # API constants (Literal type definitions, env var names, defaults)
│   ├── endpoints.py                # Centralized API endpoint paths
│   ├── exceptions.py               # RFC 9457 exception hierarchy
│   ├── registry.py                 # Default client management and factory functions
│   ├── validate_constants.py       # Constants validation against live API
│   └── py.typed                    # PEP 561 type hints marker
├── tests/
│   ├── unit/                       # Unit tests (no HTTP)
│   │   ├── conftest.py             # Test fixtures and setup
│   │   ├── models/                 # Model validation tests (one file per model module)
│   │   │   ├── test_books.py
│   │   │   ├── test_campaigns.py
│   │   │   ├── test_chapters.py
│   │   │   ├── test_character_trait.py
│   │   │   ├── test_characters.py
│   │   │   ├── test_companies.py
│   │   │   ├── test_developers.py
│   │   │   ├── test_global_admin.py
│   │   │   ├── test_pagination.py
│   │   │   ├── test_shared.py
│   │   │   ├── test_system.py
│   │   │   └── test_users.py
│   │   ├── test_exceptions.py      # Exception handling tests
│   │   ├── test_registry.py        # Factory function tests
│   │   └── test_validate_constants.py
│   ├── integration/                # Integration tests (respx HTTP mocking)
│   │   ├── test_*.py               # One file per service
│   │   └── ...
│   ├── conftest.py                 # Top-level fixtures
│   ├── shared_response_fixtures.py # Shared mock response data
│   └── __init__.py
├── scripts/
│   └── validate_constants.py       # CLI wrapper for constants validation
├── docs/                           # Documentation (external link to valentina-noir repo)
├── .github/                        # GitHub Actions workflows
├── pyproject.toml                  # Project metadata, dependencies, build config
├── CLAUDE.md                       # Project guidelines for Claude
├── README.md                       # Project overview
├── CHANGELOG.md                    # Version history
└── duties.py                       # Task runner commands (invoke-style)
```

## Directory Purposes

**src/vclient/:**
- Purpose: Main package code
- Contains: All client, service, model, and utility code
- Key files: `client.py` (entry point), `registry.py` (factory functions), `exceptions.py` (error types)

**src/vclient/models/:**
- Purpose: Pydantic v2 data models for request/response validation
- Contains: Response models (`Campaign`, `Company`, `Character`), request models (`CampaignCreate`, `CompanyUpdate`), internal DTOs (`_GrantAccess`, `_ExperienceAddRemove`)
- Key files: `__init__.py` (central export), `shared.py` (reusable subdocuments)

**src/vclient/services/:**
- Purpose: Service implementations providing domain-specific API operations
- Contains: One service class per major entity (Companies, Users, Campaigns, Characters, etc.)
- Key files: `base.py` (abstract base with HTTP helpers), one implementation per entity

**tests/unit/:**
- Purpose: Fast tests of models and core logic without HTTP requests
- Contains: Pydantic model validation tests, exception tests, registry tests
- Pattern: One test file per models module, tests validate field names, types, defaults, validation rules

**tests/integration/:**
- Purpose: Service method tests with respx HTTP mocking
- Contains: Mock responses and assertions for each service method
- Pattern: One test file per service, tests verify request construction and response parsing

**tests/shared_response_fixtures.py:**
- Purpose: Centralized mock response data reused across integration tests
- Contains: Sample JSON responses for common entities
- Usage: Imported by integration test files to avoid duplication

## Key File Locations

**Entry Points:**

- `src/vclient/client.py`: VClient class initialization, service properties, scoping methods
- `src/vclient/__init__.py`: Package exports (VClient, factory functions, logging setup)
- `src/vclient/registry.py`: Factory functions (`companies_service()`, `users_service()`, etc.)

**Configuration:**

- `src/vclient/config.py`: `_APIConfig` dataclass with all client settings
- `src/vclient/constants.py`: API constant definitions and environment variable names
- `pyproject.toml`: Project metadata, dependencies, version

**Core Logic:**

- `src/vclient/services/base.py`: HTTP request handling, retry logic, response parsing
- `src/vclient/exceptions.py`: Exception hierarchy and RFC 9457 Problem Details
- `src/vclient/endpoints.py`: Centralized API endpoint path strings

**Testing:**

- `tests/unit/conftest.py`: Common test fixtures
- `tests/shared_response_fixtures.py`: Mock response data
- `tests/integration/`: Service-specific integration tests

## Naming Conventions

**Files:**

- Service files: `{entity}.py` - lowercase, singular (e.g., `companies.py`, `users.py`, `campaigns.py`)
- Model files: `{entity}.py` - lowercase, singular (e.g., `companies.py`, `characters.py`)
- Test files: `test_{module}.py` - matches module being tested (e.g., `test_companies.py`)
- Test subdirectories: Mirror source structure (e.g., `tests/unit/models/`, `tests/integration/`)

**Directories:**

- Package directories: `snake_case`, lowercase (e.g., `vclient`, `models`, `services`)
- Test directories: Prefix with `test_` for integration tests (e.g., `tests/unit/`, `tests/integration/`)

**Classes:**

- Service classes: `{Entity}Service` - PascalCase (e.g., `CompaniesService`, `UsersService`)
- Model classes: `{Entity}` for response (e.g., `Company`, `Campaign`), `{Entity}Create` for create request, `{Entity}Update` for update request
- Internal models: `_{Internal}` - leading underscore (e.g., `_GrantAccess`, `_ExperienceAddRemove`)
- Exception classes: `{Specific}Error` - PascalCase (e.g., `NotFoundError`, `ValidationError`, `RateLimitError`)

**Functions:**

- Service methods: `snake_case` (e.g., `list_all()`, `get_page()`, `iter_all()`)
- BaseService helpers: `_snake_case` - protected/private with leading underscore (e.g., `_request()`, `_get()`, `_post()`)
- Factory functions: `{entity}_service()` - lowercase (e.g., `companies_service()`, `campaigns_service()`)

**Constants:**

- Public constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`, `API_KEY_HEADER`, `ENV_BASE_URL`)
- Type aliases: `PascalCase` Literal definitions (e.g., `CharacterClass`, `GameVersion`, `PermissionLevel`)
- Internal constants: `_UPPER_SNAKE_CASE` - leading underscore (e.g., `_BASE` in Endpoints class)

## Where to Add New Code

**New Service (e.g., for a new API entity):**
- Implementation: `src/vclient/services/{entity}.py`
- Models: `src/vclient/models/{entity}.py` (response) + `src/vclient/models/__init__.py` (export)
- Endpoints: Add constants to `src/vclient/endpoints.py`
- Client method: Add property/method to `src/vclient/client.py`
- Factory function: Add to `src/vclient/registry.py`
- Tests: `tests/unit/models/test_{entity}.py` + `tests/integration/test_{entity}.py`

**New Service Method (e.g., additional operation on existing service):**
- Implementation: Add method to service class in `src/vclient/services/{entity}.py`
- Models: If new request/response shape, add to `src/vclient/models/{entity}.py`
- Endpoints: Add constant to `src/vclient/endpoints.py` if new URL pattern
- Tests: Add test to `tests/integration/test_{entity}.py`

**New Model/Type:**
- Response model: `src/vclient/models/{entity}.py`
- Request model: Same file as response (request models in same module as related response)
- Export: Add to `models/__init__.py` in `__all__` and import statement
- Tests: `tests/unit/models/test_{entity}.py`

**Shared Utilities (used across multiple services):**
- Shared helpers: `src/vclient/services/base.py` as protected methods (leading `_`)
- Shared models: `src/vclient/models/shared.py` for reusable subdocuments
- Shared constants: `src/vclient/constants.py` for type aliases and settings

## Special Directories

**src/vclient/models/__pycache__:**
- Purpose: Python bytecode cache
- Generated: Yes (automatically by Python)
- Committed: No (.gitignore)

**tests/__pycache__:**
- Purpose: Pytest bytecode cache
- Generated: Yes (automatically by pytest)
- Committed: No (.gitignore)

**.planning/:**
- Purpose: GSD-generated analysis documents
- Generated: Yes (by /gsd:map-codebase command)
- Committed: No (.gitignore)

**dist/:**
- Purpose: Package distribution artifacts
- Generated: Yes (by build system)
- Committed: No (.gitignore)

**.venv/:**
- Purpose: Python virtual environment for development
- Generated: Yes (by uv)
- Committed: No (.gitignore)

**.cache/**:
- Purpose: Temporary cache files
- Generated: Yes (by linting and build tools)
- Committed: No (.gitignore)

## Service Hierarchy and Scoping

Services use hierarchical scoping through method parameters. Understanding the scope is critical for correct usage:

**Top-level (no scoping):**
- `client.companies` → `CompaniesService` - Access all accessible companies
- `client.developer` → `DeveloperService` - Manage own developer profile
- `client.global_admin` → `GlobalAdminService` - Manage all developers (admin only)
- `client.system` → `SystemService` - System health checks

**Company-scoped:**
- `client.users(company_id)` → `UsersService` - Users within a company
- `client.dictionary(company_id)` → `DictionaryService` - Terms within a company
- `client.character_blueprint(company_id)` → `CharacterBlueprintService` - Blueprint for a company
- `client.options(company_id)` → `OptionsService` - API options for a company

**User-scoped (requires company_id and user_id):**
- `client.campaigns(user_id, company_id)` → `CampaignsService` - Campaigns for a user
- `client.dicerolls(user_id, company_id)` → `DicerollService` - Dice rolls by a user

**Campaign-scoped (requires company_id, user_id, campaign_id):**
- `client.books(user_id, campaign_id, company_id)` → `BooksService` - Books in a campaign
- `client.characters(user_id, campaign_id, company_id)` → `CharactersService` - Characters in a campaign
- `client.character_autogen(user_id, campaign_id, company_id)` → `CharacterAutogenService` - Character generation for a campaign

**Character-scoped (requires company_id, user_id, campaign_id, character_id):**
- `client.character_traits(user_id, campaign_id, character_id, company_id)` → `CharacterTraitsService`
- `client.chapters(user_id, campaign_id, book_id, company_id)` → `ChaptersService` - Chapters in a book

Each service stores its scope context internally and passes it to all API calls automatically, eliminating the need to repeat these parameters on every method call.

---

*Structure analysis: 2026-02-20*
