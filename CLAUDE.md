# vclient

Async Python client for the Valentina API. Python 3.13+ required.

## Commands

```bash
uv run duty lint    # Run all linting (ruff, ty, typos, format)
uv run duty test    # Run tests with coverage (requires Docker)
uv run duty clean   # Clean build artifacts
```

## Project Structure

```
src/vclient/
├── services/     # API service classes (companies, campaigns, characters, etc.)
├── models/       # Pydantic v2 models
├── config.py     # APIConfig
├── client.py     # VClient
└── endpoints.py  # API endpoint paths

tests/
├── unit/         # Model validation tests
└── integration/  # Service tests with respx HTTP mocking
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

Services extend `BaseService` and provide:

-   `get_page()` - paginated results
-   `list_all()` - all results as list
-   `iter_all()` - async iterator for large datasets
-   `get(id)`, `create()`, `update(id)`, `delete(id)`

## Code Style

-   Google-style docstrings
-   Type hints required
-   Pydantic v2 models with field validation
-   Async/await throughout (httpx for HTTP)

## Testing

-   Unit tests: model validation, no HTTP
-   RESPX mocking is used for integration tests. No HTTP requests.
-   Integration tests: service methods with respx mocking
-   Shared fixtures in `tests/shared_response_fixtures.py`

## Documentation

**IMPORTANT:** The public-facing documentation for this client library is maintained in a separate repository.

-   **Location:** `../valentina-noir/docs/python-api-client/`
-   **Published URL:** https://docs.valentina-noir.com/python-api-client/

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

<!-- agent-glue-rules -->
@.glue/rules/git-commit-message-rules.md
@.glue/rules/global-coding-standards.md
@.glue/rules/inline-comments-standards.md
@.glue/rules/python-git-workflow.md
@.glue/rules/python-packaging.md
@.glue/rules/python-standards.md
@.glue/rules/python-testing-standards.md
<!-- agent-glue-rules -->
