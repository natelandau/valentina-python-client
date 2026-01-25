"""Tests for vclient.api.models.companies."""

import pytest
from pydantic import ValidationError as PydanticValidationError

from vclient.models.companies import (
    Company,
    CompanyPermissions,
    CompanySettings,
    CreateCompanyRequest,
    GrantAccessRequest,
    UpdateCompanyRequest,
)


class TestCompanySettings:
    """Tests for CompanySettings model."""

    def test_all_fields_default_to_none(self):
        """Verify all fields default to None for partial updates."""
        # When: Creating settings with no arguments
        settings = CompanySettings()

        # Then: All values are None
        assert settings.character_autogen_xp_cost is None
        assert settings.character_autogen_num_choices is None
        assert settings.permission_manage_campaign is None
        assert settings.permission_grant_xp is None
        assert settings.permission_free_trait_changes is None

    def test_partial_settings(self):
        """Verify partial settings for updates."""
        # When: Creating settings with only some values
        settings = CompanySettings(
            character_autogen_xp_cost=20,
            permission_manage_campaign="STORYTELLER",
        )

        # Then: Specified values are set, others are None
        assert settings.character_autogen_xp_cost == 20
        assert settings.character_autogen_num_choices is None
        assert settings.permission_manage_campaign == "STORYTELLER"
        assert settings.permission_grant_xp is None
        assert settings.permission_free_trait_changes is None

    def test_model_dump_excludes_none(self):
        """Verify model_dump with exclude_none works correctly."""
        # Given: Settings with some values set
        settings = CompanySettings(
            character_autogen_xp_cost=15,
            permission_manage_campaign="STORYTELLER",
        )

        # When: Dumping with exclude_none
        data = settings.model_dump(exclude_none=True)

        # Then: Only non-None values are included
        assert data == {
            "character_autogen_xp_cost": 15,
            "permission_manage_campaign": "STORYTELLER",
        }

    def test_invalid_permission_value_rejected(self):
        """Verify invalid permission values are rejected by Pydantic."""
        # When/Then: Creating settings with invalid permission raises error
        with pytest.raises(PydanticValidationError):
            CompanySettings(permission_manage_campaign="INVALID_VALUE")


class TestCompany:
    """Tests for Company model."""

    def test_all_fields_required(self):
        """Verify all fields are required for response DTO."""
        # When: Creating company with all fields
        company = Company(
            id="507f1f77bcf86cd799439011",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Test",
            description=None,
            email="test@example.com",
            user_ids=[],
            settings=None,
        )

        # Then: Company is created correctly
        assert company.id == "507f1f77bcf86cd799439011"
        assert company.date_created is not None
        assert company.date_modified is not None
        assert company.name == "Test"
        assert company.email == "test@example.com"
        assert company.description is None
        assert company.user_ids == []
        assert company.settings is None

    def test_full_company(self):
        """Verify creating company with all fields populated."""
        # Given: Settings with some values
        settings = CompanySettings(character_autogen_xp_cost=15)

        # When: Creating company with all fields
        company = Company(
            id="507f1f77bcf86cd799439011",
            date_created="2024-01-15T10:30:00Z",
            date_modified="2024-01-15T10:30:00Z",
            name="Full Company",
            description="A complete company",
            email="full@example.com",
            user_ids=["user1", "user2"],
            settings=settings,
        )

        # Then: All fields are set correctly
        assert company.id == "507f1f77bcf86cd799439011"
        assert company.date_created is not None
        assert company.date_modified is not None
        assert company.name == "Full Company"
        assert company.description == "A complete company"
        assert company.email == "full@example.com"
        assert company.user_ids == ["user1", "user2"]
        assert company.settings is not None
        assert company.settings.character_autogen_xp_cost == 15

    def test_company_from_api_response(self):
        """Verify creating company from API response dict."""
        # Given: API response data
        data = {
            "id": "507f1f77bcf86cd799439011",
            "date_created": "2024-01-15T10:30:00Z",
            "date_modified": "2024-01-15T10:30:00Z",
            "name": "API Company",
            "description": "From API",
            "email": "api@example.com",
            "user_ids": ["u1"],
            "settings": {
                "character_autogen_xp_cost": 10,
                "character_autogen_num_choices": 3,
                "permission_manage_campaign": "UNRESTRICTED",
                "permission_grant_xp": "PLAYER",
                "permission_free_trait_changes": "WITHIN_24_HOURS",
            },
        }

        # When: Creating company from dict
        company = Company.model_validate(data)

        # Then: Company is created correctly
        assert company.id == "507f1f77bcf86cd799439011"
        assert company.name == "API Company"
        assert company.settings is not None
        assert company.settings.permission_grant_xp == "PLAYER"

    def test_missing_required_field_raises_error(self):
        """Verify missing required fields raises ValidationError."""
        # When/Then: Missing required field raises error
        with pytest.raises(PydanticValidationError):
            Company(
                id="507f1f77bcf86cd799439011",
                date_created="2024-01-15T10:30:00Z",
                date_modified="2024-01-15T10:30:00Z",
                name="Test",
                email="test@example.com",
                # Missing: description, user_ids, settings
            )


