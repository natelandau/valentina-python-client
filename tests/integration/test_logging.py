"""Tests for structured logging across the vclient package."""

import logging

import httpx
import pytest
import respx
from loguru import logger

from vclient import VClient
from vclient.services.base import BaseService

pytestmark = pytest.mark.anyio


class ConcreteService(BaseService):
    """Concrete implementation of BaseService for testing."""


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
        vclient_records = [r for r in caplog.records if r.name.startswith("vclient")]
        assert len(vclient_records) == 0

    @respx.mock
    async def test_logging_enabled_captures_request_logs(self, base_url, api_key, caplog):
        """Verify logs appear after explicit enable."""
        # Given: Logging is explicitly enabled
        logger.enable("vclient")

        respx.get(f"{base_url}/test").respond(200, json={"ok": True})

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key) as client:
                    service = ConcreteService(client)
                    await service._get("/test")

            # Then: vclient log records appear
            vclient_records = [r for r in caplog.records if r.name.startswith("vclient")]
            assert len(vclient_records) > 0
        finally:
            logger.disable("vclient")


class TestRequestLogging:
    """Tests for HTTP request lifecycle logging."""

    @respx.mock
    async def test_log_request_start_and_response(self, base_url, api_key, caplog):
        """Verify 'Send GET' and 'Receive 200' logged at DEBUG."""
        # Given: Logging is enabled
        logger.enable("vclient")

        respx.get(f"{base_url}/test").respond(200, json={"ok": True})

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key) as client:
                    service = ConcreteService(client)
                    await service._get("/test")

            # Then: "Send GET" and "Receive 200" messages are present at DEBUG
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Send GET /test" in m for m in messages)
            assert any("Receive 200" in m and "GET" in m and "/test" in m for m in messages)

            debug_levels = [
                r.levelno
                for r in caplog.records
                if r.name.startswith("vclient")
                and ("Send GET" in r.message or "Receive 200" in r.message)
            ]
            assert all(level == logging.DEBUG for level in debug_levels)
        finally:
            logger.disable("vclient")

    @respx.mock
    async def test_log_retry_on_rate_limit(self, base_url, api_key, caplog, mocker):
        """Verify 'Retry GET /test after rate limit' logged at WARNING."""
        # Given: Logging is enabled and sleep is mocked
        logger.enable("vclient")
        mocker.patch("vclient.services.base.asyncio.sleep")

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

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key) as client:
                    service = ConcreteService(client)
                    await service._get("/test")

            # Then: Rate limit retry warning is present
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Retry GET /test after rate limit" in m for m in messages)

            warning_records = [
                r
                for r in caplog.records
                if r.name.startswith("vclient") and "Retry GET /test after rate limit" in r.message
            ]
            assert all(r.levelno == logging.WARNING for r in warning_records)
        finally:
            logger.disable("vclient")

    @respx.mock
    async def test_log_retry_on_server_error(self, base_url, api_key, caplog, mocker):
        """Verify 'Retry GET /test after 500' logged at WARNING."""
        # Given: Logging is enabled and sleep is mocked
        logger.enable("vclient")
        mocker.patch("vclient.services.base.asyncio.sleep")

        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.Response(500, json={"detail": "Server error"}),
                httpx.Response(200, json={"ok": True}),
            ]
        )

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key) as client:
                    service = ConcreteService(client)
                    await service._get("/test")

            # Then: Server error retry warning is present
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Retry GET /test after 500" in m for m in messages)

            warning_records = [
                r
                for r in caplog.records
                if r.name.startswith("vclient") and "Retry GET /test after 500" in r.message
            ]
            assert all(r.levelno == logging.WARNING for r in warning_records)
        finally:
            logger.disable("vclient")

    @respx.mock
    async def test_log_retry_on_network_error(self, base_url, api_key, caplog, mocker):
        """Verify 'Retry GET /test after ConnectError' logged at WARNING."""
        # Given: Logging is enabled and sleep is mocked
        logger.enable("vclient")
        mocker.patch("vclient.services.base.asyncio.sleep")

        respx.get(f"{base_url}/test").mock(
            side_effect=[
                httpx.ConnectError("Connection refused"),
                httpx.Response(200, json={"ok": True}),
            ]
        )

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key) as client:
                    service = ConcreteService(client)
                    await service._get("/test")

            # Then: Network error retry warning is present
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Retry GET /test after ConnectError" in m for m in messages)

            warning_records = [
                r
                for r in caplog.records
                if r.name.startswith("vclient")
                and "Retry GET /test after ConnectError" in r.message
            ]
            assert all(r.levelno == logging.WARNING for r in warning_records)
        finally:
            logger.disable("vclient")

    @respx.mock
    async def test_log_max_retries_exhausted(self, base_url, api_key, caplog, mocker):
        """Verify 'Exhaust retries for GET /test' logged at ERROR."""
        # Given: Logging is enabled and sleep is mocked
        logger.enable("vclient")
        mocker.patch("vclient.services.base.asyncio.sleep")

        respx.get(f"{base_url}/test").respond(
            429,
            json={"detail": "Rate limited"},
            headers={"RateLimit": '"default";r=0;t=1'},
        )

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key) as client:
                    service = ConcreteService(client)
                    with pytest.raises(Exception):  # noqa: B017
                        await service._get("/test")

            # Then: Exhaust retries error is present
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Exhaust retries for GET /test" in m for m in messages)

            error_records = [
                r
                for r in caplog.records
                if r.name.startswith("vclient") and "Exhaust retries for GET /test" in r.message
            ]
            assert all(r.levelno == logging.ERROR for r in error_records)
        finally:
            logger.disable("vclient")


