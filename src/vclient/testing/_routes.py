"""Named route constants for use with FakeVClient's set_response() and set_error()."""

from __future__ import annotations

from typing import NamedTuple

from vclient.endpoints import Endpoints
from vclient.testing._router import NO_CONTENT, PAGINATED, RAW_JSON, SINGLE


class RouteSpec(NamedTuple):
    """Identify an API route by HTTP method, URL pattern, and response style.

    Attributes:
        method: HTTP method (GET, POST, PATCH, PUT, DELETE).
        pattern: Endpoint URL pattern from the Endpoints class.
        style: Response style — one of PAGINATED, SINGLE, NO_CONTENT, or RAW_JSON.
    """

    method: str
    pattern: str
    style: str


class Routes:
    """Named constants for every API route supported by FakeVClient.

    Use these with ``set_response()`` and ``set_error()`` to override the default
    fake responses for specific endpoints.

    Example::

        from vclient.testing import FakeVClient, Routes

        async with FakeVClient() as client:
            # Override the campaigns list endpoint
            client.set_response(Routes.CAMPAIGNS_LIST, json={"items": [], "total": 0, "limit": 10, "offset": 0})

            # Make a specific route return an error
            client.set_error(Routes.CHARACTERS_GET, status_code=404, detail="Not found")
    """

    # Health
    HEALTH_GET = RouteSpec("GET", Endpoints.HEALTH, SINGLE)

    # Admin developers
    ADMIN_DEVELOPERS_LIST = RouteSpec("GET", Endpoints.ADMIN_DEVELOPERS, PAGINATED)
    ADMIN_DEVELOPERS_GET = RouteSpec("GET", Endpoints.ADMIN_DEVELOPER, SINGLE)
    ADMIN_DEVELOPERS_CREATE = RouteSpec("POST", Endpoints.ADMIN_DEVELOPERS, SINGLE)
    ADMIN_DEVELOPERS_UPDATE = RouteSpec("PATCH", Endpoints.ADMIN_DEVELOPER, SINGLE)
    ADMIN_DEVELOPERS_DELETE = RouteSpec("DELETE", Endpoints.ADMIN_DEVELOPER, NO_CONTENT)
    ADMIN_DEVELOPERS_NEW_KEY = RouteSpec("POST", Endpoints.ADMIN_DEVELOPER_NEW_KEY, SINGLE)

    # Developer self-service
    DEVELOPERS_ME_GET = RouteSpec("GET", Endpoints.DEVELOPER_ME, SINGLE)
    DEVELOPERS_ME_UPDATE = RouteSpec("PATCH", Endpoints.DEVELOPER_ME, SINGLE)
    DEVELOPERS_ME_NEW_KEY = RouteSpec("POST", Endpoints.DEVELOPER_ME_NEW_KEY, SINGLE)

    # Companies
    COMPANIES_LIST = RouteSpec("GET", Endpoints.COMPANIES, PAGINATED)
    COMPANIES_GET = RouteSpec("GET", Endpoints.COMPANY, SINGLE)
    COMPANIES_CREATE = RouteSpec("POST", Endpoints.COMPANIES, SINGLE)
    COMPANIES_UPDATE = RouteSpec("PATCH", Endpoints.COMPANY, SINGLE)
    COMPANIES_DELETE = RouteSpec("DELETE", Endpoints.COMPANY, NO_CONTENT)
    COMPANIES_ACCESS = RouteSpec("POST", Endpoints.COMPANY_ACCESS, SINGLE)
    COMPANIES_STATISTICS = RouteSpec("GET", Endpoints.COMPANY_STATISTICS, SINGLE)

    # Users
    USERS_LIST = RouteSpec("GET", Endpoints.USERS, PAGINATED)
    USERS_GET = RouteSpec("GET", Endpoints.USER, SINGLE)
    USERS_CREATE = RouteSpec("POST", Endpoints.USERS, SINGLE)
    USERS_UPDATE = RouteSpec("PATCH", Endpoints.USER, SINGLE)
    USERS_DELETE = RouteSpec("DELETE", Endpoints.USER, NO_CONTENT)
    USERS_STATISTICS = RouteSpec("GET", Endpoints.USER_STATISTICS, SINGLE)

    # User assets
    USERS_ASSETS_LIST = RouteSpec("GET", Endpoints.USER_ASSETS, PAGINATED)
    USERS_ASSETS_GET = RouteSpec("GET", Endpoints.USER_ASSET, SINGLE)
    USERS_ASSETS_DELETE = RouteSpec("DELETE", Endpoints.USER_ASSET, NO_CONTENT)
    USERS_ASSETS_UPLOAD = RouteSpec("POST", Endpoints.USER_ASSET_UPLOAD, SINGLE)

    # User experience
    USERS_EXPERIENCE_GET = RouteSpec("GET", Endpoints.USER_EXPERIENCE_CAMPAIGN, SINGLE)
    USERS_EXPERIENCE_XP_ADD = RouteSpec("POST", Endpoints.USER_EXPERIENCE_XP_ADD, SINGLE)
    USERS_EXPERIENCE_XP_REMOVE = RouteSpec("POST", Endpoints.USER_EXPERIENCE_XP_REMOVE, SINGLE)
    USERS_EXPERIENCE_CP_ADD = RouteSpec("POST", Endpoints.USER_EXPERIENCE_CP_ADD, SINGLE)

    # User notes
    USERS_NOTES_LIST = RouteSpec("GET", Endpoints.USER_NOTES, PAGINATED)
    USERS_NOTES_GET = RouteSpec("GET", Endpoints.USER_NOTE, SINGLE)
    USERS_NOTES_CREATE = RouteSpec("POST", Endpoints.USER_NOTES, SINGLE)
    USERS_NOTES_UPDATE = RouteSpec("PATCH", Endpoints.USER_NOTE, SINGLE)
    USERS_NOTES_DELETE = RouteSpec("DELETE", Endpoints.USER_NOTE, NO_CONTENT)

    # User quickrolls
    USERS_QUICKROLLS_LIST = RouteSpec("GET", Endpoints.USER_QUICKROLLS, PAGINATED)
    USERS_QUICKROLLS_GET = RouteSpec("GET", Endpoints.USER_QUICKROLL, SINGLE)
    USERS_QUICKROLLS_CREATE = RouteSpec("POST", Endpoints.USER_QUICKROLLS, SINGLE)
    USERS_QUICKROLLS_UPDATE = RouteSpec("PATCH", Endpoints.USER_QUICKROLL, SINGLE)
    USERS_QUICKROLLS_DELETE = RouteSpec("DELETE", Endpoints.USER_QUICKROLL, NO_CONTENT)

    # Campaigns
    CAMPAIGNS_LIST = RouteSpec("GET", Endpoints.CAMPAIGNS, PAGINATED)
    CAMPAIGNS_GET = RouteSpec("GET", Endpoints.CAMPAIGN, SINGLE)
    CAMPAIGNS_CREATE = RouteSpec("POST", Endpoints.CAMPAIGNS, SINGLE)
    CAMPAIGNS_UPDATE = RouteSpec("PATCH", Endpoints.CAMPAIGN, SINGLE)
    CAMPAIGNS_DELETE = RouteSpec("DELETE", Endpoints.CAMPAIGN, NO_CONTENT)
    CAMPAIGNS_STATISTICS = RouteSpec("GET", Endpoints.CAMPAIGN_STATISTICS, SINGLE)

    # Campaign assets
    CAMPAIGNS_ASSETS_LIST = RouteSpec("GET", Endpoints.CAMPAIGN_ASSETS, PAGINATED)
    CAMPAIGNS_ASSETS_GET = RouteSpec("GET", Endpoints.CAMPAIGN_ASSET, SINGLE)
    CAMPAIGNS_ASSETS_DELETE = RouteSpec("DELETE", Endpoints.CAMPAIGN_ASSET, NO_CONTENT)
    CAMPAIGNS_ASSETS_UPLOAD = RouteSpec("POST", Endpoints.CAMPAIGN_ASSET_UPLOAD, SINGLE)

    # Campaign notes
    CAMPAIGNS_NOTES_LIST = RouteSpec("GET", Endpoints.CAMPAIGN_NOTES, PAGINATED)
    CAMPAIGNS_NOTES_GET = RouteSpec("GET", Endpoints.CAMPAIGN_NOTE, SINGLE)
    CAMPAIGNS_NOTES_CREATE = RouteSpec("POST", Endpoints.CAMPAIGN_NOTES, SINGLE)
    CAMPAIGNS_NOTES_UPDATE = RouteSpec("PATCH", Endpoints.CAMPAIGN_NOTE, SINGLE)
    CAMPAIGNS_NOTES_DELETE = RouteSpec("DELETE", Endpoints.CAMPAIGN_NOTE, NO_CONTENT)

    # Books
    BOOKS_LIST = RouteSpec("GET", Endpoints.CAMPAIGN_BOOKS, PAGINATED)
    BOOKS_GET = RouteSpec("GET", Endpoints.CAMPAIGN_BOOK, SINGLE)
    BOOKS_CREATE = RouteSpec("POST", Endpoints.CAMPAIGN_BOOKS, SINGLE)
    BOOKS_UPDATE = RouteSpec("PATCH", Endpoints.CAMPAIGN_BOOK, SINGLE)
    BOOKS_DELETE = RouteSpec("DELETE", Endpoints.CAMPAIGN_BOOK, NO_CONTENT)
    BOOKS_RENUMBER = RouteSpec("PUT", Endpoints.CAMPAIGN_BOOK_NUMBER, SINGLE)

    # Book notes
    BOOKS_NOTES_LIST = RouteSpec("GET", Endpoints.BOOK_NOTES, PAGINATED)
    BOOKS_NOTES_GET = RouteSpec("GET", Endpoints.BOOK_NOTE, SINGLE)
    BOOKS_NOTES_CREATE = RouteSpec("POST", Endpoints.BOOK_NOTES, SINGLE)
    BOOKS_NOTES_UPDATE = RouteSpec("PATCH", Endpoints.BOOK_NOTE, SINGLE)
    BOOKS_NOTES_DELETE = RouteSpec("DELETE", Endpoints.BOOK_NOTE, NO_CONTENT)

    # Book assets
    BOOKS_ASSETS_LIST = RouteSpec("GET", Endpoints.BOOK_ASSETS, PAGINATED)
    BOOKS_ASSETS_GET = RouteSpec("GET", Endpoints.BOOK_ASSET, SINGLE)
    BOOKS_ASSETS_DELETE = RouteSpec("DELETE", Endpoints.BOOK_ASSET, NO_CONTENT)
    BOOKS_ASSETS_UPLOAD = RouteSpec("POST", Endpoints.BOOK_ASSET_UPLOAD, SINGLE)

    # Chapters
    CHAPTERS_LIST = RouteSpec("GET", Endpoints.BOOK_CHAPTERS, PAGINATED)
    CHAPTERS_GET = RouteSpec("GET", Endpoints.BOOK_CHAPTER, SINGLE)
    CHAPTERS_CREATE = RouteSpec("POST", Endpoints.BOOK_CHAPTERS, SINGLE)
    CHAPTERS_UPDATE = RouteSpec("PATCH", Endpoints.BOOK_CHAPTER, SINGLE)
    CHAPTERS_DELETE = RouteSpec("DELETE", Endpoints.BOOK_CHAPTER, NO_CONTENT)
    CHAPTERS_RENUMBER = RouteSpec("PUT", Endpoints.BOOK_CHAPTER_NUMBER, SINGLE)

    # Chapter notes
    CHAPTERS_NOTES_LIST = RouteSpec("GET", Endpoints.BOOK_CHAPTER_NOTES, PAGINATED)
    CHAPTERS_NOTES_GET = RouteSpec("GET", Endpoints.BOOK_CHAPTER_NOTE, SINGLE)
    CHAPTERS_NOTES_CREATE = RouteSpec("POST", Endpoints.BOOK_CHAPTER_NOTES, SINGLE)
    CHAPTERS_NOTES_UPDATE = RouteSpec("PATCH", Endpoints.BOOK_CHAPTER_NOTE, SINGLE)
    CHAPTERS_NOTES_DELETE = RouteSpec("DELETE", Endpoints.BOOK_CHAPTER_NOTE, NO_CONTENT)

    # Chapter assets
    CHAPTERS_ASSETS_LIST = RouteSpec("GET", Endpoints.BOOK_CHAPTER_ASSETS, PAGINATED)
    CHAPTERS_ASSETS_GET = RouteSpec("GET", Endpoints.BOOK_CHAPTER_ASSET, SINGLE)
    CHAPTERS_ASSETS_DELETE = RouteSpec("DELETE", Endpoints.BOOK_CHAPTER_ASSET, NO_CONTENT)
    CHAPTERS_ASSETS_UPLOAD = RouteSpec("POST", Endpoints.BOOK_CHAPTER_ASSET_UPLOAD, SINGLE)

    # Characters
    CHARACTERS_LIST = RouteSpec("GET", Endpoints.CHARACTERS, PAGINATED)
    CHARACTERS_GET = RouteSpec("GET", Endpoints.CHARACTER, SINGLE)
    CHARACTERS_CREATE = RouteSpec("POST", Endpoints.CHARACTERS, SINGLE)
    CHARACTERS_UPDATE = RouteSpec("PATCH", Endpoints.CHARACTER, SINGLE)
    CHARACTERS_DELETE = RouteSpec("DELETE", Endpoints.CHARACTER, NO_CONTENT)
    CHARACTERS_STATISTICS = RouteSpec("GET", Endpoints.CHARACTER_STATISTICS, SINGLE)

    # Character assets
    CHARACTERS_ASSETS_LIST = RouteSpec("GET", Endpoints.CHARACTER_ASSETS, PAGINATED)
    CHARACTERS_ASSETS_GET = RouteSpec("GET", Endpoints.CHARACTER_ASSET, SINGLE)
    CHARACTERS_ASSETS_DELETE = RouteSpec("DELETE", Endpoints.CHARACTER_ASSET, NO_CONTENT)
    CHARACTERS_ASSETS_UPLOAD = RouteSpec("POST", Endpoints.CHARACTER_ASSET_UPLOAD, SINGLE)

    # Character notes
    CHARACTERS_NOTES_LIST = RouteSpec("GET", Endpoints.CHARACTER_NOTES, PAGINATED)
    CHARACTERS_NOTES_GET = RouteSpec("GET", Endpoints.CHARACTER_NOTE, SINGLE)
    CHARACTERS_NOTES_CREATE = RouteSpec("POST", Endpoints.CHARACTER_NOTES, SINGLE)
    CHARACTERS_NOTES_UPDATE = RouteSpec("PATCH", Endpoints.CHARACTER_NOTE, SINGLE)
    CHARACTERS_NOTES_DELETE = RouteSpec("DELETE", Endpoints.CHARACTER_NOTE, NO_CONTENT)

    # Character inventory
    CHARACTERS_INVENTORY_LIST = RouteSpec("GET", Endpoints.CHARACTER_INVENTORY, PAGINATED)
    CHARACTERS_INVENTORY_GET = RouteSpec("GET", Endpoints.CHARACTER_INVENTORY_ITEM, SINGLE)
    CHARACTERS_INVENTORY_CREATE = RouteSpec("POST", Endpoints.CHARACTER_INVENTORY, SINGLE)
    CHARACTERS_INVENTORY_UPDATE = RouteSpec("PATCH", Endpoints.CHARACTER_INVENTORY_ITEM, SINGLE)
    CHARACTERS_INVENTORY_DELETE = RouteSpec(
        "DELETE", Endpoints.CHARACTER_INVENTORY_ITEM, NO_CONTENT
    )

    # Character werewolf gifts
    CHARACTERS_WEREWOLF_GIFTS_LIST = RouteSpec("GET", Endpoints.CHARACTER_WEREWOLF_GIFTS, PAGINATED)
    CHARACTERS_WEREWOLF_GIFTS_GET = RouteSpec(
        "GET", Endpoints.CHARACTER_WEREWOLF_GIFT_DETAIL, SINGLE
    )
    CHARACTERS_WEREWOLF_GIFTS_CREATE = RouteSpec("POST", Endpoints.CHARACTER_WEREWOLF_GIFTS, SINGLE)
    CHARACTERS_WEREWOLF_GIFTS_DELETE = RouteSpec(
        "DELETE", Endpoints.CHARACTER_WEREWOLF_GIFT_DETAIL, NO_CONTENT
    )

    # Character werewolf rites
    CHARACTERS_WEREWOLF_RITES_LIST = RouteSpec("GET", Endpoints.CHARACTER_WEREWOLF_RITES, PAGINATED)
    CHARACTERS_WEREWOLF_RITES_GET = RouteSpec(
        "GET", Endpoints.CHARACTER_WEREWOLF_RITE_DETAIL, SINGLE
    )
    CHARACTERS_WEREWOLF_RITES_CREATE = RouteSpec("POST", Endpoints.CHARACTER_WEREWOLF_RITES, SINGLE)
    CHARACTERS_WEREWOLF_RITES_DELETE = RouteSpec(
        "DELETE", Endpoints.CHARACTER_WEREWOLF_RITE_DETAIL, NO_CONTENT
    )

    # Character hunter edges
    CHARACTERS_HUNTER_EDGES_LIST = RouteSpec("GET", Endpoints.CHARACTER_HUNTER_EDGES, PAGINATED)
    CHARACTERS_HUNTER_EDGES_GET = RouteSpec("GET", Endpoints.CHARACTER_HUNTER_EDGE_DETAIL, SINGLE)
    CHARACTERS_HUNTER_EDGES_CREATE = RouteSpec("POST", Endpoints.CHARACTER_HUNTER_EDGES, SINGLE)
    CHARACTERS_HUNTER_EDGES_DELETE = RouteSpec(
        "DELETE", Endpoints.CHARACTER_HUNTER_EDGE_DETAIL, NO_CONTENT
    )

    # Character hunter edge perks
    CHARACTERS_HUNTER_EDGE_PERKS_LIST = RouteSpec(
        "GET", Endpoints.CHARACTER_HUNTER_EDGE_PERKS, PAGINATED
    )
    CHARACTERS_HUNTER_EDGE_PERKS_GET = RouteSpec(
        "GET", Endpoints.CHARACTER_HUNTER_EDGE_PERK_DETAIL, SINGLE
    )
    CHARACTERS_HUNTER_EDGE_PERKS_CREATE = RouteSpec(
        "POST", Endpoints.CHARACTER_HUNTER_EDGE_PERKS, SINGLE
    )
    CHARACTERS_HUNTER_EDGE_PERKS_DELETE = RouteSpec(
        "DELETE", Endpoints.CHARACTER_HUNTER_EDGE_PERK_DETAIL, NO_CONTENT
    )

    # Character generation
    CHARACTERS_AUTOGENERATE = RouteSpec("POST", Endpoints.AUTOGENERATE, SINGLE)
    CHARACTERS_CHARGEN_START = RouteSpec("POST", Endpoints.CHARGEN_START, SINGLE)
    CHARACTERS_CHARGEN_FINALIZE = RouteSpec("POST", Endpoints.CHARGEN_FINALIZE, SINGLE)

    # Character traits
    CHARACTER_TRAITS_LIST = RouteSpec("GET", Endpoints.CHARACTER_TRAITS, PAGINATED)
    CHARACTER_TRAITS_GET = RouteSpec("GET", Endpoints.CHARACTER_TRAIT, SINGLE)
    CHARACTER_TRAITS_DELETE = RouteSpec("DELETE", Endpoints.CHARACTER_TRAIT, NO_CONTENT)
    CHARACTER_TRAITS_ASSIGN = RouteSpec("POST", Endpoints.CHARACTER_TRAIT_ASSIGN, SINGLE)
    CHARACTER_TRAITS_CREATE = RouteSpec("POST", Endpoints.CHARACTER_TRAIT_CREATE, SINGLE)
    CHARACTER_TRAITS_VALUE_OPTIONS = RouteSpec(
        "GET", Endpoints.CHARACTER_TRAIT_VALUE_OPTIONS, SINGLE
    )
    CHARACTER_TRAITS_VALUE_UPDATE = RouteSpec("PUT", Endpoints.CHARACTER_TRAIT_VALUE, SINGLE)

    # Blueprint sections
    BLUEPRINT_SECTIONS_LIST = RouteSpec("GET", Endpoints.BLUEPRINT_SECTIONS, PAGINATED)
    BLUEPRINT_SECTIONS_GET = RouteSpec("GET", Endpoints.BLUEPRINT_SECTION_DETAIL, SINGLE)

    # Blueprint categories
    BLUEPRINT_CATEGORIES_LIST = RouteSpec("GET", Endpoints.BLUEPRINT_CATEGORIES, PAGINATED)
    BLUEPRINT_CATEGORIES_GET = RouteSpec("GET", Endpoints.BLUEPRINT_CATEGORY_DETAIL, SINGLE)
    BLUEPRINT_CATEGORIES_TRAITS = RouteSpec("GET", Endpoints.BLUEPRINT_CATEGORY_TRAITS, PAGINATED)

    # Blueprint traits
    BLUEPRINT_TRAITS_LIST = RouteSpec("GET", Endpoints.BLUEPRINT_TRAITS, PAGINATED)
    BLUEPRINT_TRAITS_GET = RouteSpec("GET", Endpoints.BLUEPRINT_TRAIT_DETAIL, SINGLE)

    # Blueprint concepts
    BLUEPRINT_CONCEPTS_LIST = RouteSpec("GET", Endpoints.CONCEPTS, PAGINATED)
    BLUEPRINT_CONCEPTS_GET = RouteSpec("GET", Endpoints.CONCEPT_DETAIL, SINGLE)

    # Blueprint vampire clans
    BLUEPRINT_VAMPIRE_CLANS_LIST = RouteSpec("GET", Endpoints.VAMPIRE_CLANS, PAGINATED)
    BLUEPRINT_VAMPIRE_CLANS_GET = RouteSpec("GET", Endpoints.VAMPIRE_CLAN_DETAIL, SINGLE)

    # Blueprint werewolf tribes
    BLUEPRINT_WEREWOLF_TRIBES_LIST = RouteSpec("GET", Endpoints.WEREWOLF_TRIBES, PAGINATED)
    BLUEPRINT_WEREWOLF_TRIBES_GET = RouteSpec("GET", Endpoints.WEREWOLF_TRIBE_DETAIL, SINGLE)

    # Blueprint werewolf auspices
    BLUEPRINT_WEREWOLF_AUSPICES_LIST = RouteSpec("GET", Endpoints.WEREWOLF_AUSPICES, PAGINATED)
    BLUEPRINT_WEREWOLF_AUSPICES_GET = RouteSpec("GET", Endpoints.WEREWOLF_AUSPICE_DETAIL, SINGLE)

    # Blueprint werewolf gifts
    BLUEPRINT_WEREWOLF_GIFTS_LIST = RouteSpec("GET", Endpoints.WEREWOLF_GIFTS, PAGINATED)
    BLUEPRINT_WEREWOLF_GIFTS_GET = RouteSpec("GET", Endpoints.WEREWOLF_GIFT_DETAIL, SINGLE)

    # Blueprint werewolf rites
    BLUEPRINT_WEREWOLF_RITES_LIST = RouteSpec("GET", Endpoints.WEREWOLF_RITES, PAGINATED)
    BLUEPRINT_WEREWOLF_RITES_GET = RouteSpec("GET", Endpoints.WEREWOLF_RITE_DETAIL, SINGLE)

    # Blueprint hunter edges
    BLUEPRINT_HUNTER_EDGES_LIST = RouteSpec("GET", Endpoints.HUNTER_EDGES, PAGINATED)
    BLUEPRINT_HUNTER_EDGES_GET = RouteSpec("GET", Endpoints.HUNTER_EDGE_DETAIL, SINGLE)

    # Blueprint hunter edge perks
    BLUEPRINT_HUNTER_EDGE_PERKS_LIST = RouteSpec("GET", Endpoints.HUNTER_EDGE_PERKS, PAGINATED)
    BLUEPRINT_HUNTER_EDGE_PERKS_GET = RouteSpec("GET", Endpoints.HUNTER_EDGE_PERK_DETAIL, SINGLE)

    # Dictionary
    DICTIONARY_LIST = RouteSpec("GET", Endpoints.DICTIONARY_TERMS, PAGINATED)
    DICTIONARY_GET = RouteSpec("GET", Endpoints.DICTIONARY_TERM, SINGLE)
    DICTIONARY_CREATE = RouteSpec("POST", Endpoints.DICTIONARY_TERMS, SINGLE)
    DICTIONARY_UPDATE = RouteSpec("PUT", Endpoints.DICTIONARY_TERM, SINGLE)
    DICTIONARY_DELETE = RouteSpec("DELETE", Endpoints.DICTIONARY_TERM, NO_CONTENT)

    # Dicerolls
    DICEROLLS_LIST = RouteSpec("GET", Endpoints.DICEROLLS, PAGINATED)
    DICEROLLS_GET = RouteSpec("GET", Endpoints.DICEROLL, SINGLE)
    DICEROLLS_CREATE = RouteSpec("POST", Endpoints.DICEROLLS, SINGLE)
    DICEROLLS_QUICKROLL = RouteSpec("POST", Endpoints.DICEROLL_QUICKROLL, SINGLE)

    # Options
    OPTIONS_GET = RouteSpec("GET", Endpoints.OPTIONS, RAW_JSON)
