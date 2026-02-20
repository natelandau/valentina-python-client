"""Tests for structured logging across the vclient package."""

import logging
from typing import Any

import httpx
import pytest
import respx
from loguru import logger

from vclient import VClient
from vclient.services.base import BaseService

pytestmark = pytest.mark.anyio


class ConcreteService(BaseService):
    """Concrete implementation of BaseService for testing."""


@pytest.fixture
def enable_vclient_logging():
    """Enable vclient logging for the test, disable on teardown."""
    logger.enable("vclient")
    yield
    logger.disable("vclient")


def _vclient_records(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    """Return all caplog records from the vclient namespace."""
    return [r for r in caplog.records if r.name.startswith("vclient")]


def _find_record(caplog: pytest.LogCaptureFixture, message: str) -> Any:
    """Find the first vclient record matching the given message."""
    for r in caplog.records:
        if r.name.startswith("vclient") and r.message == message:
            return r
    return None


class TestLoggingInitialization:
    """Tests for logging initialization and default behavior."""

    @respx.mock
    async def test_logging_disabled_by_default(self, base_url, api_key, caplog):
        """Verify no vclient logs appear without explicit enable."""
        # Given: A client with logging at default state (disabled)
        respx.get(f"{base_url}/test").respond(200, json={"ok": True})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                await service._get("/test")

        # Then: No vclient log records appear
        assert len(_vclient_records(caplog)) == 0

    @respx.mock
    async def test_logging_enabled_captures_request_logs(
        self, base_url, api_key, caplog, enable_vclient_logging
    ):
        """Verify logs appear after explicit enable."""
        # Given: A mocked endpoint
        respx.get(f"{base_url}/test").respond(200, json={"ok": True})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request with logging enabled
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                await service._get("/test")

        # Then: vclient log records appear
        assert len(_vclient_records(caplog)) > 0


class TestRequestLogging:
    """Tests for HTTP request lifecycle logging."""

    @respx.mock
    async def test_log_request_start_and_response(
        self, base_url, api_key, caplog, enable_vclient_logging
    ):
        """Verify 'Send request' and 'Receive response' logged at DEBUG with structured fields."""
        # Given: A mocked endpoint
        respx.get(f"{base_url}/test").respond(200, json={"ok": True})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a GET request
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                await service._get("/test")

        # Then: "Send request" is present at DEBUG with correct structured fields
        send = _find_record(caplog, "Send request")
        assert send is not None
        assert send.levelno == logging.DEBUG
        assert send.extra["method"] == "GET"
        assert send.extra["url"] == "/test"

        # Then: "Receive response" is present at DEBUG with correct structured fields
        receive = _find_record(caplog, "Receive response")
        assert receive is not None
        assert receive.levelno == logging.DEBUG
        assert receive.extra["method"] == "GET"
        assert receive.extra["url"] == "/test"
        assert receive.extra["status"] == 200

    @respx.mock
    async def test_log_retry_on_rate_limit(
        self, base_url, api_key, caplog, mocker, enable_vclient_logging
    ):
        """Verify 'Retry after rate limit' logged at WARNING with structured fields."""
        # Given: Sleep is mocked to avoid delays
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: An endpoint that returns 429 then succeeds
        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.Response(
                    429,
                    json={"detail": "Rate limited"},
                    headers={"RateLimit": '"default";r=0;t=1'},
                ),
                httpx.Response(200, json={"ok": True}),
            ]
        )

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that gets rate limited
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                await service._get("/test")

        # Then: Rate limit retry warning is present with structured fields
        record = _find_record(caplog, "Retry after rate limit")
        assert record is not None
        assert record.levelno == logging.WARNING
        assert record.extra["method"] == "GET"
        assert record.extra["url"] == "/test"

    @respx.mock
    async def test_log_retry_on_server_error(
        self, base_url, api_key, caplog, mocker, enable_vclient_logging
    ):
        """Verify 'Retry after server error' logged at WARNING with structured fields."""
        # Given: Sleep is mocked to avoid delays
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: An endpoint that returns 500 then succeeds
        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.Response(500, json={"detail": "Server error"}),
                httpx.Response(200, json={"ok": True}),
            ]
        )

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that hits a server error
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                await service._get("/test")

        # Then: Server error retry warning is present with structured fields
        record = _find_record(caplog, "Retry after server error")
        assert record is not None
        assert record.levelno == logging.WARNING
        assert record.extra["method"] == "GET"
        assert record.extra["url"] == "/test"
        assert record.extra["status"] == 500

    @respx.mock
    async def test_log_retry_on_network_error(
        self, base_url, api_key, caplog, mocker, enable_vclient_logging
    ):
        """Verify 'Retry after network error' logged at WARNING with structured fields."""
        # Given: Sleep is mocked to avoid delays
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: An endpoint that raises ConnectError then succeeds
        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.ConnectError("Connection refused"),
                httpx.Response(200, json={"ok": True}),
            ]
        )

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that hits a network error
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                await service._get("/test")

        # Then: Network error retry warning is present with structured fields
        record = _find_record(caplog, "Retry after network error")
        assert record is not None
        assert record.levelno == logging.WARNING
        assert record.extra["method"] == "GET"
        assert record.extra["url"] == "/test"
        assert record.extra["error_type"] == "ConnectError"

    @respx.mock
    async def test_log_max_retries_exhausted(
        self, base_url, api_key, caplog, mocker, enable_vclient_logging
    ):
        """Verify 'Exhaust retries' logged at ERROR with structured fields."""
        # Given: Sleep is mocked to avoid delays
        mocker.patch("vclient.services.base.asyncio.sleep")

        # Given: An endpoint that always returns 429
        respx.get(f"{base_url}/test").respond(
            429,
            json={"detail": "Rate limited"},
            headers={"RateLimit": '"default";r=0;t=1'},
        )

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that exhausts retries
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                with pytest.raises(Exception):  # noqa: B017
                    await service._get("/test")

        # Then: Exhaust retries error is present with structured fields
        record = _find_record(caplog, "Exhaust retries")
        assert record is not None
        assert record.levelno == logging.ERROR
        assert record.extra["method"] == "GET"
        assert record.extra["url"] == "/test"


