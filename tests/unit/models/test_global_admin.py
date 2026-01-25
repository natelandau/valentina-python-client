"""Tests for vclient.api.models.global_admin."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from vclient.models.global_admin import (
    CreateDeveloperRequest,
    Developer,
    DeveloperCompanyPermission,
    DeveloperWithApiKey,
    UpdateDeveloperRequest,
)


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


class TestCreateDeveloperRequest:
    """Tests for CreateDeveloperRequest model."""

    def test_create_with_required_fields(self):
        """Verify creating request with required fields only."""
        # When: Creating with required fields
        request = CreateDeveloperRequest(
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
        request = CreateDeveloperRequest(
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
        request = CreateDeveloperRequest(
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


class TestUpdateDeveloperRequest:
    """Tests for UpdateDeveloperRequest model."""

    def test_all_fields_optional(self):
        """Verify all fields are optional."""
        # When: Creating with no fields
        request = UpdateDeveloperRequest()

        # Then: All fields are None
        assert request.username is None
        assert request.email is None
        assert request.is_global_admin is None

    def test_partial_update(self):
        """Verify partial update with some fields."""
        # When: Creating with only username
        request = UpdateDeveloperRequest(username="newusername")

        # Then: Only username is set
        assert request.username == "newusername"
        assert request.email is None
        assert request.is_global_admin is None

    def test_model_dump_excludes_none(self):
        """Verify model_dump with exclude_none works correctly."""
        # Given: Request with only email
        request = UpdateDeveloperRequest(email="new@example.com")

        # When: Dumping with exclude_none
        data = request.model_dump(exclude_none=True, mode="json")

        # Then: Only set fields are included
        assert data == {"email": "new@example.com"}

    def test_model_dump_full_update(self):
        """Verify model_dump includes all fields when set."""
        # Given: Request with all fields
        request = UpdateDeveloperRequest(
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
