"""Default client registry and service factory functions.

This module provides a way to access services from any module without passing
the client explicitly. VClient automatically registers itself as the default
when instantiated (unless `set_as_default=False` is passed).

Example:
    ```python
    from vclient import VClient, companies_service

    # Client auto-registers as default
    client = VClient(api_key="...")

    # Use services anywhere
    async def some_function():
        companies = companies_service()
        return await companies.list_all()
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vclient.client import VClient
    from vclient.services import (
        BooksService,
        CampaignsService,
        ChaptersService,
        CharacterBlueprintService,
        CharactersService,
        CharacterTraitsService,
        CompaniesService,
        DeveloperService,
        DicreollService,
        DictionaryService,
        GlobalAdminService,
        SystemService,
        UsersService,
    )

_default_client: "VClient | None" = None


def configure_default_client(client: "VClient") -> None:
    """Configure the default client for service factory functions.

    Note: This is called automatically when VClient is instantiated (unless
    `set_as_default=False` is passed). You typically don't need to call this
    directly unless you're switching between multiple clients.

    Args:
        client (VClient): The configured VClient instance to use as the default.

    Example:
        ```python
        # Switch to a different client
        client2 = VClient(api_key="other-key", set_as_default=False)
        configure_default_client(client2)
        ```
    """
    global _default_client  # noqa: PLW0603
    _default_client = client


def default_client() -> "VClient":
    """Retrieve the configured default client.

    Use this when you need direct access to the VClient instance that was
    configured via `configure_default_client()`.

    Returns:
        VClient: The configured default client instance.

    Raises:
        RuntimeError: If no default client has been configured.
    """
    if _default_client is None:
        msg = "No default client configured. Call configure_default_client() first."
        raise RuntimeError(msg)
    return _default_client


def companies_service() -> "CompaniesService":
    """Create a CompaniesService using the default client.

    Provides access to company management operations (list, get, create, update, delete)
    without needing to pass a client instance.

    Returns:
        CompaniesService: A service instance for company operations.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        companies = companies_service()
        all_companies = await companies.list_all()
        ```
    """
    from vclient.services.companies import CompaniesService

    return CompaniesService(default_client())


def developer_service() -> "DeveloperService":
    """Create a DeveloperService using the default client.

    Provides access to self-service developer operations (view profile, update profile,
    regenerate API key) without needing to pass a client instance.

    Returns:
        DeveloperService: A service instance for developer self-service operations.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        developer = developer_service()
        me = await developer.get_me()
        ```
    """
    from vclient.services.developers import DeveloperService

    return DeveloperService(default_client())


def global_admin_service() -> "GlobalAdminService":
    """Create a GlobalAdminService using the default client.

    Provides access to global admin operations (developer management, API keys)
    without needing to pass a client instance. Requires global admin privileges.

    Returns:
        GlobalAdminService: A service instance for global admin operations.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        admins = global_admin_service()
        developers = await admins.list_all()
        ```
    """
    from vclient.services.global_admin import GlobalAdminService

    return GlobalAdminService(default_client())


def system_service() -> "SystemService":
    """Create a SystemService using the default client.

    Provides access to system-level operations (health checks, status)
    without needing to pass a client instance.

    Returns:
        SystemService: A service instance for system operations.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        system = system_service()
        health = await system.health()
        ```
    """
    from vclient.services.system import SystemService

    return SystemService(default_client())


def users_service(company_id: str) -> "UsersService":
    """Create a UsersService scoped to a specific company using the default client.

    Provides access to user management operations (list, get, create, update, delete)
    within a specific company without needing to pass a client instance.

    Args:
        company_id: The ID of the company to operate within.

    Returns:
        UsersService: A service instance scoped to the specified company.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        users = users_service("company_id")
        all_users = await users.list_all()
        user = await users.get("user_id")
        ```
    """
    from vclient.services.users import UsersService

    return UsersService(default_client(), company_id)


def campaigns_service(company_id: str, user_id: str) -> "CampaignsService":
    """Create a CampaignsService scoped to a specific company and user.

    Provides access to campaign management operations (list, get, create, update, delete)
    within a specific company and user context without needing to pass a client instance.

    Args:
        company_id: The ID of the company to operate within.
        user_id: The ID of the user to operate as.

    Returns:
        CampaignsService: A service instance scoped to the specified company and user.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        campaigns = campaigns_service("company_id", "user_id")
        all_campaigns = await campaigns.list_all()
        campaign = await campaigns.get("campaign_id")
        ```
    """
    from vclient.services.campaigns import CampaignsService

    return CampaignsService(default_client(), company_id, user_id)


def books_service(company_id: str, user_id: str, campaign_id: str) -> "BooksService":
    """Create a BooksService scoped to a specific company, user, and campaign.

    Provides access to campaign book management operations (list, get, create, update, delete)
    within a specific company, user, and campaign context without needing to pass a client instance.

    Args:
        company_id: The ID of the company to operate within.
        user_id: The ID of the user to operate as.
        campaign_id: The ID of the campaign to operate within.

    Returns:
        BooksService: A service instance scoped to the specified context.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        books = books_service("company_id", "user_id", "campaign_id")
        all_books = await books.list_all()
        book = await books.get("book_id")
        ```
    """
    from vclient.services.campaign_books import BooksService

    return BooksService(default_client(), company_id, user_id, campaign_id)


def chapters_service(
    company_id: str, user_id: str, campaign_id: str, book_id: str
) -> "ChaptersService":
    """Create a ChaptersService scoped to a specific company, user, campaign, and book.

    Provides access to campaign book chapter management operations (list, get, create, update, delete)
    within a specific company, user, campaign, and book context without needing to pass a client instance.
    """
    from vclient.services.campaign_book_chapters import ChaptersService

    return ChaptersService(default_client(), company_id, user_id, campaign_id, book_id)


def characters_service(company_id: str, user_id: str, campaign_id: str) -> "CharactersService":
    """Create a CharactersService scoped to a specific company, user, and campaign.

    Provides access to character management operations (list, get, create, update, delete)
    within a specific company, user, and campaign context without needing to pass a client instance.
    """
    from vclient.services.characters import CharactersService

    return CharactersService(default_client(), company_id, user_id, campaign_id)


def character_traits_service(
    company_id: str, user_id: str, campaign_id: str, character_id: str
) -> "CharacterTraitsService":
    """Create a CharacterTraitsService scoped to a specific company, user, campaign, and character.

    Provides access to character trait management operations (list, get, create, update, delete)
    within a specific company, user, campaign, and character context without needing to pass a client instance.
    """
    from vclient.services.character_traits import CharacterTraitsService

    return CharacterTraitsService(default_client(), company_id, user_id, campaign_id, character_id)


def character_blueprint_service(company_id: str) -> "CharacterBlueprintService":
    """Create a CharacterBlueprintService scoped to a specific company.

    Provides access to character blueprint management operations (list, get, create, update, delete)
    within a specific company context without needing to pass a client instance.
    """
    from vclient.services.character_blueprint import CharacterBlueprintService

    return CharacterBlueprintService(default_client(), company_id)


def dictionary_service(company_id: str) -> "DictionaryService":
    """Create a DictionaryService scoped to a specific company.

    Provides access to dictionary term management operations (list, get, create, update, delete)
    within a specific company context without needing to pass a client instance.
    """
    from vclient.services.dictionary import DictionaryService

    return DictionaryService(default_client(), company_id)


def dicreolls_service(company_id: str, user_id: str) -> "DicreollService":
    """Create a DicreollService scoped to a specific company and user.

    Provides access to dicreoll management operations (list, get, create, update, delete)
    within a specific company and user context without needing to pass a client instance.
    """
    from vclient.services.diecrolls import DicreollService

    return DicreollService(default_client(), company_id, user_id)
