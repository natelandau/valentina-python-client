---
name: vclient-guide
description: >-
  Comprehensive guide for building applications with vclient, the async/sync Python client
  for the Valentina API. Use this skill whenever writing code that imports from vclient,
  integrating with the Valentina API, working with vclient models (Company, User, Campaign,
  Character, etc.), handling vclient exceptions, setting up tests with FakeVClient, or
  asking about any Valentina API endpoint, model shape, or service method. Also use when
  the user asks about character sheets, dice rolls, campaigns, books, chapters, traits,
  or any tabletop RPG game management features provided by the Valentina platform.
---

# vclient Developer Guide

vclient is an async-first Python client for the Valentina API with a generated sync variant. It provides typed Pydantic v2 models, automatic pagination, retry logic, and a fake client for testing.

## Quick Start

```python
# Async (primary)
from vclient import VClient

async with VClient(base_url="https://api.example.com", api_key="key") as client:
    companies = await client.companies.list_all()
    users_svc = client.users(on_behalf_of="user-123", company_id="comp-123")
    all_users = await users_svc.list_all()

# Sync
from vclient import SyncVClient

with SyncVClient(base_url="https://api.example.com", api_key="key") as client:
    companies = client.companies.list_all()
```

Environment variables can replace constructor arguments:
- `VALENTINA_CLIENT_BASE_URL` -> `base_url`
- `VALENTINA_CLIENT_API_KEY` -> `api_key`
- `VALENTINA_CLIENT_DEFAULT_COMPANY_ID` -> `default_company_id`

## Architecture

### Service Hierarchy

Services are scoped at initialization time. The scoping reflects the API's resource hierarchy:

```
VClient
├── .companies               # No scoping needed (property)
├── .developer               # No scoping (property)
├── .global_admin            # No scoping (property)
├── .system                  # No scoping (property)
├── .user_lookup             # No scoping (property)
├── .users(on_behalf_of, company_id=)
├── .identity(company_id=)                 # no on_behalf_of, API key auth only
├── .campaigns(on_behalf_of, company_id=)
├── .books(on_behalf_of, campaign_id, company_id=)
├── .chapters(on_behalf_of, campaign_id, book_id, company_id=)
├── .characters(on_behalf_of, company_id=)
├── .character_traits(on_behalf_of, character_id, company_id=)
├── .character_blueprint(company_id=)
├── .character_autogen(on_behalf_of, campaign_id, company_id=)
├── .dictionary(company_id=)
├── .dicerolls(on_behalf_of, company_id=)
└── .options(company_id=)
```

When `default_company_id` is set on the client (via constructor or env var), `company_id` can be omitted from all service factory calls.

### Factory Functions

For apps that register a default client, factory functions provide shorthand access:

```python
from vclient import VClient, campaigns_service

async with VClient(base_url="...", api_key="...", default_company_id="comp-1") as client:
    # These are equivalent:
    svc = client.campaigns(on_behalf_of="u1")
    svc = campaigns_service(on_behalf_of="u1")
```

Sync equivalents use the `sync_` prefix: `sync_campaigns_service(...)`, `sync_identity_service(...)`.

### Verified Identity Resolution

Use `IdentityService.identify()` to resolve a third-party provider login (Apple, Google, Discord, GitHub) to a canonical Valentina user. The service handles three cases automatically: matching an existing provider identity, auto-linking by provider-verified email, and creating a new UNAPPROVED user. To connect an additional provider to an existing authenticated user, use `UsersService.link_identity()`. For Apple and Google, the token's audience must appear in the union of the server allowlists and the per-developer audiences registered via `client.developer.update_me(provider_audiences={...})`; see `references/services.md` for full parameter and error-code details.

### Standard Service Methods

Most services provide these methods (where applicable):

| Method | Returns | Purpose |
|--------|---------|---------|
| `get_page(*, limit, offset, **filters)` | `PaginatedResponse[T]` | Single page |
| `list_all(**filters)` | `list[T]` | All items across pages |
| `iter_all(**filters)` | `AsyncIterator[T]` | Stream items lazily |
| `get(id, *, include=None)` | `T` | Single resource (some support `include` for embedding) |
| `create(request=None, **kwargs)` | `T` | Create resource |
| `update(id, request=None, **kwargs)` | `T` | Update resource |
| `delete(id)` | `None` | Delete resource |

Create/update methods accept either a Pydantic model instance or keyword arguments:
```python
# Both work:
await svc.create(CampaignCreate(name="My Campaign"))
await svc.create(name="My Campaign")
```

### Pagination

`PaginatedResponse[T]` wraps paginated results:
- `.items: list[T]` - current page
- `.total: int` - total count
- `.limit: int`, `.offset: int` - page parameters
- `.has_more: bool` - computed property
- `.next_offset: int` - computed next offset
- `.total_pages: int`, `.current_page: int` - computed helpers

Default `limit` is 10, max is 100. Exception: the reference/catalog services (`CharacterBlueprintService`, `DictionaryService`) accept `limit` up to 1000 so a full catalog fits in one request. Limits above the endpoint max are clamped down.

### Error Handling

All exceptions inherit from `APIError` and follow RFC 9457 Problem Details. Import from `vclient.exceptions`:

