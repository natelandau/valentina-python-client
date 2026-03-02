# AUTO-GENERATED — do not edit. Run 'uv run duty generate_sync' to regenerate.
"""Base service class for API services."""

import random
import time
import uuid
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, TypeVar

import httpx
from loguru import logger
from pydantic import BaseModel, ValidationError as PydanticValidationError

from vclient.constants import (
    DEFAULT_PAGE_LIMIT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_600_UPPER_BOUND,
    IDEMPOTENCY_KEY_HEADER,
    IDEMPOTENT_HTTP_METHODS,
    MAX_PAGE_LIMIT,
    RATE_LIMIT_HEADER,
)
from vclient.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    RequestValidationError,
    ServerError,
    ValidationError,
)
from vclient.models.pagination import PaginatedResponse

T = TypeVar("T", bound=BaseModel)
if TYPE_CHECKING:
    from vclient._sync.client import SyncVClient


class SyncBaseService:
    """Base class for all API services.

    Provides common functionality for making HTTP requests and handling responses.
    """

    def __init__(self, client: "SyncVClient") -> None:
        """Initialize the service.

        Args:
            client: The SyncVClient instance to use for requests.
        """
        self._client = client

    @property
    def _http(self) -> httpx.Client:
        """Get the HTTP client from the parent SyncVClient."""
        return self._client._http

    @staticmethod
    def _generate_idempotency_key() -> str:
        """Generate a new UUID v4 idempotency key.

        Returns:
            A unique idempotency key string.
        """
        return str(uuid.uuid4())

    def _validate_request(self, request_class: type[T], **kwargs: Any) -> T:
        """Validate and create a request model, converting Pydantic errors.

        Args:
            request_class: The Pydantic model class to instantiate.
            **kwargs: Fields to pass to the model constructor.

        Returns:
            The validated request model instance.

        Raises:
            RequestValidationError: If validation fails.
        """
        try:
            return request_class(**kwargs)
        except PydanticValidationError as e:
            raise RequestValidationError(e) from e

    def _calculate_backoff_delay(self, attempt: int, retry_after: int | None) -> float:
        """Calculate the delay before the next retry attempt.

        Uses exponential backoff with jitter: base_delay * (2 ** attempt) + random jitter.
        If retry_after is provided from the RateLimit header, uses that as the base.

        Args:
            attempt: The current attempt number (0-indexed).
            retry_after: Seconds to wait from the RateLimit header, or None.

        Returns:
            Number of seconds to wait before retrying.
        """
        config = self._client._config
        base_delay = config.retry_delay
        if retry_after is not None and retry_after > 0:
            base_delay = max(base_delay, float(retry_after))
        delay = base_delay * 2**attempt
        jitter = random.uniform(0, delay * 0.25)
        return delay + jitter

    @staticmethod
    def _is_retryable_method(method: str, headers: dict[str, str] | None) -> bool:
        """Check if a request method is safe to retry.

        Idempotent methods (GET, PUT, DELETE) are always safe. Non-idempotent
        methods (POST, PATCH) are only safe if an idempotency key is present.

        Args:
            method: The HTTP method (uppercase).
            headers: The request headers, or None.

        Returns:
            True if the request is safe to retry.
        """
        if method in IDEMPOTENT_HTTP_METHODS:
            return True
        return IDEMPOTENCY_KEY_HEADER in (headers or {})

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        files: Any | None = None,
    ) -> httpx.Response:
        """Make an HTTP request with automatic retry on transient errors.

        Retries on rate limits (429), server errors (5xx in retry_statuses),
        and network errors (ConnectError, TimeoutException). Non-idempotent
        methods (POST, PATCH) only retry on 5xx/network errors when an
        idempotency key header is present. Rate limit retries (429) always
        apply regardless of method.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            path: API endpoint path (will be appended to base_url).
            params: Query parameters.
            json: JSON body data.
            data: Form data.
            headers: Additional headers to include in the request.
            files: Files to upload (passed through to httpx).

        Returns:
            The HTTP response.

        Raises:
            RateLimitError: When rate limit is exceeded and max retries are exhausted.
            ServerError: When server error occurs and max retries are exhausted.
            httpx.ConnectError: When connection fails and max retries are exhausted.
            httpx.TimeoutException: When request times out and max retries are exhausted.
            APIError: For other API error responses.
        """
        config = self._client._config
        max_attempts = config.max_retries + 1 if config.auto_retry_rate_limit else 1
        retry_statuses = config.retry_statuses
        request_logger = logger.bind(method=method, url=path)
        request_logger.debug("Send request")
        last_error: RateLimitError | ServerError | None = None
        for attempt in range(max_attempts):
            try:
                response = self._http.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json,
                    data=data,
                    headers=headers,
                    files=files,
                )
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                if not self._is_retryable_method(method, headers) or attempt >= max_attempts - 1:
                    raise
                error_type = type(exc).__name__
                delay = self._calculate_backoff_delay(attempt, retry_after=None)
                request_logger.bind(
                    error_type=error_type,
                    attempt=attempt + 1,
                    max_attempts=max_attempts,
                    delay=delay,
                ).warning("Retry after network error")
                time.sleep(delay)
                continue
            try:
                self._raise_for_status(response, method, path)
                elapsed_ms = response.elapsed.total_seconds() * 1000
                request_logger.bind(status=response.status_code, elapsed_ms=elapsed_ms).debug(
                    "Receive response"
                )
                return response
            except RateLimitError as e:
                last_error = e
                if attempt >= max_attempts - 1:
                    break
                delay = self._calculate_backoff_delay(attempt, e.retry_after)
                request_logger.bind(
                    attempt=attempt + 1, max_attempts=max_attempts, delay=delay
                ).warning("Retry after rate limit")
                time.sleep(delay)
            except ServerError as e:
                if e.status_code not in retry_statuses or not self._is_retryable_method(
                    method, headers
                ):
                    raise
                last_error = e
                if attempt >= max_attempts - 1:
                    break
                delay = self._calculate_backoff_delay(attempt, retry_after=None)
                request_logger.bind(
                    status=e.status_code,
                    attempt=attempt + 1,
                    max_attempts=max_attempts,
                    delay=delay,
                ).warning("Retry after server error")
                time.sleep(delay)
        if last_error is not None:
            request_logger.bind(attempts=max_attempts).error("Exhaust retries")
            raise last_error
        msg = "Unexpected state: no response or error"
        raise RuntimeError(msg)

    def _raise_for_status(self, response: httpx.Response, method: str, url: str) -> None:
        """Raise appropriate exception for error responses.

        Args:
            response: The HTTP response to check.
            method: The HTTP method of the request.
            url: The URL path of the request.

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
        error_logger = logger.bind(method=method, url=url, status=status_code)
        if status_code == 429:
            retry_after = self._parse_retry_after(response)
            remaining = self._parse_remaining_tokens(response)
            raise RateLimitError(
                message, status_code, response_data, retry_after=retry_after, remaining=remaining
            )
        if status_code == 401:
            error_logger.error("Fail authentication")
            raise AuthenticationError(message, status_code, response_data)
        if status_code == 403:
            error_logger.error("Deny authorization")
            raise AuthorizationError(message, status_code, response_data)
        if status_code == 404:
            error_logger.debug("Return 404")
            raise NotFoundError(message, status_code, response_data)
        if status_code == 400:
            error_logger.warning("Reject with validation error")
            raise ValidationError(message, status_code, response_data)
        if status_code == 409:
            error_logger.warning("Return 409 conflict")
            raise ConflictError(message, status_code, response_data)
        if HTTP_500_INTERNAL_SERVER_ERROR <= status_code < HTTP_600_UPPER_BOUND:
            raise ServerError(message, status_code, response_data)
        raise APIError(message, status_code, response_data)

    @staticmethod
    def _parse_rate_limit_header_value(header_value: str, parameter: str) -> int | None:
        """Parse a parameter value from a RateLimit header.

        The RateLimit header format is: "policy_name";r=REMAINING;t=RETRY_SECONDS
        Multiple policies are comma-separated.

        Args:
            header_value: The full RateLimit header value.
            parameter: The parameter to extract (e.g., "r" for remaining, "t" for retry).

        Returns:
            The parsed integer value, or None if not found or invalid.
        """
        search_pattern = f";{parameter}="
        if search_pattern not in header_value:
            return None
        try:
            value_start = header_value.split(search_pattern)[1]
            value_str = value_start.split(";")[0].split(",")[0].strip()
            return int(value_str)
        except (IndexError, ValueError):
            return None

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> int | None:
        """Parse the retry time from response headers.

        First checks the RateLimit header for the "t" parameter (seconds until next token),
        then falls back to the standard Retry-After header.

        Args:
            response: The HTTP response containing rate limit headers.

        Returns:
            Number of seconds to wait, or None if no retry info is available.
        """
        rate_limit_header = response.headers.get(RATE_LIMIT_HEADER)
        if rate_limit_header:
            retry_time = SyncBaseService._parse_rate_limit_header_value(rate_limit_header, "t")
            if retry_time is not None:
                return retry_time
        retry_after = response.headers.get("Retry-After")
        if retry_after is None:
            return None
        try:
            return int(retry_after)
        except ValueError:
            return None

    @staticmethod
    def _parse_remaining_tokens(response: httpx.Response) -> int | None:
        """Parse the remaining tokens from the RateLimit header.

        Args:
            response: The HTTP response containing the RateLimit header.

        Returns:
            Number of remaining tokens, or None if not available.
        """
        rate_limit_header = response.headers.get(RATE_LIMIT_HEADER)
        if not rate_limit_header:
            return None
        return SyncBaseService._parse_rate_limit_header_value(rate_limit_header, "r")

    def _get(self, path: str, *, params: dict[str, Any] | None = None) -> httpx.Response:
        """Make a GET request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            The HTTP response.
        """
        return self._request("GET", path, params=params)

    def _build_idempotency_headers(self, idempotency_key: str | None) -> dict[str, str] | None:
        """Build headers dict with idempotency key if provided.

        Args:
            idempotency_key: Optional idempotency key for the request.

        Returns:
            Headers dict with idempotency key, or None if no key provided.
        """
        if idempotency_key is None:
            return None
        return {IDEMPOTENCY_KEY_HEADER: idempotency_key}

    @staticmethod
    def _build_params(**kwargs: Any) -> dict[str, Any] | None:
        """Build query params dict, filtering out None values.

        Args:
            **kwargs: Key-value pairs for query parameters.

        Returns:
            Dict with non-None values, or None if all values are None.
        """
        params = {k: v for k, v in kwargs.items() if v is not None}
        return params or None

    def _post(
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
        if idempotency_key is None and self._client._config.auto_idempotency_keys:
            idempotency_key = self._generate_idempotency_key()
        return self._request(
            "POST",
            path,
            json=json,
            data=data,
            params=params,
            headers=self._build_idempotency_headers(idempotency_key),
        )

    def _put(
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
        if idempotency_key is None and self._client._config.auto_idempotency_keys:
            idempotency_key = self._generate_idempotency_key()
        return self._request(
            "PUT",
            path,
            json=json,
            data=data,
            params=params,
            headers=self._build_idempotency_headers(idempotency_key),
        )

    def _patch(
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
        if idempotency_key is None and self._client._config.auto_idempotency_keys:
            idempotency_key = self._generate_idempotency_key()
        return self._request(
            "PATCH",
            path,
            json=json,
            data=data,
            params=params,
            headers=self._build_idempotency_headers(idempotency_key),
        )

    def _delete(self, path: str, *, params: dict[str, Any] | None = None) -> httpx.Response:
        """Make a DELETE request.

        Args:
            path: API endpoint path.
            params: Query parameters.

        Returns:
            The HTTP response.
        """
        return self._request("DELETE", path, params=params)

    def _post_file(
        self, path: str, *, file: tuple[str, bytes, str], idempotency_key: str | None = None
    ) -> httpx.Response:
        """Make a POST request with a file upload (multipart/form-data).

        Args:
            path: API endpoint path.
            file: Tuple of (filename, content, content_type) for the file to upload.
            idempotency_key: Optional idempotency key for safe retries.

        Returns:
            The HTTP response.

        Raises:
            ServerError: When server error occurs and max retries are exhausted.
            RateLimitError: When rate limit is exceeded and max retries are exhausted.
            APIError: For other API error responses.
        """
        filename, content, content_type = file
        return self._request(
            "POST",
            path,
            files={"data": (filename, content, content_type)},
            headers=self._build_idempotency_headers(idempotency_key),
        )

    def _get_paginated(
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
            "limit": min(max(limit, 0), MAX_PAGE_LIMIT),
            "offset": max(offset, 0),
            **(params or {}),
        }
        response = self._get(path, params=request_params)
        return PaginatedResponse.from_dict(response.json())

    def _get_paginated_as(
        self,
        path: str,
        model_class: type[T],
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        params: dict[str, Any] | None = None,
    ) -> PaginatedResponse[T]:
        """Make a paginated GET request and parse items into the given model class.

        Args:
            path: API endpoint path.
            model_class: Pydantic model class to validate each item into.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).
            params: Additional query parameters.

        Returns:
            A PaginatedResponse containing validated model instances.
        """
        response = self._get_paginated(path, limit=limit, offset=offset, params=params)
        return PaginatedResponse(
            items=[model_class.model_validate(item) for item in response.items],
            limit=response.limit,
            offset=response.offset,
            total=response.total,
        )

    def _iter_all_pages(
        self, path: str, *, limit: int = MAX_PAGE_LIMIT, params: dict[str, Any] | None = None
    ) -> Iterator[dict[str, Any]]:
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
            page = self._get_paginated(path, limit=limit, offset=offset, params=params)
            for item in page.items:
                yield item
            if not page.has_more:
                break
            offset = page.next_offset

    def _get_all(
        self, path: str, *, limit: int = MAX_PAGE_LIMIT, params: dict[str, Any] | None = None
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
        return [item for item in self._iter_all_pages(path, limit=limit, params=params)]
