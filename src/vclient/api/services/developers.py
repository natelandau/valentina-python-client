"""Service for interacting with the Developer API."""

from pydantic import ValidationError as PydanticValidationError

from vclient.api.endpoints import Endpoints
from vclient.api.exceptions import RequestValidationError
from vclient.api.models.developers import (
    MeDeveloper,
    MeDeveloperWithApiKey,
    UpdateMeDeveloperRequest,
)
from vclient.api.services.base import BaseService


class DeveloperService(BaseService):
    """Service for managing the current developer's profile in the Valentina API.

    Provides methods to retrieve and update the authenticated developer's account,
    as well as regenerate API keys.

    Example:
        >>> async with VClient() as client:
        ...     me = await client.developer.get_me()
        ...     print(f"Logged in as: {me.username}")
    """

    async def get_me(self) -> MeDeveloper:
        """Retrieve the current developer's profile.

        Returns the developer account associated with the current API key.
        Use this to verify authentication and view account details.

        Returns:
            The MeDeveloper object with the current developer's details.

        Raises:
            AuthenticationError: If the API key is invalid or missing.
        """
        response = await self._get(Endpoints.DEVELOPER_ME)
        return MeDeveloper.model_validate(response.json())

    async def update_me(
        self,
        *,
        username: str | None = None,
        email: str | None = None,
    ) -> MeDeveloper:
        """Update the current developer's profile.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            username: New username for the developer.
            email: New email address for the developer.

        Returns:
            The updated MeDeveloper object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        try:
            body = UpdateMeDeveloperRequest(
                username=username,
                email=email,
            )
        except PydanticValidationError as e:
            raise RequestValidationError(e) from e

        response = await self._patch(
            Endpoints.DEVELOPER_ME,
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return MeDeveloper.model_validate(response.json())

    async def regenerate_api_key(self) -> MeDeveloperWithApiKey:
        """Generate a new API key for the current developer.

        The current key will be immediately invalidated and all cached
        authentication data will be cleared.

        **Be certain to save the API key from the response. It will not be displayed again.**

        Returns:
            The MeDeveloperWithApiKey object containing the new API key.

        Raises:
            AuthenticationError: If the current API key is invalid.
        """
        response = await self._post(Endpoints.DEVELOPER_ME_NEW_KEY)
        return MeDeveloperWithApiKey.model_validate(response.json())