class TestErrorClassificationLogging:
    """Tests for error classification logging in _raise_for_status."""

    @respx.mock
    async def test_log_authentication_error(
        self, base_url, api_key, caplog, enable_vclient_logging
    ):
        """Verify 'Fail authentication' logged at ERROR with structured fields for 401."""
        # Given: An endpoint that returns 401
        respx.get(f"{base_url}/test").respond(401, json={"detail": "Unauthorized"})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that fails authentication
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                with pytest.raises(Exception):  # noqa: B017
                    await service._get("/test")

        # Then: Authentication error is present at ERROR with structured fields
        record = _find_record(caplog, "Fail authentication")
        assert record is not None
        assert record.levelno == logging.ERROR
        assert record.extra["status"] == 401

    @respx.mock
    async def test_log_authorization_error(self, base_url, api_key, caplog, enable_vclient_logging):
        """Verify 'Deny authorization' logged at ERROR with structured fields for 403."""
        # Given: An endpoint that returns 403
        respx.get(f"{base_url}/test").respond(403, json={"detail": "Forbidden"})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that fails authorization
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                with pytest.raises(Exception):  # noqa: B017
                    await service._get("/test")

        # Then: Authorization error is present at ERROR with structured fields
        record = _find_record(caplog, "Deny authorization")
        assert record is not None
        assert record.levelno == logging.ERROR
        assert record.extra["status"] == 403

    @respx.mock
    async def test_log_not_found_at_debug(self, base_url, api_key, caplog, enable_vclient_logging):
        """Verify 'Return 404' logged at DEBUG with structured fields."""
        # Given: An endpoint that returns 404
        respx.get(f"{base_url}/test").respond(404, json={"detail": "Not found"})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request to a missing resource
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                with pytest.raises(Exception):  # noqa: B017
                    await service._get("/test")

        # Then: 404 message is present at DEBUG with structured fields
        record = _find_record(caplog, "Return 404")
        assert record is not None
        assert record.levelno == logging.DEBUG
        assert record.extra["status"] == 404
        assert record.extra["method"] == "GET"
        assert record.extra["url"] == "/test"

    @respx.mock
    async def test_log_validation_error(self, base_url, api_key, caplog, enable_vclient_logging):
        """Verify 'Reject with validation error' logged at WARNING with structured fields."""
        # Given: An endpoint that returns 400
        respx.post(f"{base_url}/test").respond(400, json={"detail": "Validation failed"})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that fails validation
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                with pytest.raises(Exception):  # noqa: B017
                    await service._post("/test", json={"bad": "data"})

        # Then: Validation error warning is present with structured fields
        record = _find_record(caplog, "Reject with validation error")
        assert record is not None
        assert record.levelno == logging.WARNING
        assert record.extra["method"] == "POST"
        assert record.extra["url"] == "/test"

    @respx.mock
    async def test_log_conflict_error(self, base_url, api_key, caplog, enable_vclient_logging):
        """Verify 'Return 409 conflict' logged at WARNING with structured fields."""
        # Given: An endpoint that returns 409
        respx.post(f"{base_url}/test").respond(409, json={"detail": "Conflict"})

        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Making a request that conflicts
            async with VClient(base_url=base_url, api_key=api_key) as client:
                service = ConcreteService(client)
                with pytest.raises(Exception):  # noqa: B017
                    await service._post("/test", json={"data": "value"})

        # Then: Conflict warning is present with structured fields
        record = _find_record(caplog, "Return 409 conflict")
        assert record is not None
        assert record.levelno == logging.WARNING
        assert record.extra["method"] == "POST"
        assert record.extra["url"] == "/test"


class TestClientLifecycleLogging:
    """Tests for VClient lifecycle logging."""

    async def test_log_client_initialization(
        self, base_url, api_key, caplog, enable_vclient_logging
    ):
        """Verify 'Initialize VClient' logged at INFO with structured fields."""
        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Creating a client
            async with VClient(base_url=base_url, api_key=api_key):
                pass

        # Then: Initialization message is present at INFO with structured fields
        record = _find_record(caplog, "Initialize VClient")
        assert record is not None
        assert record.levelno == logging.INFO
        assert record.extra["base_url"] == base_url

    async def test_log_client_close(self, base_url, api_key, caplog, enable_vclient_logging):
        """Verify 'Close VClient' logged at INFO with structured fields."""
        with caplog.at_level(logging.DEBUG, logger="vclient"):
            # When: Closing a client
            client = VClient(base_url=base_url, api_key=api_key)
            await client.close()

        # Then: Close message is present at INFO with structured fields
        record = _find_record(caplog, "Close VClient")
        assert record is not None
        assert record.levelno == logging.INFO
        assert record.extra["base_url"] == base_url
