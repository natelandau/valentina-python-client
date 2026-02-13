"""API client for the vclient service.

Primary exports:
    VClient: The main API client class

Factory functions (primary access pattern):
    books_service, campaigns_service, chapters_service, etc.

For exceptions, use: from vclient.exceptions import APIError, NotFoundError, ...
For models, use: from vclient.models import Character, Campaign, ...
For service classes, use: from vclient.services import CharactersService, ...
"""

from vclient.client import VClient
from vclient.registry import (
    books_service,
    campaigns_service,
    chapters_service,
    character_autogen_service,
    character_blueprint_service,
    character_traits_service,
    characters_service,
    companies_service,
    developer_service,
    dicerolls_service,
    dictionary_service,
    global_admin_service,
    options_service,
    system_service,
    users_service,
)

__all__ = (
    # Core
    "VClient",
    # Factory functions
    "books_service",
    "campaigns_service",
    "chapters_service",
    "character_autogen_service",
    "character_blueprint_service",
    "character_traits_service",
    "characters_service",
    "companies_service",
    "developer_service",
    "dicerolls_service",
    "dictionary_service",
    "global_admin_service",
    "options_service",
    "system_service",
    "users_service",
)
