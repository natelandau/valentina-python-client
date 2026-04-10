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
    users_svc = client.users(company_id="comp-123")
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
├── .users(company_id)
├── .campaigns(user_id, company_id)
├── .books(user_id, campaign_id, company_id=)
├── .chapters(user_id, campaign_id, book_id, company_id=)
├── .characters(user_id, campaign_id, company_id=)
├── .character_traits(user_id, campaign_id, character_id, company_id=)
├── .character_blueprint(company_id=)
├── .character_autogen(user_id, campaign_id, company_id=)
├── .dictionary(company_id=)
├── .dicerolls(user_id, company_id=)
└── .options(company_id=)
```

When `default_company_id` is set on the client (via constructor or env var), `company_id` can be omitted from all service factory calls.

### Factory Functions

For apps that register a default client, factory functions provide shorthand access:

```python
from vclient import VClient, campaigns_service

async with VClient(base_url="...", api_key="...", default_company_id="comp-1") as client:
    # These are equivalent:
    svc = client.campaigns(user_id="u1")
    svc = campaigns_service(user_id="u1")
```

Sync equivalents use the `sync_` prefix: `sync_campaigns_service(...)`.

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

### Error Handling

All exceptions inherit from `APIError` and follow RFC 9457 Problem Details:

| Exception | HTTP | When |
|-----------|------|------|
| `AuthenticationError` | 401 | Invalid/missing API key |
| `AuthorizationError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `ValidationError` | 400 | Server validation failed (check `.invalid_parameters`) |
| `RequestValidationError` | - | Client-side Pydantic validation (pre-request) |
| `ConflictError` | 409 | Idempotency key conflict |
| `RateLimitError` | 429 | Rate limited (check `.retry_after`, `.remaining`) |
| `ServerError` | 5xx | Server error |

All have `.status_code`, `.title`, `.detail`, `.instance`, `.request_id` properties.

```python
from vclient.exceptions import NotFoundError, RateLimitError

try:
    user = await users_svc.get("nonexistent")
except NotFoundError as e:
    print(f"{e.title}: {e.detail}")
except RateLimitError as e:
    print(f"Retry after {e.retry_after}s")
```

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
    users = await client.users(company_id="fake-company").list_all()

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
