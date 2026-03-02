"""API client for the vclient service.

Primary exports:
    VClient: The main async API client class
    SyncVClient: The synchronous API client class

Factory functions (primary access pattern):
    Async: books_service, campaigns_service, chapters_service, etc.
    Sync: sync_books_service, sync_campaigns_service, sync_chapters_service, etc.

For exceptions, use: from vclient.exceptions import APIError, NotFoundError, ...
For models, use: from vclient.models import Character, Campaign, ...
For service classes, use: from vclient.services import CharactersService, ...
"""

import logging as _logging

from loguru import logger as _logger


class _PropagateHandler(_logging.Handler):
    """Forward loguru messages to stdlib logging for caplog/handler compatibility."""

    def emit(self, record: _logging.LogRecord) -> None:
        _logging.getLogger(record.name).handle(record)


_logger.add(
    _PropagateHandler(),
    format="{message}",
    filter=lambda record: record["name"].startswith("vclient"),
)

_logger.disable("vclient")

from vclient._sync import (  # noqa: E402
    SyncVClient,
    sync_books_service,
    sync_campaigns_service,
    sync_chapters_service,
    sync_character_autogen_service,
    sync_character_blueprint_service,
    sync_character_traits_service,
    sync_characters_service,
    sync_companies_service,
    sync_developer_service,
    sync_dicerolls_service,
    sync_dictionary_service,
    sync_global_admin_service,
    sync_options_service,
    sync_system_service,
    sync_users_service,
)
from vclient.client import VClient  # noqa: E402
from vclient.registry import (  # noqa: E402
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
    "SyncVClient",
    "VClient",
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
    "sync_books_service",
    "sync_campaigns_service",
    "sync_chapters_service",
    "sync_character_autogen_service",
    "sync_character_blueprint_service",
    "sync_character_traits_service",
    "sync_characters_service",
    "sync_companies_service",
    "sync_developer_service",
    "sync_dicerolls_service",
    "sync_dictionary_service",
    "sync_global_admin_service",
    "sync_options_service",
    "sync_system_service",
    "sync_users_service",
    "system_service",
    "users_service",
)

__version__ = "1.6.1"
