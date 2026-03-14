"""Named route constants for use with FakeVClient's set_response() and set_error()."""

from __future__ import annotations

from typing import NamedTuple

from vclient.endpoints import Endpoints
from vclient.models import (
    Asset,
    Campaign,
    CampaignBook,
    CampaignChapter,
    Character,
    CharacterConcept,
    CharacterTrait,
    CharacterTraitValueOptionsResponse,
    Company,
    CompanyPermissions,
    Developer,
    DeveloperWithApiKey,
    Diceroll,
    DictionaryTerm,
    EdgeAndPerks,
    HunterEdge,
    HunterEdgePerk,
    InventoryItem,
    MeDeveloper,
    MeDeveloperWithApiKey,
    NewCompanyResponse,
    Note,
    Perk,
    Quickroll,
    RollStatistics,
    SheetSection,
    SystemHealth,
    Trait,
    TraitCategory,
    User,
    VampireClan,
    WerewolfAuspice,
    WerewolfGift,
    WerewolfRite,
    WerewolfTribe,
)
from vclient.models.character_autogen import ChargenSessionResponse
from vclient.models.users import CampaignExperience

# Response style constants
PAGINATED = "paginated"
SINGLE = "single"
NO_CONTENT = "no_content"
RAW_JSON = "raw_json"
LIST = "list"


