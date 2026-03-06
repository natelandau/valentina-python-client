"""Fake async API client for testing downstream applications.

FakeVClient is a drop-in replacement for VClient that uses httpx.MockTransport
instead of real HTTP. All real service classes work unmodified.
"""

from __future__ import annotations

from typing import Any

import httpx

from vclient.client import VClient
from vclient.testing._router import _FakeRouter


class FakeVClient(VClient):
    """A fake VClient for testing that uses mock HTTP transport.

    Drop-in replacement for VClient that returns auto-generated responses
    for all endpoints. Registers itself as the default client so factory
    functions like campaigns_service() work without configuration.

    Example:
        ```python
        from vclient.testing import FakeVClient
        from vclient import campaigns_service

        async with FakeVClient() as client:
            campaigns = campaigns_service("user123")
            result = await campaigns.list_all()
        ```
    """

    def __init__(
        self,
        *,
        default_company_id: str = "fake-company",
        set_as_default: bool = True,
        **kwargs: Any,
    ) -> None:
        self._router = _FakeRouter()
        super().__init__(
            base_url="https://fake.valentina-api.test",
            api_key="fake-api-key",
            default_company_id=default_company_id,
            set_as_default=set_as_default,
            **kwargs,
        )

    def _create_http_client(self) -> httpx.AsyncClient:
        """Create an HTTP client backed by the fake router."""
        return httpx.AsyncClient(
            transport=httpx.MockTransport(self._router.handle),
            base_url="https://fake.valentina-api.test",
        )

    def add_route(
        self,
        method: str,
        pattern: str,
        *,
        json: dict[str, Any],
        status_code: int = 200,
    ) -> None:
        """Add a custom route override.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE, PUT).
            pattern: Endpoint pattern from vclient.endpoints.Endpoints.
            json: The JSON response body to return.
            status_code: HTTP status code to return (default 200).
        """
        self._router.add_route(method, pattern, json=json, status_code=status_code)
