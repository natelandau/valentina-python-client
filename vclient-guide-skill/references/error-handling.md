# Error Handling Reference

Complete reference for exceptions, retry behavior, and recovery patterns in vclient.

## Contents

- [Exception Hierarchy](#exception-hierarchy)
- [Common Properties (RFC 9457)](#common-properties-rfc-9457)
- [Per-Exception Details](#per-exception-details)
- [Retry Behavior](#retry-behavior)
- [Recipes](#recipes)
- [Testing Error Paths](#testing-error-paths)

## Exception Hierarchy

All exceptions live in `vclient.exceptions` and inherit from `APIError`, which inherits from `Exception`. A broad `except APIError` catches every error the client raises — `httpx` transport failures surface as `httpx.HTTPError` subclasses and are **not** wrapped.

```
Exception
└── APIError                       # base class, RFC 9457 shape
    ├── AuthenticationError        # 401
    ├── AuthorizationError         # 403
    ├── NotFoundError              # 404
    ├── ConflictError              # 409
    ├── UnprocessableEntityError   # 422 (check .code for specific failure)
    ├── ValidationError            # 400 (adds .invalid_parameters)
    ├── RequestValidationError     # client-side (adds .errors)
    ├── RateLimitError             # 429 (adds .retry_after, .remaining)
    └── ServerError                # 5xx
```

## Common Properties (RFC 9457)

Every exception exposes these properties. All are nullable because the server may omit fields or the failure may be client-side.

| Property | Type | Source | Notes |
|----------|------|--------|-------|
| `.status_code` | `int \| None` | HTTP response | `None` for `RequestValidationError` (no request sent) |
| `.title` | `str \| None` | `response_data["title"]` | Short problem type label |
| `.detail` | `str \| None` | `response_data["detail"]` | Human-readable explanation — suitable for display |
| `.instance` | `str \| None` | `response_data["instance"]` | URI reference to the specific failure occurrence |
| `.request_id` | `str \| None` | `response_data["request_id"]` | Correlate with server logs — **always log this** |
| `.code` | `str \| None` | `response_data["code"]` | Machine-readable error code extension; `None` on most errors |
| `.response_data` | `dict[str, Any]` | raw body | The full RFC 9457 payload |
| `.message` | `str` | constructor arg | The initial exception message |

### Machine-readable error codes (`.code`)

Some endpoints set a `code` extension member in the RFC 9457 body to let callers branch on the specific failure without parsing `.detail` text.

| Code | Exception | Endpoint | Meaning |
|------|-----------|----------|---------|
| `TOKEN_VERIFICATION_FAILED` | `UnprocessableEntityError` (422) | `IdentityService.identify()`, `UsersService.link_identity()` | The provider rejected or could not verify the credential |
| `EMAIL_REQUIRED` | `UnprocessableEntityError` (422) | `IdentityService.identify()` | Creating a new user but provider supplied no email and none was passed in the request |
| `IDENTITY_ALREADY_LINKED` | `ConflictError` (409) | `UsersService.link_identity()` | The provider identity belongs to a different user, or the target user already has a different identity from this provider |
| `PROVIDER_UNAVAILABLE` | `ServerError` (sent with HTTP 503; `ServerError` covers all 5xx) | `IdentityService.identify()` | The identity provider is unreachable |

### String formatting

`str(exc)` produces a pipe-separated summary:

```
[404] Resource not found | Detail: No user with id 'u-123' | Instance: /errors/abc | Request-ID: req-7f2
```

This is safe to pass directly to `logger.error()` or print — it will not leak sensitive data beyond what the server already returned in the response.

## Per-Exception Details

### `AuthenticationError` (401)

Raised when the API key is missing, malformed, or revoked. Not retried automatically — there's no point. Surface this as "please log in again" or a startup check.

### `AuthorizationError` (403)

The key is valid but the caller cannot perform this action (often wrong `on_behalf_of`, wrong `company_id`, or missing role). Check permission requirements in `docs/services/`. Not retried.

### `NotFoundError` (404)

The URL or resource id doesn't exist. Sometimes used to hide 403s from unauthorized users, so don't assume the resource is truly absent without context.

```python
try:
    campaign = await campaigns_svc.get(campaign_id)
except NotFoundError:
    campaign = None
```

### `ConflictError` (409)

Most commonly raised when an idempotency key is reused with a different request body. If you see this, regenerate your idempotency key; don't retry with the same key.

### `UnprocessableEntityError` (422)

Raised by the identity endpoints when a request is well-formed but cannot be processed. Always check `.code` to determine the specific failure:

```python
from vclient.exceptions import UnprocessableEntityError

try:
    result = await identity_svc.identify(provider="google", token=id_token)
except UnprocessableEntityError as e:
    if e.code == "TOKEN_VERIFICATION_FAILED":
        # The provider rejected the credential; ask the user to log in again
        raise
    if e.code == "EMAIL_REQUIRED":
        # Need to collect the user's email before retrying
        raise
    raise  # unexpected code
```

### `ValidationError` (400) — server-side

The server rejected the request. The `.invalid_parameters` list names offending fields:

```python
try:
    await campaigns_svc.create(request=CampaignCreate(name=""))
except ValidationError as e:
    # e.invalid_parameters -> [{"field": "name", "message": "must not be empty"}, ...]
    for param in e.invalid_parameters:
        field = param.get("field", "?")
        message = param.get("message", "invalid")
        logger.warning("validation failed", field=field, message=message)
```

`str(e)` appends a `Fields:` section automatically:

```
[400] Bad Request | Detail: Validation failed | Fields: name: must not be empty; email: invalid format
```

### `RequestValidationError` — client-side

Raised by services when keyword args fail to construct the underlying Pydantic request model, **before any HTTP call**. Wraps a `pydantic.ValidationError`. Exposes `.errors` (list of Pydantic error dicts):

```python
try:
    await users_svc.create(email="not-an-email")
except RequestValidationError as e:
    for err in e.errors:
        # err = {"type": "value_error", "loc": ("email",), "msg": "...", "input": "..."}
        loc = ".".join(str(p) for p in err["loc"])
        logger.info("client validation failed", location=loc, message=err["msg"])
```

Use this to short-circuit bad input in forms before paying for a round trip.

### `RateLimitError` (429)

Only raised when `auto_retry_rate_limit=False` or retries are exhausted. Read rate limit headers through:

| Property | Purpose |
|----------|---------|
| `.retry_after` | Seconds to wait before retrying (from `RateLimit` t-parameter or `Retry-After`) |
| `.remaining` | Tokens remaining in the bucket at the time of the error |

```python
try:
    await svc.create(...)
except RateLimitError as e:
    await asyncio.sleep(e.retry_after or 1)
    # ...retry with fresh idempotency key if applicable
```

### `ServerError` (5xx)

Transient server failures. These are included in the default `retry_statuses`, so a `ServerError` bubbling up means retries already ran. Log `.request_id` so backend engineers can correlate.

## Retry Behavior

The client performs automatic retries with exponential backoff. Retries are invisible to your code — you only see the final exception (or the eventual success).

Configuration (all constructor args):

| Arg | Default | Meaning |
|-----|---------|---------|
| `max_retries` | 3 | Retry attempts for transient failures |
| `retry_delay` | 1.0s | Base delay, multiplied by attempt number |
| `retry_statuses` | `{429, 500, 502, 503, 504}` | Status codes that trigger retries |
| `auto_retry_rate_limit` | `True` | Honor `Retry-After` / RateLimit headers on 429 |
| `auto_idempotency_keys` | `False` | Auto-generate `Idempotency-Key` for POST/PUT/PATCH |

### When automatic retries run

- Response status is in `retry_statuses` → retried with backoff.
- 429 with `auto_retry_rate_limit=True` → retried using the server's `retry_after` value.
- Network-level `httpx.TransportError` → retried.

### When they don't

- 4xx other than 429 → raised immediately (retrying a 400 will not help).
- Retries exhausted → the last exception propagates.
- `auto_idempotency_keys=False` on unsafe methods — retrying a POST without an idempotency key risks duplicate side effects; either enable the flag or pass your own.

### Interaction with idempotency

For `create()` calls that use `auto_idempotency_keys=True`, the same key is reused across retries of a single logical request. If the server returns `ConflictError` on retry, it means the original request succeeded — treat as success and refetch the resource.

## Recipes

### Wrap the client for structured logging

```python
import logging
from vclient.exceptions import APIError

logger = logging.getLogger(__name__)

async def call_api(coro):
    try:
        return await coro
    except APIError as e:
        logger.error(
            "api_error",
            extra={
                "status": e.status_code,
                "title": e.title,
                "request_id": e.request_id,
                "instance": e.instance,
            },
        )
        raise
```

### Map exceptions to HTTP responses (FastAPI)

```python
from fastapi import HTTPException
from vclient.exceptions import (
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    APIError,
)

def translate(exc: APIError) -> HTTPException:
    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=404, detail=exc.detail)
    if isinstance(exc, AuthenticationError):
        return HTTPException(status_code=401, detail=exc.detail)
    if isinstance(exc, AuthorizationError):
        return HTTPException(status_code=403, detail=exc.detail)
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=422, detail=exc.invalid_parameters)
    if isinstance(exc, RateLimitError):
        headers = {"Retry-After": str(exc.retry_after)} if exc.retry_after else None
        return HTTPException(status_code=429, detail=exc.detail, headers=headers)
    return HTTPException(status_code=502, detail="Upstream error")
```

### Bounded manual retry with jitter

Useful when you need retry semantics beyond the built-in ones (for example, retrying `ConflictError` from optimistic concurrency):

```python
import asyncio
import random
from vclient.exceptions import ConflictError

async def with_conflict_retry(fn, *, attempts: int = 5):
    for attempt in range(attempts):
        try:
            return await fn()
        except ConflictError:
            if attempt == attempts - 1:
                raise
            await asyncio.sleep((2 ** attempt) * 0.1 + random.random() * 0.1)
```

### Separating recoverable from fatal errors

```python
from vclient.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
)

FATAL = (AuthenticationError, AuthorizationError)

try:
    result = await svc.do_something()
except FATAL:
    raise                     # caller cannot recover — bubble up
except NotFoundError:
    result = default_value    # absent is fine
except APIError as e:
    logger.warning("transient failure, skipping", request_id=e.request_id)
    result = None
```

## Testing Error Paths

`FakeVClient.set_error()` simulates server errors without real HTTP. Pair with route constants from `Routes`. Pass `code=` to set the machine-readable `APIError.code` extension member when testing logic that branches on specific codes (e.g. `set_error(Routes.IDENTITY_IDENTIFY, status_code=422, code="TOKEN_VERIFICATION_FAILED")`):

```python
import pytest
from vclient.endpoints import Endpoints
from vclient.exceptions import NotFoundError, RateLimitError, ValidationError
from vclient.testing import FakeVClient, Routes

async def test_handles_missing_user():
    async with FakeVClient() as client:
        client.set_error(Routes.USERS_GET, status_code=404, detail="no such user")
        with pytest.raises(NotFoundError):
            await client.users(on_behalf_of="u", company_id="c").get("missing")

async def test_surfaces_invalid_parameters():
    async with FakeVClient() as client:
        # set_error() covers detail and code; use the low-level add_route()
        # for other extension members such as invalid_parameters
        client.add_route(
            "POST",
            Endpoints.CAMPAIGNS,
            status_code=400,
            json={
                "title": "Bad Request",
                "detail": "validation failed",
                "invalid_parameters": [{"field": "name", "message": "required"}],
            },
        )
        with pytest.raises(ValidationError) as exc_info:
            await client.campaigns(on_behalf_of="u", company_id="c").create(name="abc")
        assert exc_info.value.invalid_parameters[0]["field"] == "name"

async def test_handles_rate_limit():
    async with FakeVClient(auto_retry_rate_limit=False) as client:
        client.set_error(Routes.USERS_LIST, status_code=429, detail="slow down")
        with pytest.raises(RateLimitError):
            await client.users(on_behalf_of="u", company_id="c").list_all()
```

Disable `auto_retry_rate_limit` in tests that assert `RateLimitError` is raised, otherwise the fake client's repeated error will be absorbed by the retry loop until `max_retries` is exhausted.

For client-side validation (`RequestValidationError`), no HTTP mock is needed — constructing the bad input is enough:

```python
import pytest
from vclient.exceptions import RequestValidationError
from vclient.testing import FakeVClient

async def test_rejects_bad_email_before_request():
    async with FakeVClient() as client:
        svc = client.users(on_behalf_of="u", company_id="c")
        with pytest.raises(RequestValidationError) as exc_info:
            await svc.create(email="not-an-email", username="x")
        assert any("email" in str(e["loc"]) for e in exc_info.value.errors)
```
