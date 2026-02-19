# Structured Logging Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add loguru-based structured logging to vclient with stdlib bridge, disabled by default.

**Architecture:** Centralized HTTP logging in `BaseService._request()` and `_raise_for_status()`, lifecycle logging in `VClient.__init__()` and `close()`. A `_PropagateHandler` bridges loguru to stdlib `logging`. All logs disabled by default via `logger.disable("vclient")`.

**Tech Stack:** loguru, Python stdlib logging, pytest caplog for testing

**Design doc:** `docs/plans/2026-02-19-structured-logging-design.md`

---

### Task 1: Add loguru dependency

**Files:**
- Modify: `pyproject.toml:7` (dependencies line)

**Step 1: Add loguru to dependencies**

In `pyproject.toml`, change the dependencies line from:

```toml
dependencies = ["anyio>=4.12.1", "httpx>=0.28.1", "pydantic[email]>=2.12.5"]
```

to:

```toml
dependencies = ["anyio>=4.12.1", "httpx>=0.28.1", "loguru>=0.7.3", "pydantic[email]>=2.12.5"]
```

**Step 2: Sync dependencies**

Run: `uv sync`
Expected: loguru installed, lock file updated

**Step 3: Commit**

```
feat(logging): add loguru dependency
```

---

### Task 2: Add logging initialization to `__init__.py`

**Files:**
- Modify: `src/vclient/__init__.py`

**Step 1: Write a failing test for the PropagateHandler bridge**

Add a new test file `tests/integration/test_logging.py`:

```python
"""Tests for vclient structured logging."""

import logging

import pytest
import respx
from loguru import logger

from vclient import VClient
from vclient.services.base import BaseService

pytestmark = pytest.mark.anyio


class TestLoggingInitialization:
    """Tests for logging initialization and PropagateHandler bridge."""

    def test_logging_disabled_by_default(self, caplog):
        """Verify vclient logs are silent by default."""
        # Given: A logger that has not been explicitly enabled
        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: A log message is emitted from vclient
            logger.bind().opt(depth=0).debug("test message")

        # Then: No vclient log messages appear
        vclient_records = [r for r in caplog.records if r.name.startswith("vclient")]
        assert len(vclient_records) == 0

    @respx.mock
    async def test_logging_enabled_captures_request_logs(self, base_url, api_key, caplog):
        """Verify enabling vclient logging produces debug logs for requests."""
        # Given: vclient logging is enabled
        logger.enable("vclient")

        # Given: A mocked API endpoint
        respx.get(f"{base_url}/test").respond(200, json={"ok": True})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = BaseService(client)
                await service._get("/test")

        # Then: Request logs appear
        log_text = caplog.text
        assert "Send GET" in log_text
        assert "Receive 200" in log_text

        # Cleanup
        logger.disable("vclient")
```

**Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/integration/test_logging.py -x -v -p no:xdist`
Expected: FAIL — no log messages captured yet

**Step 3: Add PropagateHandler and logger setup to `__init__.py`**

At the top of `src/vclient/__init__.py`, before the existing imports, add:

```python
import logging as _logging

from loguru import logger as _logger


class _PropagateHandler(_logging.Handler):
    """Forward loguru messages to stdlib logging for caplog/handler compatibility."""

    def emit(self, record: _logging.LogRecord) -> None:
        _logging.getLogger(record.name).handle(record)


_logger.add(
    _PropagateHandler(),
    format="{message}",
    filter=lambda record: record["name"].startswith("vclient"),
)

