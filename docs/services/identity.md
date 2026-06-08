---
icon: lucide/fingerprint
---

# IdentityService

Resolve verified provider logins to canonical users. Your app forwards the credential it obtained from the provider's own login flow; the API verifies it with the provider and returns the matching user, creating a new `UNAPPROVED` user if nobody matches. This service authenticates with API key only and does not require an `on_behalf_of` user ID.

There are two trust models for identifying users:

- **Assertion (`On-Behalf-Of` header):** your app authenticates users itself and asserts identity via the `On-Behalf-Of` header. Appropriate for trusted clients such as bots.
- **Verified (this service):** your app forwards the provider credential to the API, which verifies it with the provider. Use the returned `user.id` in `On-Behalf-Of` for subsequent requests.

## Usage

```python
from vclient import identity_service

svc = identity_service(company_id="COMPANY_ID")
```

## Methods

| Method                             | Returns              | Description                                 |
| ---------------------------------- | -------------------- | ------------------------------------------- |
| `identify(request=None, **kwargs)` | `IdentityResolution` | Resolve a verified provider login to a user |

### `identify()` Parameters

| Parameter  | Type               | Required | Description                                                         |
| ---------- | ------------------ | -------- | ------------------------------------------------------------------- |
| `provider` | `IdentityProvider` | Yes      | One of `"apple"`, `"google"`, `"discord"`, `"github"`               |
| `token`    | `str`              | Yes      | OIDC ID token (apple/google) or OAuth access token (discord/github) |
| `username` | `str \| None`      | No       | Username to use only if a new user is created                       |
| `email`    | `str \| None`      | No       | Email to use on create, only if the provider supplied none          |

### Resolution Order

The API tries the following steps in order and reports which one succeeded in the `resolution` field:

1. `matched`: an existing user already holds this provider identity.
2. `linked`: the provider supplied a verified email that matches an existing user, so the identity was attached to that user.
3. `created`: a new `UNAPPROVED` user was registered.

### Errors

| Error                      | Status | `code`                      | Meaning                                            |
| -------------------------- | ------ | --------------------------- | -------------------------------------------------- |
| `UnprocessableEntityError` | 422    | `TOKEN_VERIFICATION_FAILED` | The provider rejected the credential               |
| `UnprocessableEntityError` | 422    | `EMAIL_REQUIRED`            | Creation needs an `email` the provider didn't send |
| `ServerError`              | 503    | `PROVIDER_UNAVAILABLE`      | The provider could not be reached                  |

## Audience Registration

Apple and Google tokens carry an audience claim identifying the app they were issued to (for example, a bundle ID like `com.example.iosapp` or an OAuth client ID). The API accepts a token only when its audience appears in the combined allowlist formed by two sources:

1. The server's own environment allowlists (configured by the platform operator).
2. The per-developer audiences you register on your developer profile via `update_me(provider_audiences={"apple": [...], "google": [...]})` on the [Developer Service](developers.md).

If your app's identifier is absent from both sources, `identify()` raises `UnprocessableEntityError` with code `TOKEN_VERIFICATION_FAILED`. Register your bundle ID or client ID once, and the API will accept tokens from that app.

Discord and GitHub use OAuth access tokens, which do not carry audience claims, so they are not affected by this requirement.

## Examples

### Identify a Provider Login (Async)

```python
from vclient import VClient

async with VClient(base_url="https://api.valentina-noir.com", api_key="...") as client:
    svc = client.identity(company_id="COMPANY_ID")

    result = await svc.identify(provider="google", token=google_id_token)
    print(f"{result.resolution}: {result.user.username}")

    # Use the canonical user for subsequent requests
    users = client.users(result.user.id, company_id="COMPANY_ID")
```

### Identify a Provider Login (Sync)

```python
from vclient import SyncVClient

with SyncVClient(base_url="https://api.valentina-noir.com", api_key="...") as client:
    svc = client.identity(company_id="COMPANY_ID")
    result = svc.identify(provider="apple", token=apple_id_token)
```

### Handle a Rejected Token

```python
from vclient.exceptions import UnprocessableEntityError

try:
    result = await svc.identify(provider="apple", token=token)
except UnprocessableEntityError as e:
    if e.code == "TOKEN_VERIFICATION_FAILED":
        ...  # ask the user to sign in again
    elif e.code == "EMAIL_REQUIRED":
        result = await svc.identify(provider="apple", token=token, email=collected_email)  # prompt the user for an email address, then retry
```

## Related Documentation

- [Users](users.md) - `link_identity()` for connect-your-account flows, and the merge workflow for cleaning up pre-existing duplicates
- [User Self Registration](user_self_registration.md) - assertion-style registration without a provider credential
