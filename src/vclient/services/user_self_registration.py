"""Service for user self-registration via SSO onboarding."""

from typing import TYPE_CHECKING

from vclient.endpoints import Endpoints
from vclient.models import User, UserRegisterDTO
from vclient.services.base import BaseService

if TYPE_CHECKING:
    from vclient.client import VClient


class UserSelfRegistrationService(BaseService):
    """Service for user self-registration via SSO onboarding.

    This service handles the registration endpoint that does not require
    an acting user (no On-Behalf-Of header). Authentication is via
    developer API key only.

    Example:
        >>> async with VClient() as client:
        ...     registration = client.user_self_registration()
        ...     user = await registration.register(
        ...         username="alice", email="alice@example.com"
        ...     )
    """

    def __init__(self, client: "VClient", company_id: str) -> None:
        """Initialize the service scoped to a specific company.

        Args:
            client: The VClient instance to use for requests.
            company_id: The ID of the company to register the user in.
        """
        super().__init__(client)
        self._company_id = company_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id plus any extra params."""
        return endpoint.format(company_id=self._company_id, **kwargs)

    async def register(
        self,
        request: UserRegisterDTO | None = None,
        **kwargs,
    ) -> User:
        """Register a new user via SSO onboarding.

        This endpoint is used during external auth provider flows and does
        not require admin privileges or an acting user. Only developer API
        key authentication is needed.

        Args:
            request: A UserRegisterDTO model, OR pass fields as keyword arguments.
            **kwargs: Fields for UserRegisterDTO if request is not provided.
                Accepts: username (str, required), email (str, required),
                name_first (str | None), name_last (str | None),
                discord_profile (DiscordProfileUpdate | None),
                google_profile (GoogleProfile | None),
                github_profile (GitHubProfile | None).

        Returns:
            The newly registered User object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = request if request is not None else self._validate_request(UserRegisterDTO, **kwargs)
        response = await self._post(
            self._format_endpoint(Endpoints.USER_REGISTER),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return User.model_validate(response.json())
