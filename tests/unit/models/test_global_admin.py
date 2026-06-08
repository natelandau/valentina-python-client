"""Tests for vclient.api.models.global_admin."""

import dataclasses
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from vclient.models.global_admin import (
    Developer,
    DeveloperCompanyPermission,
    DeveloperCreate,
    DeveloperUpdate,
    DeveloperWithApiKey,
    ServerLogArchive,
    ServerLogEntry,
)


def _developer_payload() -> dict:
    """Return a minimal valid Developer payload."""
    now = "2024-01-15T10:30:00Z"
    return {
        "id": "507f1f77bcf86cd799439011",
        "date_created": now,
        "date_modified": now,
        "username": "testuser",
        "email": "test@example.com",
        "key_generated": None,
        "is_global_admin": False,
        "companies": [],
    }


class TestAdminProviderAudiences:
    """Tests for the provider_audiences field on admin developer models."""

    def test_update_accepts_provider_audiences(self):
        """Verify provider_audiences accepts apple and google keys."""
        # When: Creating an update with audiences for both providers
        dto = DeveloperUpdate(
            provider_audiences={
                "apple": ["com.example.iosapp"],
                "google": ["1234-abc.apps.googleusercontent.com"],
            }
        )

        # Then: The audiences are stored
        assert dto.provider_audiences == {
            "apple": ["com.example.iosapp"],
            "google": ["1234-abc.apps.googleusercontent.com"],
        }

    def test_update_defaults_to_none(self):
        """Verify provider_audiences is omitted unless set."""
        # When: Creating an update without audiences
        dto = DeveloperUpdate(username="dev")

        # Then: The field defaults to None and is excluded from dumps
        assert dto.provider_audiences is None
        assert "provider_audiences" not in dto.model_dump(exclude_none=True)

    def test_unknown_provider_key_rejected(self):
        """Verify non-OIDC provider keys fail validation."""
        # When/Then: A discord key raises a validation error
        with pytest.raises(ValidationError):
            DeveloperUpdate(provider_audiences={"discord": ["abc"]})

    def test_more_than_twenty_audiences_rejected(self):
        """Verify the per-provider audience cap is enforced client-side."""
        # When/Then: 21 audiences raise a validation error
        with pytest.raises(ValidationError):
            DeveloperUpdate(provider_audiences={"apple": [f"aud-{i}" for i in range(21)]})

    def test_audience_length_limits_rejected(self):
        """Verify empty and over-long audience strings fail validation."""
        # When/Then: An empty audience raises a validation error
        with pytest.raises(ValidationError):
            DeveloperUpdate(provider_audiences={"apple": [""]})

        # When/Then: A 256-char audience raises a validation error
        with pytest.raises(ValidationError):
            DeveloperUpdate(provider_audiences={"apple": ["a" * 256]})

    def test_response_defaults_to_empty_dict(self):
        """Verify developer responses without the field still parse."""
        # When: Validating a developer payload predating the field
        developer = Developer.model_validate(_developer_payload())

        # Then: provider_audiences defaults to empty
        assert developer.provider_audiences == {}

    def test_limits_accepted_at_boundary(self):
        """Verify exactly 20 audiences of 255 chars each are accepted."""
        # When: Creating an update at the documented limits
        dto = DeveloperUpdate(provider_audiences={"apple": ["a" * 255] * 20})

        # Then: The audiences are stored
        assert len(dto.provider_audiences["apple"]) == 20


class TestDeveloperCompanyPermission:
    """Tests for DeveloperCompanyPermission model."""

    def test_all_fields_required(self):
        """Verify all fields are required for response DTO."""
        # When: Creating with all fields
        permission = DeveloperCompanyPermission(
            company_id="507f1f77bcf86cd799439011",
            name=None,
            permission="USER",
        )

        # Then: Fields are set correctly
        assert permission.company_id == "507f1f77bcf86cd799439011"
        assert permission.permission == "USER"
        assert permission.name is None

    def test_create_with_all_fields(self):
        """Verify creating permission with all fields."""
        # When: Creating with all fields using string value
        permission = DeveloperCompanyPermission(
            company_id="507f1f77bcf86cd799439011",
            name="Test Company",
            permission="ADMIN",
        )

        # Then: All fields are set correctly
        assert permission.company_id == "507f1f77bcf86cd799439011"
        assert permission.name == "Test Company"
        assert permission.permission == "ADMIN"

    def test_missing_required_fields_raises_error(self):
        """Verify missing required fields raises ValidationError."""
        # When/Then: Missing fields raises error
        with pytest.raises(ValidationError):
            DeveloperCompanyPermission()

    def test_invalid_permission_rejected(self):
        """Verify invalid permission values are rejected by Pydantic."""
        # When/Then: Creating with invalid permission raises error
        with pytest.raises(ValidationError):
            DeveloperCompanyPermission(
                company_id="507f1f77bcf86cd799439011",
                permission="INVALID",
            )