class TestCompanyPermissions:
    """Tests for CompanyPermissions model."""

    def test_all_fields_required(self):
        """Verify all fields are required for response DTO."""
        # When: Creating permissions with all fields
        perms = CompanyPermissions(
            company_id="company123",
            name=None,
            permission="USER",
        )

        # Then: Permissions are created correctly
        assert perms.company_id == "company123"
        assert perms.permission == "USER"
        assert perms.name is None

    def test_full_permissions(self):
        """Verify creating permissions with all fields."""
        # When: Creating permissions with all fields
        perms = CompanyPermissions(
            company_id="company123",
            name="Test Company",
            permission="ADMIN",
        )

        # Then: All fields are set correctly
        assert perms.company_id == "company123"
        assert perms.name == "Test Company"
        assert perms.permission == "ADMIN"

    def test_permissions_from_api_response(self):
        """Verify creating permissions from API response dict."""
        # Given: API response data
        data = {
            "company_id": "507f1f77bcf86cd799439011",
            "name": "API Company",
            "permission": "OWNER",
        }

        # When: Creating permissions from dict
        perms = CompanyPermissions.model_validate(data)

        # Then: Permissions are created correctly
        assert perms.company_id == "507f1f77bcf86cd799439011"
        assert perms.name == "API Company"
        assert perms.permission == "OWNER"

    def test_invalid_permission_rejected(self):
        """Verify invalid permission values are rejected by Pydantic."""
        # When/Then: Creating permissions with invalid permission raises error
        with pytest.raises(PydanticValidationError):
            CompanyPermissions(company_id="company123", permission="INVALID")


class TestCreateCompanyRequest:
    """Tests for CreateCompanyRequest model."""

    def test_minimal_request(self):
        """Verify creating request with minimal fields."""
        # When: Creating request with required fields only
        request = CreateCompanyRequest(name="Test", email="test@example.com")

        # Then: Request is created with correct values
        assert request.name == "Test"
        assert request.email == "test@example.com"
        assert request.description is None
        assert request.settings is None

    def test_full_request(self):
        """Verify creating request with all fields."""
        # Given: Settings with some values
        settings = CompanySettings(character_autogen_xp_cost=20)

        # When: Creating request with all fields
        request = CreateCompanyRequest(
            name="Full Company",
            email="full@example.com",
            description="A complete company",
            settings=settings,
        )

        # Then: All fields are set correctly
        assert request.name == "Full Company"
        assert request.email == "full@example.com"
        assert request.description == "A complete company"
        assert request.settings is not None
        assert request.settings.character_autogen_xp_cost == 20

    def test_model_dump_excludes_unset(self):
        """Verify model_dump with exclude_unset excludes unset fields."""
        # Given: Request with only required fields
        request = CreateCompanyRequest(name="Test", email="test@example.com")

        # When: Dumping with exclude_none and exclude_unset
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Only set fields are included
        assert data == {"name": "Test", "email": "test@example.com"}

    def test_model_dump_with_settings(self):
        """Verify model_dump includes settings correctly."""
        # Given: Request with partial settings
        settings = CompanySettings(
            character_autogen_xp_cost=15,
            permission_manage_campaign="STORYTELLER",
        )
        request = CreateCompanyRequest(
            name="Test",
            email="test@example.com",
            settings=settings,
        )

        # When: Dumping with exclude_none and exclude_unset
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Settings are included with correct values
        assert data["settings"]["character_autogen_xp_cost"] == 15
        assert data["settings"]["permission_manage_campaign"] == "STORYTELLER"

    def test_name_validation(self):
        """Verify name validation is enforced."""
        # When/Then: Creating request with invalid name raises error
        with pytest.raises(PydanticValidationError):
            CreateCompanyRequest(name="AB", email="test@example.com")


class TestUpdateCompanyRequest:
    """Tests for UpdateCompanyRequest model."""

    def test_empty_request(self):
        """Verify creating empty update request."""
        # When: Creating request with no fields
        request = UpdateCompanyRequest()

        # Then: All fields are None
        assert request.name is None
        assert request.email is None
        assert request.description is None
        assert request.settings is None

    def test_partial_update(self):
        """Verify creating request with only some fields."""
        # When: Creating request with only name
        request = UpdateCompanyRequest(name="Updated Name")

        # Then: Only name is set
        assert request.name == "Updated Name"
        assert request.email is None

    def test_model_dump_excludes_unset(self):
        """Verify model_dump with exclude_unset only includes set fields."""
        # Given: Request with only name set
        request = UpdateCompanyRequest(name="Updated Name")

        # When: Dumping with exclude_none and exclude_unset
        data = request.model_dump(exclude_none=True, exclude_unset=True, mode="json")

        # Then: Only name is in the output
        assert data == {"name": "Updated Name"}


class TestGrantAccessRequest:
    """Tests for GrantAccessRequest model."""

    def test_create_request(self):
        """Verify creating grant access request."""
        # When: Creating request
        request = GrantAccessRequest(
            developer_id="dev123",
            permission="ADMIN",
        )

        # Then: Fields are set correctly
        assert request.developer_id == "dev123"
        assert request.permission == "ADMIN"

    def test_model_dump_serializes_correctly(self):
        """Verify model_dump serializes permission to string."""
        # Given: Request with permission
        request = GrantAccessRequest(
            developer_id="dev123",
            permission="OWNER",
        )

        # When: Dumping with mode="json"
        data = request.model_dump(mode="json")

        # Then: Permission is serialized as string
        assert data["permission"] == "OWNER"

    def test_invalid_permission_rejected(self):
        """Verify invalid permission values are rejected by Pydantic."""
        # When/Then: Creating request with invalid permission raises error
        with pytest.raises(PydanticValidationError):
            GrantAccessRequest(developer_id="dev123", permission="INVALID")
