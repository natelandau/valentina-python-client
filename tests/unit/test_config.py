"""Tests for vclient.api.config."""

import pytest

from vclient.api.config import APIConfig


class TestAPIConfig:
    """Tests for APIConfig dataclass."""

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
            auto_idempotency_keys=True,
            headers={"X-Custom": "value"},
        )

        # Then: Custom values are stored
        assert config.base_url == "https://custom.api.com"
        assert config.api_key == "my-key"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.auto_retry_rate_limit is False
        assert config.auto_idempotency_keys is True
        assert config.headers == {"X-Custom": "value"}

    def test_auto_idempotency_keys_default_false(self):
        """Verify auto_idempotency_keys defaults to False."""
        # When: Creating a config with only required values
        config = APIConfig(base_url="https://api.example.com", api_key="my-key")

        # Then: auto_idempotency_keys defaults to False
        assert config.auto_idempotency_keys is False

    @pytest.mark.parametrize(
        ("input_url", "expected"),
        [
            ("https://api.example.com/", "https://api.example.com"),
            ("https://api.example.com///", "https://api.example.com"),
            ("https://api.example.com", "https://api.example.com"),
        ],
    )
    def test_trailing_slash_normalization(self, input_url, expected):
        """Verify trailing slashes are normalized in base_url."""
        # When: Creating a config with the input URL
        config = APIConfig(base_url=input_url, api_key="my-key")

        # Then: URL is normalized correctly
        assert config.base_url == expected
