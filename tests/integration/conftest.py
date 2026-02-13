"""Integration test fixtures."""

import pytest
import respx

from vclient import VClient
from vclient.services.base import BaseService

pytestmark = pytest.mark.anyio


@pytest.fixture
def mock_api(base_url) -> respx.Router:
    """Return a respx mock router for the API."""
    with respx.mock(base_url=base_url, assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
async def vclient(base_url, api_key) -> VClient:
    """Return a VClient for testing."""
    client = VClient(base_url=base_url, api_key=api_key, timeout=10.0)
    yield client
    await client.close()


@pytest.fixture
async def vclient_with_auto_idempotency(base_url, api_key) -> VClient:
    """Return a VClient with auto_idempotency_keys enabled for testing."""
    client = VClient(
        base_url=base_url,
        api_key=api_key,
        auto_idempotency_keys=True,
    )
    yield client
    await client.close()


class ConcreteService(BaseService):
    """Concrete implementation of BaseService for testing."""


@pytest.fixture
async def base_service(vclient) -> ConcreteService:
    """Return a BaseService instance for testing."""
    return ConcreteService(vclient)


@pytest.fixture
async def base_service_with_auto_idempotency(
    vclient_with_auto_idempotency,
) -> ConcreteService:
    """Return a BaseService instance with auto_idempotency_keys enabled."""
    return ConcreteService(vclient_with_auto_idempotency)
