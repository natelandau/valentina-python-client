# Architecture

**Analysis Date:** 2026-02-20

## Pattern Overview

**Overall:** Async REST API client using service-oriented architecture with factory pattern for dependency injection.

**Key Characteristics:**
- Hierarchical scoping: Services created with increasing context requirements (company → user → campaign → character)
- Single HTTP client (`httpx.AsyncClient`) shared across all services via the main `VClient` instance
- Lazy service instantiation: Services only created when first accessed (properties/methods)
- Automatic retry logic with exponential backoff and jitter for transient failures
- RFC 9457 Problem Details format for all API errors
- Structured logging via `loguru` with contextual fields

## Layers

**Client Layer (VClient):**
- Purpose: Single entry point for API interaction, manages HTTP session and configuration
- Location: `src/vclient/client.py`
- Contains: HTTP client initialization, service factory methods, environment variable resolution
- Depends on: `_APIConfig`, `httpx`, all service classes
- Used by: Application code directly or via registry factory functions

**Service Layer (BaseService subclasses):**
- Purpose: Domain-specific operations (Companies, Users, Campaigns, Characters, etc.)
- Location: `src/vclient/services/`
- Contains: Methods for CRUD operations (`get_page`, `list_all`, `iter_all`, `get`, `create`, `update`, `delete`), pagination logic, request/response handling
- Depends on: `BaseService` for HTTP methods, models for request/response validation, `Endpoints` for URL paths
- Used by: Application code via client methods or factory functions

**Base Service Layer:**
- Purpose: Common HTTP request handling, retry logic, error handling, response parsing
- Location: `src/vclient/services/base.py`
- Contains: `_request()` with exponential backoff retry, response status checking, idempotency key generation, pagination helpers
- Depends on: `httpx`, exception classes, Pydantic models
- Used by: All concrete service implementations

**Model Layer (Pydantic v2):**
- Purpose: Request/response data validation and serialization
- Location: `src/vclient/models/`
- Contains: Response models (`{Entity}`), request models (`{Entity}Create`, `{Entity}Update`), shared DTOs
- Depends on: Pydantic v2 for validation
- Used by: Service layer for request validation and response parsing

**Configuration Layer:**
- Purpose: Internal client configuration and environment variable handling
- Location: `src/vclient/config.py`
- Contains: `_APIConfig` dataclass with all client settings (base URL, API key, timeouts, retry settings, headers)
- Depends on: Constants module
- Used by: VClient and BaseService for accessing configuration

**Registry Layer:**
- Purpose: Global default client management and factory functions for stateless service access
- Location: `src/vclient/registry.py`
- Contains: Default client registration, factory functions (`companies_service()`, `users_service()`, etc.)
- Depends on: VClient and all service classes
- Used by: Application code for convenient access without explicit client passing

**Exception Layer:**
- Purpose: Consistent error representation following RFC 9457 Problem Details
- Location: `src/vclient/exceptions.py`
- Contains: Exception hierarchy (`APIError` → `AuthenticationError`, `NotFoundError`, `RateLimitError`, `ValidationError`, `ServerError`, etc.)
- Depends on: Pydantic for `RequestValidationError`
- Used by: BaseService._raise_for_status() for error conversion

## Data Flow

**Request Flow:**

1. Application calls service method (e.g., `client.companies.list_all()`)
2. Service method validates request data using Pydantic model if needed (`_validate_request()`)
3. Service calls `BaseService._request()` with HTTP method, path, and optional JSON/params
4. BaseService adds idempotency key if configured and method is non-idempotent
5. httpx sends request with retry loop:
   - On success: parses JSON, checks status, returns response
   - On network error: retries with exponential backoff
   - On 429/5xx: retries based on configuration and method idempotency
   - On 4xx/5xx that shouldn't retry: raises appropriate `APIError` subclass
6. Service parses response using Pydantic model (`Model.model_validate()`)
7. Service returns typed object to application

**Pagination Flow:**

1. Application calls `service.list_all()` or `service.iter_all()`
2. Service calls `_iter_all_pages(endpoint, limit=100)` from BaseService
3. BaseService calls `_request()` with `limit` and `offset=0`
4. Response parsed as `PaginatedResponse[T]`, yields individual items
5. If response indicates more pages (`offset + limit < total`), fetches next page
6. Continues until all pages exhausted or application breaks iteration

**Error Handling Flow:**

1. HTTP response received by BaseService._raise_for_status()
2. Status code determines exception type:
   - 401 → `AuthenticationError`
   - 403 → `AuthorizationError`
   - 404 → `NotFoundError`
   - 400 → `ValidationError`
   - 409 → `ConflictError`
   - 429 → `RateLimitError` (with retry_after and remaining tokens parsed from headers)
   - 5xx → `ServerError`
   - Other → `APIError`
3. All exceptions include RFC 9457 fields from response: `title`, `detail`, `instance`
4. Retry logic in BaseService._request() catches `RateLimitError` and `ServerError`, retries if conditions met
5. After max retries exhausted, exception propagates to application

