---
icon: lucide/search
---

# User Lookup Service

Look up users across companies for login and registration flows. Discover which of your companies a person has a user record in by searching via email, Discord ID, Google ID, GitHub ID, or Apple ID.

Unlike other user operations, this service is not scoped to a single company — it searches across all companies where you have permission.

## Usage

```python
from vclient import user_lookup_service

lookup = user_lookup_service()
```

Or via the client directly:

```python
from vclient import VClient

async with VClient() as client:
    results = await client.user_lookup.by_email("alice@example.com")
```

## Methods

| Method                    | Returns                   | Description                   |
| ------------------------- | ------------------------- | ----------------------------- |
| `by_email(email)`         | `list[UserLookupResult]`  | Look up by email address      |
| `by_discord_id(discord_id)` | `list[UserLookupResult]` | Look up by Discord profile ID |
| `by_google_id(google_id)` | `list[UserLookupResult]`  | Look up by Google profile ID  |
| `by_github_id(github_id)` | `list[UserLookupResult]`  | Look up by GitHub profile ID  |
| `by_apple_id(apple_id)`   | `list[UserLookupResult]`  | Look up by Apple profile ID   |

All methods return an empty list when no matches are found.

## Example

```python
from vclient import user_lookup_service

lookup = user_lookup_service()

# Find which companies a user belongs to
results = await lookup.by_email("alice@example.com")

for result in results:
    print(f"{result.company_name} — {result.role}")

# Handle no results
results = await lookup.by_discord_id("123456789")
if not results:
    print("User not found in any company")
```

See [Response Models](../models/user_lookup.md) for `UserLookupResult` field details.
