# AUTO-GENERATED — do not edit. Run 'uv run duty generate_sync' to regenerate.
"""Options and enumerations service."""

import json
from typing import TYPE_CHECKING

from vclient._sync.services.base import SyncBaseService
from vclient.endpoints import Endpoints

if TYPE_CHECKING:
    from vclient._sync.client import SyncVClient


class SyncOptionsService(SyncBaseService):
    """Service for interacting with the Options and Enumerations API."""

    def __init__(self, client: "SyncVClient", company_id: str) -> None:
        """Initialize the service.

        Args:
            client: The SyncVClient instance to use for requests.
            company_id: The ID of the company to operate within.
        """
        super().__init__(client)
        self._company_id = company_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id plus any extra params."""
        return endpoint.format(company_id=self._company_id, **kwargs)

    def get_options(self) -> dict[str, dict[str, list[str] | dict[str, str]]]:
        """Retrieve all options and enumerations for the api.

        Returns:
            A dictionary of options and enumerations for the api.
        """
        response = self._get(self._format_endpoint(Endpoints.OPTIONS))
        return json.loads(response.content)
