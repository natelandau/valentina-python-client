"""Options and enumerations service."""

import json
from typing import TYPE_CHECKING

from vclient.endpoints import Endpoints
from vclient.services.base import BaseService

if TYPE_CHECKING:
    from vclient.client import VClient


class OptionsService(BaseService):
    """Service for interacting with the Options and Enumerations API."""

    def __init__(self, client: "VClient", company_id: str) -> None:
        """Initialize the service.

        Args:
            client: The VClient instance to use for requests.
            company_id: The ID of the company to operate within.
        """
        super().__init__(client)
        self._company_id = company_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id plus any extra params."""
        return endpoint.format(company_id=self._company_id, **kwargs)

    # -------------------------------------------------------------------------
    # Options and Enumerations Methods
    # -------------------------------------------------------------------------

    async def get_options(self) -> dict[str, dict[str, list[str] | dict[str, str]]]:
        """Retrieve all options and enumerations for the api.

        Returns:
            A dictionary of options and enumerations for the api.
        """
        response = await self._get(self._format_endpoint(Endpoints.OPTIONS))
        return json.loads(response.content)
