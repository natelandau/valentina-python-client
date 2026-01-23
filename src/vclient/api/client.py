"""Main API client for Valentina."""

from types import TracebackType
from typing import TYPE_CHECKING, Self

import httpx

from vclient.api.config import APIConfig
from vclient.api.constants import API_KEY, API_KEY_HEADER, DEFAULT_BASE_URL

if TYPE_CHECKING:
    from vclient.api.services.companies import CompaniesService
    from vclient.api.services.global_admin import GlobalAdminService
    from vclient.api.services.system import SystemService


class VClient:
    """Async API client for the Valentina API.

    This is the main entry point for interacting with the API. It manages
    the HTTP session and provides access to domain-specific services.

    Example:
        ```python
        async with VClient(base_url="https://api.example.com", api_key="...") as client:
            # Use services here
            pass
        ```
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        *,
        timeout: float = 30.0,
        config: APIConfig | None = None,
    ) -> None:
        """Initialize the API client.

        Args:
            base_url: Base URL for the API. Defaults to DEFAULT_BASE_URL.
            api_key: API key for authentication. Falls back to API_KEY constant.
            timeout: Request timeout in seconds.
            config: Optional APIConfig instance (overrides other parameters).
        """
        if config is not None:
            self._config = config
        else:
            self._config = APIConfig(
                base_url=base_url or DEFAULT_BASE_URL,
                api_key=api_key or API_KEY,
                timeout=timeout,
            )

        self._http: httpx.AsyncClient = self._create_http_client()
        self._companies: CompaniesService | None = None
        self._global_admin: GlobalAdminService | None = None
        self._system: SystemService | None = None

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