class TestDeveloper:
    """Tests for Developer model."""

    def test_all_fields_required(self):
        """Verify all fields are required for response DTO."""
        # Given: Timestamps
        now = datetime.now(tz=UTC)

        # When: Creating with all fields
        developer = Developer(
            id="507f1f77bcf86cd799439011",
            date_created=now,
            date_modified=now,
            username="testuser",
            email="test@example.com",
            key_generated=None,
            is_global_admin=False,
            companies=[],
        )

        # Then: All fields are set correctly
        assert developer.id == "507f1f77bcf86cd799439011"
        assert developer.date_created == now
        assert developer.date_modified == now
        assert developer.username == "testuser"
        assert developer.email == "test@example.com"
        assert developer.key_generated is None
        assert developer.is_global_admin is False
        assert developer.companies == []

    def test_create_with_all_fields(self):
        """Verify creating developer with all fields."""
        # Given: Timestamps and company permissions using string value
        now = datetime.now(tz=UTC)
        company_permission = DeveloperCompanyPermission(
            company_id="company123",
            name="Test Company",
            permission="OWNER",
        )

        # When: Creating with all fields
        developer = Developer(
            id="507f1f77bcf86cd799439011",
            date_created=now,
            date_modified=now,
            username="testuser",
            email="test@example.com",
            key_generated=now,
            is_global_admin=True,
            companies=[company_permission],
        )

        # Then: All fields are set correctly
        assert developer.id == "507f1f77bcf86cd799439011"
        assert developer.date_created == now
        assert developer.date_modified == now
        assert developer.username == "testuser"
        assert developer.email == "test@example.com"
        assert developer.key_generated == now
        assert developer.is_global_admin is True
        assert len(developer.companies) == 1
        assert developer.companies[0].company_id == "company123"

    def test_missing_required_fields_raises_error(self):
        """Verify missing required fields raises ValidationError."""
        # When/Then: Missing email raises error
        with pytest.raises(ValidationError):
            Developer(username="testuser")

        # When/Then: Missing username raises error
        with pytest.raises(ValidationError):
            Developer(email="test@example.com")

    def test_model_validate_from_dict(self):
        """Verify model_validate parses dict correctly."""
        # Given: Response data as dict
        data = {
            "id": "507f1f77bcf86cd799439011",
            "date_created": "2024-01-15T10:30:00Z",
            "date_modified": "2024-01-15T10:30:00Z",
            "username": "testuser",
            "email": "test@example.com",
            "key_generated": "2024-01-15T10:30:00Z",
            "is_global_admin": True,
            "companies": [
                {
                    "company_id": "company123",
                    "name": "Test Company",
                    "permission": "ADMIN",
                }
            ],
        }

        # When: Parsing with model_validate
        developer = Developer.model_validate(data)

        # Then: All fields are parsed correctly
        assert developer.id == "507f1f77bcf86cd799439011"
        assert developer.username == "testuser"
        assert developer.is_global_admin is True
        assert len(developer.companies) == 1
        assert developer.companies[0].permission == "ADMIN"


class TestDeveloperWithApiKey:
    """Tests for DeveloperWithApiKey model."""

    def test_inherits_from_developer(self):
        """Verify DeveloperWithApiKey inherits Developer fields."""
        # Given: Timestamps
        now = datetime.now(tz=UTC)

        # When: Creating with all fields
        developer = DeveloperWithApiKey(
            id="507f1f77bcf86cd799439011",
            date_created=now,
            date_modified=now,
            username="testuser",
            email="test@example.com",
            key_generated=None,
            is_global_admin=True,
            companies=[],
            api_key="vapi_abc123xyz",
        )

        # Then: All fields are accessible
        assert developer.id == "507f1f77bcf86cd799439011"
        assert developer.username == "testuser"
        assert developer.email == "test@example.com"
        assert developer.is_global_admin is True
        assert developer.api_key == "vapi_abc123xyz"

    def test_api_key_can_be_none(self):
        """Verify api_key can be None."""
        # Given: Timestamps
        now = datetime.now(tz=UTC)

        # When: Creating with api_key as None
        developer = DeveloperWithApiKey(
            id="507f1f77bcf86cd799439011",
            date_created=now,
            date_modified=now,
            username="testuser",
            email="test@example.com",
            key_generated=None,
            is_global_admin=False,
            companies=[],
            api_key=None,
        )

        # Then: api_key is None
        assert developer.api_key is None


