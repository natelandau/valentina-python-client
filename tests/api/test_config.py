"""Tests for vclient.api.config."""

from vclient.api.config import APIConfig
from vclient.api.constants import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
)


class TestAPIConfig:
    """Tests for APIConfig dataclass."""

    def test_default_values(self):
        """Verify default values are applied."""
        # When: Creating a config with no arguments
        config = APIConfig()

        # Then: Default values are used
        assert config.base_url == DEFAULT_BASE_URL
        assert config.api_key is None
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.max_retries == DEFAULT_MAX_RETRIES
        assert config.retry_delay == DEFAULT_RETRY_DELAY
        assert config.auto_retry_rate_limit is True
        assert config.headers == {}

    def test_custom_values(self):
        """Verify custom values are stored."""
        # When: Creating a config with custom values
        config = APIConfig(
            base_url="https://custom.api.com",
            api_key="my-key",
            timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
            auto_retry_rate_limit=False,
            headers={"X-Custom": "value"},
        )

        # Then: Custom values are stored
        assert config.base_url == "https://custom.api.com"
        assert config.api_key == "my-key"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.auto_retry_rate_limit is False
        assert config.headers == {"X-Custom": "value"}

    def test_trailing_slash_removed(self):
        """Verify trailing slashes are removed from base_url."""
        # When: Creating a config with trailing slash
        config = APIConfig(base_url="https://api.example.com/")

        # Then: Trailing slash is removed
        assert config.base_url == "https://api.example.com"

    def test_multiple_trailing_slashes_removed(self):
        """Verify multiple trailing slashes are removed."""
        # When: Creating a config with multiple trailing slashes
        config = APIConfig(base_url="https://api.example.com///")

        # Then: All trailing slashes are removed
        assert config.base_url == "https://api.example.com"

    def test_no_slash_unchanged(self):
        """Verify URLs without trailing slash are unchanged."""
        # When: Creating a config without trailing slash
        config = APIConfig(base_url="https://api.example.com")

        # Then: URL is unchanged
        assert config.base_url == "https://api.example.com"
