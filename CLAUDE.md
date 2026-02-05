# vclient

Async Python client for the Valentina API. Python 3.13+ required.

## SPRINT.md

**Always check SPRINT.md at the start of a session.** This file tracks the current sprint backlog, in-progress work, and prioritized tasks. Update it when starting or completing tasks.

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

<!-- agent-glue-rules -->

## MANDATORY PROJECT-SPECIFIC INSTRUCTIONS

The following rule files contain project-specific instructions that MUST be read and followed. These rules are not optional - you MUST read each linked file and understand its contents before starting any work.

-   [`.glue/rules/git-commit-message-rules.md`](.glue/rules/git-commit-message-rules.md) - Git commit message rules
-   [`.glue/rules/global-coding-standards.md`](.glue/rules/global-coding-standards.md) - Global coding style and standards
-   [`.glue/rules/inline-comments-standards.md`](.glue/rules/inline-comments-standards.md) - How to write inline comments
-   [`.glue/rules/python-packaging.md`](.glue/rules/python-packaging.md) - Python packaging standards
-   [`.glue/rules/python-standards.md`](.glue/rules/python-standards.md) - Python coding standards
-   [`.glue/rules/python-testing-standards.md`](.glue/rules/python-testing-standards.md) - Python testing standards

<!-- agent-glue-rules -->
