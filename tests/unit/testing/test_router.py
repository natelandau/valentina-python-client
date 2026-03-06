"""Tests for the _FakeRouter."""

import json

import httpx

from vclient.endpoints import Endpoints
from vclient.testing._router import _FakeRouter


class TestFakeRouterPatternMatching:
    """Router should match requests to registered routes."""

    def test_matches_simple_endpoint(self):
        router = _FakeRouter()
        request = httpx.Request("GET", "https://fake.test/api/v1/health")
        response = router.handle(request)
        assert response.status_code == 200

    def test_matches_parameterized_endpoint(self):
        router = _FakeRouter()
        request = httpx.Request(
            "GET",
            "https://fake.test/api/v1/companies/abc123/users/user456/campaigns",
        )
        response = router.handle(request)
        assert response.status_code == 200
        body = json.loads(response.content)
        assert "items" in body
        assert "total" in body

    def test_detail_endpoint_returns_single_object(self):
        router = _FakeRouter()
        request = httpx.Request(
            "GET",
            "https://fake.test/api/v1/companies/abc/users/u1/campaigns/c1",
        )
        response = router.handle(request)
        assert response.status_code == 200
        body = json.loads(response.content)
        assert "items" not in body
        assert "id" in body

    def test_delete_returns_204(self):
        router = _FakeRouter()
        request = httpx.Request(
            "DELETE",
            "https://fake.test/api/v1/companies/abc/users/u1/campaigns/c1",
        )
        response = router.handle(request)
        assert response.status_code == 204

    def test_unmatched_route_returns_404(self):
        router = _FakeRouter()
        request = httpx.Request("GET", "https://fake.test/api/v1/nonexistent")
        response = router.handle(request)
        assert response.status_code == 404


class TestFakeRouterOverrides:
    """Router should support user-defined route overrides."""

    def test_override_replaces_default(self):
        router = _FakeRouter()
        custom_json = {"items": [{"id": "custom"}], "total": 1, "limit": 10, "offset": 0}
        router.add_route("GET", Endpoints.CAMPAIGNS, json=custom_json)
        request = httpx.Request(
            "GET",
            "https://fake.test/api/v1/companies/abc/users/u1/campaigns",
        )
        response = router.handle(request)
        body = json.loads(response.content)
        assert body["items"][0]["id"] == "custom"

    def test_override_with_status_code(self):
        router = _FakeRouter()
        router.add_route("GET", Endpoints.CAMPAIGN, json={"error": "not found"}, status_code=404)
        request = httpx.Request(
            "GET",
            "https://fake.test/api/v1/companies/abc/users/u1/campaigns/c1",
        )
        response = router.handle(request)
        assert response.status_code == 404
