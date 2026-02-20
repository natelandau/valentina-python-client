# Coding Conventions

**Analysis Date:** 2026-02-20

## Naming Patterns

**Files:**

- Python modules: `snake_case.py` (e.g., `client.py`, `base_service.py`, `exceptions.py`)
- Private/internal modules: Leading underscore for internal config (e.g., `_api_config.py`)
- Package directories: `snake_case` (e.g., `services/`, `models/`)

**Functions:**

- Public functions: `snake_case` (e.g., `list_all()`, `get_page()`, `create()`)
- Private methods: Leading underscore (e.g., `_validate_request()`, `_calculate_backoff_delay()`, `_resolve_company_id()`)
- Factory functions: `{service_name}_service()` (e.g., `companies_service()`, `campaigns_service()`)
- Static helper methods: `_is_retryable_method()`, `_generate_idempotency_key()`

**Variables:**

- Local variables: `snake_case` (e.g., `resolved_base_url`, `request_class`, `retry_after`)
- Instance attributes: `_snake_case` with leading underscore for private (e.g., `self._client`, `self._http`, `self._config`)
- Type variables: `T` for bound TypeVars (e.g., `T = TypeVar("T", bound=BaseModel)`)

**Types/Classes:**

- Model classes: `PascalCase` (e.g., `Company`, `User`, `Character`)
- Request models: `{Entity}Create`, `{Entity}Update` (e.g., `CompanyCreate`, `CompanyUpdate`)
- Internal models: Leading underscore (e.g., `_GrantAccess`, `_APIConfig`)
- Service classes: `{Entity}Service` (e.g., `CompaniesService`, `UsersService`)
- Exception classes: `PascalCase` ending with `Error` (e.g., `APIError`, `ValidationError`, `RateLimitError`)
- Literal type constants: `PascalCase` (e.g., `CharacterClass`, `PermissionLevel`, `GameVersion`)

**Constants:**

- Module-level constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`, `API_KEY_HEADER`, `ENV_BASE_URL`)
- Frozenset constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_RETRY_STATUSES`, `IDEMPOTENT_HTTP_METHODS`)

## Code Style

**Formatting:**

- Tool: Ruff formatter
- Line length: 100 characters (configured in `pyproject.toml`)
- Quote style: Double quotes (`"text"` not `'text'`)
- Indentation: 4 spaces
- Skip magic trailing comma: False (Ruff will reformat collections across multiple lines)

**Linting:**

- Tool: Ruff (rustfmt-inspired Python linter)
- Configuration: `pyproject.toml` `[tool.ruff]` section
- Severity: Selected rules set to ALL with specific ignores per file type
- Maximum cyclomatic complexity: 10 (McCabe complexity)
- Per-file ignores for services and tests (allow more parameters, skip certain checks in test context)

**Type Checking:**

- Tool: Ty (type checker)
- Coverage: Source only, tests excluded

## Import Organization

**Order:**

1. Standard library imports (e.g., `os`, `asyncio`, `platform`, `types`)
2. Third-party imports (e.g., `httpx`, `loguru`, `pydantic`)
3. Local application imports (e.g., `from vclient.config import ...`)
4. `TYPE_CHECKING` block for type hints only (at module level after other imports)

**Pattern from codebase:**

```python
import os
import platform
from types import TracebackType
from typing import TYPE_CHECKING, Self

import httpx
from loguru import logger

from vclient.config import _APIConfig
from vclient.constants import API_KEY_HEADER

if TYPE_CHECKING:
    from vclient.services import BooksService
```

**Path Aliases:**

- Use absolute imports from `vclient` root (e.g., `from vclient.services.clients import CompaniesService`)
- No relative imports (e.g., NOT `from .config import ...`)
- Import specific classes/functions, not modules when possible

**Barrel Exports:**

- `vclient/__init__.py` exports public API (VClient, all services)
- `vclient/models/__init__.py` exports all model classes
- `vclient/services/__init__.py` exports all service classes

## Error Handling

**Strategy:** RFC 9457 Problem Details format. All HTTP errors mapped to specific exception types.

**Patterns:**

1. **Request Validation (Client-side):**
    - Wrap Pydantic `ValidationError` in `RequestValidationError`
    - Example from `BaseService._validate_request()`:

    ```python
    try:
        return request_class(**kwargs)
    except PydanticValidationError as e:
        raise RequestValidationError(e) from e
    ```

