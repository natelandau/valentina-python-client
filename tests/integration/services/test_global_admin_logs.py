"""Tests for the server-log methods of vclient.services.global_admin."""

import pytest
import respx

from vclient.endpoints import Endpoints
from vclient.exceptions import AuthorizationError, ConflictError
from vclient.models import ServerLogEntry

pytestmark = pytest.mark.anyio


@pytest.fixture
def log_entries() -> list[dict]:
    """Return a sample server-log tail payload (newest first)."""
    return [
        {
            "timestamp": "2026-05-25T12:00:00.123Z",
            "level": "INFO",
            "name": "vapi.server",
            "message": "Request completed",
            "exception": None,
            "extra": {"status_code": 200, "path": "/api/v1/companies"},
            "raw": None,
        },
        {
            "timestamp": "2026-05-25T11:59:59.000Z",
            "level": "WARNING",
            "name": "vapi.server",
            "message": "Slow query",
            "exception": None,
            "extra": {},
            "raw": None,
        },
    ]


class TestTailLogs:
    """Tests for GlobalAdminService.tail_logs."""

    @respx.mock
    async def test_tail_logs_parses_array(self, vclient, base_url, log_entries):
        """Verify tail_logs returns ServerLogEntry objects in server order."""
        # Given: A mocked logs endpoint returning two entries (newest first)
        route = respx.get(f"{base_url}{Endpoints.ADMIN_LOGS}", params={"limit": "100"}).respond(
            200, json=log_entries
        )

        # When: Tailing logs with defaults
        result = await vclient.global_admin.tail_logs()

        # Then: Entries are parsed and order is preserved
        assert route.called
        assert len(result) == 2
        assert isinstance(result[0], ServerLogEntry)
        assert result[0].level == "INFO"
        assert result[1].level == "WARNING"
        assert result[0].extra == {"status_code": 200, "path": "/api/v1/companies"}

    @respx.mock
    async def test_tail_logs_forwards_level_and_limit(self, vclient, base_url):
        """Verify tail_logs forwards the level and limit query parameters."""
        # Given: A mocked endpoint expecting level and a custom limit
        route = respx.get(
            f"{base_url}{Endpoints.ADMIN_LOGS}", params={"level": "ERROR", "limit": "50"}
        ).respond(200, json=[])

        # When: Tailing only error-level entries with a custom limit
        result = await vclient.global_admin.tail_logs(level="ERROR", limit=50)

        # Then: The request carried both params and an empty list is returned
        assert route.called
        assert result == []

    @respx.mock
    async def test_tail_logs_clamps_limit_to_max(self, vclient, base_url):
        """Verify tail_logs clamps an over-range limit to the maximum."""
        # Given: A mocked endpoint expecting the clamped maximum limit
        route = respx.get(f"{base_url}{Endpoints.ADMIN_LOGS}", params={"limit": "500"}).respond(
            200, json=[]
        )

        # When: Requesting more than the maximum
        result = await vclient.global_admin.tail_logs(limit=10_000)

        # Then: The request used the clamped maximum and an empty list is returned
        assert route.called
        assert result == []

    @respx.mock
    async def test_tail_logs_clamps_limit_to_min(self, vclient, base_url):
        """Verify tail_logs clamps a below-range limit to the minimum."""
        # Given: A mocked endpoint expecting the clamped minimum limit
        route = respx.get(f"{base_url}{Endpoints.ADMIN_LOGS}", params={"limit": "1"}).respond(
            200, json=[]
        )

        # When: Requesting fewer than the minimum
        result = await vclient.global_admin.tail_logs(limit=0)

        # Then: The request used the clamped minimum and an empty list is returned
        assert route.called
        assert result == []

    @respx.mock
    async def test_tail_logs_raises_authorization_error(self, vclient, base_url):
        """Verify a 403 response raises AuthorizationError."""
        # Given: A mocked endpoint returning 403
        respx.get(f"{base_url}{Endpoints.ADMIN_LOGS}").respond(
            403, json={"detail": "Global admin required"}
        )

        # When/Then: Tailing logs raises AuthorizationError
        with pytest.raises(AuthorizationError):
            await vclient.global_admin.tail_logs()

    @respx.mock
    async def test_tail_logs_raises_conflict_when_disabled(self, vclient, base_url):
        """Verify a 409 response raises ConflictError when file logging is off."""
        # Given: A mocked endpoint returning 409
        respx.get(f"{base_url}{Endpoints.ADMIN_LOGS}").respond(
            409, json={"detail": "File logging is not enabled"}
        )

        # When/Then: Tailing logs raises ConflictError
        with pytest.raises(ConflictError):
            await vclient.global_admin.tail_logs()


class TestDownloadLogs:
    """Tests for GlobalAdminService.download_logs."""

    @respx.mock
    async def test_download_logs_returns_archive(self, vclient, base_url):
        """Verify download_logs returns the zip bytes and parsed filename."""
        # Given: A mocked download endpoint streaming zip bytes with a filename
        route = respx.get(f"{base_url}{Endpoints.ADMIN_LOGS_DOWNLOAD}").respond(
            200,
            content=b"PK\x03\x04fake-zip-bytes",
            headers={
                "Content-Disposition": 'attachment; filename="vapi-logs-20260525T120000Z.zip"'
            },
        )

        # When: Downloading the log archive
        archive = await vclient.global_admin.download_logs()

        # Then: The archive carries the filename and raw bytes
        assert route.called
        assert archive.filename == "vapi-logs-20260525T120000Z.zip"
        assert archive.content == b"PK\x03\x04fake-zip-bytes"

    @respx.mock
    async def test_download_logs_sends_zip_accept_header(self, vclient, base_url):
        """Verify download_logs requests application/zip."""
        # Given: A mocked download endpoint
        route = respx.get(f"{base_url}{Endpoints.ADMIN_LOGS_DOWNLOAD}").respond(
            200, content=b"PK", headers={"Content-Disposition": 'attachment; filename="x.zip"'}
        )

        # When: Downloading the log archive
        await vclient.global_admin.download_logs()

        # Then: The request asked for a zip
        assert route.calls.last.request.headers["accept"] == "application/zip"

    @respx.mock
    async def test_download_logs_falls_back_when_no_filename(self, vclient, base_url):
        """Verify a missing Content-Disposition yields the fallback filename."""
        # Given: A mocked endpoint with no Content-Disposition header
        respx.get(f"{base_url}{Endpoints.ADMIN_LOGS_DOWNLOAD}").respond(200, content=b"PK")

        # When: Downloading the log archive
        archive = await vclient.global_admin.download_logs()

        # Then: The fallback filename is used
        assert archive.filename == "vapi-logs.zip"

    @respx.mock
    async def test_download_logs_raises_conflict_when_disabled(self, vclient, base_url):
        """Verify a 409 response raises ConflictError."""
        # Given: A mocked endpoint returning 409
        respx.get(f"{base_url}{Endpoints.ADMIN_LOGS_DOWNLOAD}").respond(
            409, json={"detail": "File logging is not enabled"}
        )

        # When/Then: Downloading raises ConflictError
        with pytest.raises(ConflictError):
            await vclient.global_admin.download_logs()