**State Management:**

- No persistent state: Services are stateless except for reference to VClient
- HTTP session state: Managed by single shared `httpx.AsyncClient` instance
- Configuration state: Stored in `_APIConfig` dataclass on VClient instance
- Default client state: Global module-level `_default_client` variable in registry module

## Key Abstractions

**BaseService:**
- Purpose: Encapsulate all HTTP operations, retry logic, and response parsing
- Examples: `CompaniesService`, `UsersService`, `CharactersService` all extend this
- Pattern: Template method - subclasses call `_request()`, `_get()`, `_post()`, `_patch()`, `_delete()`, `_iter_all_pages()` helper methods

**Endpoints:**
- Purpose: Centralize all API path strings to avoid magic strings and enable refactoring
- Examples: `Endpoints.COMPANIES`, `Endpoints.COMPANY.format(company_id=company_id)`
- Pattern: Simple constant class with path concatenation

**Models as Request/Response DTOs:**
- Purpose: Single source of truth for data shape and validation
- Examples: `Company` (response), `CompanyCreate` (request), `CompanyUpdate` (request)
- Pattern: Pydantic BaseModel with Field validation, snake_case Python field names map to camelCase API fields via `Field(alias="...")`

**PaginatedResponse[T]:**
- Purpose: Generic container for paginated API responses with metadata
- Contains: `items: list[T]`, `offset: int`, `limit: int`, `total: int`
- Pattern: Generic TypeVar-based model for type safety across different list endpoints

**Factory Functions:**
- Purpose: Convenient global access to services without managing client reference
- Examples: `companies_service()`, `users_service(company_id)`, `campaigns_service(user_id, company_id)`
- Pattern: Functions that call `default_client()` and invoke appropriate client method

## Entry Points

**VClient Constructor:**
- Location: `src/vclient/client.py` lines 72-163
- Triggers: Called by application to initialize API client
- Responsibilities: Resolve configuration from args and environment variables, create HTTP client, register as default client, lazy-load service instances

**Service Methods (e.g., client.companies):**
- Location: `src/vclient/client.py` lines 237-559
- Triggers: Called by application to access domain-specific operations
- Responsibilities: Return service instance (property returns cached instance), apply scoping context (company_id, user_id, campaign_id)

**Async Context Manager (async with VClient(...)):**
- Location: `src/vclient/client.py` lines 187-206
- Triggers: Used in `async with` statements
- Responsibilities: Setup (`__aenter__`), cleanup (`__aexit__`), close HTTP session

**Service Methods (e.g., companies.list_all()):**
- Location: Examples in `src/vclient/services/companies.py` lines 55-64
- Triggers: Called by application to perform API operations
- Responsibilities: Validate request data, call BaseService methods, parse response, return typed object

## Error Handling

**Strategy:** Fail fast with clear, typed exceptions. All API errors inherit from `APIError` and expose RFC 9457 Problem Details.

**Patterns:**

- **Automatic Retry:** BaseService._request() retries on:
  - Rate limit (429) with Retry-After header support
  - 5xx errors if idempotent or has Idempotency-Key header
  - Network errors (ConnectError, TimeoutException)
  - Exponential backoff: `base_delay * (2 ** attempt) + jitter(0-25%)`

- **Request Validation:** Pydantic errors from model instantiation converted to `RequestValidationError` by `_validate_request()`

- **Response Status Checking:** All non-2xx responses checked in `_raise_for_status()`, specific exception raised based on status code

- **Logging:** Each request logged with structured fields (method, url, status, elapsed_ms, attempt, delay)

## Cross-Cutting Concerns

**Logging:**
- Framework: `loguru` with structured fields via `.bind(key=value)`
- Patterns: Initialized in `__init__.py` to propagate to stdlib logging for test caplog compatibility
- Example: `logger.bind(method=method, url=path, status=status).debug("Receive response")`
- Disabled by default: `logger.disable("vclient")` unless explicitly enabled

**Validation:**
- Client-side: Pydantic v2 models validate before sending requests (raised as `RequestValidationError`)
- Server-side: API returns 400 with validation details (raised as `ValidationError`)
- Pattern: Service methods accept either full model or `**kwargs` passed to `_validate_request()`

**Authentication:**
- HTTP header-based: API key passed as `X-API-KEY` header on every request
- Environment fallback: `VALENTINA_CLIENT_API_KEY` env var used if not provided to constructor
- Lazy resolution: Resolved at client creation time, error if missing

**Configuration:**
- Environment variables: `VALENTINA_CLIENT_BASE_URL`, `VALENTINA_CLIENT_API_KEY`, `VALENTINA_CLIENT_DEFAULT_COMPANY_ID`
- Constructor args take precedence over environment variables
- Retry/timeout settings: Configurable via VClient constructor
- Automatic defaults: Provided in `constants.py`

---

*Architecture analysis: 2026-02-20*
