"""Main API client for Valentina."""

from types import TracebackType
from typing import TYPE_CHECKING, Self

import httpx

from vclient.config import APIConfig
from vclient.constants import API_KEY_HEADER

if TYPE_CHECKING:
    from vclient.services import (
        BooksService,
        CampaignsService,
        ChaptersService,
        CharacterBlueprintService,
        CharactersService,
        CharacterTraitsService,
        CompaniesService,
        DeveloperService,
        GlobalAdminService,
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

        if set_as_default:
            from vclient.registry import configure_default_client

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

    def users(self, company_id: str) -> "UsersService":
        """Get a UsersService scoped to a specific company.

        Provides methods to create, retrieve, update, and delete users,
        as well as access user statistics and assets.

        Args:
            company_id: The ID of the company to operate within.

        Returns:
            A UsersService instance scoped to the specified company.

        Example:
            >>> users = client.users("company_id")
            >>> all_users = await users.list_all()
            >>> user = await users.get("user_id")
        """
        from vclient.services.users import UsersService

        return UsersService(self, company_id)

    def campaigns(self, company_id: str, user_id: str) -> "CampaignsService":
        """Get a CampaignsService scoped to a specific company and user.

        Provides methods to create, retrieve, update, and delete campaigns,
        as well as access campaign statistics, assets, and notes.

        Args:
            company_id: The ID of the company to operate within.
            user_id: The ID of the user to operate as.

        Returns:
            A CampaignsService instance scoped to the specified company and user.

        Example:
            >>> campaigns = client.campaigns("company_id", "user_id")
            >>> all_campaigns = await campaigns.list_all()
            >>> campaign = await campaigns.get("campaign_id")
        """
        from vclient.services.campaigns import CampaignsService

        return CampaignsService(self, company_id, user_id)

    def books(self, company_id: str, user_id: str, campaign_id: str) -> "BooksService":
        """Get a BooksService scoped to a specific company, user, and campaign.

        Provides methods to create, retrieve, update, and delete campaign books,
        as well as access book notes and assets.

        Args:
            company_id: The ID of the company to operate within.
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.

        Returns:
            A BooksService instance scoped to the specified context.

        Example:
            >>> books = client.books("company_id", "user_id", "campaign_id")
            >>> all_books = await books.list_all()
            >>> book = await books.get("book_id")
        """
        from vclient.services.campaign_books import BooksService

        return BooksService(self, company_id, user_id, campaign_id)

    def chapters(
        self, company_id: str, user_id: str, campaign_id: str, book_id: str
    ) -> "ChaptersService":
        """Get a ChaptersService scoped to a specific company, user, campaign, and book.

        Provides methods to create, retrieve, update, and delete campaign book chapters,
        as well as access chapter notes and assets.

        Args:
            company_id: The ID of the company to operate within.
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.
            book_id: The ID of the book to operate within.

        Returns:
            A ChaptersService instance scoped to the specified context.

        Example:
            >>> chapters = client.chapters("company_id", "user_id", "campaign_id", "book_id")
            >>> all_chapters = await chapters.list_all()
            >>> chapter = await chapters.get("chapter_id")
        """
        from vclient.services.campaign_book_chapters import ChaptersService

        return ChaptersService(self, company_id, user_id, campaign_id, book_id)

    def characters(self, company_id: str, user_id: str, campaign_id: str) -> "CharactersService":
        """Get a CharactersService scoped to a specific company, user, and campaign.

        Provides methods to create, retrieve, update, and delete characters within
        a campaign.

        Args:
            company_id: The ID of the company to operate within.
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.

        Returns:
            A CharactersService instance scoped to the specified context.

        Example:
            >>> characters = client.characters("company_id", "user_id", "campaign_id")
            >>> all_characters = await characters.list_all()
            >>> character = await characters.get("character_id")
        """
        from vclient.services.characters import CharactersService

        return CharactersService(self, company_id, user_id, campaign_id)

    def character_traits(
        self, company_id: str, user_id: str, campaign_id: str, character_id: str
    ) -> "CharacterTraitsService":
        """Get a CharacterTraitsService scoped to a specific company, user, campaign, and character.

        Provides methods to create, retrieve, update, and delete character traits within
        a character.

        Args:
            company_id: The ID of the company to operate within.
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.
            character_id: The ID of the character to operate within.

        Returns:
            A CharacterTraitsService instance scoped to the specified context.

        Example:
            >>> character_traits = client.character_traits("company_id", "user_id", "campaign_id", "character_id")
            >>> all_character_traits = await character_traits.list_all()
            >>> character_trait = await character_traits.get("character_trait_id")
        """
        from vclient.services.character_traits import CharacterTraitsService

        return CharacterTraitsService(self, company_id, user_id, campaign_id, character_id)

    def character_blueprint(self, company_id: str) -> "CharacterBlueprintService":
        """Get a CharacterBlueprintService scoped to a specific company.

        Provides methods to create, retrieve, update, and delete character blueprint sections,
        categories, traits, and edges.

        Args:
            company_id: The ID of the company to operate within.
        """
        from vclient.services.character_blueprint import CharacterBlueprintService

        return CharacterBlueprintService(self, company_id)
