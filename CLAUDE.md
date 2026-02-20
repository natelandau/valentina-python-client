# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

vclient - Async Python client for the Valentina API. Python 3.13+ required.

## Commands

```bash
uv run duty lint                          # Run all linting (ruff, ty, typos, format)
uv run duty test                          # Run tests with coverage
uv run duty clean                         # Clean build artifacts
uv run duty validate_constants            # Validate constants against live API

# Single test or specific tests
uv run pytest tests/path/to/test_file.py -x
uv run pytest tests/ -k "test_name_pattern" -x
```

## Project Structure

```
src/vclient/
├── services/              # API service classes (companies, campaigns, characters, etc.)
├── models/                # Pydantic v2 models
├── client.py              # VClient
├── config.py              # Internal configuration (_APIConfig)
├── constants.py           # Shared constants (Literal types for API enums)
├── endpoints.py           # API endpoint paths
├── exceptions.py          # RFC 9457 exception classes
├── registry.py            # Service factory functions
└── validate_constants.py  # Constants validation against API options

scripts/
└── validate_constants.py  # CLI script for constants validation

tests/
├── unit/          # Model validation tests
└── integration/   # Service tests with respx HTTP mocking
```

## Model Naming Conventions

| Pattern          | Purpose             | Example         |
| ---------------- | ------------------- | --------------- |
| `{Entity}`       | Response model      | `Company`       |
| `{Entity}Create` | Create request      | `CompanyCreate` |
| `{Entity}Update` | Update request      | `CompanyUpdate` |
| `_{Internal}`    | Internal-only model | `_GrantAccess`  |

Models are defined in `models/*.py` and exported from `models/__init__.py`.

## Service Pattern

Services extend `BaseService` and provide standard methods:
`get_page()`, `list_all()`, `iter_all()`, `get(id)`, `create()`, `update(id)`, `delete(id)`

**Service Hierarchy** - Services are scoped at initialization time:

```
VClient
├── companies()           # Top-level: no scoping
├── users(company_id)     # Scoped to company
├── campaigns(user_id, company_id)
├── characters(user_id, campaign_id, company_id)
├── character_traits(user_id, campaign_id, character_id, company_id)
└── ... etc
```

**Primary access via factory functions** (preferred over direct instantiation):

```python
from vclient import VClient, campaigns_service

async with VClient(base_url="https://api.valentina-noir.com", api_key="...") as client:
    campaigns = client.campaigns(user_id="123")
    all_campaigns = await campaigns.list_all()
```

**Environment variable configuration** — `base_url`, `api_key`, and `default_company_id` can be set via environment variables instead of constructor arguments. Explicit arguments always take precedence.

| Env Var                               | Maps To              |
| ------------------------------------- | -------------------- |
| `VALENTINA_CLIENT_BASE_URL`           | `base_url`           |
| `VALENTINA_CLIENT_API_KEY`            | `api_key`            |
| `VALENTINA_CLIENT_DEFAULT_COMPANY_ID` | `default_company_id` |

Constants for these names are in `constants.py`: `ENV_BASE_URL`, `ENV_API_KEY`, `ENV_DEFAULT_COMPANY_ID`.

Factory functions in `registry.py`: `books_service`, `campaigns_service`, `chapters_service`, `characters_service`, `companies_service`, `dicerolls_service`, `dictionary_service`, `users_service`, etc.

## Code Style

- Google-style docstrings
- Type hints required
- Pydantic v2 models with field validation
- Async/await throughout (httpx for HTTP)

## Exceptions

All exceptions inherit from `APIError` and follow RFC 9457 Problem Details format.

| Exception                | HTTP Status | Use Case                                                  |
| ------------------------ | ----------- | --------------------------------------------------------- |
| `AuthenticationError`    | 401         | Invalid/missing API key                                   |
| `AuthorizationError`     | 403         | Valid key, insufficient permissions                       |
| `NotFoundError`          | 404         | Resource not found                                        |
| `ValidationError`        | 400         | Server-side validation failed (has `.invalid_parameters`) |
| `RequestValidationError` | -           | Client-side Pydantic validation (pre-request)             |
| `ConflictError`          | 409         | Idempotency key reuse                                     |
| `RateLimitError`         | 429         | Rate limited (has `.retry_after`, `.remaining`)           |
| `ServerError`            | 5xx         | Server errors                                             |

All have `.status_code`, `.title`, `.detail`, `.instance` properties from RFC 9457.

## Constants Validation

The `Literal` type constants in `constants.py` must stay in sync with the API's `/options` endpoint. The validation system detects drift.

**Key files:**

- `src/vclient/validate_constants.py` — mapping table (`CONSTANT_MAP`), `validate()`, `print_report()`
- `scripts/validate_constants.py` — CLI wrapper (reads `.env.secret`, env vars, or CLI args)

**When adding/changing a constant:** Update both `constants.py` and `CONSTANT_MAP` in `validate_constants.py`. The mapping links each local constant name to its API location (`api_category`, `api_option`). Some names differ between local and API (e.g., `CharacterInventoryType` → `InventoryItemType`, `PermissionLevel` → `CompanyPermission`).

**Running validation:** `uv run duty validate_constants` (requires live API access with credentials in `.env.secret` or environment).

## Testing

- Unit tests: model validation, no HTTP
- RESPX mocking is used for integration tests. No HTTP requests.
- Integration tests: service methods with respx mocking
- Shared fixtures in `tests/shared_response_fixtures.py`

## Documentation

**IMPORTANT:** The public-facing documentation for this client library is maintained in a separate repository.

- **Location:** `../valentina-noir/docs/python-api-client/`
- **Published URL:** https://docs.valentina-noir.com/python-api-client/

When making changes to this client that affect the public API, you MUST review and update the corresponding documentation:

| Change Type                    | Documentation to Update                  |
| ------------------------------ | ---------------------------------------- |
| New service                    | Create new service doc                   |
| New method on existing service | Update the relevant service doc          |
| Changed method signature       | Update the relevant service doc          |
| New/changed model              | Update `models.md`                       |
| New/changed exception          | Update `index.md` Error Handling section |
| Configuration option changes   | Update `index.md` Configuration section  |

Documentation files follow the pattern `{service_name}.md` (e.g., `campaigns.md`, `users.md`).

The documentation is managed by zensical and navigation is managed in `../valentina-noir/zensical.toml.`.
