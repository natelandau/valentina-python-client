"""Tests for vclient.api.models.system."""

import pytest
from pydantic import ValidationError

from vclient.api.models.system import ServiceStatus, SystemHealth


class TestServiceStatus:
    """Tests for ServiceStatus enum."""

    def test_online_value(self):
        """Verify ONLINE status has correct value."""
        assert ServiceStatus.ONLINE == "online"

    def test_offline_value(self):
        """Verify OFFLINE status has correct value."""
        assert ServiceStatus.OFFLINE == "offline"

    def test_all_values(self):
        """Verify all expected status values exist."""
        values = [status.value for status in ServiceStatus]
        assert values == ["online", "offline"]


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
        assert health.database_status == ServiceStatus.ONLINE
        assert health.cache_status == ServiceStatus.ONLINE
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
        assert health.database_status == ServiceStatus.OFFLINE
        assert health.cache_status == ServiceStatus.OFFLINE

    def test_health_missing_database_status_raises(self):
        """Verify missing database_status raises ValidationError."""
        # Given: Health response missing database_status
        data = {
            "cache_status": "online",
            "version": "1.0.0",
        }

        # When/Then: Parsing raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            SystemHealth.model_validate(data)

        assert "database_status" in str(exc_info.value)

    def test_health_missing_cache_status_raises(self):
        """Verify missing cache_status raises ValidationError."""
        # Given: Health response missing cache_status
        data = {
            "database_status": "online",
            "version": "1.0.0",
        }

        # When/Then: Parsing raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            SystemHealth.model_validate(data)

        assert "cache_status" in str(exc_info.value)

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
