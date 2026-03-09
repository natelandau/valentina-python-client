"""Integration tests for FakeVClient.set_response() and set_error()."""

import pytest

from vclient.exceptions import NotFoundError
from vclient.models import CampaignBook, PaginatedResponse, User
from vclient.registry import books_service, campaigns_service, users_service
from vclient.testing import CampaignBookFactory, CampaignFactory, FakeVClient, UserFactory
from vclient.testing._routes import Routes

pytestmark = pytest.mark.anyio


class TestSetResponsePaginated:
    """set_response() should correctly handle paginated routes."""

    async def test_empty_list(self):
        """Verify set_response with empty items returns an empty list."""
        async with FakeVClient() as client:
            # Given a paginated route overridden with no items
            client.set_response(Routes.USERS_LIST, items=[])

            # When listing all users
            result = await users_service().list_all()

            # Then an empty list is returned
            assert result == []

    async def test_list_with_model_instances(self):
        """Verify set_response with model instances returns them correctly."""
        async with FakeVClient() as client:
            # Given two User model instances
            user_a = UserFactory.build()
            user_b = UserFactory.build()
            client.set_response(Routes.USERS_LIST, items=[user_a, user_b])

            # When listing all users
            result = await users_service().list_all()

            # Then both users are returned with matching IDs
            assert len(result) == 2
            assert result[0].id == user_a.id
            assert result[1].id == user_b.id

    async def test_list_with_dicts(self):
        """Verify set_response with raw dicts returns valid models."""
        async with FakeVClient() as client:
            # Given a user serialized to a dict
            user = UserFactory.build()
            user_dict = user.model_dump(mode="json")
            client.set_response(Routes.USERS_LIST, items=[user_dict])

            # When listing all users
            result = await users_service().list_all()

            # Then the user is returned correctly
            assert len(result) == 1
            assert result[0].id == user.id

    async def test_get_page_returns_paginated_response(self):
        """Verify set_response populates PaginatedResponse with correct total."""
        async with FakeVClient() as client:
            # Given three users set on the paginated route
            users = [UserFactory.build() for _ in range(3)]
            client.set_response(Routes.USERS_LIST, items=users)

            # When getting a page of users
            result = await users_service().get_page()

            # Then the response is a PaginatedResponse with the correct total
            assert isinstance(result, PaginatedResponse)
            assert result.total == 3
            assert len(result.items) == 3
            assert isinstance(result.items[0], User)


class TestSetResponseSingle:
    """set_response() should correctly handle single-object routes."""

    async def test_single_with_model_instance(self):
        """Verify set_response with a model instance on a single route."""
        async with FakeVClient() as client:
            # Given a campaign model set on the get route
            campaign = CampaignFactory.build()
            client.set_response(Routes.CAMPAIGNS_GET, model=campaign)

            # When fetching the campaign
            result = await campaigns_service("user123").get(campaign.id)

            # Then the correct campaign is returned
            assert result.id == campaign.id

    async def test_single_with_dict(self):
        """Verify set_response with a dict on a single route."""
        async with FakeVClient() as client:
            # Given a campaign serialized to a dict
            campaign = CampaignFactory.build()
            campaign_dict = campaign.model_dump(mode="json")
            client.set_response(Routes.CAMPAIGNS_GET, model=campaign_dict)

            # When fetching the campaign
            result = await campaigns_service("user123").get(campaign.id)

            # Then the correct campaign is returned
            assert result.id == campaign.id

    async def test_renumber_with_model(self):
        """Verify set_response works for a PUT route like renumber."""
        async with FakeVClient() as client:
            # Given a book model set on the renumber route
            book = CampaignBookFactory.build()
            client.set_response(Routes.BOOKS_RENUMBER, model=book)

            # When renumbering the book
            result = await books_service("user123", "campaign123").renumber(book.id, 5)

            # Then the book is returned
            assert isinstance(result, CampaignBook)
            assert result.id == book.id


