---
icon: lucide/user-plus
---

# UserSelfRegistrationService

Register new users via SSO onboarding. This service is intended for SSO flows where a user is being registered on their own behalf — it authenticates with API key only and does not require an `on_behalf_of` user ID.

## Usage

```python
from vclient import user_self_registration_service

svc = user_self_registration_service(company_id="COMPANY_ID")
```

## Methods

| Method                       | Returns | Description                        |
| ---------------------------- | ------- | ---------------------------------- |
| `register(request=None, **kwargs)` | `User`  | Register a new user via SSO |

### `register()` Parameters

| Parameter        | Type           | Required | Description                          |
| ---------------- | -------------- | -------- | ------------------------------------ |
| `username`       | `str`          | Yes      | Unique username for the new account  |
| `email`          | `str`          | Yes      | Email address for the new account    |
| `name_first`     | `str \| None`  | No       | First name                           |
| `name_last`      | `str \| None`  | No       | Last name                            |
| `discord_profile`| `str \| None`  | No       | Discord profile identifier           |
| `google_profile` | `str \| None`  | No       | Google profile identifier            |
| `github_profile` | `str \| None`  | No       | GitHub profile identifier            |

## Examples

### Register a User via SSO (keyword arguments)

```python
from vclient import VClient

async with VClient(base_url="https://api.valentina-noir.com", api_key="...") as client:
    svc = client.user_self_registration(company_id="COMPANY_ID")

    user = await svc.register(
        username="jane_doe",
        email="jane@example.com",
        name_first="Jane",
        name_last="Doe",
    )
    print(f"Registered: {user.username}")
```

### Register a User via SSO (model object)

```python
from vclient import VClient
from vclient.models import UserRegisterDTO

async with VClient(base_url="https://api.valentina-noir.com", api_key="...") as client:
    svc = client.user_self_registration(company_id="COMPANY_ID")

    request = UserRegisterDTO(
        username="jane_doe",
        email="jane@example.com",
        name_first="Jane",
        name_last="Doe",
    )
    user = await svc.register(request=request)
    print(f"Registered: {user.username}")
```

### Sync client

```python
from vclient import SyncVClient, sync_user_self_registration_service

with SyncVClient(base_url="https://api.valentina-noir.com", api_key="...") as client:
    svc = client.user_self_registration(company_id="COMPANY_ID")
    user = svc.register(username="jane_doe", email="jane@example.com")
```

### With social profile links

```python
user = await svc.register(
    username="jane_doe",
    email="jane@example.com",
    name_first="Jane",
    name_last="Doe",
    discord_profile="jane_doe#1234",
    github_profile="janedoe",
)
```

## Related Documentation

- [Response Models](../models/users.md) - View `User` and `UserRegisterDTO` model schemas
- [UsersService](users.md) - Full user management (requires `on_behalf_of`)
