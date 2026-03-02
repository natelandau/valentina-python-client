---
icon: lucide/repeat
---

# Sync Client

The package includes a synchronous client, `SyncVClient`, for use in applications that don't use `async`/`await`. It provides the same API surface as the async `VClient` — identical configuration options, service methods, and models — without requiring an event loop.

## When to Use Sync vs Async

Use **`SyncVClient`** when your application is synchronous:

- Flask or Django views
- CLI tools and scripts
- Data pipelines
- Jupyter notebooks
- Any code that doesn't use `async`/`await`

Use **`VClient`** (async) when your application already uses an event loop:

- FastAPI / Starlette endpoints
- `asyncio`-based services
- Applications using `async with` / `await` patterns

## Creating the Client

`SyncVClient` accepts the same constructor options as `VClient`. See [Configuration](configuration.md) for the full options reference.

```python
from vclient import SyncVClient

client = SyncVClient(
    base_url="https://api.valentina-noir.com",
    api_key="YOUR_API_KEY",
)
```

Environment variables work identically — see [Environment Variables](configuration.md#environment-variables).

```python
client = SyncVClient()  # reads from VALENTINA_CLIENT_BASE_URL / VALENTINA_CLIENT_API_KEY
```

## Context Manager

Use `with` instead of `async with` to ensure the HTTP client is closed when you're done:

```python
from vclient import SyncVClient

with SyncVClient() as client:
    companies = client.companies
    all_companies = companies.list_all()
    # HTTP client is automatically closed when exiting the context
```

## Factory Functions

Every async factory function has a sync counterpart prefixed with `sync_`:

| Async                            | Sync                                  |
| -------------------------------- | ------------------------------------- |
| `companies_service()`            | `sync_companies_service()`            |
| `users_service()`                | `sync_users_service()`                |
| `campaigns_service()`            | `sync_campaigns_service()`            |
| `characters_service()`           | `sync_characters_service()`           |
| `character_traits_service()`     | `sync_character_traits_service()`     |
| `books_service()`                | `sync_books_service()`                |
| `chapters_service()`             | `sync_chapters_service()`             |
| `dicerolls_service()`            | `sync_dicerolls_service()`            |
| `dictionary_service()`           | `sync_dictionary_service()`           |
| `character_blueprint_service()`  | `sync_character_blueprint_service()`  |
| `options_service()`              | `sync_options_service()`              |

Factory functions work the same way — create a `SyncVClient` first, then call the factory from any module:

```python
from vclient import SyncVClient, sync_companies_service

client = SyncVClient()

companies = sync_companies_service()
all_companies = companies.list_all()
```

## Key Differences from Async

The sync client is auto-generated from the async source, so the API is nearly identical. The only differences are syntactic:

| Async                              | Sync                          |
| ---------------------------------- | ----------------------------- |
| `async with VClient() as client:`  | `with SyncVClient() as client:` |
| `await companies.list_all()`       | `companies.list_all()`        |
| `await companies.get("id")`        | `companies.get("id")`         |
| `async for c in companies.iter_all():` | `for c in companies.iter_all():` |
| Returns `AsyncIterator[T]`         | Returns `Iterator[T]`         |

Models, exceptions, and configuration are shared between both clients.

## Complete Example

```python
from vclient import SyncVClient, sync_companies_service, sync_campaigns_service

with SyncVClient(
    base_url="https://api.valentina-noir.com",
    api_key="YOUR_API_KEY",
    default_company_id="COMPANY_ID",
) as client:
    # List companies via factory function
    companies = sync_companies_service()
    for company in companies.list_all():
        print(f"Company: {company.name} ({company.id})")

    # Get campaigns for a user
    campaigns = sync_campaigns_service(user_id="USER_ID")
    for campaign in campaigns.list_all():
        print(f"Campaign: {campaign.name}")

    # Paginate through results
    page = companies.get_page(limit=10, offset=0)
    print(f"Page {page.current_page} of {page.total_pages}")

    # Stream all items with iter_all()
    for company in companies.iter_all():
        print(company.name)
```
