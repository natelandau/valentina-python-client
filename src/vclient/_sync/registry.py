# AUTO-GENERATED — do not edit. Run 'uv run duty generate_sync' to regenerate.
"""Default client registry and service factory functions.

This module provides a way to access services from any module without passing
the client explicitly. SyncVClient automatically registers itself as the default
when instantiated (unless `set_as_default=False` is passed).

Example:
    ```python
    from vclient import SyncVClient, sync_companies_service

    # Client auto-registers as default
    client = SyncVClient(api_key="...")

    # Use services anywhere
    async def some_function():
        companies = sync_companies_service()
        return await companies.list_all()
    ```
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vclient._sync.client import SyncVClient
    from vclient._sync.services import (
        SyncBooksService,
        SyncCampaignsService,
        SyncChaptersService,
        SyncCharacterAutogenService,
        SyncCharacterBlueprintService,
        SyncCharactersService,
        SyncCharacterTraitsService,
        SyncCompaniesService,
        SyncDeveloperService,
        SyncDicerollService,
        SyncDictionaryService,
        SyncGlobalAdminService,
        SyncOptionsService,
        SyncSystemService,
        SyncUsersService,
    )
_default_client: "SyncVClient | None" = None


def sync_configure_default_client(client: "SyncVClient") -> None:
    """Configure the default client for service factory functions.

    Note: This is called automatically when SyncVClient is instantiated (unless
    `set_as_default=False` is passed). You typically don't need to call this
    directly unless you're switching between multiple clients.

    Args:
        client (SyncVClient): The configured SyncVClient instance to use as the default.

    Example:
        ```python
        # Switch to a different client
        client2 = SyncVClient(api_key="other-key", set_as_default=False)
        sync_configure_sync_default_client(client2)
        ```
    """
    global _default_client
    _default_client = client


def sync_clear_default_client(client: "SyncVClient") -> None:
    """Clear the default client if it matches the given instance.

    Called automatically by ``SyncVClient.close()`` so that subsequent calls to
    ``sync_default_client()`` raise a clear ``RuntimeError`` instead of returning a
    closed HTTP session.

    Args:
        client: The client instance to compare against the current default.
    """
    global _default_client
    if _default_client is client:
        _default_client = None


def sync_default_client() -> "SyncVClient":
    """Retrieve the configured default client.

    Use this when you need direct access to the SyncVClient instance that was
    configured via `sync_configure_sync_default_client()`.

    Returns:
        SyncVClient: The configured default client instance.

    Raises:
        RuntimeError: If no default client has been configured.
    """
    if _default_client is None:
        msg = "No default client configured. Call sync_configure_sync_default_client() first."
        raise RuntimeError(msg)
    return _default_client


def sync_companies_service() -> "SyncCompaniesService":
    """Create a SyncCompaniesService using the default client.

    Provides access to company management operations (list, get, create, update, delete)
    without needing to pass a client instance.

    Returns:
        SyncCompaniesService: A service instance for company operations.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        companies = sync_companies_service()
        all_companies = await companies.list_all()
        ```
    """
    from vclient._sync.services.companies import SyncCompaniesService

    return SyncCompaniesService(sync_default_client())


def sync_developer_service() -> "SyncDeveloperService":
    """Create a SyncDeveloperService using the default client.

    Provides access to self-service developer operations (view profile, update profile,
    regenerate API key) without needing to pass a client instance.

    Returns:
        SyncDeveloperService: A service instance for developer self-service operations.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        developer = sync_developer_service()
        me = await developer.get_me()
        ```
    """
    from vclient._sync.services.developers import SyncDeveloperService

    return SyncDeveloperService(sync_default_client())


def sync_global_admin_service() -> "SyncGlobalAdminService":
    """Create a SyncGlobalAdminService using the default client.

    Provides access to global admin operations (developer management, API keys)
    without needing to pass a client instance. Requires global admin privileges.

    Returns:
        SyncGlobalAdminService: A service instance for global admin operations.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        admins = sync_global_admin_service()
        developers = await admins.list_all()
        ```
    """
    from vclient._sync.services.global_admin import SyncGlobalAdminService

    return SyncGlobalAdminService(sync_default_client())


def sync_system_service() -> "SyncSystemService":
    """Create a SyncSystemService using the default client.

    Provides access to system-level operations (health checks, status)
    without needing to pass a client instance.

    Returns:
        SyncSystemService: A service instance for system operations.

    Raises:
        RuntimeError: If no default client has been configured.

    Example:
        ```python
        system = sync_system_service()
        health = await system.health()
        ```
    """
    from vclient._sync.services.system import SyncSystemService

    return SyncSystemService(sync_default_client())


def sync_users_service(company_id: str | None = None) -> "SyncUsersService":
    """Create a SyncUsersService scoped to a specific company using the default client.

    Provides access to user management operations (list, get, create, update, delete)
    within a specific company without needing to pass a client instance.

    Args:
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Returns:
        SyncUsersService: A service instance scoped to the specified company.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.

    Example:
        ```python
        users = sync_users_service("company_id")
        all_users = await users.list_all()
        user = await users.get("user_id")
        ```
    """
    return sync_default_client().users(company_id)


def sync_campaigns_service(user_id: str, company_id: str | None = None) -> "SyncCampaignsService":
    """Create a SyncCampaignsService scoped to a specific company and user.

    Provides access to campaign management operations (list, get, create, update, delete)
    within a specific company and user context without needing to pass a client instance.

    Args:
        user_id: The ID of the user to operate as.
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Returns:
        SyncCampaignsService: A service instance scoped to the specified company and user.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.

    Example:
        ```python
        campaigns = sync_campaigns_service("user_id")
        all_campaigns = await campaigns.list_all()
        campaign = await campaigns.get("campaign_id")
        ```
    """
    return sync_default_client().campaigns(user_id, company_id)


def sync_books_service(
    user_id: str, campaign_id: str, *, company_id: str | None = None
) -> "SyncBooksService":
    """Create a SyncBooksService scoped to a specific company, user, and campaign.

    Provides access to campaign book management operations (list, get, create, update, delete)
    within a specific company, user, and campaign context without needing to pass a client instance.

    Args:
        user_id: The ID of the user to operate as.
        campaign_id: The ID of the campaign to operate within.
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Returns:
        SyncBooksService: A service instance scoped to the specified context.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.

    Example:
        ```python
        books = sync_books_service("user_id", "campaign_id")
        all_books = await books.list_all()
        book = await books.get("book_id")
        ```
    """
    return sync_default_client().books(user_id, campaign_id, company_id=company_id)


def sync_chapters_service(
    user_id: str, campaign_id: str, book_id: str, *, company_id: str | None = None
) -> "SyncChaptersService":
    """Create a SyncChaptersService scoped to a specific company, user, campaign, and book.

    Provides access to campaign book chapter management operations (list, get, create, update, delete)
    within a specific company, user, campaign, and book context without needing to pass a client instance.

    Args:
        user_id: The ID of the user to operate as.
        campaign_id: The ID of the campaign to operate within.
        book_id: The ID of the book to operate within.
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.
    """
    return sync_default_client().chapters(user_id, campaign_id, book_id, company_id=company_id)


def sync_characters_service(
    user_id: str, campaign_id: str, *, company_id: str | None = None
) -> "SyncCharactersService":
    """Create a SyncCharactersService scoped to a specific company, user, and campaign.

    Provides access to character management operations (list, get, create, update, delete)
    within a specific company, user, and campaign context without needing to pass a client instance.

    Args:
        user_id: The ID of the user to operate as.
        campaign_id: The ID of the campaign to operate within.
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.
    """
    return sync_default_client().characters(user_id, campaign_id, company_id=company_id)


def sync_character_traits_service(
    user_id: str, campaign_id: str, character_id: str, *, company_id: str | None = None
) -> "SyncCharacterTraitsService":
    """Create a SyncCharacterTraitsService scoped to a specific company, user, campaign, and character.

    Provides access to character trait management operations (list, get, create, update, delete)
    within a specific company, user, campaign, and character context without needing to pass a client instance.

    Args:
        user_id: The ID of the user to operate as.
        campaign_id: The ID of the campaign to operate within.
        character_id: The ID of the character to operate within.
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.
    """
    return sync_default_client().character_traits(
        user_id, campaign_id, character_id, company_id=company_id
    )


def sync_character_blueprint_service(
    company_id: str | None = None,
) -> "SyncCharacterBlueprintService":
    """Create a SyncCharacterBlueprintService scoped to a specific company.

    Provides access to character blueprint management operations (list, get, create, update, delete)
    within a specific company context without needing to pass a client instance.

    Args:
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.
    """
    return sync_default_client().character_blueprint(company_id)


def sync_dictionary_service(company_id: str | None = None) -> "SyncDictionaryService":
    """Create a SyncDictionaryService scoped to a specific company.

    Provides access to dictionary term management operations (list, get, create, update, delete)
    within a specific company context without needing to pass a client instance.

    Args:
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.
    """
    return sync_default_client().dictionary(company_id)


def sync_dicerolls_service(user_id: str, company_id: str | None = None) -> "SyncDicerollService":
    """Create a SyncDicerollService scoped to a specific company and user.

    Provides access to dice roll management operations (list, get, create)
    within a specific company and user context without needing to pass a client instance.

    Args:
        user_id: The ID of the user to operate as.
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.
    """
    return sync_default_client().dicerolls(user_id, company_id)


def sync_options_service(company_id: str | None = None) -> "SyncOptionsService":
    """Create a SyncOptionsService scoped to a specific company.

    Provides access to options and enumerations management operations (list, get, create, update, delete)
    within a specific company context without needing to pass a client instance.

    Args:
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.
    """
    return sync_default_client().options(company_id)


def sync_character_autogen_service(
    user_id: str, campaign_id: str, *, company_id: str | None = None
) -> "SyncCharacterAutogenService":
    """Create a SyncCharacterAutogenService scoped to a specific company, user, and campaign.

    Provides access to character autogen management operations (list, get, create, update, delete)
    within a specific company, user, and campaign context without needing to pass a client instance.

    Args:
        user_id: The ID of the user to operate as.
        campaign_id: The ID of the campaign to operate within.
        company_id: The ID of the company to operate within. If not provided,
            uses the default_company_id from the client config.

    Raises:
        RuntimeError: If no default client has been configured.
        ValueError: If no company_id provided and no default configured.
    """
    return sync_default_client().character_autogen(user_id, campaign_id, company_id=company_id)