_logger.disable("vclient")
```

The existing imports (`from vclient.client import VClient`, etc.) remain unchanged below this block.

**Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/integration/test_logging.py -x -v -p no:xdist`
Expected: `test_logging_disabled_by_default` PASS. `test_logging_enabled_captures_request_logs` still fails (no log calls in `_request()` yet — that's Task 3).

**Step 5: Lint**

Run: `uv run ruff check src/vclient/__init__.py --fix && uv run ruff format src/vclient/__init__.py`

**Step 6: Commit**

```
feat(logging): add PropagateHandler and disable logging by default
```

---

### Task 3: Add logging to `BaseService._request()`

**Files:**
- Modify: `src/vclient/services/base.py:1-10` (imports), `base.py:132-224` (`_request` method)

**Step 1: Write failing tests for HTTP lifecycle logging**

Add to `tests/integration/test_logging.py`:

```python
class TestRequestLogging:
    """Tests for HTTP request/response logging in BaseService._request()."""

    @respx.mock
    async def test_log_request_start_and_response(self, base_url, api_key, caplog):
        """Verify debug logs for request start and response received."""
        # Given: vclient logging is enabled
        logger.enable("vclient")

        # Given: A mocked endpoint
        respx.get(f"{base_url}/companies").respond(200, json={"items": []})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a GET request
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = BaseService(client)
                await service._get("/companies")

        # Then: Both request and response are logged
        log_text = caplog.text
        assert "Send GET /companies" in log_text
        assert "Receive 200 from GET /companies" in log_text

        # Cleanup
        logger.disable("vclient")

    @respx.mock
    async def test_log_retry_on_rate_limit(self, base_url, api_key, caplog, mocker):
        """Verify warning log on rate limit retry."""
        # Given: Mock sleep to avoid delays
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: vclient logging is enabled
        logger.enable("vclient")

        # Given: An endpoint that returns 429 then succeeds
        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.Response(
                    429,
                    json={"detail": "Rate limited"},
                    headers={"RateLimit": '"default";r=0;t=1'},
                ),
                httpx.Response(200, json={"ok": True}),
            ]
        )

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that gets rate limited
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = BaseService(client)
                await service._get("/test")

        # Then: Retry warning is logged
        log_text = caplog.text
        assert "Retry GET /test after rate limit" in log_text

        # Cleanup
        logger.disable("vclient")

    @respx.mock
    async def test_log_retry_on_server_error(self, base_url, api_key, caplog, mocker):
        """Verify warning log on server error retry."""
        # Given: Mock sleep to avoid delays
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: vclient logging is enabled
        logger.enable("vclient")

        # Given: An endpoint that returns 500 then succeeds
        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.Response(500, json={"detail": "Server error"}),
                httpx.Response(200, json={"ok": True}),
            ]
        )

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that hits a server error
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = BaseService(client)
                await service._get("/test")

        # Then: Retry warning is logged
        log_text = caplog.text
        assert "Retry GET /test after 500" in log_text

        # Cleanup
        logger.disable("vclient")

    @respx.mock
    async def test_log_retry_on_network_error(self, base_url, api_key, caplog, mocker):
        """Verify warning log on network error retry."""
        # Given: Mock sleep to avoid delays
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: vclient logging is enabled
        logger.enable("vclient")

        # Given: An endpoint that raises ConnectError then succeeds
        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.ConnectError("Connection refused"),
                httpx.Response(200, json={"ok": True}),
            ]
        )

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that hits a network error
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = BaseService(client)
                await service._get("/test")

        # Then: Retry warning is logged
        log_text = caplog.text
        assert "Retry GET /test after ConnectError" in log_text

        # Cleanup
        logger.disable("vclient")

    @respx.mock
    async def test_log_max_retries_exhausted(self, base_url, api_key, caplog, mocker):
        """Verify error log when max retries are exhausted."""
        # Given: Mock sleep to avoid delays
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: vclient logging is enabled
        logger.enable("vclient")

        # Given: An endpoint that always returns 429
        respx.get(f"{base_url}/test").respond(
            429,
            json={"detail": "Rate limited"},
            headers={"RateLimit": '"default";r=0;t=0'},
        )

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that exhausts retries
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = BaseService(client)
                with pytest.raises(Exception):
                    await service._get("/test")

        # Then: Exhaustion error is logged
        log_text = caplog.text
        assert "Exhaust retries for GET /test" in log_text

        # Cleanup
        logger.disable("vclient")
```

Add `import httpx` to the imports at the top of the test file.

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/integration/test_logging.py::TestRequestLogging -x -v -p no:xdist`
Expected: FAIL — no logging calls exist in `_request()` yet

**Step 3: Add logging to `_request()` in `base.py`**

Add import at the top of `src/vclient/services/base.py` (after the existing imports):

```python
from loguru import logger
```

Then modify `_request()` (lines 132-224). The full replacement for the method body:

```python
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        files: Any | None = None,
    ) -> httpx.Response:
        """Make an HTTP request with automatic retry on transient errors.

        Retries on rate limits (429), server errors (5xx in retry_statuses),
        and network errors (ConnectError, TimeoutException). Non-idempotent
        methods (POST, PATCH) only retry on 5xx/network errors when an
        idempotency key header is present. Rate limit retries (429) always
        apply regardless of method.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            path: API endpoint path (will be appended to base_url).
            params: Query parameters.
            json: JSON body data.
            data: Form data.
            headers: Additional headers to include in the request.
            files: Files to upload (passed through to httpx).

        Returns:
            The HTTP response.

        Raises:
            RateLimitError: When rate limit is exceeded and max retries are exhausted.
            ServerError: When server error occurs and max retries are exhausted.
            httpx.ConnectError: When connection fails and max retries are exhausted.
            httpx.TimeoutException: When request times out and max retries are exhausted.
            APIError: For other API error responses.
        """
        config = self._client._config  # noqa: SLF001
        max_attempts = config.max_retries + 1 if config.auto_retry_rate_limit else 1
        retry_statuses = config.retry_statuses
        request_logger = logger.bind(method=method, url=path)

        last_error: RateLimitError | ServerError | None = None

        request_logger.debug("Send {method} {url}", method=method, url=path)

        for attempt in range(max_attempts):
            try:
                response = await self._http.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json,
                    data=data,
                    headers=headers,
                    files=files,
                )
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                if not self._is_retryable_method(method, headers) or attempt >= max_attempts - 1:
                    raise

                delay = self._calculate_backoff_delay(attempt, retry_after=None)
                request_logger.bind(
                    attempt=attempt + 1,
                    max_attempts=max_attempts,
                    error_type=type(e).__name__,
                    delay=round(delay, 2),
                ).warning(
                    "Retry {method} {url} after {error_type} (attempt {attempt}/{max_attempts})",
                    method=method,
                    url=path,
                    error_type=type(e).__name__,
                    attempt=attempt + 1,
                    max_attempts=max_attempts,
                )
                await asyncio.sleep(delay)
                continue

            try:
                self._raise_for_status(response)
                elapsed_ms = int(response.elapsed.total_seconds() * 1000)
                request_logger.bind(status=response.status_code, elapsed_ms=elapsed_ms).debug(
                    "Receive {status} from {method} {url} ({elapsed_ms}ms)",
                    status=response.status_code,
                    method=method,
                    url=path,
                    elapsed_ms=elapsed_ms,
                )
                return response  # noqa: TRY300
            except RateLimitError as e:
                last_error = e

                if attempt >= max_attempts - 1:
                    break

                delay = self._calculate_backoff_delay(attempt, e.retry_after)
                request_logger.bind(
                    attempt=attempt + 1,
                    max_attempts=max_attempts,
                    retry_after=e.retry_after,
                    delay=round(delay, 2),
                ).warning(
                    "Retry {method} {url} after rate limit (attempt {attempt}/{max_attempts}, delay {delay}s)",
                    method=method,
                    url=path,
                    attempt=attempt + 1,
                    max_attempts=max_attempts,
                    delay=round(delay, 2),
                )
                await asyncio.sleep(delay)
            except ServerError as e:
                if e.status_code not in retry_statuses or not self._is_retryable_method(
                    method, headers
                ):
                    raise

                last_error = e

                if attempt >= max_attempts - 1:
                    break

                delay = self._calculate_backoff_delay(attempt, retry_after=None)
                request_logger.bind(
                    status=e.status_code,
                    attempt=attempt + 1,
                    max_attempts=max_attempts,
                    delay=round(delay, 2),
                ).warning(
                    "Retry {method} {url} after {status} error (attempt {attempt}/{max_attempts}, delay {delay}s)",
                    method=method,
                    url=path,
                    status=e.status_code,
                    attempt=attempt + 1,
                    max_attempts=max_attempts,
                    delay=round(delay, 2),
                )
                await asyncio.sleep(delay)

        if last_error is not None:
            request_logger.bind(attempts=max_attempts).error(
                "Exhaust retries for {method} {url} after {attempts} attempts",
                method=method,
                url=path,
                attempts=max_attempts,
            )
            raise last_error

        msg = "Unexpected state: no response or error"
        raise RuntimeError(msg)
