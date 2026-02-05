"""Tests for vclient.api.models.developers."""

from datetime import UTC, datetime

from vclient.models.developers import (
    MeDeveloper,
    MeDeveloperCompanyPermission,
    MeDeveloperUpdate,
    MeDeveloperWithApiKey,
)


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


class TestMeDeveloperUpdate:
    """Tests for MeDeveloperUpdate model."""

    def test_all_fields_optional(self):
        """Verify all fields are optional."""
        # When: Creating with no fields
        request = MeDeveloperUpdate()

        # Then: All fields are None
        assert request.username is None
        assert request.email is None

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
