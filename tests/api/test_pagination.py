"""Tests for vclient.api.models.pagination."""

from vclient.api.models.pagination import PaginatedResponse


class TestPaginatedResponse:
    """Tests for PaginatedResponse dataclass."""

    def test_from_dict(self):
        """Test creating PaginatedResponse from a dictionary."""
        data = {
            "items": [{"id": 1}, {"id": 2}],
            "limit": 10,
            "offset": 0,
            "total": 47,
        }
        response = PaginatedResponse.from_dict(data)
        assert response.items == [{"id": 1}, {"id": 2}]
        assert response.limit == 10
        assert response.offset == 0
        assert response.total == 47

    def test_from_dict_with_defaults(self):
        """Test that missing keys get default values."""
        response = PaginatedResponse.from_dict({})
        assert response.items == []
        assert response.limit == 0
        assert response.offset == 0
        assert response.total == 0

    def test_has_more_true(self):
        """Test has_more returns True when more pages exist."""
        response = PaginatedResponse(
            items=[{"id": 1}] * 10,
            limit=10,
            offset=0,
            total=47,
        )
        assert response.has_more is True

    def test_has_more_false_on_last_page(self):
        """Test has_more returns False on the last page."""
        response = PaginatedResponse(
            items=[{"id": 1}] * 7,
            limit=10,
            offset=40,
            total=47,
        )
        assert response.has_more is False

    def test_has_more_false_when_exact_fit(self):
        """Test has_more returns False when items fit exactly."""
        response = PaginatedResponse(
            items=[{"id": 1}] * 10,
            limit=10,
            offset=0,
            total=10,
        )
        assert response.has_more is False

    def test_next_offset(self):
        """Test next_offset calculation."""
        response = PaginatedResponse(
            items=[{"id": 1}] * 10,
            limit=10,
            offset=20,
            total=100,
        )
        assert response.next_offset == 30

    def test_total_pages(self):
        """Test total_pages calculation."""
        response = PaginatedResponse(
            items=[],
            limit=10,
            offset=0,
            total=47,
        )
        assert response.total_pages == 5

    def test_total_pages_exact_division(self):
        """Test total_pages when total divides evenly."""
        response = PaginatedResponse(
            items=[],
            limit=10,
            offset=0,
            total=50,
        )
        assert response.total_pages == 5

    def test_total_pages_zero_limit(self):
        """Test total_pages returns 0 when limit is 0."""
        response = PaginatedResponse(
            items=[],
            limit=0,
            offset=0,
            total=47,
        )
        assert response.total_pages == 0

    def test_current_page_first(self):
        """Test current_page returns 1 for first page."""
        response = PaginatedResponse(
            items=[],
            limit=10,
            offset=0,
            total=47,
        )
        assert response.current_page == 1

    def test_current_page_middle(self):
        """Test current_page calculation for middle pages."""
        response = PaginatedResponse(
            items=[],
            limit=10,
            offset=20,
            total=47,
        )
        assert response.current_page == 3

    def test_current_page_last(self):
        """Test current_page for last page."""
        response = PaginatedResponse(
            items=[],
            limit=10,
            offset=40,
            total=47,
        )
        assert response.current_page == 5

    def test_current_page_zero_limit(self):
        """Test current_page returns 0 when limit is 0."""
        response = PaginatedResponse(
            items=[],
            limit=0,
            offset=0,
            total=47,
        )
        assert response.current_page == 0
