"""API endpoint paths for the Valentina API.

Centralized location for all API endpoint paths to avoid magic strings throughout the codebase.
"""


class Endpoints:
    """Container for all API endpoint paths.

    Use these constants when making API requests to ensure consistency and enable easy refactoring.

    Example:
        >>> response = await self._get(Endpoints.COMPANIES)
        >>> response = await self._get(Endpoints.COMPANY.format(company_id=company_id))
    """

    _BASE = "/api/v1"

    # System endpoints
    HEALTH = f"{_BASE}/health"

    # Global Admin endpoints
    ADMIN_DEVELOPERS = f"{_BASE}/admin/developers"
    ADMIN_DEVELOPER = f"{_BASE}/admin/developers/{{developer_id}}"
    ADMIN_DEVELOPER_NEW_KEY = f"{_BASE}/admin/developers/{{developer_id}}/new-key"

    # Developer endpoints (self-service)
    DEVELOPER_ME = f"{_BASE}/developers/me"
    DEVELOPER_ME_NEW_KEY = f"{_BASE}/developers/me/new-key"

    # Companies endpoints
    COMPANIES = f"{_BASE}/companies"
    COMPANY = f"{COMPANIES}/{{company_id}}"
    COMPANY_ACCESS = f"{COMPANY}/access"

    # User endpoints
    USERS = f"{COMPANY}/users"
    USER = f"{USERS}/{{user_id}}"
    USER_STATISTICS = f"{USER}/statistics"
    USER_ASSETS = f"{USER}/assets"
    USER_ASSET = f"{USER_ASSETS}/{{asset_id}}"
    USER_ASSET_UPLOAD = f"{USER_ASSETS}/upload"
    USER_EXPERIENCE_CAMPAIGN = f"{USER}/experience/{{campaign_id}}"
    USER_EXPERIENCE_XP_ADD = f"{USER}/experience/xp/add"
    USER_EXPERIENCE_XP_REMOVE = f"{USER}/experience/xp/remove"
    USER_EXPERIENCE_CP_ADD = f"{USER}/experience/cp/add"
    USER_NOTES = f"{USER}/notes"
    USER_NOTE = f"{USER_NOTES}/{{note_id}}"
    USER_QUICKROLLS = f"{USER}/quickrolls"
    USER_QUICKROLL = f"{USER_QUICKROLLS}/{{quickroll_id}}"

    # Campaign endpoints
    CAMPAIGNS = f"{USER}/campaigns"
    CAMPAIGN = f"{CAMPAIGNS}/{{campaign_id}}"
    CAMPAIGN_STATISTICS = f"{CAMPAIGN}/statistics"
    CAMPAIGN_ASSETS = f"{CAMPAIGN}/assets"
    CAMPAIGN_ASSET = f"{CAMPAIGN_ASSETS}/{{asset_id}}"
    CAMPAIGN_ASSET_UPLOAD = f"{CAMPAIGN_ASSETS}/upload"
    CAMPAIGN_NOTES = f"{CAMPAIGN}/notes"
    CAMPAIGN_NOTE = f"{CAMPAIGN_NOTES}/{{note_id}}"

    # Campaign book endpoints
    CAMPAIGN_BOOKS = f"{CAMPAIGN}/books"
    CAMPAIGN_BOOK = f"{CAMPAIGN_BOOKS}/{{book_id}}"
    CAMPAIGN_BOOK_NUMBER = f"{CAMPAIGN_BOOK}/number"
    BOOK_NOTES = f"{CAMPAIGN_BOOK}/notes"
    BOOK_NOTE = f"{BOOK_NOTES}/{{note_id}}"
    BOOK_ASSETS = f"{CAMPAIGN_BOOK}/assets"
    BOOK_ASSET_UPLOAD = f"{BOOK_ASSETS}/upload"
    BOOK_ASSET = f"{BOOK_ASSETS}/{{asset_id}}"

    # Book chapter endpoints
    BOOK_CHAPTERS = f"{CAMPAIGN_BOOK}/chapters"
    BOOK_CHAPTER = f"{BOOK_CHAPTERS}/{{chapter_id}}"
    BOOK_CHAPTER_NUMBER = f"{BOOK_CHAPTER}/number"
    BOOK_CHAPTER_NOTES = f"{BOOK_CHAPTER}/notes"
    BOOK_CHAPTER_NOTE = f"{BOOK_CHAPTER_NOTES}/{{note_id}}"
    BOOK_CHAPTER_ASSETS = f"{BOOK_CHAPTER}/assets"
    BOOK_CHAPTER_ASSET_UPLOAD = f"{BOOK_CHAPTER_ASSETS}/upload"
    BOOK_CHAPTER_ASSET = f"{BOOK_CHAPTER_ASSETS}/{{asset_id}}"

    # Character endpoints
    CHARACTERS = f"{CAMPAIGN}/characters"
    CHARACTER = f"{CHARACTERS}/{{character_id}}"
    CHARACTER_STATISTICS = f"{CHARACTER}/statistics"
    CHARACTER_ASSETS = f"{CHARACTER}/assets"
    CHARACTER_ASSET = f"{CHARACTER_ASSETS}/{{asset_id}}"
    CHARACTER_ASSET_UPLOAD = f"{CHARACTER_ASSETS}/upload"
    CHARACTER_NOTES = f"{CHARACTER}/notes"
    CHARACTER_NOTE = f"{CHARACTER_NOTES}/{{note_id}}"
    CHARACTER_INVENTORY = f"{CHARACTER}/inventory"
    CHARACTER_INVENTORY_ITEM = f"{CHARACTER_INVENTORY}/{{item_id}}"
    # Character Specials
    CHARACTER_WEREWOLF_GIFTS = f"{CHARACTER}/gifts"
    CHARACTER_WEREWOLF_GIFT_DETAIL = f"{CHARACTER_WEREWOLF_GIFTS}/{{werewolf_gift_id}}"
    CHARACTER_WEREWOLF_RITES = f"{CHARACTER}/rites"
    CHARACTER_WEREWOLF_RITE_DETAIL = f"{CHARACTER_WEREWOLF_RITES}/{{werewolf_rite_id}}"
    CHARACTER_HUNTER_EDGES = f"{CHARACTER}/edges"
    CHARACTER_HUNTER_EDGE_DETAIL = f"{CHARACTER_HUNTER_EDGES}/{{hunter_edge_id}}"
    CHARACTER_HUNTER_EDGE_PERKS = f"{CHARACTER_HUNTER_EDGE_DETAIL}/perks"
    CHARACTER_HUNTER_EDGE_PERK_DETAIL = f"{CHARACTER_HUNTER_EDGE_PERKS}/{{hunter_edge_perk_id}}"

    # Character RNG generation
    AUTOGENERATE = f"{CHARACTERS}/autogenerate"
    CHARGEN_START = f"{CHARACTERS}/chargen/start"
    CHARGEN_FINALIZE = f"{CHARACTERS}/chargen/finalize"

    # Character trait endpoints
    CHARACTER_TRAITS = f"{CHARACTER}/traits"
    CHARACTER_TRAIT_ASSIGN = f"{CHARACTER_TRAITS}/assign"
    CHARACTER_TRAIT_CREATE = f"{CHARACTER_TRAITS}/create"
    CHARACTER_TRAIT = f"{CHARACTER_TRAITS}/{{character_trait_id}}"
    CHARACTER_TRAIT_VALUE_OPTIONS = f"{CHARACTER_TRAIT}/value-options"
    CHARACTER_TRAIT_VALUE = f"{CHARACTER_TRAIT}/value"

    # Character Blueprint endpoints
    BLUEPRINT_BASE = f"{COMPANY}/characterblueprint"
    BLUEPRINT_SECTIONS = f"{BLUEPRINT_BASE}/{{game_version}}/sections"
    BLUEPRINT_SECTION_DETAIL = f"{BLUEPRINT_SECTIONS}/{{section_id}}"
    BLUEPRINT_CATEGORIES = f"{BLUEPRINT_SECTION_DETAIL}/categories"
    BLUEPRINT_CATEGORY_DETAIL = f"{BLUEPRINT_CATEGORIES}/{{category_id}}"
    BLUEPRINT_CATEGORY_TRAITS = f"{BLUEPRINT_CATEGORY_DETAIL}/traits"
    BLUEPRINT_TRAITS = f"{BLUEPRINT_BASE}/traits"
    BLUEPRINT_TRAIT_DETAIL = f"{BLUEPRINT_TRAITS}/{{trait_id}}"
    CONCEPTS = f"{BLUEPRINT_BASE}/concepts"
    CONCEPT_DETAIL = f"{CONCEPTS}/{{concept_id}}"
    VAMPIRE_CLANS = f"{BLUEPRINT_BASE}/vampire-clans"
    VAMPIRE_CLAN_DETAIL = f"{VAMPIRE_CLANS}/{{vampire_clan_id}}"
    WEREWOLF_TRIBES = f"{BLUEPRINT_BASE}/werewolf-tribes"
    WEREWOLF_TRIBE_DETAIL = f"{WEREWOLF_TRIBES}/{{werewolf_tribe_id}}"
    WEREWOLF_AUSPICES = f"{BLUEPRINT_BASE}/werewolf-auspices"
    WEREWOLF_AUSPICE_DETAIL = f"{WEREWOLF_AUSPICES}/{{werewolf_auspice_id}}"
    WEREWOLF_GIFTS = f"{BLUEPRINT_BASE}/werewolf-gifts"
    WEREWOLF_GIFT_DETAIL = f"{WEREWOLF_GIFTS}/{{werewolf_gift_id}}"
    WEREWOLF_RITES = f"{BLUEPRINT_BASE}/werewolf-rites"
    WEREWOLF_RITE_DETAIL = f"{WEREWOLF_RITES}/{{werewolf_rite_id}}"
    HUNTER_EDGES = f"{BLUEPRINT_BASE}/hunter-edges"
    HUNTER_EDGE_DETAIL = f"{HUNTER_EDGES}/{{hunter_edge_id}}"
    HUNTER_EDGE_PERKS = f"{HUNTER_EDGE_DETAIL}/perks"
    HUNTER_EDGE_PERK_DETAIL = f"{HUNTER_EDGE_PERKS}/{{hunter_edge_perk_id}}"

    # Dictionary endpoints
    DICTIONARY_TERMS = f"{COMPANY}/dictionaries"
    DICTIONARY_TERM = f"{DICTIONARY_TERMS}/{{term_id}}"

    # Dice Rolls
    DICEROLLS = f"{USER}/dicerolls"
    DICEROLL = f"{DICEROLLS}/{{diceroll_id}}"
    DICEROLL_QUICKROLL = f"{DICEROLLS}/quickroll"

    # Options and enumerations
    OPTIONS = f"{COMPANY}/options"
