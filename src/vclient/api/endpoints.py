"""API endpoint paths for the Valentina API.

Centralized location for all API endpoint paths to avoid magic strings throughout the codebase.
"""


class Endpoints:
    """Container for all API endpoint paths.

    Use these constants when making API requests to ensure consistency and enable easy refactoring.

    Example:
        >>> response = await self._get(Endpoints.COMPANIES)
        >>> response = await self._get(Endpoints.company(company_id))
    """

    # Companies endpoints
    COMPANIES = "/api/v1/companies"

    @staticmethod
    def company(company_id: str) -> str:
        """Get the endpoint path for a specific company.

        Args:
            company_id: The ID of the company.

        Returns:
            The formatted endpoint path.
        """
        return f"/api/v1/companies/{company_id}"

    @staticmethod
    def company_access(company_id: str) -> str:
        """Get the endpoint path for granting company access.

        Args:
            company_id: The ID of the company.

        Returns:
            The formatted endpoint path.
        """
        return f"/api/v1/companies/{company_id}/access"
