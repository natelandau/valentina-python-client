# Testing Patterns

**Analysis Date:** 2026-02-20

## Test Framework

**Runner:**
- Framework: Pytest 9.0.2+
- Config: `pyproject.toml` `[tool.pytest.ini_options]`
- Async support: `pytest-anyio` (all tests marked with `@pytest.mark.anyio`)

**Assertion Library:**
- Built-in Pytest assertions (no external library needed)
- `pytest.raises()` for exception testing
- Type-safe comparison operators

**Run Commands:**
```bash
uv run duty test              # Run all tests with coverage
uv run pytest tests/ -x       # Run tests, stop on first failure
uv run pytest tests/ -k pattern -x  # Run specific tests by pattern
```

**Pytest Configuration:**
- Default: `-n auto` (parallel execution via `pytest-xdist`)
- Strict markers: Only registered markers allowed (`@pytest.mark.serial` for sequential)
- Filter warnings: Treat warnings as errors except Pydantic deprecation warnings
- Doctest modules enabled (tests can be in docstrings)
- Cache directory: `.cache/pytest`

## Test File Organization

**Location:**
- Unit tests: `tests/unit/` (no HTTP, model validation only)
- Integration tests: `tests/integration/` (HTTP mocking with respx)
- Shared fixtures: `tests/shared_response_fixtures.py`

**Naming:**
- Test files: `test_{feature}.py` (e.g., `test_client.py`, `test_exceptions.py`)
- Test classes: `Test{Feature}` (e.g., `TestVClientInit`, `TestAPIError`)
- Test functions: `test_{scenario}` (e.g., `test_init_with_base_url_and_api_key`)
- Fixtures: Function-scoped unless async (then session/function with `async def`)

**Structure:**
```
tests/
├── conftest.py                          # Global fixtures (api_key, base_url)
├── shared_response_fixtures.py          # Shared fixture data (character_response_data, user_response_data)
├── unit/
│   ├── conftest.py                      # Unit test fixtures (empty in this codebase)
│   ├── models/
│   │   ├── test_companies.py
│   │   ├── test_characters.py
│   │   └── ...
│   ├── test_client.py
│   ├── test_exceptions.py
│   └── test_registry.py
└── integration/
    ├── conftest.py                      # Integration fixtures (mock_api, vclient, base_service)
    ├── services/
    │   ├── test_developers.py
    │   ├── test_companies.py
    │   └── ...
    ├── test_client.py
    └── test_logging.py
```

## Test Structure

**Suite Organization:**
```python
class TestAPIError:
    """Tests for APIError base class."""

    def test_init_with_message_only(self):
        """Verify creating an error with just a message."""
        # Given
        # When
        # Then
```

**Patterns:**

1. **Given-When-Then Comments:**
   - All tests follow this structure for clarity
   - Comment each logical section
   - Makes intent and assertion targets obvious

2. **Fixture-Based Setup:**
   - Avoid setup/teardown methods
   - Use fixtures instead: `def test_something(fixture_name):`
   - Fixtures are auto-injected by pytest

3. **Single Assertion Focus:**
   - Each test verifies one specific behavior
   - Multiple assertions OK if testing facets of same behavior
   - One logical failure per test

## Mocking

**Framework:** `respx` for HTTP mocking (not `responses` or `unittest.mock`)

**Patterns:**

1. **Basic Mock Setup:**
```python
@respx.mock
async def test_get_me_returns_developer(self, vclient, base_url, me_developer_response_data):
    """Verify get_me returns MeDeveloper object."""
    # Given: A mocked developer me endpoint
    route = respx.get(f"{base_url}{Endpoints.DEVELOPER_ME}").respond(
        200, json=me_developer_response_data
    )

    # When: Getting current developer
    result = await vclient.developer.get_me()

    # Then: Returns MeDeveloper object with correct data
    assert route.called
    assert isinstance(result, MeDeveloper)
```

2. **Respx Router (for multiple endpoints):**
```python
@pytest.fixture
def mock_api(base_url) -> respx.Router:
    """Return a respx mock router for the API."""
    with respx.mock(base_url=base_url, assert_all_called=False) as respx_mock:
        yield respx_mock
```

3. **Verifying Request Contents:**
```python
# Given
route = respx.patch(f"{base_url}{Endpoints.DEVELOPER_ME}").respond(200, json=updated_data)

# When
result = await vclient.developer.update_me(username="newusername")

# Then: Verify request body
request = route.calls.last.request
body = json.loads(request.content)
assert body == {"username": "newusername"}
```

4. **Error Responses:**
```python
# Mock a 401 Unauthorized
respx.get(f"{base_url}{Endpoints.DEVELOPER_ME}").respond(
    401, json={"detail": "Invalid API key"}
)

# Then expect specific exception
with pytest.raises(AuthenticationError):
    await vclient.developer.get_me()
```

**What to Mock:**
- HTTP requests (via respx)
- External service calls
- Time-based behavior (via `pytest-freezegun` if needed)

**What NOT to Mock:**
- Internal service methods
- Pydantic models (validate actual data structures)
- Business logic

## Fixtures and Factories

**Test Data:**
```python
@pytest.fixture
def character_response_data() -> dict:
    """Return sample character response data."""
    return {
        "id": "char123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "name_first": "John",
        "name_last": "Doe",
        # ... full object
    }
```

