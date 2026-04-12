"""Tests for GlobalAdminService audit log methods."""

import pytest
import respx

from vclient.endpoints import Endpoints
from vclient.models import AuditLog, AuditLogDetail, PaginatedResponse

pytestmark = pytest.mark.anyio

DEVELOPER_ID = "dev123"


@pytest.fixture
def audit_log_response_data() -> dict:
    """Return sample audit log response data."""
    return {
        "id": "log123",
        "date_created": "2024-01-15T10:30:00Z",
        "entity_type": "USER",
        "operation": "UPDATE",
        "target_entity_id": "user456",
        "description": "Updated user role",
        "changes": {"role": {"old": "PLAYER", "new": "ADMIN"}},
        "company_id": "company789",
        "acting_user_id": "user111",
        "user_id": "user456",
        "campaign_id": None,
        "book_id": None,
        "chapter_id": None,
        "character_id": None,
        "request_id": "req789",
    }


@pytest.fixture
def paginated_audit_logs_response(audit_log_response_data) -> dict:
    """Return sample paginated audit logs response."""
    return {
        "items": [audit_log_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


class TestGlobalAdminServiceGetAuditLogPage:
    """Tests for GlobalAdminService.get_audit_log_page method."""

    @respx.mock
    async def test_get_audit_log_page(self, vclient, base_url, paginated_audit_logs_response):
        """Verify get_audit_log_page returns paginated AuditLog objects."""
        route = respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER_AUDIT_LOGS.format(developer_id=DEVELOPER_ID)}",
            params={"limit": "10", "offset": "0"},
        ).respond(200, json=paginated_audit_logs_response)

        result = await vclient.global_admin.get_audit_log_page(DEVELOPER_ID)

        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], AuditLog)
        assert result.items[0].entity_type == "USER"

    @respx.mock
    async def test_get_audit_log_page_with_company_filter(
        self, vclient, base_url, paginated_audit_logs_response
    ):
        """Verify get_audit_log_page accepts company_id filter."""
        route = respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER_AUDIT_LOGS.format(developer_id=DEVELOPER_ID)}",
            params={"limit": "10", "offset": "0", "company_id": "company789"},
        ).respond(200, json=paginated_audit_logs_response)

        result = await vclient.global_admin.get_audit_log_page(
            DEVELOPER_ID, company_id="company789"
        )

        assert route.called
        assert isinstance(result, PaginatedResponse)

    @respx.mock
    async def test_get_audit_log_page_with_include_returns_detail(
        self, vclient, base_url, audit_log_response_data
    ):
        """Verify get_audit_log_page returns AuditLogDetail with include=request_details."""
        detail_data = {
            **audit_log_response_data,
            "method": "PATCH",
            "url": "/api/v1/companies/c1/users/u1",
            "request_json": {"role": "ADMIN"},
            "request_body": '{"role": "ADMIN"}',
            "path_params": {"company_id": "c1", "user_id": "u1"},
            "query_params": {},
            "operation_id": "update_user",
            "handler_name": "UsersHandler.update",
            "name": "Update User",
            "summary": "Update a user",
        }
        route = respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER_AUDIT_LOGS.format(developer_id=DEVELOPER_ID)}",
            params={"limit": "10", "offset": "0", "include": "request_details"},
        ).respond(
            200,
            json={"items": [detail_data], "limit": 10, "offset": 0, "total": 1},
        )

        result = await vclient.global_admin.get_audit_log_page(
            DEVELOPER_ID, include=["request_details"]
        )

        assert route.called
        assert isinstance(result.items[0], AuditLogDetail)
        assert result.items[0].method == "PATCH"


class TestGlobalAdminServiceListAllAuditLogs:
    """Tests for GlobalAdminService.list_all_audit_logs method."""

    @respx.mock
    async def test_list_all_audit_logs(self, vclient, base_url, audit_log_response_data):
        """Verify list_all_audit_logs returns all audit logs."""
        respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER_AUDIT_LOGS.format(developer_id=DEVELOPER_ID)}",
            params={"limit": "100", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [audit_log_response_data],
                "limit": 100,
                "offset": 0,
                "total": 1,
            },
        )

        result = await vclient.global_admin.list_all_audit_logs(DEVELOPER_ID)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], AuditLog)


class TestGlobalAdminServiceIterAllAuditLogs:
    """Tests for GlobalAdminService.iter_all_audit_logs method."""

    @respx.mock
    async def test_iter_all_audit_logs(self, vclient, base_url, audit_log_response_data):
        """Verify iter_all_audit_logs yields AuditLog objects."""
        respx.get(
            f"{base_url}{Endpoints.ADMIN_DEVELOPER_AUDIT_LOGS.format(developer_id=DEVELOPER_ID)}",
            params={"limit": "100", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [audit_log_response_data],
                "limit": 100,
                "offset": 0,
                "total": 1,
            },
        )

        logs = [log async for log in vclient.global_admin.iter_all_audit_logs(DEVELOPER_ID)]

        assert len(logs) == 1
        assert isinstance(logs[0], AuditLog)
