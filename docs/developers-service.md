# Developers Service

Manage your own developer profile, including viewing account details, updating your profile, and regenerating your API key.

## Usage

```python
from vclient import developer_service

developer = developer_service()
```

## Methods

| Method                                   | Returns                 | Description                |
| ---------------------------------------- | ----------------------- | -------------------------- |
| `get_me()`                               | `MeDeveloper`           | Get your developer profile |
| `update_me(MeDeveloperUpdate, **kwargs)` | `MeDeveloper`           | Update your profile        |
| `regenerate_api_key()`                   | `MeDeveloperWithApiKey` | Generate a new API key     |

## Example

```python
from vclient.models import MeDeveloperUpdate

# Get your profile
me = await developer.get_me()
print(f"Username: {me.username}")
print(f"Companies: {len(me.companies)}")

# Update profile (preferred: use model object)
update = MeDeveloperUpdate(username="new_username")
updated = await developer.update_me(update)

# Alternative: pass fields as kwargs
updated = await developer.update_me(username="new_username")

# Regenerate API key (save immediately - only shown once)
result = await developer.regenerate_api_key()
print(f"New API Key: {result.api_key}")
```

> **Warning:** Regenerating your API key immediately invalidates the current key. Save the new key from the response - it won't be displayed again.

See [Response Models](models.md) for `MeDeveloper` and related types.
