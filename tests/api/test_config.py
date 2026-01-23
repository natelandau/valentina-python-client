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
        """Test that default values are applied."""
        config = APIConfig()
        assert config.base_url == DEFAULT_BASE_URL
        assert config.api_key is None
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.max_retries == DEFAULT_MAX_RETRIES
        assert config.retry_delay == DEFAULT_RETRY_DELAY
        assert config.headers == {}

    def test_custom_values(self):
        """Test that custom values are stored."""
        config = APIConfig(
            base_url="https://custom.api.com",
            api_key="my-key",
            timeout=60.0,
            max_retries=5,
            retry_delay=2.0,
            headers={"X-Custom": "value"},
        )
        assert config.base_url == "https://custom.api.com"
        assert config.api_key == "my-key"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.headers == {"X-Custom": "value"}

    def test_trailing_slash_removed(self):
        """Test that trailing slashes are removed from base_url."""
        config = APIConfig(base_url="https://api.example.com/")
        assert config.base_url == "https://api.example.com"

    def test_multiple_trailing_slashes_removed(self):
        """Test that multiple trailing slashes are removed."""
        config = APIConfig(base_url="https://api.example.com///")
        assert config.base_url == "https://api.example.com"

    def test_no_slash_unchanged(self):
        """Test that URLs without trailing slash are unchanged."""
        config = APIConfig(base_url="https://api.example.com")
        assert config.base_url == "https://api.example.com"
