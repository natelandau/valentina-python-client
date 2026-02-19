# Structured Logging Design

## Overview

Add structured logging to vclient using loguru. Logs are disabled by default following loguru's library convention. Consumers opt in with `logger.enable("vclient")`. A stdlib `logging` bridge ensures compatibility with consumers not using loguru directly.

## Audience

Library consumers who want to debug API interactions, observe retries, and understand failures. Logs are opt-in only.

## Architecture

### Approach: Hybrid — centralized HTTP + lifecycle events

- All HTTP logging lives in `BaseService._request()` (single funnel for every API call)
- Lifecycle logging in `VClient.__init__()` and `VClient.close()`
- Error classification logging in `BaseService._raise_for_status()`

This touches ~3 files vs ~20 for distributed logging across each service.

### Initialization

In `src/vclient/__init__.py`:

```python
import logging as _logging

from loguru import logger

class _PropagateHandler(_logging.Handler):
    """Forward loguru messages to stdlib logging."""

    def emit(self, record: _logging.LogRecord) -> None:
        _logging.getLogger(record.name).handle(record)

logger.add(
    _PropagateHandler(),
    format="{message}",
    filter=lambda record: record["name"].startswith("vclient"),
)

logger.disable("vclient")
```

- `logger.disable("vclient")` — silent by default
- `_PropagateHandler` bridges loguru to stdlib `logging`, filtered to vclient messages only
- No new public API surface for logging control

### Consumer usage

```python
# Loguru users
from loguru import logger
logger.enable("vclient")

# Stdlib logging users
from loguru import logger
logger.enable("vclient")
import logging
logging.getLogger("vclient").addHandler(logging.StreamHandler())
logging.getLogger("vclient").setLevel(logging.DEBUG)
```

## Log Points

### BaseService._request() — HTTP lifecycle

| Event              | Level   | Bound Context                                            | Message (imperative)                                                     |
| ------------------ | ------- | -------------------------------------------------------- | ------------------------------------------------------------------------ |
| Request start      | DEBUG   | `method`, `url`                                          | `Send {method} {url}`                                                    |
| Response received  | DEBUG   | `method`, `url`, `status`, `elapsed_ms`                  | `Receive {status} from {method} {url} ({elapsed_ms}ms)`                  |
| Retry rate limit   | WARNING | `method`, `url`, `attempt`, `max_attempts`, `retry_after`, `delay` | `Retry {method} {url} after rate limit (attempt {n}/{max}, delay {d}s)`  |
| Retry server error | WARNING | `method`, `url`, `status`, `attempt`, `max_attempts`, `delay`      | `Retry {method} {url} after {status} error (attempt {n}/{max}, delay {d}s)` |
| Retry network error| WARNING | `method`, `url`, `error_type`, `attempt`, `max_attempts` | `Retry {method} {url} after {error_type} (attempt {n}/{max})`            |
| Max retries exhausted | ERROR | `method`, `url`, `attempts`                             | `Exhaust retries for {method} {url} after {attempts} attempts`           |

### VClient — lifecycle

| Event           | Level | Bound Context                   | Message                                      |
| --------------- | ----- | ------------------------------- | -------------------------------------------- |
| Client init     | DEBUG | `base_url`, `timeout`, `max_retries` | `Initialize VClient (base_url={base_url})`   |
| Client close    | DEBUG | `base_url`                      | `Close VClient`                              |

### BaseService._raise_for_status() — error classification

| Event            | Level   | Bound Context          | Message                                             |
| ---------------- | ------- | ---------------------- | --------------------------------------------------- |
| Auth error (401) | ERROR   | `method`, `url`, `status` | `Fail authentication for {method} {url} ({status})` |
| Auth error (403) | ERROR   | `method`, `url`, `status` | `Fail authentication for {method} {url} ({status})` |
| Not found (404)  | DEBUG   | `method`, `url`        | `Return 404 for {method} {url}`                     |
| Validation (400) | WARNING | `method`, `url`        | `Reject {method} {url} with validation error`       |
| Conflict (409)   | WARNING | `method`, `url`        | `Return 409 conflict for {method} {url}`             |

## Structured Context

Use `logger.bind()` to attach structured metadata to each log message. Consumers with JSON serialization (`serialize=True`) get rich, searchable fields. Plain text consumers see the formatted message.

```python
request_logger = logger.bind(method=method, url=path)
request_logger.debug("Send {method} {url}", method=method, url=path)
```

## Files to Modify

| File                                    | Change                                                     |
| --------------------------------------- | ---------------------------------------------------------- |
| `pyproject.toml`                        | Add `loguru` to dependencies                               |
| `src/vclient/__init__.py`               | Add `_PropagateHandler`, logger setup, `logger.disable()`  |
| `src/vclient/services/base.py`          | Add logging to `_request()` and `_raise_for_status()`      |
| `src/vclient/client.py`                 | Add logging to `__init__()` and `close()`                  |
| `tests/integration/services/test_base.py` | Add tests for log output                                 |
| External: `../valentina-noir/docs/python-api-client/index.md` | Add logging section   |

No new files created. No changes to public API surface beyond loguru as a dependency.

## Testing

Use pytest's `caplog` fixture, which captures logs via the `_PropagateHandler` stdlib bridge:

```python
def test_request_logs_debug_on_success(base_service, caplog):
    with caplog.at_level("DEBUG"):
        logger.enable("vclient")
        # ... make request with respx mock
        assert "Send GET" in caplog.text
        assert "Receive 200" in caplog.text
```

No special loguru test fixtures needed.

## Design Decisions

1. **loguru over stdlib logging** — requested by user; provides structured binding, simpler API
2. **Disabled by default** — standard loguru library convention; zero noise for consumers who don't want it
3. **PropagateHandler bridge** — stdlib compatibility without requiring consumers to use loguru directly
4. **Centralized + lifecycle (hybrid)** — HTTP logging in `_request()` covers 90% of value; lifecycle logs in `client.py` round it out; avoids ~20 file changes for distributed approach
5. **No convenience helper** — consumers use standard `logger.enable("vclient")`; their own handlers control level/format/destination
6. **404 at DEBUG** — often expected (existence checks); not an error condition
7. **Imperative voice** — all log messages use imperative voice per project conventions
