"""Unit test fixtures."""

import pytest

from vclient import APIConfig


@pytest.fixture
def api_config(base_url, api_key) -> APIConfig:
    """Return a test API configuration."""
    return APIConfig(
        base_url=base_url,
        api_key=api_key,
        timeout=10.0,
    )