| Exception | HTTP | When |
|-----------|------|------|
| `AuthenticationError` | 401 | Invalid/missing API key |
| `AuthorizationError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `ValidationError` | 400 | Server validation failed (check `.invalid_parameters`) |
| `RequestValidationError` | - | Client-side Pydantic validation (pre-request) |
| `ConflictError` | 409 | Idempotency key conflict |
| `UnprocessableEntityError` | 422 | Well-formed request that cannot be processed (identity endpoints; check `.code`) |
| `RateLimitError` | 429 | Rate limited (check `.retry_after`, `.remaining`) |
| `ServerError` | 5xx | Server error |

#### Common properties (all exceptions)

| Property | Type | Purpose |
|----------|------|---------|
| `.status_code` | `int \| None` | HTTP status (None for client-side errors) |
| `.title` | `str \| None` | RFC 9457 short summary |
| `.detail` | `str \| None` | RFC 9457 human-readable explanation |
| `.instance` | `str \| None` | RFC 9457 URI reference to this occurrence |
| `.request_id` | `str \| None` | Server-generated ID — include this when reporting bugs |
| `.response_data` | `dict` | Raw RFC 9457 payload from the server |

`str(exc)` produces a formatted message with status, title, detail, instance, and request_id — safe to log directly.

#### Client-side vs server-side validation

`RequestValidationError` is raised **before** any HTTP call when a Pydantic model (request body or query params) fails validation locally. It wraps a `pydantic.ValidationError` and exposes `.errors` (list of Pydantic error dicts with `type`, `loc`, `msg`, `input`). Use this to fail fast on bad input without hitting the network.

`ValidationError` is raised for **server-side** validation failures (HTTP 400). It adds `.invalid_parameters`, a list of `{"field": ..., "message": ...}` dicts describing exactly which fields the server rejected — useful for surfacing per-field errors in a UI.

#### Rate limit handling

When `auto_retry_rate_limit=True` (the default), the client transparently waits and retries on 429 up to `max_retries` times. `RateLimitError` is only raised when retries are exhausted or auto-retry is disabled. Read `.retry_after` (seconds) and `.remaining` (tokens left in the bucket) to implement backoff when you handle 429s yourself.

#### Automatic retries

Transient errors in `retry_statuses` (default `{429, 500, 502, 503, 504}`) are retried up to `max_retries` times with exponential backoff starting at `retry_delay`. The exception you catch is the final failure after retries are exhausted, not the first transient error.

#### Typical patterns

```python
from vclient.exceptions import (
    APIError,
    NotFoundError,
    RateLimitError,
    RequestValidationError,
    ValidationError,
)

# Narrow handling — recover from specific failure modes
try:
    user = await users_svc.get("nonexistent")
except NotFoundError:
    user = None  # treat as absent
except RateLimitError as e:
    await asyncio.sleep(e.retry_after or 1)

# Surface field-level errors to the caller
try:
    await campaigns_svc.create(name="")
except ValidationError as e:
    for p in e.invalid_parameters:
        print(f"{p['field']}: {p['message']}")
except RequestValidationError as e:
    for err in e.errors:
        print(f"{'.'.join(map(str, err['loc']))}: {err['msg']}")

# Catch-all for logging / error reporting — always capture request_id
try:
    await svc.do_something()
except APIError as e:
    logger.exception("API call failed", extra={"request_id": e.request_id})
    raise
```

See `references/error-handling.md` for deeper patterns (correlation IDs, retry-aware wrappers, mapping to HTTP responses in web frameworks).

### Client Configuration

```python
VClient(
    base_url="...",
    api_key="...",
    timeout=30.0,              # Request timeout (seconds)
    max_retries=3,             # Retry attempts for transient errors
    retry_delay=1.0,           # Base delay between retries
    auto_retry_rate_limit=True,  # Auto-retry on 429
    auto_idempotency_keys=False, # Auto-generate idempotency keys for POST/PUT/PATCH
    retry_statuses={429, 500, 502, 503, 504},
    default_company_id="...",
    headers={"X-Custom": "value"},
)
```

## Testing with FakeVClient

`FakeVClient` is a drop-in replacement that uses mock HTTP transport with factory-generated responses:

```python
from vclient.testing import FakeVClient, Routes

async with FakeVClient() as client:
    # All service methods work out of the box with generated fake data
    users = await client.users(on_behalf_of="user-123", company_id="fake-company").list_all()

    # Override specific routes
    client.set_response(Routes.USERS_LIST, items=[
        {"id": "u1", "username": "alice", "email": "a@b.com", "role": "PLAYER", ...}
    ])

    # Simulate errors
    client.set_error(Routes.USERS_GET, status_code=404, detail="Not found")

    # Parameterized overrides (match specific path values)
    client.set_response(Routes.CAMPAIGNS_GET, model=my_campaign, params={"campaign_id": "abc"})
```

`SyncFakeVClient` is the sync equivalent. Install with `pip install vclient[testing]`.

## Reference Files

For detailed information, read the appropriate reference file:

- **`references/services.md`** — Complete method signatures for every service, including all parameters, return types, and filter options. Read this when you need to know exactly what methods a service offers or what parameters they accept.

- **`references/models.md`** — Every Pydantic model with all fields, types, and validation constraints. Read this when you need to know the shape of request/response objects.

- **`references/constants.md`** — All Literal types (enums), configuration constants, and endpoint paths. Read this when you need valid values for fields like `character_class`, `game_version`, `user_role`, etc.

- **`references/error-handling.md`** — Full exception hierarchy, property details, client vs server validation differences, retry behavior, and recipes for logging, web framework integration, and testing error paths. Read this when designing error handling strategy or debugging a specific exception.
