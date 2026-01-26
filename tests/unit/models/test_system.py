"""Tests for vclient.api.models.system."""

import pytest
from pydantic import ValidationError

from vclient.models.system import SystemHealth


class TestSystemHealth:
    """Tests for SystemHealth model."""

    def test_valid_health_response(self):
        """Verify parsing a valid health response."""
        # Given: Valid health response data
        data = {
            "database_status": "online",
            "cache_status": "online",
            "version": "1.0.0",
        }

        # When: Parsing the data
        health = SystemHealth.model_validate(data)

        # Then: All fields are correctly parsed
        assert health.database_status == "online"
        assert health.cache_status == "online"
        assert health.version == "1.0.0"

    def test_health_with_offline_status(self):
        """Verify parsing health response with offline services."""
        # Given: Health response with offline services
        data = {
            "database_status": "offline",
            "cache_status": "offline",
            "version": "1.0.0",
        }

        # When: Parsing the data
        health = SystemHealth.model_validate(data)

        # Then: Offline status is correctly parsed
        assert health.database_status == "offline"
        assert health.cache_status == "offline"

    @pytest.mark.parametrize(
        ("data", "missing_field"),
        [
            ({"cache_status": "online", "version": "1.0.0"}, "database_status"),
            ({"database_status": "online", "version": "1.0.0"}, "cache_status"),
        ],
    )
    def test_health_missing_required_field_raises(self, data, missing_field):
        """Verify missing required fields raise ValidationError."""
        # When/Then: Parsing raises ValidationError with field name
        with pytest.raises(ValidationError) as exc_info:
            SystemHealth.model_validate(data)

        assert missing_field in str(exc_info.value)

    def test_health_invalid_status_raises(self):
        """Verify invalid status value raises ValidationError."""
        # Given: Health response with invalid status
        data = {
            "database_status": "unknown",
            "cache_status": "online",
        }

        # When/Then: Parsing raises ValidationError
        with pytest.raises(ValidationError):
            SystemHealth.model_validate(data)
