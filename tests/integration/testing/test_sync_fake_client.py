"""Integration tests for SyncFakeVClient."""

from vclient._sync.registry import sync_campaigns_service, sync_companies_service
from vclient.models import Campaign, Company
from vclient.testing import SyncFakeVClient


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
            result = sync_campaigns_service("user123").list_all()

            # Then the result contains Campaign instances
            assert isinstance(result, list)
            assert isinstance(result[0], Campaign)