**Location:**
- Shared fixtures: `tests/shared_response_fixtures.py` (e.g., `character_response_data`, `user_response_data`)
- Global fixtures: `tests/conftest.py` (e.g., `api_key`, `base_url`)
- Feature-specific fixtures: `tests/{category}/conftest.py` (e.g., integration conftest has `mock_api`, `vclient`)

**Fixture Scope:**
- Function scope (default): Fresh instance per test
- Session scope: Shared across entire test run (use sparingly)
- Async fixtures: Use `async def` with `yield` for async setup/teardown

**Example Async Fixture:**
```python
@pytest.fixture
async def vclient(base_url, api_key) -> VClient:
    """Return a VClient for testing."""
    client = VClient(base_url=base_url, api_key=api_key, timeout=10.0)
    yield client
    await client.close()  # Cleanup
```

## Coverage

**Requirements:** No minimum enforced (`fail_under = 0` in config)

**View Coverage:**
```bash
uv run duty test              # Generates coverage report during test run
# Coverage data: .cache/coverage
# Coverage XML: .cache/coverage.xml
```

**Configuration (`pyproject.toml`):**
- Branch coverage: Enabled
- Source: `src/` only
- Omit: All tests (`tests/*`)
- Exclude lines: `__repr__`, exception handlers, `if TYPE_CHECKING`, pragma comments

## Test Types

**Unit Tests** (`tests/unit/`)
- Scope: Pydantic model validation, parsing, field constraints
- No HTTP mocking needed (purely data structure validation)
- No external dependencies
- Fast: Runs in milliseconds
- Example: `tests/unit/models/test_companies.py` validates model initialization and field rules

**Integration Tests** (`tests/integration/`)
- Scope: Full service methods with respx HTTP mocking
- Test request/response flow end-to-end
- Include error scenarios and edge cases
- Example: `tests/integration/services/test_developers.py` tests actual DeveloperService methods

**E2E Tests:**
- Not used in codebase (HTTP mocking is sufficient)
- Could be added with real API credentials if needed

## Common Patterns

**Async Testing:**
```python
# All tests marked with @pytest.mark.anyio
pytestmark = pytest.mark.anyio

class TestVClientInit:
    """Tests for VClient initialization."""

    def test_init_with_base_url_and_api_key(self):  # Note: sync test
        """Verify client initialization with custom base_url and api_key."""
        # When: Creating a client with custom values
        client = VClient(base_url="https://custom.api.com", api_key="my-key")

        # Then: Custom values are stored
        assert client._config.base_url == "https://custom.api.com"
```

**Async Service Methods:**
```python
@respx.mock
async def test_get_me_returns_developer(self, vclient, base_url, me_developer_response_data):
    """Verify get_me returns MeDeveloper object."""
    # Given
    route = respx.get(f"{base_url}{Endpoints.DEVELOPER_ME}").respond(
        200, json=me_developer_response_data
    )

    # When: Async service call
    result = await vclient.developer.get_me()

    # Then
    assert isinstance(result, MeDeveloper)
```

**Error Testing:**
```python
class TestValidationError:
    """Tests for ValidationError class."""

    def test_invalid_parameters_property(self):
        """Verify invalid_parameters extracts validation errors from response_data."""
        # Given
        error = ValidationError(
            message="Validation failed",
            status_code=400,
            response_data={
                "invalid_parameters": [
                    {"field": "name", "message": "Field required"},
                ]
            },
        )

        # Then
        assert len(error.invalid_parameters) == 1
        assert error.invalid_parameters[0]["field"] == "name"
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize(
    ("error_class", "expected_parent"),
    [
        (AuthenticationError, APIError),
        (AuthorizationError, APIError),
        (NotFoundError, APIError),
    ],
)
def test_inheritance(self, error_class, expected_parent):
    """Verify all error classes inherit from APIError."""
    assert issubclass(error_class, expected_parent)
```

**Exception Testing:**
```python
def test_is_exception(self):
    """Verify APIError is a proper exception."""
    # Given
    msg = "Test error"

    # When/Then: Error can be raised and caught
    with pytest.raises(APIError) as exc_info:
        raise APIError(msg, status_code=500)

    assert exc_info.value.status_code == 500
```

## Test Data & Fixtures

**Shared Test Data:**
Location: `tests/shared_response_fixtures.py`

Contains reusable response objects:
- `character_response_data`: Full character entity response
- `user_response_data`: Full user entity response
- More added as needed

**Usage Pattern:**
```python
@pytest.fixture
def character_response_data() -> dict:
    """Return sample character response data."""
    return { ... }  # Complete, valid API response

# In tests:
def test_something(self, character_response_data):
    route = respx.get(...).respond(200, json=character_response_data)
```

**When to Create New Fixtures:**
- Response data that will be used in multiple tests
- Complex or deeply nested objects
- Data that represents API contract (not test-specific values)

## Pytest Plugins & Extensions

**Installed:**
- `pytest-anyio`: Async test support
- `pytest-cov`: Coverage reporting
- `pytest-xdist`: Parallel execution (`-n auto`)
- `pytest-mock`: Mock fixture (integrated, use `mocker` parameter)
- `pytest-repeat`: Test repetition (`--repeat=N`)
- `pytest-clarity`: Better assertion output
- `pytest-sugar`: Pretty output with progress bar
- `pytest-devtools`: Enhanced debugging

---

*Testing analysis: 2026-02-20*
