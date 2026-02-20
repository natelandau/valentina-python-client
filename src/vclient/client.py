"""Main API client for Valentina."""

import os
import platform
from types import TracebackType
from typing import TYPE_CHECKING, Self

import httpx
from loguru import logger

from vclient.config import _APIConfig
from vclient.constants import (
    API_KEY_HEADER,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_RETRY_STATUSES,
    DEFAULT_TIMEOUT,
    ENV_API_KEY,
    ENV_BASE_URL,
    ENV_DEFAULT_COMPANY_ID,
)

if TYPE_CHECKING:
    from vclient.services import (
        BooksService,
        CampaignsService,
        ChaptersService,
        CharacterAutogenService,
        CharacterBlueprintService,
        CharactersService,
        CharacterTraitsService,
        CompaniesService,
        DeveloperService,
        DicerollService,
        DictionaryService,
        GlobalAdminService,
        OptionsService,
        SystemService,
        UsersService,
    )


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

        # Use scoped services
        users = client.users("company_id")
        all_users = await users.list_all()

        campaigns = client.campaigns("company_id", "user_id")
        all_campaigns = await campaigns.list_all()
        ```
    """

    def __init__(  # noqa: PLR0913
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        auto_retry_rate_limit: bool = True,
        auto_idempotency_keys: bool = False,
        retry_statuses: set[int] | frozenset[int] | None = None,
        default_company_id: str | None = None,
        headers: dict[str, str] | None = None,
        set_as_default: bool = True,
    ) -> None:
        """Initialize the API client.

        Values for ``base_url``, ``api_key``, and ``default_company_id`` can be
        provided as constructor arguments or via environment variables. Explicit
        arguments always take precedence over environment variables.

        Environment variables:
            VALENTINA_CLIENT_BASE_URL: Base URL for the API.
            VALENTINA_CLIENT_API_KEY: API key for authentication.
            VALENTINA_CLIENT_DEFAULT_COMPANY_ID: Default company ID.

        Args:
            base_url: Base URL for the API. Falls back to VALENTINA_CLIENT_BASE_URL.
            api_key: API key for authentication. Falls back to VALENTINA_CLIENT_API_KEY.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
            retry_delay: Base delay between retries in seconds.
            auto_retry_rate_limit: Automatically retry requests that hit rate limits.
            auto_idempotency_keys: Automatically generate idempotency keys for
                POST/PUT/PATCH requests.
            retry_statuses: HTTP status codes that trigger automatic retries.
                Defaults to {429, 500, 502, 503, 504}.
            default_company_id: Default company ID to use when not explicitly provided
                to service factory methods. Falls back to
                VALENTINA_CLIENT_DEFAULT_COMPANY_ID.
            headers: Additional headers to include with all requests.
            set_as_default: If True, register this client as the default for factory
                functions. Set to False when creating multiple clients or when using
                the context manager pattern exclusively.

        Raises:
            ValueError: If base_url or api_key is not provided and the corresponding
                environment variable is not set.
        """
        resolved_base_url = base_url or os.environ.get(ENV_BASE_URL)
        if resolved_base_url is None:
            msg = "base_url is required (set it directly or via the VALENTINA_CLIENT_BASE_URL environment variable)"
            raise ValueError(msg)

        resolved_api_key = api_key or os.environ.get(ENV_API_KEY)
        if resolved_api_key is None:
            msg = "api_key is required (set it directly or via the VALENTINA_CLIENT_API_KEY environment variable)"
            raise ValueError(msg)

        resolved_company_id = default_company_id or os.environ.get(ENV_DEFAULT_COMPANY_ID)

        self._config = _APIConfig(
            base_url=resolved_base_url,
            api_key=resolved_api_key,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            auto_retry_rate_limit=auto_retry_rate_limit,
            auto_idempotency_keys=auto_idempotency_keys,
            retry_statuses=frozenset(retry_statuses)
            if retry_statuses is not None
            else DEFAULT_RETRY_STATUSES,
            default_company_id=resolved_company_id,
            headers=headers or {},
        )

        self._http: httpx.AsyncClient = self._create_http_client()
        self._companies: CompaniesService | None = None
        self._developer: DeveloperService | None = None
        self._global_admin: GlobalAdminService | None = None
        self._system: SystemService | None = None

        if set_as_default:
            from vclient.registry import configure_default_client

            configure_default_client(self)

        logger.bind(
            base_url=self._config.base_url,
            timeout=self._config.timeout,
            max_retries=self._config.max_retries,
        ).info("Initialize VClient")

    def _create_http_client(self) -> httpx.AsyncClient:
        """Create and configure the HTTP client."""
        from vclient import __version__

        user_agent = f"vclient/{__version__} Python/{platform.python_version()}"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": user_agent,
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
        from vclient.registry import clear_default_client

        logger.bind(base_url=self._config.base_url).info("Close VClient")
        await self._http.aclose()
        clear_default_client(self)

    @property
    def is_closed(self) -> bool:
        """Check if the client has been closed."""
        return self._http.is_closed

    @property
    def default_company_id(self) -> str | None:
        """Return the default company ID from config."""
        return self._config.default_company_id

    def _resolve_company_id(self, company_id: str | None) -> str:
        """Resolve company_id, falling back to default if not provided.

        Args:
            company_id: Explicitly provided company ID, or None to use default.

        Returns:
            The resolved company ID.

        Raises:
            ValueError: If no company_id provided and no default configured.
        """
        resolved = company_id or self._config.default_company_id
        if resolved is None:
            msg = "company_id is required (no default_company_id configured)"
            raise ValueError(msg)
        return resolved

    @property
    def companies(self) -> "CompaniesService":
        """Access the Companies service for managing companies.

        Returns:
            The CompaniesService instance for company operations.
        """
        if self._companies is None:
            from vclient.services.companies import CompaniesService

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
            from vclient.services.developers import DeveloperService

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
            from vclient.services.global_admin import GlobalAdminService

            self._global_admin = GlobalAdminService(self)
        return self._global_admin

    @property
    def system(self) -> "SystemService":
        """Access the System service for system-level operations.

        Returns:
            The SystemService instance for system operations like health checks.
        """
        if self._system is None:
            from vclient.services.system import SystemService

            self._system = SystemService(self)
        return self._system

    def users(self, company_id: str | None = None) -> "UsersService":
        """Get a UsersService scoped to a specific company.

        Provides methods to create, retrieve, update, and delete users,
        as well as access user statistics and assets.

        Args:
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Returns:
            A UsersService instance scoped to the specified company.

        Raises:
            ValueError: If no company_id provided and no default configured.

        Example:
            >>> users = client.users("company_id")
            >>> all_users = await users.list_all()
            >>> user = await users.get("user_id")
        """
        from vclient.services.users import UsersService

        return UsersService(self, self._resolve_company_id(company_id))

    def campaigns(self, user_id: str, company_id: str | None = None) -> "CampaignsService":
        """Get a CampaignsService scoped to a specific company and user.

        Provides methods to create, retrieve, update, and delete campaigns,
        as well as access campaign statistics, assets, and notes.

        Args:
            user_id: The ID of the user to operate as.
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Returns:
            A CampaignsService instance scoped to the specified company and user.

        Raises:
            ValueError: If no company_id provided and no default configured.

        Example:
            >>> campaigns = client.campaigns("user_id")
            >>> all_campaigns = await campaigns.list_all()
            >>> campaign = await campaigns.get("campaign_id")
        """
        from vclient.services.campaigns import CampaignsService

        return CampaignsService(self, self._resolve_company_id(company_id), user_id)

    def books(
        self, user_id: str, campaign_id: str, *, company_id: str | None = None
    ) -> "BooksService":
        """Get a BooksService scoped to a specific company, user, and campaign.

        Provides methods to create, retrieve, update, and delete campaign books,
        as well as access book notes and assets.

        Args:
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Returns:
            A BooksService instance scoped to the specified context.

        Raises:
            ValueError: If no company_id provided and no default configured.

        Example:
            >>> books = client.books("user_id", "campaign_id")
            >>> all_books = await books.list_all()
            >>> book = await books.get("book_id")
        """
        from vclient.services.campaign_books import BooksService

        return BooksService(self, self._resolve_company_id(company_id), user_id, campaign_id)

    def chapters(
        self, user_id: str, campaign_id: str, book_id: str, *, company_id: str | None = None
    ) -> "ChaptersService":
        """Get a ChaptersService scoped to a specific company, user, campaign, and book.

        Provides methods to create, retrieve, update, and delete campaign book chapters,
        as well as access chapter notes and assets.

        Args:
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.
            book_id: The ID of the book to operate within.
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Returns:
            A ChaptersService instance scoped to the specified context.

        Raises:
            ValueError: If no company_id provided and no default configured.

        Example:
            >>> chapters = client.chapters("user_id", "campaign_id", "book_id")
            >>> all_chapters = await chapters.list_all()
            >>> chapter = await chapters.get("chapter_id")
        """
        from vclient.services.campaign_book_chapters import ChaptersService

        return ChaptersService(
            self, self._resolve_company_id(company_id), user_id, campaign_id, book_id
        )

    def characters(
        self, user_id: str, campaign_id: str, *, company_id: str | None = None
    ) -> "CharactersService":
        """Get a CharactersService scoped to a specific company, user, and campaign.

        Provides methods to create, retrieve, update, and delete characters within
        a campaign.

        Args:
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Returns:
            A CharactersService instance scoped to the specified context.

        Raises:
            ValueError: If no company_id provided and no default configured.

        Example:
            >>> characters = client.characters("user_id", "campaign_id")
            >>> all_characters = await characters.list_all()
            >>> character = await characters.get("character_id")
        """
        from vclient.services.characters import CharactersService

        return CharactersService(self, self._resolve_company_id(company_id), user_id, campaign_id)

    def character_traits(
        self,
        user_id: str,
        campaign_id: str,
        character_id: str,
        *,
        company_id: str | None = None,
    ) -> "CharacterTraitsService":
        """Get a CharacterTraitsService scoped to a specific company, user, campaign, and character.

        Provides methods to create, retrieve, update, and delete character traits within
        a character.

        Args:
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.
            character_id: The ID of the character to operate within.
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Returns:
            A CharacterTraitsService instance scoped to the specified context.

        Raises:
            ValueError: If no company_id provided and no default configured.

        Example:
            >>> character_traits = client.character_traits("user_id", "campaign_id", "character_id")
            >>> all_character_traits = await character_traits.list_all()
            >>> character_trait = await character_traits.get("character_trait_id")
        """
        from vclient.services.character_traits import CharacterTraitsService

        return CharacterTraitsService(
            self, self._resolve_company_id(company_id), user_id, campaign_id, character_id
        )

    def character_blueprint(self, company_id: str | None = None) -> "CharacterBlueprintService":
        """Get a CharacterBlueprintService scoped to a specific company.

        Provides methods to create, retrieve, update, and delete character blueprint sections,
        categories, traits, and edges.

        Args:
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Raises:
            ValueError: If no company_id provided and no default configured.
        """
        from vclient.services.character_blueprint import CharacterBlueprintService

        return CharacterBlueprintService(self, self._resolve_company_id(company_id))

    def dictionary(self, company_id: str | None = None) -> "DictionaryService":
        """Get a DictionaryService scoped to a specific company.

        Provides methods to create, retrieve, update, and delete dictionary terms.

        Args:
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Raises:
            ValueError: If no company_id provided and no default configured.
        """
        from vclient.services.dictionary import DictionaryService

        return DictionaryService(self, self._resolve_company_id(company_id))

    def dicerolls(self, user_id: str, company_id: str | None = None) -> "DicerollService":
        """Get a DicerollService scoped to a specific company and user.

        Provides methods to create, retrieve, and list dice rolls.

        Args:
            user_id: The ID of the user to operate as.
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Raises:
            ValueError: If no company_id provided and no default configured.
        """
        from vclient.services.dicerolls import DicerollService

        return DicerollService(self, self._resolve_company_id(company_id), user_id)

    def options(self, company_id: str | None = None) -> "OptionsService":
        """Get a OptionsService scoped to a specific company.

        Provides methods to retrieve all options and enumerations for the api.

        Args:
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Raises:
            ValueError: If no company_id provided and no default configured.
        """
        from vclient.services.options import OptionsService

        return OptionsService(self, self._resolve_company_id(company_id))

    def character_autogen(
        self, user_id: str, campaign_id: str, *, company_id: str | None = None
    ) -> "CharacterAutogenService":
        """Get a CharacterAutogenService scoped to a specific company, user, and campaign.

        Provides methods to create, retrieve, update, and delete character autogen.

        Args:
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.
            company_id: The ID of the company to operate within. If not provided,
                uses the default_company_id from config.

        Raises:
            ValueError: If no company_id provided and no default configured.
        """
        from vclient.services.character_autogen import CharacterAutogenService

        return CharacterAutogenService(
            self, self._resolve_company_id(company_id), user_id, campaign_id
        )