```

**Step 4: Run the new tests**

Run: `uv run pytest tests/integration/test_logging.py -x -v -p no:xdist`
Expected: All tests PASS

**Step 5: Run the full test suite to verify no regressions**

Run: `uv run pytest tests/ -x --tb=short`
Expected: All existing tests still pass

**Step 6: Lint**

Run: `uv run ruff check src/vclient/services/base.py --fix && uv run ruff format src/vclient/services/base.py`

**Step 7: Commit**

```
feat(logging): add structured logging to BaseService._request()
```

---

### Task 4: Add logging to `_raise_for_status()`

**Files:**
- Modify: `src/vclient/services/base.py:226-275` (`_raise_for_status` method)
- Test: `tests/integration/test_logging.py`

**Step 1: Write failing tests for error classification logging**

Add to `tests/integration/test_logging.py`:

```python
class TestErrorClassificationLogging:
    """Tests for error classification logging in _raise_for_status()."""

    @respx.mock
    async def test_log_authentication_error(self, base_url, api_key, caplog, mocker):
        """Verify error log on 401 authentication failure."""
        # Given: Mock sleep to avoid delays
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: vclient logging is enabled
        logger.enable("vclient")

        # Given: An endpoint that returns 401
        respx.get(f"{base_url}/test").respond(401, json={"detail": "Unauthorized"})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that fails auth
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = BaseService(client)
                with pytest.raises(Exception):
                    await service._get("/test")

        # Then: Auth error is logged
        assert "Fail authentication for GET /test (401)" in caplog.text

        # Cleanup
        logger.disable("vclient")

    @respx.mock
    async def test_log_not_found_at_debug(self, base_url, api_key, caplog):
        """Verify 404 is logged at DEBUG level."""
        # Given: vclient logging is enabled
        logger.enable("vclient")

        # Given: An endpoint that returns 404
        respx.get(f"{base_url}/test").respond(404, json={"detail": "Not found"})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request to a missing resource
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = BaseService(client)
                with pytest.raises(Exception):
                    await service._get("/test")

        # Then: 404 is logged at DEBUG
        assert "Return 404 for GET /test" in caplog.text

        # Cleanup
        logger.disable("vclient")

    @respx.mock
    async def test_log_validation_error(self, base_url, api_key, caplog):
        """Verify validation error is logged at WARNING."""
        # Given: vclient logging is enabled
        logger.enable("vclient")

        # Given: An endpoint that returns 400
        respx.post(f"{base_url}/test").respond(400, json={"detail": "Validation failed"})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that fails validation
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = BaseService(client)
                with pytest.raises(Exception):
                    await service._post("/test", json={})

        # Then: Validation error is logged
        assert "Reject POST /test with validation error" in caplog.text

        # Cleanup
        logger.disable("vclient")

    @respx.mock
    async def test_log_conflict_error(self, base_url, api_key, caplog):
        """Verify conflict error is logged at WARNING."""
        # Given: vclient logging is enabled
        logger.enable("vclient")

        # Given: An endpoint that returns 409
        respx.post(f"{base_url}/test").respond(409, json={"detail": "Conflict"})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that conflicts
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = BaseService(client)
                with pytest.raises(Exception):
                    await service._post("/test", json={})

        # Then: Conflict is logged
        assert "Return 409 conflict for POST /test" in caplog.text

        # Cleanup
        logger.disable("vclient")
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/integration/test_logging.py::TestErrorClassificationLogging -x -v -p no:xdist`
Expected: FAIL — no logging calls in `_raise_for_status()` yet

**Step 3: Modify `_raise_for_status()` to add logging**

The `_raise_for_status()` method needs the request context (method, url) which isn't currently available. Two options:

**Option A (recommended):** Pass `method` and `url` as parameters to `_raise_for_status()`. Update the call site in `_request()` to pass them. This keeps things explicit.

Change the signature from:
```python
def _raise_for_status(self, response: httpx.Response) -> None:
```
to:
```python
def _raise_for_status(self, response: httpx.Response, method: str, url: str) -> None:
```

Update the call in `_request()`:
```python
self._raise_for_status(response, method, path)
```

Then add logging calls before each `raise` in `_raise_for_status()`:

```python
    def _raise_for_status(self, response: httpx.Response, method: str, url: str) -> None:
        """Raise appropriate exception for error responses.

        Args:
            response: The HTTP response to check.
            method: The HTTP method of the request.
            url: The URL path of the request.

        Raises:
            AuthenticationError: For 401 responses.
            AuthorizationError: For 403 responses.
            NotFoundError: For 404 responses.
            ValidationError: For 400 responses.
            ConflictError: For 409 responses.
            RateLimitError: For 429 responses.
            ServerError: For 5xx responses.
            APIError: For other error responses.
        """
        if response.is_success:
            return

        status_code = response.status_code
        try:
            response_data = response.json()
            message = response_data.get("detail", response.text)
        except (ValueError, KeyError, TypeError):
            response_data = {}
            message = response.text or f"HTTP {status_code}"

        error_logger = logger.bind(method=method, url=url, status=status_code)

        error_map: dict[int, type[APIError]] = {
            400: ValidationError,
            401: AuthenticationError,
            403: AuthorizationError,
            404: NotFoundError,
            409: ConflictError,
            429: RateLimitError,
        }

        if status_code == 429:  # noqa: PLR2004
            retry_after = self._parse_retry_after(response)
            remaining = self._parse_remaining_tokens(response)
            raise RateLimitError(
                message, status_code, response_data, retry_after=retry_after, remaining=remaining
            )

        if status_code in (401, 403):
            error_logger.error(
                "Fail authentication for {method} {url} ({status})",
                method=method,
                url=url,
                status=status_code,
            )

        if status_code == 404:  # noqa: PLR2004
            error_logger.debug(
                "Return 404 for {method} {url}",
                method=method,
                url=url,
            )

        if status_code == 400:  # noqa: PLR2004
            error_logger.warning(
                "Reject {method} {url} with validation error",
                method=method,
                url=url,
            )

        if status_code == 409:  # noqa: PLR2004
            error_logger.warning(
                "Return 409 conflict for {method} {url}",
                method=method,
                url=url,
            )

        if status_code in error_map:
            raise error_map[status_code](message, status_code, response_data)

        if HTTP_500_INTERNAL_SERVER_ERROR <= status_code < HTTP_600_UPPER_BOUND:
            raise ServerError(message, status_code, response_data)

        raise APIError(message, status_code, response_data)
