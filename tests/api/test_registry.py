"""Tests for the registry module."""

import pytest

from vclient.api import VClient
from vclient.api.registry import (
    companies_service,
    configure_default_client,
    default_client,
    global_admin_service,
    system_service,
)
from vclient.api.services.companies import CompaniesService
from vclient.api.services.global_admin import GlobalAdminService
from vclient.api.services.system import SystemService


@pytest.fixture(autouse=True)
def reset_default_client():
    """Reset the default client before and after each test."""
    # Given: Clear any existing default client
    from vclient.api import registry

    registry._default_client = None
    yield
    # Then: Clean up after test
    registry._default_client = None


class TestConfigureDefaultClient:
    """Tests for configure_default_client function."""

    def test_configure_default_client_stores_client(self, api_config) -> None:
        """Verify configure_default_client stores the client in module state."""
        # Given: A VClient instance
        client = VClient(config=api_config)

        # When: Configuring the default client
        configure_default_client(client)

        # Then: The client is stored
        from vclient.api import registry

        assert registry._default_client is client

    def test_configure_default_client_overwrites_previous(self, api_config) -> None:
        """Verify configure_default_client overwrites a previously configured client."""
        # Given: Two VClient instances
        client1 = VClient(config=api_config)
        client2 = VClient(config=api_config)

        # When: Configuring the first, then the second
        configure_default_client(client1)
        configure_default_client(client2)

        # Then: The second client is stored
        from vclient.api import registry

        assert registry._default_client is client2


class TestDefaultClient:
    """Tests for default_client function."""

    def test_default_client_raises_when_not_configured(self) -> None:
        """Verify default_client raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling default_client raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            default_client()

    def test_default_client_returns_configured_client(self, api_config) -> None:
        """Verify default_client returns the configured client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the default client
        result = default_client()

        # Then: The configured client is returned
        assert result is client


class TestCompaniesService:
    """Tests for companies_service factory function."""

    def test_companies_service_raises_when_not_configured(self) -> None:
        """Verify companies_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling companies_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            companies_service()

    def test_companies_service_returns_service_instance(self, api_config) -> None:
        """Verify companies_service returns a CompaniesService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the companies service
        service = companies_service()

        # Then: A CompaniesService is returned with the correct client
        assert isinstance(service, CompaniesService)
        assert service._client is client


class TestGlobalAdminService:
    """Tests for global_admin_service factory function."""

    def test_global_admin_service_raises_when_not_configured(self) -> None:
        """Verify global_admin_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling global_admin_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            global_admin_service()

    def test_global_admin_service_returns_service_instance(self, api_config) -> None:
        """Verify global_admin_service returns a GlobalAdminService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the global admin service
        service = global_admin_service()

        # Then: A GlobalAdminService is returned with the correct client
        assert isinstance(service, GlobalAdminService)
        assert service._client is client


class TestSystemService:
    """Tests for system_service factory function."""

    def test_system_service_raises_when_not_configured(self) -> None:
        """Verify system_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling system_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            system_service()

    def test_system_service_returns_service_instance(self, api_config) -> None:
        """Verify system_service returns a SystemService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the system service
        service = system_service()

        # Then: A SystemService is returned with the correct client
        assert isinstance(service, SystemService)
        assert service._client is client


class TestTopLevelImports:
    """Tests for top-level package imports."""

    def test_imports_from_vclient(self) -> None:
        """Verify factory functions are importable from vclient package."""
        # When: Importing from vclient
        from vclient import (
            companies_service,
            configure_default_client,
            default_client,
            global_admin_service,
            system_service,
        )

        # Then: All functions are callable
        assert callable(configure_default_client)
        assert callable(default_client)
        assert callable(companies_service)
        assert callable(global_admin_service)
        assert callable(system_service)

    def test_imports_from_vclient_api(self) -> None:
        """Verify factory functions are importable from vclient.api package."""
        # When: Importing from vclient.api
        from vclient.api import (
            companies_service,
            configure_default_client,
            default_client,
            global_admin_service,
            system_service,
        )

        # Then: All functions are callable
        assert callable(configure_default_client)
        assert callable(default_client)
        assert callable(companies_service)
        assert callable(global_admin_service)
        assert callable(system_service)
