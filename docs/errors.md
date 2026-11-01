---
icon: lucide/alert-triangle
---

# Error Handling

The client provides specific exception types for different error conditions. All exceptions inherit from `APIError`, so you can catch broad or narrow depending on your needs.

## Exception Hierarchy

Every API error maps to a specific exception class based on the HTTP status code:

| Exception                  | HTTP Status | Description                                                                                      |
| -------------------------- | ----------- | ------------------------------------------------------------------------------------------------ |
| `APIError`                 | -           | Base class for all API errors                                                                    |
| `AuthenticationError`      | 401         | Invalid or missing API key                                                                       |
| `AuthorizationError`       | 403         | Insufficient permissions                                                                         |
| `NotFoundError`            | 404         | Resource not found                                                                               |
| `ValidationError`          | 400         | Server-side validation failed                                                                    |
| `RequestValidationError`   | -           | Client-side validation failed                                                                    |
| `ConflictError`            | 409         | Resource conflict (e.g., duplicate ID, in-flight idempotency key, concurrent trait value change) |
| `UnprocessableEntityError` | 422         | Well-formed request that cannot be processed (has `.code`)                                       |
| `RateLimitError`           | 429         | Rate limit exceeded, or too many failed authentication attempts                                  |
| `ServerError`              | 5xx         | Server-side error                                                                                |

## The `code` Property

`APIError` exposes a `code` property that carries a machine-readable string identifying the specific failure. Not every error includes a code; check for `None` before branching on it.

The identity endpoints set `code` on every error they return. Known codes:

| `code`                      | Exception                  | Meaning                                                             |
| --------------------------- | -------------------------- | ------------------------------------------------------------------- |
| `TOKEN_VERIFICATION_FAILED` | `UnprocessableEntityError` | The provider rejected the credential; ask the user to sign in again |
| `EMAIL_REQUIRED`            | `UnprocessableEntityError` | A new user cannot be created because the provider sent no email     |
| `IDENTITY_ALREADY_LINKED`   | `ConflictError`            | The identity belongs to another user or the user already has one    |
| `IDENTITY_NOT_LINKED`       | `NotFoundError`            | The user has no identity from the provider being unlinked           |
| `LAST_IDENTITY`             | `ConflictError`            | Cannot unlink the user's only remaining identity                    |
| `PROVIDER_UNAVAILABLE`      | `ServerError`              | The provider could not be reached                                   |

```python
from vclient.exceptions import ConflictError, UnprocessableEntityError

try:
    result = await svc.identify(provider="apple", token=token)
except UnprocessableEntityError as e:
    if e.code == "TOKEN_VERIFICATION_FAILED":
        ...  # ask the user to sign in again
    elif e.code == "EMAIL_REQUIRED":
        result = await svc.identify(provider="apple", token=token, email=collected_email)
except ConflictError as e:
    if e.code == "IDENTITY_ALREADY_LINKED":
        ...  # inform the user that this provider account is already in use
```

## Conflicts

`ConflictError` has these extra properties:

| Property                     | Type          | Description                                                              |
| ---------------------------- | ------------- | ------------------------------------------------------------------------ |
| `retry_after`                | `int \| None` | Seconds from the `Retry-After` header, or `None` if the header is absent |
| `is_idempotency_in_progress` | `bool`        | `True` when `code == "IDEMPOTENCY_IN_PROGRESS"`                          |

The `IDEMPOTENCY_IN_PROGRESS` code means the API is still processing an earlier request with the same `Idempotency-Key`. The client handles it for you. A request that carries an idempotency key, passed by you or added by `auto_idempotency_keys`, waits for `Retry-After` (or backs off exponentially) and retries with the same key. This uses `max_retries` and needs `auto_retry_rate_limit` on. When the retries run out, the client raises the last `ConflictError`. Without an idempotency key, the in-progress 409 raises at once. Any other 409 also raises at once.

A same-key retry after the original request finished replays the original response, so it does not raise. If a `ConflictError` with `is_idempotency_in_progress` remains after retries run out, the outcome is unknown: the original may still be running or may fail. Refetch the resource to check, or retry later with the same key. Never treat it as success.

Restoring an archived user with the global admin `update_user(user_id, is_archived=False)` also returns 409 when another active user in the same company holds one of the restored user's provider identities. The `detail` names the provider.

## Request Too Large

The API returns 413 when a request body exceeds its size limit. The client raises the base `APIError` for it, with no subclass. See the API documentation for the limit.

## The `instance` Property

`.instance` is the request path only. It has no scheme, host, or query string.

## Example

Catch specific exceptions to handle different failure modes:

```python
from vclient import companies_service
from vclient.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    RequestValidationError,
    ServerError,
    UnprocessableEntityError,
    ValidationError,
)

companies = companies_service()

try:
    company = await companies.get("invalid-id")
except NotFoundError:
    print("Company not found")
except AuthorizationError:
    print("You don't have access to this company")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Server validation failed: {e}")
except RequestValidationError as e:
    print(f"Client validation failed: {e}")
except ConflictError:
    print("Conflict: reused idempotency key, or trait changed (refetch and retry)")
except UnprocessableEntityError as e:
    print(f"Cannot process request: {e.code}")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except ServerError:
    print("Server error, try again later")
except APIError as e:
    print(f"API error: {e}")
```

!!! tip

    Catch `APIError` as a fallback to handle any unexpected API error. Place it last in your `except` chain so more specific exceptions are matched first.

!!! warning "Repeated authentication failures"

    After 20 requests with an invalid API key from one address within 5 minutes, the API answers requests from that address with 429 until the 5-minute window ends. A key that authenticated within the last minute keeps working. The client waits out the `Retry-After` time once, and the next attempt then fails with `AuthenticationError`. Fix the API key instead of retrying an `AuthenticationError` in a loop.
