"""Tests for vclient.services.user_self_registration."""

import json

import pytest
import respx

from vclient.endpoints import Endpoints
from vclient.exceptions import RequestValidationError
from vclient.models import User, UserRegisterDTO

pytestmark = pytest.mark.anyio


class TestUserSelfRegistrationServiceRegister:
    """Tests for UserSelfRegistrationService.register method."""

    @respx.mock
    async def test_register_user_with_kwargs(self, vclient, base_url, user_response_data):
        """Verify registering a user via kwargs returns a User object."""
        # Given: A mocked register endpoint
        company_id = "company123"
        route = respx.post(
            f"{base_url}{Endpoints.USER_REGISTER.format(company_id=company_id)}"
        ).respond(201, json=user_response_data)

        # When: Registering a user with kwargs
        result = await vclient.user_self_registration(company_id=company_id).register(
            username="testuser",
            email="test@example.com",
            name_first="Test",
            name_last="User",
        )

        # Then: Returns created User object with correct fields
        assert route.called
        assert isinstance(result, User)
        assert result.username == "testuser"

        body = json.loads(route.calls.last.request.content)
        assert body["username"] == "testuser"
        assert body["email"] == "test@example.com"
        assert body["name_first"] == "Test"
        assert body["name_last"] == "User"

    @respx.mock
    async def test_register_user_with_model(self, vclient, base_url, user_response_data):
        """Verify registering a user via UserRegisterDTO model returns a User object."""
        # Given: A mocked register endpoint
        company_id = "company123"
        route = respx.post(
            f"{base_url}{Endpoints.USER_REGISTER.format(company_id=company_id)}"
        ).respond(201, json=user_response_data)

        # When: Registering with a model object
        request = UserRegisterDTO(
            username="testuser",
            email="test@example.com",
            name_first="Test",
            name_last="User",
        )
        result = await vclient.user_self_registration(company_id=company_id).register(
            request=request
        )

        # Then: Returns created User object and optional fields are excluded
        assert route.called
        assert isinstance(result, User)

        body = json.loads(route.calls.last.request.content)
        assert body["username"] == "testuser"
        assert body["email"] == "test@example.com"
        assert "discord_profile" not in body
        assert "google_profile" not in body
        assert "github_profile" not in body

    @respx.mock
    async def test_register_user_validation_error(self, vclient):
        """Verify missing required fields raises RequestValidationError."""
        # When/Then: Registering without required email raises RequestValidationError
        with pytest.raises(RequestValidationError):
            await vclient.user_self_registration(company_id="company123").register(
                username="testuser",
            )

    @respx.mock
    async def test_register_does_not_send_on_behalf_of_header(
        self, vclient, base_url, user_response_data
    ):
        """Verify the On-Behalf-Of header is absent from register requests."""
        # Given: A mocked register endpoint
        company_id = "company123"
        route = respx.post(
            f"{base_url}{Endpoints.USER_REGISTER.format(company_id=company_id)}"
        ).respond(201, json=user_response_data)

        # When: Registering a user
        await vclient.user_self_registration(company_id=company_id).register(
            username="testuser",
            email="test@example.com",
        )

        # Then: The On-Behalf-Of header is not present
        assert route.called
        request_headers = route.calls.last.request.headers
        assert "on-behalf-of" not in {k.lower() for k in request_headers}
