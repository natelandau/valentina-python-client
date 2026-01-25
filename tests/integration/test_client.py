"""Tests for vclient.api.client."""

import pytest

from vclient.api import APIConfig, VClient
from vclient.api.constants import API_KEY_HEADER

pytestmark = pytest.mark.anyio


class TestVClientInit:
    """Tests for VClient initialization."""

    def test_init_with_base_url_and_api_key(self):
        """Verify client initialization with custom base_url and api_key."""
        # When: Creating a client with custom values
        client = VClient(base_url="https://custom.api.com", api_key="my-key")

        # Then: Custom values are stored
        assert client._config.base_url == "https://custom.api.com"
        assert client._config.api_key == "my-key"

    def test_init_with_config(self):
        """Verify client initialization with APIConfig."""
        # Given: A custom API configuration
        config = APIConfig(
            base_url="https://config.api.com",
            api_key="config-key",
            timeout=60.0,
        )

        # When: Creating a client with the config
        client = VClient(config=config)

        # Then: Config values are used
        assert client._config.base_url == "https://config.api.com"
        assert client._config.api_key == "config-key"
        assert client._config.timeout == 60.0

    def test_config_overrides_other_params(self):
        """Verify config parameter takes precedence over other parameters."""
        # Given: A custom API configuration
        config = APIConfig(base_url="https://config.api.com", api_key="config-key")

        # When: Creating a client with both config and explicit params
        client = VClient(
            base_url="https://ignored.com",
            api_key="ignored-key",
            config=config,
        )

        # Then: Config values take precedence
        assert client._config.base_url == "https://config.api.com"
        assert client._config.api_key == "config-key"

    def test_auto_idempotency_keys_default_false(self):
        """Verify auto_idempotency_keys defaults to False."""
        # When: Creating a client without specifying auto_idempotency_keys
        client = VClient(base_url="https://test.api.com", api_key="my-key")

        # Then: auto_idempotency_keys defaults to False
        assert client._config.auto_idempotency_keys is False

    def test_auto_idempotency_keys_passed_to_config(self):
        """Verify auto_idempotency_keys parameter is passed to config."""
        # When: Creating a client with auto_idempotency_keys enabled
        client = VClient(
            base_url="https://test.api.com",
            api_key="my-key",
            auto_idempotency_keys=True,
        )

        # Then: Config has auto_idempotency_keys enabled
        assert client._config.auto_idempotency_keys is True


class TestVClientHTTPClient:
    """Tests for VClient HTTP client configuration."""

    def test_http_client_configuration(self):
        """Verify HTTP client is properly configured with URL, headers, and API key."""
        # When: Creating a client
        client = VClient(base_url="https://test.api.com", api_key="my-key")

        # Then: HTTP client has correct base URL
        assert str(client._http.base_url) == "https://test.api.com"

        # And: HTTP client headers include the API key
        assert client._http.headers.get(API_KEY_HEADER) == "my-key"

        # And: HTTP client has JSON headers
        assert client._http.headers.get("Accept") == "application/json"
        assert client._http.headers.get("Content-Type") == "application/json"

    def test_http_client_requires_api_key(self):
        """Verify creating a client without an API key raises ValueError."""
        # When: Creating a client without an API key
        with pytest.raises(ValueError):
            VClient(base_url="https://test.api.com", api_key=None)


class TestVClientContextManager:
    """Tests for VClient async context manager."""

    async def test_context_manager_enter(self):
        """Verify entering the context manager returns the client."""
        # When: Using client as async context manager
        async with VClient(base_url="https://test.api.com", api_key="my-key") as client:
            # Then: Client is returned and is open
            assert isinstance(client, VClient)
            assert not client.is_closed

    async def test_context_manager_exit_closes_client(self):
        """Verify exiting the context manager closes the client."""
        # When: Exiting the context manager
        async with VClient(base_url="https://test.api.com", api_key="my-key") as client:
            pass

        # Then: Client is closed
        assert client.is_closed

    async def test_close_method(self):
        """Verify close method properly closes the client."""
        # Given: An open client
        client = VClient(base_url="https://test.api.com", api_key="my-key")
        assert not client.is_closed

        # When: Calling close
        await client.close()

        # Then: Client is closed
        assert client.is_closed

    async def test_is_closed_property(self):
        """Verify is_closed property reflects client state."""
        # Given: An open client
        client = VClient(base_url="https://test.api.com", api_key="my-key")

        # Then: is_closed is False when open
        assert client.is_closed is False

        # When: Closing the client
        await client.close()

        # Then: is_closed is True when closed
        assert client.is_closed is True
