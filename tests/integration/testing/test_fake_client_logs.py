"""Tests for FakeVClient server-log route defaults."""

import pytest

from vclient.models import ServerLogEntry
from vclient.models.global_admin import ServerLogArchive
from vclient.testing import FakeVClient

pytestmark = pytest.mark.anyio


class TestFakeServerLogs:
    """Tests for the fake admin server-log routes."""

    async def test_tail_logs_returns_default_entries(self):
        """Verify FakeVClient returns ServerLogEntry objects for tail_logs."""
        # Given: A fake client
        async with FakeVClient() as client:
            # When: Tailing logs
            result = await client.global_admin.tail_logs()

        # Then: A list of ServerLogEntry objects is returned
        assert isinstance(result, list)
        assert all(isinstance(entry, ServerLogEntry) for entry in result)

    async def test_download_logs_returns_archive(self):
        """Verify FakeVClient returns a ServerLogArchive with bytes for download_logs."""
        # Given: A fake client
        async with FakeVClient() as client:
            # When: Downloading the log archive
            archive = await client.global_admin.download_logs()

        # Then: An archive with a filename and bytes is returned
        assert isinstance(archive, ServerLogArchive)
        assert archive.filename.endswith(".zip")
        assert isinstance(archive.content, bytes)
        assert archive.content  # non-empty
