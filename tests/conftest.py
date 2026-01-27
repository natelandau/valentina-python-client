"""Shared test fixtures."""

import pytest

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