```

Note: 429 does NOT get a log here because retry logging in `_request()` already handles it. 5xx also doesn't get a log here because `_request()` handles retry/exhaustion logging.

**Step 4: Run the new tests**

Run: `uv run pytest tests/integration/test_logging.py::TestErrorClassificationLogging -x -v -p no:xdist`
Expected: All PASS

**Step 5: Run the full test suite**

Run: `uv run pytest tests/ -x --tb=short`
Expected: All pass (existing tests should work fine since `_raise_for_status` call is updated in `_request`)

**Step 6: Lint**

Run: `uv run ruff check src/vclient/services/base.py --fix && uv run ruff format src/vclient/services/base.py`

**Step 7: Commit**

```
feat(logging): add error classification logging to _raise_for_status()
```

---

### Task 5: Add logging to `VClient` lifecycle

**Files:**
- Modify: `src/vclient/client.py:1-10` (imports), `client.py:71-157` (`__init__`), `client.py:193-198` (`close`)
- Test: `tests/integration/test_logging.py`

**Step 1: Write failing tests for lifecycle logging**

Add to `tests/integration/test_logging.py`:

```python
class TestClientLifecycleLogging:
    """Tests for VClient lifecycle logging."""

    async def test_log_client_initialization(self, base_url, api_key, caplog):
        """Verify debug log on client initialization."""
        # Given: vclient logging is enabled
        logger.enable("vclient")

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Creating a client
            async with VClient(base_url=base_url, api_key=api_key) as client:
                pass

        # Then: Init log appears with base_url
        assert "Initialize VClient" in caplog.text
        assert base_url in caplog.text

        # Cleanup
        logger.disable("vclient")

    async def test_log_client_close(self, base_url, api_key, caplog):
        """Verify debug log on client close."""
        # Given: vclient logging is enabled
        logger.enable("vclient")

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Closing a client
            client = VClient(base_url=base_url, api_key=api_key)
            await client.close()

        # Then: Close log appears
        assert "Close VClient" in caplog.text

        # Cleanup
        logger.disable("vclient")
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/integration/test_logging.py::TestClientLifecycleLogging -x -v -p no:xdist`
Expected: FAIL

**Step 3: Add logging to `client.py`**

Add import at the top of `src/vclient/client.py`:

```python
from loguru import logger
```

At the end of `__init__()` (after line 156, after `configure_default_client(self)` block), add:

```python
        logger.bind(
            base_url=self._config.base_url,
            timeout=self._config.timeout,
            max_retries=self._config.max_retries,
        ).debug(
            "Initialize VClient (base_url={base_url})",
            base_url=self._config.base_url,
        )
