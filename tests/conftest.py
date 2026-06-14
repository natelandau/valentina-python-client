"""Shared test fixtures."""

import pytest
import pytest_httpx2  # noqa: F401  importing registers respx's "httpcore2" mocker
import respx.mocks

# httpx2 ships its own httpcore fork (httpcore2). respx patches httpcore by module
# path, so its default mocker only intercepts upstream httpx. Point the default mocker
# at pytest-httpx2's "httpcore2" targets so every respx fixture and decorator in the
# suite intercepts httpx2 without per-callsite `using=` changes.
_HTTPX2_MOCKER = "httpcore2"
# Fail loudly at collection if the mocker is missing (e.g. a respx/pytest-httpx2 change):
# a silent fallback to the default "httpcore" mocker would let httpx2 requests escape the
# mock and hit the real network instead of raising here.
if _HTTPX2_MOCKER not in respx.mocks.Mocker.registry:
    msg = (
        f"respx mocker {_HTTPX2_MOCKER!r} is not registered; ensure pytest-httpx2 is "
        "installed so httpx2 requests are intercepted instead of reaching the network."
    )
    raise RuntimeError(msg)
respx.mocks.DEFAULT_MOCKER = _HTTPX2_MOCKER

pytest_plugins = ("tests.shared_response_fixtures",)
pytestmark = pytest.mark.anyio


@pytest.fixture
def api_key() -> str:
    """Return a test API key."""
    return "test-api-key-12345"


@pytest.fixture
def base_url() -> str:
    """Return a test base URL."""
    return "https://api.test.valentina-noir.com"
