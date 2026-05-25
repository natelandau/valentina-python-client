"""Unit tests for vclient.services.global_admin helpers."""

import pytest

from vclient.services.global_admin import _filename_from_content_disposition


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ('attachment; filename="vapi-logs-20260525T120000Z.zip"', "vapi-logs-20260525T120000Z.zip"),
        ("attachment; filename=plain.zip", "plain.zip"),
        (None, "fallback.zip"),
        ("attachment", "fallback.zip"),
        ("", "fallback.zip"),
        ("attachment; filename*=UTF-8''report.zip", "fallback.zip"),
    ],
)
def test_filename_from_content_disposition(header, expected):
    """Verify the attachment filename is parsed with a fallback when absent."""
    # When: Parsing the Content-Disposition header
    result = _filename_from_content_disposition(header, fallback="fallback.zip")

    # Then: The expected filename (or fallback) is returned
    assert result == expected
