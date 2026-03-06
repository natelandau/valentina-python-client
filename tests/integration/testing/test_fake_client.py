"""Integration tests for FakeVClient -- verifies the full stack works."""

import pytest

from vclient.models import Campaign, Company, PaginatedResponse, SystemHealth
from vclient.registry import campaigns_service, companies_service, system_service, users_service
from vclient.testing import FakeVClient

pytestmark = pytest.mark.anyio


class TestFakeVClientBasicUsage:
    """FakeVClient should work as a drop-in replacement for VClient."""

    async def test_context_manager(self):
        """Verify FakeVClient works as an async context manager."""
        # When using FakeVClient as a context manager
        async with FakeVClient() as client:
            # Then the client is open inside the block
            assert not client.is_closed

        # Then the client is closed after exiting
        assert client.is_closed

    async def test_companies_list_all(self):
        """Verify listing companies returns Company models."""
        async with FakeVClient() as client:
            # When listing all companies
            companies = client.companies
            result = await companies.list_all()

            # Then the result contains Company instances
            assert isinstance(result, list)
            assert len(result) >= 1
            assert isinstance(result[0], Company)

    async def test_factory_function_works(self):
        """Verify factory functions work with FakeVClient as default client."""
        async with FakeVClient() as _client:
            # When using a factory function
            result = await companies_service().list_all()

            # Then the result contains Company instances
            assert isinstance(result, list)
            assert isinstance(result[0], Company)

    async def test_scoped_service_works(self):
        """Verify scoped factory functions work with FakeVClient."""
        async with FakeVClient() as _client:
            # When using a scoped factory function
            result = await campaigns_service("user123").list_all()

            # Then the result contains Campaign instances
            assert isinstance(result, list)
            assert isinstance(result[0], Campaign)

    async def test_get_page_returns_paginated_response(self):
        """Verify get_page returns a PaginatedResponse with typed items."""
        async with FakeVClient() as _client:
            # When getting a page of companies
            result = await companies_service().get_page()

            # Then the result is a PaginatedResponse with Company items
            assert isinstance(result, PaginatedResponse)
            assert isinstance(result.items[0], Company)

    async def test_get_single_resource(self):
        """Verify fetching a single resource returns the correct model."""
        async with FakeVClient() as _client:
            # When fetching system health
            result = await system_service().health()

            # Then the result is a SystemHealth instance
            assert isinstance(result, SystemHealth)

    async def test_delete_succeeds(self):
        """Verify delete operations complete without error."""
        async with FakeVClient() as _client:
            # When deleting a campaign
            await campaigns_service("user123").delete("some-id")

    async def test_default_company_id(self):
        """Verify custom default_company_id is preserved."""
        # When creating a FakeVClient with a custom default_company_id
        async with FakeVClient(default_company_id="my-company") as client:
            # Then the default_company_id is accessible
            assert client.default_company_id == "my-company"


class TestFakeVClientOverrides:
    """FakeVClient should support route overrides."""

    async def test_override_list_endpoint(self):
        """Verify custom route overrides return user-defined data."""
        async with FakeVClient() as client:
            from vclient.endpoints import Endpoints

            # Given a custom route override for users
            client.add_route(
                "GET",
                Endpoints.USERS,
                json={
                    "items": [
                        {
                            "id": "custom-user",
                            "date_created": "2024-01-01T00:00:00Z",
                            "date_modified": "2024-01-01T00:00:00Z",
                            "name_first": "Test",
                            "name_last": "User",
                            "username": "testuser",
                            "email": "test@example.com",
                            "role": "PLAYER",
                            "company_id": "fake-company",
                            "discord_profile": None,
                            "campaign_experience": [],
                            "asset_ids": [],
                        }
                    ],
                    "total": 1,
                    "limit": 10,
                    "offset": 0,
                },
            )

            # When listing users
            result = await users_service().list_all()

            # Then the overridden data is returned
            assert result[0].id == "custom-user"
