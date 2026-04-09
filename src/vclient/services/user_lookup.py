"""Service for cross-company user lookup."""

from vclient.endpoints import Endpoints
from vclient.models import UserLookupResult
from vclient.services.base import BaseService


class UserLookupService(BaseService):
    """Service for looking up users across companies.

    Discover which companies a person has a user record in by searching
    via email, Discord ID, Google ID, or GitHub ID.

    Example:
        >>> async with VClient() as client:
        ...     results = await client.user_lookup.by_email("alice@example.com")
        ...     for r in results:
        ...         print(f"{r.company_name}: {r.role}")
    """

    async def by_email(self, email: str) -> list[UserLookupResult]:
        """Look up a user by email address.

        Args:
            email: Exact email address to search for.

        Returns:
            List of companies where a matching user was found. Empty list if no matches.
        """
        response = await self._get(Endpoints.USERS_LOOKUP, params={"email": email})
        return [UserLookupResult.model_validate(item) for item in response.json()]

    async def by_discord_id(self, discord_id: str) -> list[UserLookupResult]:
        """Look up a user by Discord profile ID.

        Args:
            discord_id: Discord profile ID to search for.

        Returns:
            List of companies where a matching user was found. Empty list if no matches.
        """
        response = await self._get(Endpoints.USERS_LOOKUP, params={"discord_id": discord_id})
        return [UserLookupResult.model_validate(item) for item in response.json()]

    async def by_google_id(self, google_id: str) -> list[UserLookupResult]:
        """Look up a user by Google profile ID.

        Args:
            google_id: Google profile ID to search for.

        Returns:
            List of companies where a matching user was found. Empty list if no matches.
        """
        response = await self._get(Endpoints.USERS_LOOKUP, params={"google_id": google_id})
        return [UserLookupResult.model_validate(item) for item in response.json()]

    async def by_github_id(self, github_id: str) -> list[UserLookupResult]:
        """Look up a user by GitHub profile ID.

        Args:
            github_id: GitHub profile ID to search for.

        Returns:
            List of companies where a matching user was found. Empty list if no matches.
        """
        response = await self._get(Endpoints.USERS_LOOKUP, params={"github_id": github_id})
        return [UserLookupResult.model_validate(item) for item in response.json()]
