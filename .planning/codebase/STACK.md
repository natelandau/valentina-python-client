# Technology Stack

**Analysis Date:** 2026-02-20

## Languages

**Primary:**

- Python 3.13 - Main implementation language, enforced via `.python-version`

**Secondary:**

- Python 3.14 - Listed in classifiers for forward compatibility

## Runtime

**Environment:**

- Python 3.13+ (requires-python = ">=3.13" in pyproject.toml)

**Package Manager:**

- uv (UV Package Manager) - Primary dependency manager
    - Configured in pyproject.toml with [build-system] using uv_build backend
    - Lockfile: `uv.lock` present (143KB, comprehensive dependency lock)

## Frameworks

**Core:**

- httpx 0.28.1+ - HTTP client for async/await based API requests (`src/vclient/client.py`)
- Pydantic v2 2.12.5+ - Data validation and serialization for request/response models (`src/vclient/models/`)
- Loguru 0.7.3+ - Structured logging with integration to stdlib logging (`src/vclient/__init__.py`)
- anyio 4.12.1+ - Async compatibility layer (dependency of httpx)

**Testing:**

- pytest 9.0.2+ - Test runner and framework
- pytest-anyio 0.0.0 - Async test support
- pytest-xdist 3.8.0 - Parallel test execution
- pytest-cov 7.0.0 - Coverage reporting
- pytest-mock 3.15.1 - Mocking utilities
- pytest-clarity 1.0.1 - Enhanced test output
- pytest-sugar 1.1.1 - Colored output
- pytest-repeat 0.9.4 - Test repetition
- pytest-devtools 1.0.0 - Development utilities
- respx 0.22.0 - HTTP request mocking for integration tests

**Build/Dev:**

- ruff 0.15.2+ - Fast Python linter and formatter
- ty 0.0.17 - Static type checker
- typos 1.43.5 - Spell checker
- vulture 2.14 - Dead code finder
- shellcheck-py 0.11.0.1 - Shell script linting
- yamllint 1.38.0 - YAML linting
- commitizen 4.13.8+ - Conventional commit tooling
- duty 1.9.0 - Task runner (defined in `duties.py`)
- prek 0.3.3 - Utilities for pre-commit hooks
- coverage 7.13.4 - Code coverage measurement

## Key Dependencies

**Critical:**

- httpx 0.28.1+ - Enables async HTTP operations to the Valentina API, supports automatic retry logic
- Pydantic[email] 2.12.5+ - Type-safe data validation for all API requests/responses; email extra for email field validation
- loguru 0.7.3+ - Structured logging output with context binding for debugging and monitoring

**Infrastructure:**

- anyio 4.12.1+ - Provides async compatibility, allows use of structured concurrency patterns

## Configuration

**Environment:**

- Configuration via environment variables in `src/vclient/client.py`:
    - `VALENTINA_CLIENT_BASE_URL` - API base URL (required)
    - `VALENTINA_CLIENT_API_KEY` - Authentication key (required)
    - `VALENTINA_CLIENT_DEFAULT_COMPANY_ID` - Default company scope (optional)
- Fallback to direct constructor arguments (explicit args override env vars)
- Configuration stored in `_APIConfig` dataclass (`src/vclient/config.py`)

**Build:**

- `pyproject.toml` - Primary project configuration with dependencies, tool configs
    - Python metadata (name: valentina-python-client, version: 1.3.0)
    - Tool configurations: ruff, ty, pytest, coverage, commitizen, vulture
- `.pre-commit-config.yaml` - Pre-commit hook pipeline including commitizen, ruff, typos, gitleaks, shellcheck, ty, pytest
- `ruff.toml` settings in pyproject.toml:
    - target-version: py313
    - line-length: 100
    - Google-style docstrings convention
    - Fixed formatting with isort rules
- `.python-version` - Version constraint file (3.13)
- `.yamllint.yml` - YAML linting configuration

## HTTP Client Configuration

**Default Behavior:**

- Default timeout: 30 seconds (`DEFAULT_TIMEOUT`)
- Default max retries: 3 (`DEFAULT_MAX_RETRIES`)
- Default retry delay: 1.0 seconds (`DEFAULT_RETRY_DELAY`)
- Default retry statuses: {429, 500, 502, 503, 504} (`DEFAULT_RETRY_STATUSES`)
- Auto-retry rate limits: True by default
- Idempotency keys: Optional, can be auto-generated for POST/PUT/PATCH requests

**Headers:**

- Automatic User-Agent: `vclient/{version} Python/{python_version}` (`src/vclient/client.py`)
- Content-Type: application/json
- Accept: application/json
- X-API-KEY: Authentication header (from `API_KEY_HEADER` constant)

## Platform Requirements

**Development:**

- Python 3.13+
- uv for package management
- git (for pre-commit hooks)
- Supports macOS, Linux, and Windows

**Production:**

- Python 3.13+
- async runtime capable (tested with asyncio)
- HTTP client library (httpx, included as dependency)

---

_Stack analysis: 2026-02-20_