class TestDeveloperCreate:
    """Tests for DeveloperCreate model."""

    def test_create_with_required_fields(self):
        """Verify creating request with required fields only."""
        # When: Creating with required fields
        request = DeveloperCreate(
            username="testuser",
            email="test@example.com",
        )

        # Then: Fields are set correctly with defaults
        assert request.username == "testuser"
        assert request.email == "test@example.com"
        assert request.is_global_admin is False

    def test_create_with_all_fields(self):
        """Verify creating request with all fields."""
        # When: Creating with all fields
        request = DeveloperCreate(
            username="adminuser",
            email="admin@example.com",
            is_global_admin=True,
        )

        # Then: All fields are set correctly
        assert request.username == "adminuser"
        assert request.email == "admin@example.com"
        assert request.is_global_admin is True

    def test_model_dump_excludes_unset(self):
        """Verify model_dump with exclude_unset works correctly."""
        # Given: Request with only required fields
        request = DeveloperCreate(
            username="testuser",
            email="test@example.com",
        )

        # When: Dumping with exclude_unset
        data = request.model_dump(exclude_unset=True, mode="json")

        # Then: Only set fields are included
        assert data == {
            "username": "testuser",
            "email": "test@example.com",
        }


class TestDeveloperUpdate:
    """Tests for DeveloperUpdate model."""

    def test_all_fields_optional(self):
        """Verify all fields are optional."""
        # When: Creating with no fields
        request = DeveloperUpdate()

        # Then: All fields are None
        assert request.username is None
        assert request.email is None
        assert request.is_global_admin is None
        assert request.provider_audiences is None

    def test_partial_update(self):
        """Verify partial update with some fields."""
        # When: Creating with only username
        request = DeveloperUpdate(username="newusername")

        # Then: Only username is set
        assert request.username == "newusername"
        assert request.email is None
        assert request.is_global_admin is None

    def test_model_dump_excludes_none(self):
        """Verify model_dump with exclude_none works correctly."""
        # Given: Request with only email
        request = DeveloperUpdate(email="new@example.com")

        # When: Dumping with exclude_none
        data = request.model_dump(exclude_none=True, mode="json")

        # Then: Only set fields are included
        assert data == {"email": "new@example.com"}

    def test_model_dump_full_update(self):
        """Verify model_dump includes all fields when set."""
        # Given: Request with all fields
        request = DeveloperUpdate(
            username="newuser",
            email="new@example.com",
            is_global_admin=True,
        )

        # When: Dumping
        data = request.model_dump(exclude_none=True, mode="json")

        # Then: All fields are included
        assert data == {
            "username": "newuser",
            "email": "new@example.com",
            "is_global_admin": True,
        }


class TestServerLogEntry:
    """Tests for ServerLogEntry model."""

    def test_full_payload_round_trip(self):
        """Verify a full log entry payload validates with all fields set."""
        # Given: A complete log entry payload
        payload = {
            "timestamp": "2026-05-25T12:00:00.123Z",
            "level": "INFO",
            "name": "vapi.server",
            "message": "Request completed",
            "exception": None,
            "extra": {"status_code": 200, "path": "/api/v1/companies"},
            "raw": None,
        }

        # When: Validating the payload
        entry = ServerLogEntry.model_validate(payload)

        # Then: Fields are populated
        assert entry.timestamp == "2026-05-25T12:00:00.123Z"
        assert entry.level == "INFO"
        assert entry.name == "vapi.server"
        assert entry.extra == {"status_code": 200, "path": "/api/v1/companies"}
        assert entry.raw is None

    def test_all_fields_optional_with_extra_default(self):
        """Verify an empty payload validates and extra defaults to an empty dict."""
        # When: Validating an empty payload
        entry = ServerLogEntry.model_validate({})

        # Then: Every field defaults and extra is an empty dict
        assert entry.timestamp is None
        assert entry.level is None
        assert entry.extra == {}

    def test_extra_defaults_are_independent(self):
        """Verify each instance gets its own extra dict (no shared mutable default)."""
        # Given: Two entries built from empty payloads
        first = ServerLogEntry.model_validate({})
        second = ServerLogEntry.model_validate({})

        # When: Mutating one instance's extra
        first.extra["k"] = "v"

        # Then: The other instance is unaffected
        assert second.extra == {}


class TestServerLogArchive:
    """Tests for ServerLogArchive dataclass."""

    def test_holds_filename_and_content(self):
        """Verify the archive exposes its filename and raw bytes."""
        # When: Building an archive
        archive = ServerLogArchive(filename="vapi-logs.zip", content=b"PK\x03\x04")

        # Then: Both fields are accessible
        assert archive.filename == "vapi-logs.zip"
        assert archive.content == b"PK\x03\x04"

    def test_is_frozen(self):
        """Verify the archive is immutable."""
        # Given: An archive
        archive = ServerLogArchive(filename="vapi-logs.zip", content=b"PK")

        # When/Then: Reassigning a field raises FrozenInstanceError
        with pytest.raises(dataclasses.FrozenInstanceError):
            archive.filename = "other.zip"
