"""API endpoint paths for the Valentina API.

Centralized location for all API endpoint paths to avoid magic strings throughout the codebase.

For endpoints with dynamic parameters, use .format() to substitute values:
    >>> Endpoints.COMPANY.format(company_id="123")
    '/api/v1/companies/123'
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

    # Companies endpoints
    COMPANIES = f"{_BASE}/companies"
    COMPANY = f"{_BASE}/companies/{{company_id}}"
    COMPANY_ACCESS = f"{_BASE}/companies/{{company_id}}/access"

    # Global Admin endpoints
    ADMIN_DEVELOPERS = f"{_BASE}/admin/developers"
    ADMIN_DEVELOPER = f"{_BASE}/admin/developers/{{developer_id}}"
    ADMIN_DEVELOPER_NEW_KEY = f"{_BASE}/admin/developers/{{developer_id}}/new-key"

    # Developer endpoints (self-service)
    DEVELOPER_ME = f"{_BASE}/developers/me"
    DEVELOPER_ME_NEW_KEY = f"{_BASE}/developers/me/new-key"

    # User endpoints
    USERS = f"{_BASE}/companies/{{company_id}}/users"
    USER = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}"
    USER_STATISTICS = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/statistics"
    # User asset endpoints
    USER_ASSETS = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/assets"
    USER_ASSET = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/assets/{{asset_id}}"
    USER_ASSET_UPLOAD = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/assets/upload"
    # User experience endpoints
    USER_EXPERIENCE_CAMPAIGN = (
        f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/experience/{{campaign_id}}"
    )
    USER_EXPERIENCE_XP_ADD = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/experience/xp/add"
    USER_EXPERIENCE_XP_REMOVE = (
        f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/experience/xp/remove"
    )
    USER_EXPERIENCE_CP_ADD = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/experience/cp/add"
    # User notes endpoints
    USER_NOTES = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/notes"
    USER_NOTE = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/notes/{{note_id}}"
    # User quickroll endpoints
    USER_QUICKROLLS = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/quickrolls"
    USER_QUICKROLL = (
        f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/quickrolls/{{quickroll_id}}"
    )

    # Campaign endpoints
    CAMPAIGNS = f"{_BASE}/companies/{{company_id}}/users/{{user_id}}/campaigns"
    CAMPAIGN = f"{CAMPAIGNS}/{{campaign_id}}"
    CAMPAIGN_STATISTICS = f"{CAMPAIGN}/statistics"
    # Campaign asset endpoints
    CAMPAIGN_ASSETS = f"{CAMPAIGN}/assets"
    CAMPAIGN_ASSET = f"{CAMPAIGN_ASSETS}/{{asset_id}}"
    CAMPAIGN_ASSET_UPLOAD = f"{CAMPAIGN_ASSETS}/upload"
    # Campaign note endpoints
    CAMPAIGN_NOTES = f"{CAMPAIGN}/notes"
    CAMPAIGN_NOTE = f"{CAMPAIGN_NOTES}/{{note_id}}"

    # Campaign book endpoints
    CAMPAIGN_BOOKS = f"{CAMPAIGN}/books"
    CAMPAIGN_BOOK = f"{CAMPAIGN_BOOKS}/{{book_id}}"
    CAMPAIGN_BOOK_NUMBER = f"{CAMPAIGN_BOOK}/number"
    # Book note endpoints
    BOOK_NOTES = f"{CAMPAIGN_BOOK}/notes"
    BOOK_NOTE = f"{BOOK_NOTES}/{{note_id}}"
    # Book asset endpoints
    BOOK_ASSETS = f"{CAMPAIGN_BOOK}/assets"
    BOOK_ASSET_UPLOAD = f"{BOOK_ASSETS}/upload"
    BOOK_ASSET = f"{BOOK_ASSETS}/{{asset_id}}"

    # Book chapter endpoints
    BOOK_CHAPTERS = f"{CAMPAIGN_BOOK}/chapters"
    BOOK_CHAPTER = f"{BOOK_CHAPTERS}/{{chapter_id}}"
    BOOK_CHAPTER_NUMBER = f"{BOOK_CHAPTER}/number"
    # Book chapter note endpoints
    BOOK_CHAPTER_NOTES = f"{BOOK_CHAPTER}/notes"
    BOOK_CHAPTER_NOTE = f"{BOOK_CHAPTER_NOTES}/{{note_id}}"
    # Book chapter asset endpoints
    BOOK_CHAPTER_ASSETS = f"{BOOK_CHAPTER}/assets"
    BOOK_CHAPTER_ASSET_UPLOAD = f"{BOOK_CHAPTER_ASSETS}/upload"
    BOOK_CHAPTER_ASSET = f"{BOOK_CHAPTER_ASSETS}/{{asset_id}}"

    # Character endpoints
    CHARACTERS = f"{CAMPAIGN}/characters"
    CHARACTER = f"{CHARACTERS}/{{character_id}}"
    CHARACTER_STATISTICS = f"{CHARACTER}/statistics"
    # Character asset endpoints
    CHARACTER_ASSETS = f"{CHARACTER}/assets"
    CHARACTER_ASSET = f"{CHARACTER_ASSETS}/{{asset_id}}"
    CHARACTER_ASSET_UPLOAD = f"{CHARACTER_ASSETS}/upload"
    # Character note endpoints
    CHARACTER_NOTES = f"{CHARACTER}/notes"
    CHARACTER_NOTE = f"{CHARACTER_NOTES}/{{note_id}}"
    # Character inventory endpoints
    CHARACTER_INVENTORY = f"{CHARACTER}/inventory"
    CHARACTER_INVENTORY_ITEM = f"{CHARACTER_INVENTORY}/{{item_id}}"
    # Werewolf Gifts
    CHARACTER_WEREWOLF_GIFTS = f"{CHARACTER}/gifts"
    CHARACTER_WEREWOLF_GIFT_DETAIL = f"{CHARACTER_WEREWOLF_GIFTS}/{{werewolf_gift_id}}"
    # Werewolf Rites
    CHARACTER_WEREWOLF_RITES = f"{CHARACTER}/rites"
    CHARACTER_WEREWOLF_RITE_DETAIL = f"{CHARACTER_WEREWOLF_RITES}/{{werewolf_rite_id}}"
    # Hunter Edges
    CHARACTER_HUNTER_EDGES = f"{CHARACTER}/edges"
    CHARACTER_HUNTER_EDGE_DETAIL = f"{CHARACTER_HUNTER_EDGES}/{{hunter_edge_id}}"
    # Hunter Edge Perks (nested under edges)
    CHARACTER_HUNTER_EDGE_PERKS = f"{CHARACTER_HUNTER_EDGE_DETAIL}/perks"
    CHARACTER_HUNTER_EDGE_PERK_DETAIL = f"{CHARACTER_HUNTER_EDGE_PERKS}/{{hunter_edge_perk_id}}"

    # Character trait endpoints
    CHARACTER_TRAITS = f"{CHARACTER}/traits"
    CHARACTER_TRAIT = f"{CHARACTER_TRAITS}/{{character_trait_id}}"
    CHARACTER_TRAIT_ASSIGN = f"{CHARACTER_TRAITS}/assign"
    CHARACTER_TRAIT_CREATE = f"{CHARACTER_TRAITS}/create"
    CHARACTER_TRAIT_INCREASE = f"{CHARACTER_TRAIT}/increase"
    CHARACTER_TRAIT_DECREASE = f"{CHARACTER_TRAIT}/decrease"
    CHARACTER_TRAIT_XP_PURCHASE = f"{CHARACTER_TRAIT}/xp/purchase"
    CHARACTER_TRAIT_XP_REFUND = f"{CHARACTER_TRAIT}/xp/refund"
    CHARACTER_TRAIT_STARTINGPOINTS_PURCHASE = f"{CHARACTER_TRAIT}/startingpoints/purchase"
    CHARACTER_TRAIT_STARTINGPOINTS_REFUND = f"{CHARACTER_TRAIT}/startingpoints/refund"
