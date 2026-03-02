# AUTO-GENERATED — do not edit. Run 'uv run duty generate_sync' to regenerate.
"""Service for interacting with the Developer API."""

from vclient._sync.services.base import SyncBaseService
from vclient.endpoints import Endpoints
from vclient.models import MeDeveloper, MeDeveloperUpdate, MeDeveloperWithApiKey


class SyncDeveloperService(SyncBaseService):
    """Service for managing the current developer's profile in the Valentina API.

    Provides methods to retrieve and update the authenticated developer's account,
    as well as regenerate API keys.

    Example:
        >>> async with SyncVClient() as client:
        ...     me = await client.developer.get_me()
        ...     print(f"Logged in as: {me.username}")
    """

    def get_me(self) -> MeDeveloper:
        """Retrieve the current developer's profile.

        Returns the developer account associated with the current API key.
        Use this to verify authentication and view account details.

        Returns:
            The MeDeveloper object with the current developer's details.

        Raises:
            AuthenticationError: If the API key is invalid or missing.
        """
        response = self._get(Endpoints.DEVELOPER_ME)
        return MeDeveloper.model_validate(response.json())

    def update_me(self, request: MeDeveloperUpdate | None = None, **kwargs) -> MeDeveloper:
        """Update the current developer's profile.

        Only include fields that need to be changed; omitted fields remain unchanged.

        Args:
            request: A MeDeveloperUpdate model, OR pass fields as keyword arguments.
            **kwargs: Fields for MeDeveloperUpdate if request is not provided.
                Accepts: username (str | None), email (str | None).

        Returns:
            The updated MeDeveloper object.

        Raises:
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = (
            request if request is not None else self._validate_request(MeDeveloperUpdate, **kwargs)
        )
        response = self._patch(
            Endpoints.DEVELOPER_ME,
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return MeDeveloper.model_validate(response.json())

    def regenerate_api_key(self) -> MeDeveloperWithApiKey:
        """Generate a new API key for the current developer.

        The current key will be immediately invalidated and all cached
        authentication data will be cleared.

        **Be certain to save the API key from the response. It will not be displayed again.**

        Returns:
            The MeDeveloperWithApiKey object containing the new API key.

        Raises:
            AuthenticationError: If the current API key is invalid.
        """
        response = self._post(Endpoints.DEVELOPER_ME_NEW_KEY)
        return MeDeveloperWithApiKey.model_validate(response.json())