2. **HTTP Response Error Handling:**
    - Status 401 → `AuthenticationError`
    - Status 403 → `AuthorizationError`
    - Status 404 → `NotFoundError`
    - Status 400 → `ValidationError` (with `invalid_parameters` field)
    - Status 409 → `ConflictError` (idempotency conflicts)
    - Status 429 → `RateLimitError` (with `retry_after` field)
    - Status 5xx → `ServerError`
    - All inherit from `APIError` base class

3. **Early Returns & Guard Clauses:**
    - Check preconditions at function start
    - Example from `VClient.__init__()`:

    ```python
    resolved_base_url = base_url or os.environ.get(ENV_BASE_URL)
    if resolved_base_url is None:
        msg = "base_url is required..."
        raise ValueError(msg)
    ```

4. **Exception Message Construction:**
    - Store message in variable before raising
    - Use `msg =` pattern consistently
    - Include context about what failed and why

5. **Error Properties:**
    - `APIError.status_code`: HTTP status from response or None
    - `APIError.response_data`: Full RFC 9457 response dict
    - `APIError.title`, `.detail`, `.instance`: Extracted from response_data
    - `ValidationError.invalid_parameters`: List of field-level errors
    - `RateLimitError.retry_after`: Seconds to wait
    - `RateLimitError.remaining`: Tokens remaining

## Logging

**Framework:** Loguru (structured logging with JSON export capability)

**Patterns:**

1. **When to Log:**
    - Client initialization (with config details)
    - Client shutdown
    - Before significant operations
    - After retries

2. **Structured Fields:**
    - Use `.bind()` to attach context
    - Example from `VClient.__init__()`:

    ```python
    logger.bind(
        base_url=self._config.base_url,
        timeout=self._config.timeout,
        max_retries=self._config.max_retries,
    ).info("Initialize VClient")
    ```

3. **Avoid String Formatting:**
    - Use structured fields, not f-strings in log messages
    - Log level: `.info()` for normal operations

## Comments

**When to Comment:**

- Complex algorithms or unusual behavior (e.g., exponential backoff calculation in `_calculate_backoff_delay()`)
- Explain the "why" behind non-obvious decisions
- Clarify intent when code cannot be made self-documenting

**When NOT to Comment:**

- Never describe what code does (assume reader can read Python)
- Never over-comment obvious logic
- Do not comment trivial assignments

**Example from codebase (good):**

```python
# Exponential backoff: base * 2^attempt
delay = base_delay * (2**attempt)

# Add jitter (up to 25% of the delay)
jitter = random.uniform(0, delay * 0.25)
```

**JSDoc/Docstrings:**

- Google-style docstrings for all public functions, classes, methods
- Format: Summary line, blank line, Args, Returns, Raises (if exceptions are raised)
- Use imperative voice: "Create a user" not "Creates a user"
- Type hints in signature, not in docstring

**Example:**

```python
def _resolve_company_id(self, company_id: str | None) -> str:
    """Resolve company_id, falling back to default if not provided.

    Args:
        company_id: Explicitly provided company ID, or None to use default.

    Returns:
        The resolved company ID.

    Raises:
        ValueError: If no company_id provided and no default configured.
    """
```

## Function Design

**Size:**

- Prefer functions under 50 lines
- Extract complex logic into helper functions
- Use private methods (`_`) for internal helpers

**Parameters:**

- Limit to 6 parameters (Pylint configured limit)
- Use keyword-only arguments after required positional args: `def func(pos_arg, *, kwarg1, kwarg2)`
- Always use `*` separator when mixing positional and optional args (see `client.py` methods)
- Use `| None` instead of `Optional[T]`

**Return Values:**

- Always explicitly annotate return type (Ty enforces this)
- Return early when conditions fail (guard clauses)
- Use union types for multiple return types: `str | None`, `str | list[str]`

**Async Pattern:**

- All HTTP operations are async
- Use `async def` and `await` throughout service classes
- Use `AsyncIterator[T]` for async generators
- Batch operations (e.g., `list_all()`) use pagination internally

## Module Design

**Exports:**

- Main entry: `vclient/__init__.py` exports `VClient`, factory functions, models, exceptions
- Services: Each service in separate file under `vclient/services/`
- Models: Each entity type gets model file under `vclient/models/`
- Constants: Shared in `vclient/constants.py` as Literal types and module constants

**Layering:**

- `BaseService`: All services inherit, provides `_request()`, retry logic, pagination
- `{Entity}Service`: Subclasses of BaseService, implement domain-specific methods
- `VClient`: Factory entry point, manages HTTP client lifecycle

**Barrel Files:**

- Use `__init__.py` to re-export public symbols
- Keep internal symbols private (prefix with `_`)

---

_Convention analysis: 2026-02-20_
