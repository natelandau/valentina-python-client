"""Tests for vclient.api.client."""

import pytest

from vclient.api import APIConfig, VClient
from vclient.api.constants import API_KEY_HEADER, DEFAULT_BASE_URL

pytestmark = pytest.mark.anyio


class TestVClientInit:
    """Tests for VClient initialization."""

    def test_init_with_defaults(self):
        """Test client initialization with default values."""
        client = VClient()
        assert client._config.base_url == DEFAULT_BASE_URL
        assert client._config.api_key is None

    def test_init_with_base_url_and_api_key(self):
        """Test client initialization with custom base_url and api_key."""
        client = VClient(base_url="https://custom.api.com", api_key="my-key")
        assert client._config.base_url == "https://custom.api.com"
        assert client._config.api_key == "my-key"

    def test_init_with_config(self):
        """Test client initialization with APIConfig."""
        config = APIConfig(
            base_url="https://config.api.com",
            api_key="config-key",
            timeout=60.0,
        )
        client = VClient(config=config)
        assert client._config.base_url == "https://config.api.com"
        assert client._config.api_key == "config-key"
        assert client._config.timeout == 60.0

    def test_config_overrides_other_params(self):
        """Test that config parameter takes precedence."""
        config = APIConfig(base_url="https://config.api.com", api_key="config-key")
        client = VClient(
            base_url="https://ignored.com",
            api_key="ignored-key",
            config=config,
        )
        assert client._config.base_url == "https://config.api.com"
        assert client._config.api_key == "config-key"


class TestVClientHTTPClient:
    """Tests for VClient HTTP client configuration."""

    def test_http_client_has_correct_base_url(self):
        """Test that HTTP client is configured with correct base URL."""
        client = VClient(base_url="https://test.api.com")
        assert str(client._http.base_url) == "https://test.api.com"

    def test_http_client_has_api_key_header(self):
        """Test that HTTP client includes API key header."""
        client = VClient(base_url="https://test.api.com", api_key="my-key")
        assert client._http.headers.get(API_KEY_HEADER) == "my-key"

    def test_http_client_has_json_headers(self):
        """Test that HTTP client has JSON content type headers."""
        client = VClient()
        assert client._http.headers.get("Accept") == "application/json"
        assert client._http.headers.get("Content-Type") == "application/json"

    def test_http_client_no_api_key_header_when_none(self):
        """Test that no API key header is set when api_key is None."""
        client = VClient(base_url="https://test.api.com", api_key=None)
        assert API_KEY_HEADER not in client._http.headers


class TestVClientContextManager:
    """Tests for VClient async context manager."""

    async def test_context_manager_enter(self):
        """Test entering the context manager returns the client."""
        async with VClient() as client:
            assert isinstance(client, VClient)
            assert not client.is_closed

    async def test_context_manager_exit_closes_client(self):
        """Test exiting the context manager closes the client."""
        async with VClient() as client:
            pass
        assert client.is_closed

    async def test_close_method(self):
        """Test the close method properly closes the client."""
        client = VClient()
        assert not client.is_closed
        await client.close()
        assert client.is_closed

    async def test_is_closed_property(self):
        """Test the is_closed property reflects client state."""
        client = VClient()
        assert client.is_closed is False
        await client.close()
        assert client.is_closed is True