```

In `close()` (before `await self._http.aclose()` on line 197), add:

```python
        logger.bind(base_url=self._config.base_url).debug("Close VClient")
```

**Step 4: Run tests**

Run: `uv run pytest tests/integration/test_logging.py::TestClientLifecycleLogging -x -v -p no:xdist`
Expected: All PASS

**Step 5: Run the full test suite**

Run: `uv run pytest tests/ -x --tb=short`
Expected: All pass

**Step 6: Lint**

Run: `uv run ruff check src/vclient/client.py --fix && uv run ruff format src/vclient/client.py`

**Step 7: Commit**

```
feat(logging): add lifecycle logging to VClient init and close
```

---

### Task 6: Run full validation

**Step 1: Run the complete test suite**

Run: `uv run duty test`
Expected: All tests pass with coverage

**Step 2: Run full lint**

Run: `uv run duty lint`
Expected: No lint errors

**Step 3: Verify existing tests still pass unchanged**

Run: `uv run pytest tests/integration/services/test_base.py -x -v`
Expected: All 30+ existing tests still pass

---

### Task 7: Update external documentation

**Files:**
- Modify: `../valentina-noir/docs/python-api-client/index.md`

**Step 1: Add Logging section to documentation**

In `../valentina-noir/docs/python-api-client/index.md`, add a new section after "## Configuration" (after line 198, after the retry_statuses example), before "### Default Company ID":

```markdown
### Logging

