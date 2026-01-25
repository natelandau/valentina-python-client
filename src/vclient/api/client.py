"""Main API client for Valentina."""

from types import TracebackType
from typing import TYPE_CHECKING, Self

import httpx

from vclient.api.config import APIConfig
from vclient.api.constants import API_KEY_HEADER

if TYPE_CHECKING:
    from vclient.api.services.companies import CompaniesService
    from vclient.api.services.developers import DeveloperService
    from vclient.api.services.global_admin import GlobalAdminService
    from vclient.api.services.system import SystemService
    from vclient.api.services.users import UsersService


class VClient:
    """Async API client for the Valentina API.

    This is the main entry point for interacting with the API. It manages
    the HTTP session and provides access to domain-specific services.

    By default, the client automatically registers itself as the default client
    for use with factory functions like `companies_service()`.

    Example:
        ```python
        from vclient import VClient, companies_service

        # Client auto-registers as default
        client = VClient(api_key="...")

        # Use factory functions from any module
        companies = companies_service()
        all_companies = await companies.list_all()
        ```
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        *,
        timeout: float = 30.0,
        auto_idempotency_keys: bool = False,
        config: APIConfig | None = None,
        set_as_default: bool = True,
    ) -> None:
        """Initialize the API client.

        Args:
            base_url: Base URL for the API.
            api_key: API key for authentication.
            timeout: Request timeout in seconds.
            auto_idempotency_keys: Automatically generate idempotency keys for
                POST/PUT/PATCH requests. Defaults to False.
            config: Optional APIConfig instance (overrides other parameters).
            set_as_default: If True, register this client as the default for factory
                functions. Set to False when creating multiple clients or when using
                the context manager pattern exclusively.
        """
        if config is not None:
            self._config = config
        else:
            if base_url is None:
                msg = "base_url is required"
                raise ValueError(msg)
            if api_key is None:
                msg = "api_key is required"
                raise ValueError(msg)

            self._config = APIConfig(
                base_url=base_url,
                api_key=api_key,
                timeout=timeout,
                auto_idempotency_keys=auto_idempotency_keys,
            )

        self._http: httpx.AsyncClient = self._create_http_client()
        self._companies: CompaniesService | None = None
        self._developer: DeveloperService | None = None
        self._global_admin: GlobalAdminService | None = None
        self._system: SystemService | None = None
        self._users: UsersService | None = None

        if set_as_default:
            from vclient.api.registry import configure_default_client

            configure_default_client(self)

    def _create_http_client(self) -> httpx.AsyncClient:
        """Create and configure the HTTP client."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **self._config.headers,
        }

        if self._config.api_key:
            headers[API_KEY_HEADER] = self._config.api_key

        return httpx.AsyncClient(
            base_url=self._config.base_url,
            headers=headers,
            timeout=httpx.Timeout(self._config.timeout),
        )

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context manager."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._http.aclose()

    @property
    def is_closed(self) -> bool:
        """Check if the client has been closed."""
        return self._http.is_closed

    @property
    def companies(self) -> "CompaniesService":
        """Access the Companies service for managing companies.

        Returns:
            The CompaniesService instance for company operations.
        """
        if self._companies is None:
            from vclient.api.services.companies import CompaniesService

            self._companies = CompaniesService(self)
        return self._companies

    @property
    def developer(self) -> "DeveloperService":
        """Access the Developer service for managing your own profile.

        Provides methods to view and update your developer account,
        as well as regenerate your API key.

        Returns:
            The DeveloperService instance for self-service operations.
        """
        if self._developer is None:
            from vclient.api.services.developers import DeveloperService

            self._developer = DeveloperService(self)
        return self._developer

    @property
    def global_admin(self) -> "GlobalAdminService":
        """Access the Global Admin service for managing developers.

        Requires global admin privileges. Operations will fail with AuthorizationError
        if the authenticated developer does not have global admin status.

        Returns:
            The GlobalAdminService instance for developer management operations.
        """
        if self._global_admin is None:
            from vclient.api.services.global_admin import GlobalAdminService

            self._global_admin = GlobalAdminService(self)
        return self._global_admin

    @property
    def system(self) -> "SystemService":
        """Access the System service for system-level operations.

        Returns:
            The SystemService instance for system operations like health checks.
        """
        if self._system is None:
            from vclient.api.services.system import SystemService

            self._system = SystemService(self)
        return self._system

    @property
    def users(self) -> "UsersService":
        """Access the Users service for managing users within companies.

        Provides methods to create, retrieve, update, and delete users,
        as well as access user statistics and assets.

        Returns:
            The UsersService instance for user management operations.
        """
        if self._users is None:
            from vclient.api.services.users import UsersService

            self._users = UsersService(self)
        return self._users
