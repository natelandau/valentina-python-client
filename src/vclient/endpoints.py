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