class TestSetError:
    """set_error() should make routes return error responses."""

    async def test_not_found_error(self):
        """Verify set_error with 404 raises NotFoundError."""
        async with FakeVClient() as client:
            # Given the campaigns get route set to return 404
            client.set_error(Routes.CAMPAIGNS_GET, status_code=404)

            # When fetching a campaign
            # Then a NotFoundError is raised
            with pytest.raises(NotFoundError):
                await campaigns_service("user123").get("nonexistent")

    async def test_error_with_detail(self):
        """Verify set_error includes the custom detail message."""
        async with FakeVClient() as client:
            # Given a custom error detail
            client.set_error(
                Routes.CAMPAIGNS_GET,
                status_code=404,
                detail="Campaign not found",
            )

            # When fetching a campaign
            # Then the error contains the custom detail
            with pytest.raises(NotFoundError, match="Campaign not found"):
                await campaigns_service("user123").get("nonexistent")


class TestSetResponseWithParams:
    """set_response() with params should return different responses per path parameter."""

    async def test_different_responses_per_campaign_id(self):
        """Verify different campaign_id values return different models."""
        async with FakeVClient() as client:
            # Given two campaigns with distinct IDs
            campaign_a = CampaignFactory.build()
            campaign_b = CampaignFactory.build()
            client.set_response(
                Routes.CAMPAIGNS_GET,
                model=campaign_a,
                params={"campaign_id": campaign_a.id},
            )
            client.set_response(
                Routes.CAMPAIGNS_GET,
                model=campaign_b,
                params={"campaign_id": campaign_b.id},
            )

            svc = campaigns_service("user123")

            # When fetching each campaign by its ID
            result_a = await svc.get(campaign_a.id)
            result_b = await svc.get(campaign_b.id)

            # Then the correct campaign is returned for each
            assert result_a.id == campaign_a.id
            assert result_b.id == campaign_b.id

    async def test_params_override_with_generic_fallback(self):
        """Verify parameterized override wins over generic for matching ID."""
        async with FakeVClient() as client:
            # Given a generic override and a parameterized override
            generic = CampaignFactory.build()
            specific = CampaignFactory.build()
            client.set_response(Routes.CAMPAIGNS_GET, model=generic)
            client.set_response(
                Routes.CAMPAIGNS_GET,
                model=specific,
                params={"campaign_id": "target-id"},
            )

            svc = campaigns_service("user123")

            # When fetching the targeted campaign
            result = await svc.get("target-id")

            # Then the parameterized override is returned
            assert result.id == specific.id

            # When fetching a different campaign
            result = await svc.get("other-id")

            # Then the generic fallback is returned
            assert result.id == generic.id

    async def test_set_error_with_params(self):
        """Verify set_error with params only errors for the matching ID."""
        async with FakeVClient() as client:
            # Given a 404 error only for a specific campaign
            client.set_error(
                Routes.CAMPAIGNS_GET,
                status_code=404,
                params={"campaign_id": "missing"},
            )

            svc = campaigns_service("user123")

            # When fetching the missing campaign
            with pytest.raises(NotFoundError):
                await svc.get("missing")

            # When fetching a different campaign, the default response is used
            result = await svc.get("other")
            assert result.id is not None


class TestSetResponseValidation:
    """set_response() should enforce correct kwarg usage per route style."""

    async def test_paginated_route_requires_items(self):
        """Verify passing model to a paginated route raises TypeError."""
        async with FakeVClient() as client:
            # Given a paginated route
            # When passing model instead of items
            # Then a TypeError is raised
            with pytest.raises(TypeError, match=r"paginated.*items"):
                client.set_response(Routes.USERS_LIST, model=UserFactory.build())

    async def test_single_route_requires_model(self):
        """Verify passing items to a single route raises TypeError."""
        async with FakeVClient() as client:
            # Given a single-object route
            # When passing items instead of model
            # Then a TypeError is raised
            with pytest.raises(TypeError, match=r"single object.*model"):
                client.set_response(Routes.CAMPAIGNS_GET, items=[CampaignFactory.build()])