The client uses [Loguru](https://github.com/Delgan/loguru) for structured logging, disabled by default. Enable it to see HTTP request/response details, retry attempts, and error information.

#### Enable Logging

```python
from loguru import logger

# Enable vclient logs (they flow to your existing loguru handlers)
logger.enable("vclient")
```

#### Using with Standard Library Logging

The client includes a bridge to Python's stdlib `logging` module. After enabling, logs are also available through the standard `logging` system:

```python
import logging
from loguru import logger

# Enable vclient logs
logger.enable("vclient")

# Configure stdlib handler
logging.getLogger("vclient").addHandler(logging.StreamHandler())
logging.getLogger("vclient").setLevel(logging.DEBUG)
```

#### Log Levels

| Level   | Events                                           |
| ------- | ------------------------------------------------ |
| DEBUG   | Request start, response received, 404, lifecycle |
| WARNING | Retries (rate limit, server error, network), validation errors (400), conflicts (409) |
| ERROR   | Authentication failures (401/403), retries exhausted |

#### Disable Logging

```python
from loguru import logger

logger.disable("vclient")
```
```

Also update the Features list (line 19 area) to add:

```markdown
- **Structured logging** - Loguru-based logging with stdlib bridge, disabled by default
```

**Step 2: Commit**

```
docs(logging): add logging section to client documentation
```

---

### Task 8: Final verification and cleanup

**Step 1: Run full validation**

Run: `uv run duty lint && uv run duty test`
Expected: All pass

**Step 2: Review all changes**

Run: `git diff main --stat` to verify only expected files were changed.

Expected files:
- `pyproject.toml` (1 line: dependency)
- `uv.lock` (auto-updated)
- `src/vclient/__init__.py` (PropagateHandler + logger setup)
- `src/vclient/client.py` (lifecycle logging)
- `src/vclient/services/base.py` (HTTP + error logging)
- `tests/integration/test_logging.py` (new test file)
- `../valentina-noir/docs/python-api-client/index.md` (docs)
- `docs/plans/` (design doc + this plan)
