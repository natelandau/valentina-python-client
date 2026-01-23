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
