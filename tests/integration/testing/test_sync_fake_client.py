"""Integration tests for SyncFakeVClient."""

import pytest

from vclient._sync.registry import sync_campaigns_service, sync_companies_service
from vclient.exceptions import NotFoundError
from vclient.models import Campaign, Company, DamageTracker, Health, StainsTracker
from vclient.testing import Routes, StainsTrackerFactory, SyncFakeVClient


class TestSyncFakeVClient:
    """SyncFakeVClient should work as a drop-in replacement for SyncVClient."""

    def test_context_manager(self):
        """Verify SyncFakeVClient works as a sync context manager."""
        # When using SyncFakeVClient as a context manager
        with SyncFakeVClient() as client:
            # Then the client is open inside the block
            assert not client.is_closed

        # Then the client is closed after exiting
        assert client.is_closed

    def test_companies_list_all(self):
        """Verify listing companies returns Company models."""
        with SyncFakeVClient() as client:
            # When listing all companies
            companies = client.companies
            result = companies.list_all()

            # Then the result contains Company instances
            assert isinstance(result, list)
            assert isinstance(result[0], Company)

    def test_factory_function_works(self):
        """Verify factory functions work with SyncFakeVClient as default client."""
        with SyncFakeVClient() as _client:
            # When using a factory function
            result = sync_companies_service().list_all()

            # Then the result contains Company instances
            assert isinstance(result, list)
            assert isinstance(result[0], Company)

    def test_scoped_service_works(self):
        """Verify scoped factory functions work with SyncFakeVClient."""
        with SyncFakeVClient() as _client:
            # When using a scoped factory function
            result = sync_campaigns_service("on-behalf-of-user").list_all()

            # Then the result contains Campaign instances
            assert isinstance(result, list)
            assert isinstance(result[0], Campaign)


class TestSyncTrackerAndHealthRoutes:
    """SyncFakeVClient should serve tracker and health routes."""

    def test_tracker_default_route(self):
        """Verify the default tracker route returns a DamageTracker."""
        with SyncFakeVClient() as client:
            # When getting a tracker with no override
            result = client.character_traits("ch1", "user1", company_id="co1").get_tracker("ct1")

            # Then a DamageTracker is returned
            assert isinstance(result, DamageTracker)

    def test_tracker_override_with_other_variant(self):
        """Verify any tracker variant can override a tracker route."""
        with SyncFakeVClient() as client:
            # Given the action route returns a stains tracker
            client.set_response(
                Routes.CHARACTER_TRAITS_TRACKER_ACTION, model=StainsTrackerFactory.build()
            )

            # When adding a stain
            result = client.character_traits("ch1", "user1", company_id="co1").apply_tracker_action(
                "ct1", "add_stain"
            )

            # Then the stains tracker is returned
            assert isinstance(result, StainsTracker)

    def test_health_default_route(self):
        """Verify the default health route returns Health."""
        with SyncFakeVClient() as client:
            # When getting health with no override
            result = client.characters("user1", company_id="co1").get_health("ch1")

            # Then Health is returned
            assert isinstance(result, Health)

    def test_health_error(self):
        """Verify set_error on a health route raises the mapped exception."""
        with SyncFakeVClient() as client:
            # Given the health route returns 404
            client.set_error(Routes.CHARACTERS_HEALTH_GET, status_code=404)

            # When/Then getting health raises NotFoundError
            with pytest.raises(NotFoundError):
                client.characters("user1", company_id="co1").get_health("ch1")
