"""Base service class for API services."""

import uuid
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

import httpx

from vclient.api.constants import (
    DEFAULT_PAGE_LIMIT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_600_UPPER_BOUND,
    IDEMPOTENCY_KEY_HEADER,
    MAX_PAGE_LIMIT,
)
from vclient.api.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from vclient.api.models.pagination import PaginatedResponse

if TYPE_CHECKING:
    from vclient.api.client import VClient


class BaseService:
    """Base class for all API services.

    Provides common functionality for making HTTP requests and handling responses.
    """

    def __init__(self, client: "VClient") -> None:
        """Initialize the service.

        Args:
            client: The VClient instance to use for requests.
        """
        self._client = client

    @property
    def _http(self) -> httpx.AsyncClient:
        """Get the HTTP client from the parent VClient."""
        return self._client._http  # noqa: SLF001

    @staticmethod
    def _generate_idempotency_key() -> str:
        """Generate a new UUID v4 idempotency key.

        Returns:
            A unique idempotency key string.
        """
        return str(uuid.uuid4())

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Make an HTTP request and handle errors.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            path: API endpoint path (will be appended to base_url).
            params: Query parameters.
            json: JSON body data.
            data: Form data.
            headers: Additional headers to include in the request.

        Returns:
            The HTTP response.

        Raises:
            APIError: For any API error responses.
        """
        response = await self._http.request(
            method=method,
            url=path,
            params=params,
            json=json,
            data=data,
            headers=headers,
        )

        self._raise_for_status(response)
        return response

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Raise appropriate exception for error responses.

        Args:
            response: The HTTP response to check.

        Raises:
            AuthenticationError: For 401 responses.
            AuthorizationError: For 403 responses.
            NotFoundError: For 404 responses.
            ValidationError: For 400 responses.
            ConflictError: For 409 responses.
            RateLimitError: For 429 responses.
            ServerError: For 5xx responses.
            APIError: For other error responses.
        """
        if response.is_success:
            return

        status_code = response.status_code
        try:
            response_data = response.json()
            message = response_data.get("detail", response.text)
        except (ValueError, KeyError, TypeError):
            response_data = {}
            message = response.text or f"HTTP {status_code}"

        error_map: dict[int, type[APIError]] = {
            400: ValidationError,
            401: AuthenticationError,
            403: AuthorizationError,
            404: NotFoundError,
            409: ConflictError,
            429: RateLimitError,
        }

        if status_code == 429:  # noqa: PLR2004
            retry_after = self._parse_retry_after(response)
            raise RateLimitError(message, status_code, response_data, retry_after=retry_after)

        if status_code in error_map:
            raise error_map[status_code](message, status_code, response_data)

        if HTTP_500_INTERNAL_SERVER_ERROR <= status_code < HTTP_600_UPPER_BOUND:
            raise ServerError(message, status_code, response_data)

        raise APIError(message, status_code, response_data)

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> int | None:
        """Parse the Retry-After header from a response.

        Args:
            response: The HTTP response containing the Retry-After header.

        Returns:
            Number of seconds to wait, or None if header is missing or invalid.
        """
        retry_after = response.headers.get("Retry-After")
        if retry_after is None:
            return None

        try:
            return int(retry_after)
        except ValueError:
            return None

    async def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make a GET request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            The HTTP response.
        """
        return await self._request("GET", path, params=params)

    def _build_idempotency_headers(
        self,
        idempotency_key: str | None,
    ) -> dict[str, str] | None:
        """Build headers dict with idempotency key if provided.

        Args:
            idempotency_key: Optional idempotency key for the request.

        Returns:
            Headers dict with idempotency key, or None if no key provided.
        """
        if idempotency_key is None:
            return None
        return {IDEMPOTENCY_KEY_HEADER: idempotency_key}

    async def _post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> httpx.Response:
        """Make a POST request.

        Args:
            path: API endpoint path.
            json: JSON body data.
            data: Form data.
            params: Query parameters.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The HTTP response.
        """
        return await self._request(
            "POST",
            path,
            json=json,
            data=data,
            params=params,
            headers=self._build_idempotency_headers(idempotency_key),
        )

    async def _put(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> httpx.Response:
        """Make a PUT request.

        Args:
            path: API endpoint path.
            json: JSON body data.
            data: Form data.
            params: Query parameters.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The HTTP response.
        """
        return await self._request(
            "PUT",
            path,
            json=json,
            data=data,
            params=params,
            headers=self._build_idempotency_headers(idempotency_key),
        )

    async def _patch(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> httpx.Response:
        """Make a PATCH request.

        Args:
            path: API endpoint path.
            json: JSON body data.
            data: Form data.
            params: Query parameters.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The HTTP response.
        """
        return await self._request(
            "PATCH",
            path,
            json=json,
            data=data,
            params=params,
            headers=self._build_idempotency_headers(idempotency_key),
        )

    async def _delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make a DELETE request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            The HTTP response.
        """
        return await self._request("DELETE", path, params=params)

    # -------------------------------------------------------------------------
    # Pagination Methods
    # -------------------------------------------------------------------------

    async def _get_paginated(
        self,
        path: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        params: dict[str, Any] | None = None,
    ) -> PaginatedResponse[dict[str, Any]]:
        """Make a paginated GET request.

        Args:
            path: API endpoint path.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).
            params: Additional query parameters.

        Returns:
            A PaginatedResponse containing the items and pagination metadata.
        """
        request_params = {
            "limit": min(max(limit, 0), MAX_PAGE_LIMIT),  # Clamp to valid range
            "offset": max(offset, 0),
            **(params or {}),
        }

        response = await self._get(path, params=request_params)
        return PaginatedResponse.from_dict(response.json())

    async def _iter_all_pages(
        self,
        path: str,
        *,
        limit: int = MAX_PAGE_LIMIT,
        params: dict[str, Any] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Iterate through all pages of a paginated endpoint.

        Yields individual items from each page, automatically fetching
        subsequent pages until all items have been retrieved.

        Args:
            path: API endpoint path.
            limit: Items per page (default 100 for efficiency).
            params: Additional query parameters.

        Yields:
            Individual items from the paginated response.

        Example:
            ```python
            async for user in self._iter_all_pages("/users"):
                print(user["name"])
            ```
        """
        offset = 0

        while True:
            page = await self._get_paginated(
                path,
                limit=limit,
                offset=offset,
                params=params,
            )

            for item in page.items:
                yield item

            if not page.has_more:
                break

            offset = page.next_offset

    async def _get_all(
        self,
        path: str,
        *,
        limit: int = MAX_PAGE_LIMIT,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch all items from a paginated endpoint.

        Convenience method that collects all items from _iter_all_pages
        into a list. Use _iter_all_pages for memory-efficient streaming
        of large datasets.

        Args:
            path: API endpoint path.
            limit: Items per page (default 100 for efficiency).
            params: Additional query parameters.

        Returns:
            A list of all items from all pages.
        """
        return [item async for item in self._iter_all_pages(path, limit=limit, params=params)]