class TestErrorClassificationLogging:
    """Tests for error classification logging in _raise_for_status."""

    @respx.mock
    async def test_log_authentication_error(self, base_url, api_key, caplog):
        """Verify 'Fail authentication' logged at ERROR for 401."""
        # Given: Logging is enabled
        logger.enable("vclient")

        respx.get(f"{base_url}/test").respond(401, json={"detail": "Unauthorized"})

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key) as client:
                    service = ConcreteService(client)
                    with pytest.raises(Exception):  # noqa: B017
                        await service._get("/test")

            # Then: Authentication error is present at ERROR
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Fail authentication" in m for m in messages)

            error_records = [
                r
                for r in caplog.records
                if r.name.startswith("vclient") and "Fail authentication" in r.message
            ]
            assert all(r.levelno == logging.ERROR for r in error_records)
        finally:
            logger.disable("vclient")

    @respx.mock
    async def test_log_not_found_at_debug(self, base_url, api_key, caplog):
        """Verify 'Return 404' logged at DEBUG."""
        # Given: Logging is enabled
        logger.enable("vclient")

        respx.get(f"{base_url}/test").respond(404, json={"detail": "Not found"})

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key) as client:
                    service = ConcreteService(client)
                    with pytest.raises(Exception):  # noqa: B017
                        await service._get("/test")

            # Then: 404 message is present at DEBUG
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Return 404" in m for m in messages)

            debug_records = [
                r
                for r in caplog.records
                if r.name.startswith("vclient") and "Return 404" in r.message
            ]
            assert all(r.levelno == logging.DEBUG for r in debug_records)
        finally:
            logger.disable("vclient")

    @respx.mock
    async def test_log_validation_error(self, base_url, api_key, caplog):
        """Verify 'Reject POST /test with validation error' logged at WARNING."""
        # Given: Logging is enabled
        logger.enable("vclient")

        respx.post(f"{base_url}/test").respond(400, json={"detail": "Validation failed"})

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key) as client:
                    service = ConcreteService(client)
                    with pytest.raises(Exception):  # noqa: B017
                        await service._post("/test", json={"bad": "data"})

            # Then: Validation error warning is present
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Reject POST /test with validation error" in m for m in messages)

            warning_records = [
                r
                for r in caplog.records
                if r.name.startswith("vclient")
                and "Reject POST /test with validation error" in r.message
            ]
            assert all(r.levelno == logging.WARNING for r in warning_records)
        finally:
            logger.disable("vclient")

    @respx.mock
    async def test_log_conflict_error(self, base_url, api_key, caplog):
        """Verify 'Return 409 conflict' logged at WARNING."""
        # Given: Logging is enabled
        logger.enable("vclient")

        respx.post(f"{base_url}/test").respond(409, json={"detail": "Conflict"})

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key) as client:
                    service = ConcreteService(client)
                    with pytest.raises(Exception):  # noqa: B017
                        await service._post("/test", json={"data": "value"})

            # Then: Conflict warning is present
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Return 409 conflict" in m for m in messages)

            warning_records = [
                r
                for r in caplog.records
                if r.name.startswith("vclient") and "Return 409 conflict" in r.message
            ]
            assert all(r.levelno == logging.WARNING for r in warning_records)
        finally:
            logger.disable("vclient")


class TestClientLifecycleLogging:
    """Tests for VClient lifecycle logging."""

    async def test_log_client_initialization(self, base_url, api_key, caplog):
        """Verify 'Initialize VClient' with base_url logged at DEBUG."""
        # Given: Logging is enabled
        logger.enable("vclient")

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                async with VClient(base_url=base_url, api_key=api_key):
                    pass

            # Then: Initialization message is present at DEBUG
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Initialize VClient" in m and base_url in m for m in messages)

            debug_records = [
                r
                for r in caplog.records
                if r.name.startswith("vclient") and "Initialize VClient" in r.message
            ]
            assert all(r.levelno == logging.DEBUG for r in debug_records)
        finally:
            logger.disable("vclient")

    async def test_log_client_close(self, base_url, api_key, caplog):
        """Verify 'Close VClient' logged at DEBUG."""
        # Given: Logging is enabled
        logger.enable("vclient")

        try:
            with caplog.at_level(logging.DEBUG, logger="vclient"):
                client = VClient(base_url=base_url, api_key=api_key)
                await client.close()

            # Then: Close message is present at DEBUG
            messages = [r.message for r in caplog.records if r.name.startswith("vclient")]
            assert any("Close VClient" in m for m in messages)

            debug_records = [
                r
                for r in caplog.records
                if r.name.startswith("vclient") and "Close VClient" in r.message
            ]
            assert all(r.levelno == logging.DEBUG for r in debug_records)
        finally:
            logger.disable("vclient")
