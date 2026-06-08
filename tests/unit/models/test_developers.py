"""Tests for vclient.api.models.developers."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from vclient.models.developers import (
    MeDeveloper,
    MeDeveloperCompanyPermission,
    MeDeveloperUpdate,
    MeDeveloperWithApiKey,
)


def _me_developer_payload() -> dict:
    """Return a minimal valid MeDeveloper payload."""
    now = "2024-01-15T10:30:00Z"
    return {
        "id": "507f1f77bcf86cd799439011",
        "date_created": now,
        "date_modified": now,
        "username": "testuser",
        "email": "test@example.com",
        "key_generated": None,
        "companies": [],
    }


class TestMeDeveloperCompanyPermission:
    """Tests for MeDeveloperCompanyPermission model."""

    def test_all_fields_required(self):
        """Verify all fields are required for response DTO."""
        # When: Creating with all fields
        permission = MeDeveloperCompanyPermission(
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
        permission = MeDeveloperCompanyPermission(
            company_id="507f1f77bcf86cd799439011",
            name="Test Company",
            permission="ADMIN",
        )

        # Then: All fields are set correctly
        assert permission.company_id == "507f1f77bcf86cd799439011"
        assert permission.name == "Test Company"
        assert permission.permission == "ADMIN"


class TestMeDeveloper:
    """Tests for MeDeveloper model."""

    def test_all_fields_required(self):
        """Verify all fields are required for response DTO."""
        # Given: Timestamps
        now = datetime.now(tz=UTC)

        # When: Creating with all fields
        developer = MeDeveloper(
            id="507f1f77bcf86cd799439011",
            date_created=now,
            date_modified=now,
            username="testuser",
            email="test@example.com",
            key_generated=None,
            companies=[],
        )

        # Then: All fields are set correctly
        assert developer.id == "507f1f77bcf86cd799439011"
        assert developer.date_created == now
        assert developer.date_modified == now
        assert developer.username == "testuser"
        assert developer.email == "test@example.com"
        assert developer.key_generated is None
        assert developer.companies == []

    def test_create_with_all_fields(self):
        """Verify creating developer with all fields."""
        # Given: Timestamps and company permissions using string value
        now = datetime.now(tz=UTC)
        company_permission = MeDeveloperCompanyPermission(
            company_id="company123",
            name="Test Company",
            permission="OWNER",
        )

        # When: Creating with all fields
        developer = MeDeveloper(
            id="507f1f77bcf86cd799439011",
            date_created=now,
            date_modified=now,
            username="testuser",
            email="test@example.com",
            key_generated=now,
            companies=[company_permission],
        )

        # Then: All fields are set correctly
        assert developer.id == "507f1f77bcf86cd799439011"
        assert developer.date_created == now
        assert developer.date_modified == now
        assert developer.username == "testuser"
        assert developer.email == "test@example.com"
        assert developer.key_generated == now
        assert len(developer.companies) == 1
        assert developer.companies[0].company_id == "company123"

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
            "companies": [
                {
                    "company_id": "company123",
                    "name": "Test Company",
                    "permission": "ADMIN",
                }
            ],
        }

        # When: Parsing with model_validate
        developer = MeDeveloper.model_validate(data)

        # Then: All fields are parsed correctly
        assert developer.id == "507f1f77bcf86cd799439011"
        assert developer.username == "testuser"
        assert len(developer.companies) == 1
        assert developer.companies[0].permission == "ADMIN"


class TestMeDeveloperWithApiKey:
    """Tests for MeDeveloperWithApiKey model."""

    def test_inherits_from_developer(self):
        """Verify MeDeveloperWithApiKey inherits MeDeveloper fields."""
        # Given: Timestamps
        now = datetime.now(tz=UTC)

        # When: Creating with all fields
        developer = MeDeveloperWithApiKey(
            id="507f1f77bcf86cd799439011",
            date_created=now,
            date_modified=now,
            username="testuser",
            email="test@example.com",
            key_generated=None,
            companies=[],
            api_key="vapi_abc123xyz",  # gitleaks:allow
        )

        # Then: All fields are accessible
        assert developer.id == "507f1f77bcf86cd799439011"
        assert developer.username == "testuser"
        assert developer.email == "test@example.com"
        assert developer.api_key == "vapi_abc123xyz"  # gitleaks:allow


class TestProviderAudiences:
    """Tests for the provider_audiences field on developer models."""

    def test_update_accepts_provider_audiences(self):
        """Verify provider_audiences accepts apple and google keys."""
        # When: Creating an update with audiences for both providers
        dto = MeDeveloperUpdate(
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
        dto = MeDeveloperUpdate(username="dev")

        # Then: The field defaults to None and is excluded from dumps
        assert dto.provider_audiences is None
        assert "provider_audiences" not in dto.model_dump(exclude_none=True)

    def test_unknown_provider_key_rejected(self):
        """Verify non-OIDC provider keys fail validation."""
        # When/Then: A discord key raises a validation error
        with pytest.raises(PydanticValidationError):
            MeDeveloperUpdate(provider_audiences={"discord": ["abc"]})

    def test_more_than_twenty_audiences_rejected(self):
        """Verify the per-provider audience cap is enforced client-side."""
        # When/Then: 21 audiences raise a validation error
        with pytest.raises(PydanticValidationError):
            MeDeveloperUpdate(provider_audiences={"apple": [f"aud-{i}" for i in range(21)]})

    def test_audience_length_limits_rejected(self):
        """Verify empty and over-long audience strings fail validation."""
        # When/Then: An empty audience raises a validation error
        with pytest.raises(PydanticValidationError):
            MeDeveloperUpdate(provider_audiences={"apple": [""]})

        # When/Then: A 256-char audience raises a validation error
        with pytest.raises(PydanticValidationError):
            MeDeveloperUpdate(provider_audiences={"apple": ["a" * 256]})

    def test_response_defaults_to_empty_dict(self):
        """Verify developer responses without the field still parse."""
        # When: Validating a developer payload predating the field
        developer = MeDeveloper.model_validate(_me_developer_payload())

        # Then: provider_audiences defaults to empty
        assert developer.provider_audiences == {}

    def test_limits_accepted_at_boundary(self):
        """Verify exactly 20 audiences of 255 chars each are accepted."""
        # When: Creating an update at the documented limits
        dto = MeDeveloperUpdate(provider_audiences={"apple": ["a" * 255] * 20})

        # Then: The audiences are stored
        assert len(dto.provider_audiences["apple"]) == 20


class TestMeDeveloperUpdate:
    """Tests for MeDeveloperUpdate model."""

    def test_all_fields_optional(self):
        """Verify all fields are optional."""
        # When: Creating with no fields
        request = MeDeveloperUpdate()

        # Then: All fields are None
        assert request.username is None
        assert request.email is None
        assert request.provider_audiences is None

    def test_partial_update(self):
        """Verify partial update with some fields."""
        # When: Creating with only username
        request = MeDeveloperUpdate(username="newusername")

        # Then: Only username is set
        assert request.username == "newusername"
        assert request.email is None

    def test_model_dump_excludes_none(self):
        """Verify model_dump with exclude_none works correctly."""
        # Given: Request with only email
        request = MeDeveloperUpdate(email="new@example.com")

        # When: Dumping with exclude_none
        data = request.model_dump(exclude_none=True, mode="json")

        # Then: Only set fields are included
        assert data == {"email": "new@example.com"}

    def test_model_dump_full_update(self):
        """Verify model_dump includes all fields when set."""
        # Given: Request with all fields
        request = MeDeveloperUpdate(
            username="newuser",
            email="new@example.com",
        )

        # When: Dumping
        data = request.model_dump(exclude_none=True, mode="json")

        # Then: All fields are included
        assert data == {
            "username": "newuser",
            "email": "new@example.com",
        }