class RouteSpec(NamedTuple):
    """Identify an API route by HTTP method, URL pattern, response style, and model class.

    Attributes:
        method: HTTP method (GET, POST, PATCH, PUT, DELETE).
        pattern: Endpoint URL pattern from the Endpoints class.
        style: Response style — one of PAGINATED, SINGLE, LIST, NO_CONTENT, or RAW_JSON.
        model_class: The Pydantic model class used for auto-generating responses,
            or None for NO_CONTENT and RAW_JSON routes.
    """

    method: str
    pattern: str
    style: str
    model_class: type | None


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
    HEALTH_GET = RouteSpec("GET", Endpoints.HEALTH, SINGLE, SystemHealth)

    # Admin developers
    ADMIN_DEVELOPERS_LIST = RouteSpec("GET", Endpoints.ADMIN_DEVELOPERS, PAGINATED, Developer)
    ADMIN_DEVELOPERS_GET = RouteSpec("GET", Endpoints.ADMIN_DEVELOPER, SINGLE, Developer)
    ADMIN_DEVELOPERS_CREATE = RouteSpec("POST", Endpoints.ADMIN_DEVELOPERS, SINGLE, Developer)
    ADMIN_DEVELOPERS_UPDATE = RouteSpec("PATCH", Endpoints.ADMIN_DEVELOPER, SINGLE, Developer)
    ADMIN_DEVELOPERS_DELETE = RouteSpec("DELETE", Endpoints.ADMIN_DEVELOPER, NO_CONTENT, None)
    ADMIN_DEVELOPERS_NEW_KEY = RouteSpec(
        "POST", Endpoints.ADMIN_DEVELOPER_NEW_KEY, SINGLE, DeveloperWithApiKey
    )

    # Developer self-service
    DEVELOPERS_ME_GET = RouteSpec("GET", Endpoints.DEVELOPER_ME, SINGLE, MeDeveloper)
    DEVELOPERS_ME_UPDATE = RouteSpec("PATCH", Endpoints.DEVELOPER_ME, SINGLE, MeDeveloper)
    DEVELOPERS_ME_NEW_KEY = RouteSpec(
        "POST", Endpoints.DEVELOPER_ME_NEW_KEY, SINGLE, MeDeveloperWithApiKey
    )

    # Companies
    COMPANIES_LIST = RouteSpec("GET", Endpoints.COMPANIES, PAGINATED, Company)
    COMPANIES_GET = RouteSpec("GET", Endpoints.COMPANY, SINGLE, Company)
    COMPANIES_CREATE = RouteSpec("POST", Endpoints.COMPANIES, SINGLE, NewCompanyResponse)
    COMPANIES_UPDATE = RouteSpec("PATCH", Endpoints.COMPANY, SINGLE, Company)
    COMPANIES_DELETE = RouteSpec("DELETE", Endpoints.COMPANY, NO_CONTENT, None)
    COMPANIES_ACCESS = RouteSpec("POST", Endpoints.COMPANY_ACCESS, SINGLE, CompanyPermissions)
    COMPANIES_STATISTICS = RouteSpec("GET", Endpoints.COMPANY_STATISTICS, SINGLE, RollStatistics)

    # Users
    USERS_LIST = RouteSpec("GET", Endpoints.USERS, PAGINATED, User)
    USERS_UNAPPROVED_LIST = RouteSpec("GET", Endpoints.USERS_UNAPPROVED_LIST, PAGINATED, User)
    USERS_GET = RouteSpec("GET", Endpoints.USER, SINGLE, User)
    USERS_CREATE = RouteSpec("POST", Endpoints.USERS, SINGLE, User)
    USERS_UPDATE = RouteSpec("PATCH", Endpoints.USER, SINGLE, User)
    USERS_DELETE = RouteSpec("DELETE", Endpoints.USER, NO_CONTENT, None)
    USERS_APPROVE = RouteSpec("POST", Endpoints.USER_APPROVE, SINGLE, User)
    USERS_DENY = RouteSpec("POST", Endpoints.USER_DENY, NO_CONTENT, None)
    USERS_REGISTER = RouteSpec("POST", Endpoints.USER_REGISTER, SINGLE, User)
    USERS_MERGE = RouteSpec("POST", Endpoints.USER_MERGE, SINGLE, User)
    USERS_STATISTICS = RouteSpec("GET", Endpoints.USER_STATISTICS, SINGLE, RollStatistics)

    # User assets
    USERS_ASSETS_LIST = RouteSpec("GET", Endpoints.USER_ASSETS, PAGINATED, Asset)
    USERS_ASSETS_GET = RouteSpec("GET", Endpoints.USER_ASSET, SINGLE, Asset)
    USERS_ASSETS_DELETE = RouteSpec("DELETE", Endpoints.USER_ASSET, NO_CONTENT, None)
    USERS_ASSETS_UPLOAD = RouteSpec("POST", Endpoints.USER_ASSET_UPLOAD, SINGLE, Asset)

    # User experience
    USERS_EXPERIENCE_GET = RouteSpec(
        "GET", Endpoints.USER_EXPERIENCE_CAMPAIGN, SINGLE, CampaignExperience
    )
    USERS_EXPERIENCE_XP_ADD = RouteSpec(
        "POST", Endpoints.USER_EXPERIENCE_XP_ADD, SINGLE, CampaignExperience
    )
    USERS_EXPERIENCE_XP_REMOVE = RouteSpec(
        "POST", Endpoints.USER_EXPERIENCE_XP_REMOVE, SINGLE, CampaignExperience
    )
    USERS_EXPERIENCE_CP_ADD = RouteSpec(
        "POST", Endpoints.USER_EXPERIENCE_CP_ADD, SINGLE, CampaignExperience
    )

    # User notes
    USERS_NOTES_LIST = RouteSpec("GET", Endpoints.USER_NOTES, PAGINATED, Note)
    USERS_NOTES_GET = RouteSpec("GET", Endpoints.USER_NOTE, SINGLE, Note)
    USERS_NOTES_CREATE = RouteSpec("POST", Endpoints.USER_NOTES, SINGLE, Note)
    USERS_NOTES_UPDATE = RouteSpec("PATCH", Endpoints.USER_NOTE, SINGLE, Note)
    USERS_NOTES_DELETE = RouteSpec("DELETE", Endpoints.USER_NOTE, NO_CONTENT, None)

    # User quickrolls
    USERS_QUICKROLLS_LIST = RouteSpec("GET", Endpoints.USER_QUICKROLLS, PAGINATED, Quickroll)
    USERS_QUICKROLLS_GET = RouteSpec("GET", Endpoints.USER_QUICKROLL, SINGLE, Quickroll)
    USERS_QUICKROLLS_CREATE = RouteSpec("POST", Endpoints.USER_QUICKROLLS, SINGLE, Quickroll)
    USERS_QUICKROLLS_UPDATE = RouteSpec("PATCH", Endpoints.USER_QUICKROLL, SINGLE, Quickroll)
    USERS_QUICKROLLS_DELETE = RouteSpec("DELETE", Endpoints.USER_QUICKROLL, NO_CONTENT, None)

    # Campaigns
    CAMPAIGNS_LIST = RouteSpec("GET", Endpoints.CAMPAIGNS, PAGINATED, Campaign)
    CAMPAIGNS_GET = RouteSpec("GET", Endpoints.CAMPAIGN, SINGLE, Campaign)
    CAMPAIGNS_CREATE = RouteSpec("POST", Endpoints.CAMPAIGNS, SINGLE, Campaign)
    CAMPAIGNS_UPDATE = RouteSpec("PATCH", Endpoints.CAMPAIGN, SINGLE, Campaign)
    CAMPAIGNS_DELETE = RouteSpec("DELETE", Endpoints.CAMPAIGN, NO_CONTENT, None)
    CAMPAIGNS_STATISTICS = RouteSpec("GET", Endpoints.CAMPAIGN_STATISTICS, SINGLE, RollStatistics)

    # Campaign assets
    CAMPAIGNS_ASSETS_LIST = RouteSpec("GET", Endpoints.CAMPAIGN_ASSETS, PAGINATED, Asset)
    CAMPAIGNS_ASSETS_GET = RouteSpec("GET", Endpoints.CAMPAIGN_ASSET, SINGLE, Asset)
    CAMPAIGNS_ASSETS_DELETE = RouteSpec("DELETE", Endpoints.CAMPAIGN_ASSET, NO_CONTENT, None)
    CAMPAIGNS_ASSETS_UPLOAD = RouteSpec("POST", Endpoints.CAMPAIGN_ASSET_UPLOAD, SINGLE, Asset)

    # Campaign notes
    CAMPAIGNS_NOTES_LIST = RouteSpec("GET", Endpoints.CAMPAIGN_NOTES, PAGINATED, Note)
    CAMPAIGNS_NOTES_GET = RouteSpec("GET", Endpoints.CAMPAIGN_NOTE, SINGLE, Note)
    CAMPAIGNS_NOTES_CREATE = RouteSpec("POST", Endpoints.CAMPAIGN_NOTES, SINGLE, Note)
    CAMPAIGNS_NOTES_UPDATE = RouteSpec("PATCH", Endpoints.CAMPAIGN_NOTE, SINGLE, Note)
    CAMPAIGNS_NOTES_DELETE = RouteSpec("DELETE", Endpoints.CAMPAIGN_NOTE, NO_CONTENT, None)

    # Books
    BOOKS_LIST = RouteSpec("GET", Endpoints.CAMPAIGN_BOOKS, PAGINATED, CampaignBook)
    BOOKS_GET = RouteSpec("GET", Endpoints.CAMPAIGN_BOOK, SINGLE, CampaignBook)
    BOOKS_CREATE = RouteSpec("POST", Endpoints.CAMPAIGN_BOOKS, SINGLE, CampaignBook)
    BOOKS_UPDATE = RouteSpec("PATCH", Endpoints.CAMPAIGN_BOOK, SINGLE, CampaignBook)
    BOOKS_DELETE = RouteSpec("DELETE", Endpoints.CAMPAIGN_BOOK, NO_CONTENT, None)
    BOOKS_RENUMBER = RouteSpec("PUT", Endpoints.CAMPAIGN_BOOK_NUMBER, SINGLE, CampaignBook)

    # Book notes
    BOOKS_NOTES_LIST = RouteSpec("GET", Endpoints.BOOK_NOTES, PAGINATED, Note)
    BOOKS_NOTES_GET = RouteSpec("GET", Endpoints.BOOK_NOTE, SINGLE, Note)
    BOOKS_NOTES_CREATE = RouteSpec("POST", Endpoints.BOOK_NOTES, SINGLE, Note)
    BOOKS_NOTES_UPDATE = RouteSpec("PATCH", Endpoints.BOOK_NOTE, SINGLE, Note)
    BOOKS_NOTES_DELETE = RouteSpec("DELETE", Endpoints.BOOK_NOTE, NO_CONTENT, None)

    # Book assets
    BOOKS_ASSETS_LIST = RouteSpec("GET", Endpoints.BOOK_ASSETS, PAGINATED, Asset)
    BOOKS_ASSETS_GET = RouteSpec("GET", Endpoints.BOOK_ASSET, SINGLE, Asset)
    BOOKS_ASSETS_DELETE = RouteSpec("DELETE", Endpoints.BOOK_ASSET, NO_CONTENT, None)
    BOOKS_ASSETS_UPLOAD = RouteSpec("POST", Endpoints.BOOK_ASSET_UPLOAD, SINGLE, Asset)

    # Chapters
    CHAPTERS_LIST = RouteSpec("GET", Endpoints.BOOK_CHAPTERS, PAGINATED, CampaignChapter)
    CHAPTERS_GET = RouteSpec("GET", Endpoints.BOOK_CHAPTER, SINGLE, CampaignChapter)
    CHAPTERS_CREATE = RouteSpec("POST", Endpoints.BOOK_CHAPTERS, SINGLE, CampaignChapter)
    CHAPTERS_UPDATE = RouteSpec("PATCH", Endpoints.BOOK_CHAPTER, SINGLE, CampaignChapter)
    CHAPTERS_DELETE = RouteSpec("DELETE", Endpoints.BOOK_CHAPTER, NO_CONTENT, None)
    CHAPTERS_RENUMBER = RouteSpec("PUT", Endpoints.BOOK_CHAPTER_NUMBER, SINGLE, CampaignChapter)

    # Chapter notes
    CHAPTERS_NOTES_LIST = RouteSpec("GET", Endpoints.BOOK_CHAPTER_NOTES, PAGINATED, Note)
    CHAPTERS_NOTES_GET = RouteSpec("GET", Endpoints.BOOK_CHAPTER_NOTE, SINGLE, Note)
    CHAPTERS_NOTES_CREATE = RouteSpec("POST", Endpoints.BOOK_CHAPTER_NOTES, SINGLE, Note)
    CHAPTERS_NOTES_UPDATE = RouteSpec("PATCH", Endpoints.BOOK_CHAPTER_NOTE, SINGLE, Note)
    CHAPTERS_NOTES_DELETE = RouteSpec("DELETE", Endpoints.BOOK_CHAPTER_NOTE, NO_CONTENT, None)

    # Chapter assets
    CHAPTERS_ASSETS_LIST = RouteSpec("GET", Endpoints.BOOK_CHAPTER_ASSETS, PAGINATED, Asset)
    CHAPTERS_ASSETS_GET = RouteSpec("GET", Endpoints.BOOK_CHAPTER_ASSET, SINGLE, Asset)
    CHAPTERS_ASSETS_DELETE = RouteSpec("DELETE", Endpoints.BOOK_CHAPTER_ASSET, NO_CONTENT, None)
    CHAPTERS_ASSETS_UPLOAD = RouteSpec("POST", Endpoints.BOOK_CHAPTER_ASSET_UPLOAD, SINGLE, Asset)

    # Characters
    CHARACTERS_LIST = RouteSpec("GET", Endpoints.CHARACTERS, PAGINATED, Character)
    CHARACTERS_GET = RouteSpec("GET", Endpoints.CHARACTER, SINGLE, Character)
    CHARACTERS_CREATE = RouteSpec("POST", Endpoints.CHARACTERS, SINGLE, Character)
    CHARACTERS_UPDATE = RouteSpec("PATCH", Endpoints.CHARACTER, SINGLE, Character)
    CHARACTERS_DELETE = RouteSpec("DELETE", Endpoints.CHARACTER, NO_CONTENT, None)
    CHARACTERS_STATISTICS = RouteSpec("GET", Endpoints.CHARACTER_STATISTICS, SINGLE, RollStatistics)

    # Character assets
    CHARACTERS_ASSETS_LIST = RouteSpec("GET", Endpoints.CHARACTER_ASSETS, PAGINATED, Asset)
    CHARACTERS_ASSETS_GET = RouteSpec("GET", Endpoints.CHARACTER_ASSET, SINGLE, Asset)
    CHARACTERS_ASSETS_DELETE = RouteSpec("DELETE", Endpoints.CHARACTER_ASSET, NO_CONTENT, None)
    CHARACTERS_ASSETS_UPLOAD = RouteSpec("POST", Endpoints.CHARACTER_ASSET_UPLOAD, SINGLE, Asset)

    # Character notes
    CHARACTERS_NOTES_LIST = RouteSpec("GET", Endpoints.CHARACTER_NOTES, PAGINATED, Note)
    CHARACTERS_NOTES_GET = RouteSpec("GET", Endpoints.CHARACTER_NOTE, SINGLE, Note)
    CHARACTERS_NOTES_CREATE = RouteSpec("POST", Endpoints.CHARACTER_NOTES, SINGLE, Note)
    CHARACTERS_NOTES_UPDATE = RouteSpec("PATCH", Endpoints.CHARACTER_NOTE, SINGLE, Note)
    CHARACTERS_NOTES_DELETE = RouteSpec("DELETE", Endpoints.CHARACTER_NOTE, NO_CONTENT, None)

    # Character inventory
    CHARACTERS_INVENTORY_LIST = RouteSpec(
        "GET", Endpoints.CHARACTER_INVENTORY, PAGINATED, InventoryItem
    )
    CHARACTERS_INVENTORY_GET = RouteSpec(
        "GET", Endpoints.CHARACTER_INVENTORY_ITEM, SINGLE, InventoryItem
    )
    CHARACTERS_INVENTORY_CREATE = RouteSpec(
        "POST", Endpoints.CHARACTER_INVENTORY, SINGLE, InventoryItem
    )
    CHARACTERS_INVENTORY_UPDATE = RouteSpec(
        "PATCH", Endpoints.CHARACTER_INVENTORY_ITEM, SINGLE, InventoryItem
    )
    CHARACTERS_INVENTORY_DELETE = RouteSpec(
        "DELETE", Endpoints.CHARACTER_INVENTORY_ITEM, NO_CONTENT, None
    )

    # Character werewolf gifts
    CHARACTERS_WEREWOLF_GIFTS_LIST = RouteSpec(
        "GET", Endpoints.CHARACTER_WEREWOLF_GIFTS, PAGINATED, WerewolfGift
    )
    CHARACTERS_WEREWOLF_GIFTS_GET = RouteSpec(
        "GET", Endpoints.CHARACTER_WEREWOLF_GIFT_DETAIL, SINGLE, WerewolfGift
    )
    CHARACTERS_WEREWOLF_GIFTS_CREATE = RouteSpec(
        "POST", Endpoints.CHARACTER_WEREWOLF_GIFTS, SINGLE, WerewolfGift
    )
    CHARACTERS_WEREWOLF_GIFTS_DELETE = RouteSpec(
        "DELETE", Endpoints.CHARACTER_WEREWOLF_GIFT_DETAIL, NO_CONTENT, None
    )

    # Character werewolf rites
    CHARACTERS_WEREWOLF_RITES_LIST = RouteSpec(
        "GET", Endpoints.CHARACTER_WEREWOLF_RITES, PAGINATED, WerewolfRite
    )
    CHARACTERS_WEREWOLF_RITES_GET = RouteSpec(
        "GET", Endpoints.CHARACTER_WEREWOLF_RITE_DETAIL, SINGLE, WerewolfRite
    )
    CHARACTERS_WEREWOLF_RITES_CREATE = RouteSpec(
        "POST", Endpoints.CHARACTER_WEREWOLF_RITES, SINGLE, WerewolfRite
    )
    CHARACTERS_WEREWOLF_RITES_DELETE = RouteSpec(
        "DELETE", Endpoints.CHARACTER_WEREWOLF_RITE_DETAIL, NO_CONTENT, None
    )

    # Character hunter edges
    CHARACTERS_HUNTER_EDGES_LIST = RouteSpec(
        "GET", Endpoints.CHARACTER_HUNTER_EDGES, PAGINATED, EdgeAndPerks
    )
    CHARACTERS_HUNTER_EDGES_GET = RouteSpec(
        "GET", Endpoints.CHARACTER_HUNTER_EDGE_DETAIL, SINGLE, EdgeAndPerks
    )
    CHARACTERS_HUNTER_EDGES_CREATE = RouteSpec(
        "POST", Endpoints.CHARACTER_HUNTER_EDGES, SINGLE, EdgeAndPerks
    )
    CHARACTERS_HUNTER_EDGES_DELETE = RouteSpec(
        "DELETE", Endpoints.CHARACTER_HUNTER_EDGE_DETAIL, NO_CONTENT, None
    )

    # Character hunter edge perks
    CHARACTERS_HUNTER_EDGE_PERKS_LIST = RouteSpec(
        "GET", Endpoints.CHARACTER_HUNTER_EDGE_PERKS, PAGINATED, Perk
    )
    CHARACTERS_HUNTER_EDGE_PERKS_GET = RouteSpec(
        "GET", Endpoints.CHARACTER_HUNTER_EDGE_PERK_DETAIL, SINGLE, Perk
    )
    CHARACTERS_HUNTER_EDGE_PERKS_CREATE = RouteSpec(
        "POST", Endpoints.CHARACTER_HUNTER_EDGE_PERKS, SINGLE, Perk
    )
    CHARACTERS_HUNTER_EDGE_PERKS_DELETE = RouteSpec(
        "DELETE", Endpoints.CHARACTER_HUNTER_EDGE_PERK_DETAIL, NO_CONTENT, None
    )

    # Character generation
    CHARACTERS_AUTOGENERATE = RouteSpec("POST", Endpoints.AUTOGENERATE, SINGLE, Character)
    CHARACTERS_CHARGEN_START = RouteSpec(
        "POST", Endpoints.CHARGEN_START, SINGLE, ChargenSessionResponse
    )
    CHARACTERS_CHARGEN_FINALIZE = RouteSpec("POST", Endpoints.CHARGEN_FINALIZE, SINGLE, Character)
    CHARACTERS_CHARGEN_SESSIONS_LIST = RouteSpec(
        "GET", Endpoints.CHARGEN_SESSIONS, LIST, ChargenSessionResponse
    )
    CHARACTERS_CHARGEN_SESSION_GET = RouteSpec(
        "GET", Endpoints.CHARGEN_SESSION, SINGLE, ChargenSessionResponse
    )

    # Character traits
    CHARACTER_TRAITS_LIST = RouteSpec("GET", Endpoints.CHARACTER_TRAITS, PAGINATED, CharacterTrait)
    CHARACTER_TRAITS_GET = RouteSpec("GET", Endpoints.CHARACTER_TRAIT, SINGLE, CharacterTrait)
    CHARACTER_TRAITS_DELETE = RouteSpec("DELETE", Endpoints.CHARACTER_TRAIT, NO_CONTENT, None)
    CHARACTER_TRAITS_ASSIGN = RouteSpec(
        "POST", Endpoints.CHARACTER_TRAIT_ASSIGN, SINGLE, CharacterTrait
    )
    CHARACTER_TRAITS_CREATE = RouteSpec(
        "POST", Endpoints.CHARACTER_TRAIT_CREATE, SINGLE, CharacterTrait
    )
    CHARACTER_TRAITS_VALUE_OPTIONS = RouteSpec(
        "GET", Endpoints.CHARACTER_TRAIT_VALUE_OPTIONS, SINGLE, CharacterTraitValueOptionsResponse
    )
    CHARACTER_TRAITS_VALUE_UPDATE = RouteSpec(
        "PUT", Endpoints.CHARACTER_TRAIT_VALUE, SINGLE, CharacterTrait
    )

    # Blueprint sections
    BLUEPRINT_SECTIONS_LIST = RouteSpec(
        "GET", Endpoints.BLUEPRINT_SECTIONS, PAGINATED, SheetSection
    )
    BLUEPRINT_SECTIONS_GET = RouteSpec(
        "GET", Endpoints.BLUEPRINT_SECTION_DETAIL, SINGLE, SheetSection
    )

    # Blueprint categories
    BLUEPRINT_CATEGORIES_LIST = RouteSpec(
        "GET", Endpoints.BLUEPRINT_CATEGORIES, PAGINATED, TraitCategory
    )
    BLUEPRINT_CATEGORIES_GET = RouteSpec(
        "GET", Endpoints.BLUEPRINT_CATEGORY_DETAIL, SINGLE, TraitCategory
    )
    BLUEPRINT_CATEGORIES_TRAITS = RouteSpec(
        "GET", Endpoints.BLUEPRINT_CATEGORY_TRAITS, PAGINATED, Trait
    )

    # Blueprint traits
    BLUEPRINT_TRAITS_LIST = RouteSpec("GET", Endpoints.BLUEPRINT_TRAITS, PAGINATED, Trait)
    BLUEPRINT_TRAITS_GET = RouteSpec("GET", Endpoints.BLUEPRINT_TRAIT_DETAIL, SINGLE, Trait)

    # Blueprint concepts
    BLUEPRINT_CONCEPTS_LIST = RouteSpec("GET", Endpoints.CONCEPTS, PAGINATED, CharacterConcept)
    BLUEPRINT_CONCEPTS_GET = RouteSpec("GET", Endpoints.CONCEPT_DETAIL, SINGLE, CharacterConcept)

    # Blueprint vampire clans
    BLUEPRINT_VAMPIRE_CLANS_LIST = RouteSpec("GET", Endpoints.VAMPIRE_CLANS, PAGINATED, VampireClan)
    BLUEPRINT_VAMPIRE_CLANS_GET = RouteSpec(
        "GET", Endpoints.VAMPIRE_CLAN_DETAIL, SINGLE, VampireClan
    )

    # Blueprint werewolf tribes
    BLUEPRINT_WEREWOLF_TRIBES_LIST = RouteSpec(
        "GET", Endpoints.WEREWOLF_TRIBES, PAGINATED, WerewolfTribe
    )
    BLUEPRINT_WEREWOLF_TRIBES_GET = RouteSpec(
        "GET", Endpoints.WEREWOLF_TRIBE_DETAIL, SINGLE, WerewolfTribe
    )

    # Blueprint werewolf auspices
    BLUEPRINT_WEREWOLF_AUSPICES_LIST = RouteSpec(
        "GET", Endpoints.WEREWOLF_AUSPICES, PAGINATED, WerewolfAuspice
    )
    BLUEPRINT_WEREWOLF_AUSPICES_GET = RouteSpec(
        "GET", Endpoints.WEREWOLF_AUSPICE_DETAIL, SINGLE, WerewolfAuspice
    )

    # Blueprint werewolf gifts
    BLUEPRINT_WEREWOLF_GIFTS_LIST = RouteSpec(
        "GET", Endpoints.WEREWOLF_GIFTS, PAGINATED, WerewolfGift
    )
    BLUEPRINT_WEREWOLF_GIFTS_GET = RouteSpec(
        "GET", Endpoints.WEREWOLF_GIFT_DETAIL, SINGLE, WerewolfGift
    )

    # Blueprint werewolf rites
    BLUEPRINT_WEREWOLF_RITES_LIST = RouteSpec(
        "GET", Endpoints.WEREWOLF_RITES, PAGINATED, WerewolfRite
    )
    BLUEPRINT_WEREWOLF_RITES_GET = RouteSpec(
        "GET", Endpoints.WEREWOLF_RITE_DETAIL, SINGLE, WerewolfRite
    )

    # Blueprint hunter edges
    BLUEPRINT_HUNTER_EDGES_LIST = RouteSpec("GET", Endpoints.HUNTER_EDGES, PAGINATED, HunterEdge)
    BLUEPRINT_HUNTER_EDGES_GET = RouteSpec("GET", Endpoints.HUNTER_EDGE_DETAIL, SINGLE, HunterEdge)

    # Blueprint hunter edge perks
    BLUEPRINT_HUNTER_EDGE_PERKS_LIST = RouteSpec(
        "GET", Endpoints.HUNTER_EDGE_PERKS, PAGINATED, HunterEdgePerk
    )
    BLUEPRINT_HUNTER_EDGE_PERKS_GET = RouteSpec(
        "GET", Endpoints.HUNTER_EDGE_PERK_DETAIL, SINGLE, HunterEdgePerk
    )

    # Dictionary
    DICTIONARY_LIST = RouteSpec("GET", Endpoints.DICTIONARY_TERMS, PAGINATED, DictionaryTerm)
    DICTIONARY_GET = RouteSpec("GET", Endpoints.DICTIONARY_TERM, SINGLE, DictionaryTerm)
    DICTIONARY_CREATE = RouteSpec("POST", Endpoints.DICTIONARY_TERMS, SINGLE, DictionaryTerm)
    DICTIONARY_UPDATE = RouteSpec("PUT", Endpoints.DICTIONARY_TERM, SINGLE, DictionaryTerm)
    DICTIONARY_DELETE = RouteSpec("DELETE", Endpoints.DICTIONARY_TERM, NO_CONTENT, None)

    # Dicerolls
    DICEROLLS_LIST = RouteSpec("GET", Endpoints.DICEROLLS, PAGINATED, Diceroll)
    DICEROLLS_GET = RouteSpec("GET", Endpoints.DICEROLL, SINGLE, Diceroll)
    DICEROLLS_CREATE = RouteSpec("POST", Endpoints.DICEROLLS, SINGLE, Diceroll)
    DICEROLLS_QUICKROLL = RouteSpec("POST", Endpoints.DICEROLL_QUICKROLL, SINGLE, Diceroll)

    # Options
    OPTIONS_GET = RouteSpec("GET", Endpoints.OPTIONS, RAW_JSON, None)
