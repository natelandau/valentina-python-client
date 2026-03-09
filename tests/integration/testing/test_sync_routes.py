"""Integration tests for SyncFakeVClient.set_response() and set_error()."""

import pytest

from vclient._sync.registry import sync_books_service, sync_campaigns_service, sync_users_service
from vclient.exceptions import NotFoundError
from vclient.models import CampaignBook
from vclient.testing import (
    CampaignBookFactory,
    CampaignFactory,
    Routes,
    SyncFakeVClient,
    UserFactory,
)


class TestSyncSetResponsePaginated:
    """set_response() should correctly handle paginated routes."""

    def test_empty_list(self):
        """Verify set_response with empty items returns an empty list."""
        with SyncFakeVClient() as client:
            # Given a paginated route overridden with no items
            client.set_response(Routes.USERS_LIST, items=[])

            # When listing all users
            result = sync_users_service().list_all()

            # Then an empty list is returned
            assert result == []

    def test_list_with_model_instances(self):
        """Verify set_response with model instances returns them correctly."""
        with SyncFakeVClient() as client:
            # Given two User model instances
            user_a = UserFactory.build()
            user_b = UserFactory.build()
            client.set_response(Routes.USERS_LIST, items=[user_a, user_b])

            # When listing all users
            result = sync_users_service().list_all()

            # Then both users are returned with matching IDs
            assert len(result) == 2
            assert result[0].id == user_a.id
            assert result[1].id == user_b.id


class TestSyncSetResponseSingle:
    """set_response() should correctly handle single-object routes."""

    def test_single_with_model_instance(self):
        """Verify set_response with a model instance on a single route."""
        with SyncFakeVClient() as client:
            # Given a campaign model set on the get route
            campaign = CampaignFactory.build()
            client.set_response(Routes.CAMPAIGNS_GET, model=campaign)

            # When fetching the campaign
            result = sync_campaigns_service("user123").get(campaign.id)

            # Then the correct campaign is returned
            assert result.id == campaign.id

    def test_renumber_with_model(self):
        """Verify set_response works for a PUT route like renumber."""
        with SyncFakeVClient() as client:
            # Given a book model set on the renumber route
            book = CampaignBookFactory.build()
            client.set_response(Routes.BOOKS_RENUMBER, model=book)

            # When renumbering the book
            result = sync_books_service("user123", "campaign123").renumber(book.id, 5)

            # Then the book is returned
            assert isinstance(result, CampaignBook)
            assert result.id == book.id


class TestSyncSetError:
    """set_error() should make routes return error responses."""

    def test_not_found_error(self):
        """Verify set_error with 404 raises NotFoundError."""
        with SyncFakeVClient() as client:
            # Given the campaigns get route set to return 404
            client.set_error(Routes.CAMPAIGNS_GET, status_code=404)

            # When fetching a campaign
            # Then a NotFoundError is raised
            with pytest.raises(NotFoundError):
                sync_campaigns_service("user123").get("nonexistent")
