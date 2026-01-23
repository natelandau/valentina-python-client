"""Tests for vclient.api.models.pagination."""

from vclient.api.models.pagination import PaginatedResponse


class TestPaginatedResponse:
    """Tests for PaginatedResponse dataclass."""

    def test_from_dict(self):
        """Verify creating PaginatedResponse from a dictionary."""
        # Given: A dictionary with pagination data
        data = {
            "items": [{"id": 1}, {"id": 2}],
            "limit": 10,
            "offset": 0,
            "total": 47,
        }

        # When: Creating PaginatedResponse from dict
        response = PaginatedResponse.from_dict(data)

        # Then: All values are correctly parsed
        assert response.items == [{"id": 1}, {"id": 2}]
        assert response.limit == 10
        assert response.offset == 0
        assert response.total == 47

    def test_from_dict_with_defaults(self):
        """Verify missing keys get default values."""
        # When: Creating PaginatedResponse from empty dict
        response = PaginatedResponse.from_dict({})

        # Then: Default values are applied
        assert response.items == []
        assert response.limit == 0
        assert response.offset == 0
        assert response.total == 0

    def test_has_more_true(self):
        """Verify has_more returns True when more pages exist."""
        # Given: A response with more items available
        response = PaginatedResponse(
            items=[{"id": 1}] * 10,
            limit=10,
            offset=0,
            total=47,
        )

        # When/Then: has_more is True
        assert response.has_more is True

    def test_has_more_false_on_last_page(self):
        """Verify has_more returns False on the last page."""
        # Given: A response on the last page
        response = PaginatedResponse(
            items=[{"id": 1}] * 7,
            limit=10,
            offset=40,
            total=47,
        )

        # When/Then: has_more is False
        assert response.has_more is False

    def test_has_more_false_when_exact_fit(self):
        """Verify has_more returns False when items fit exactly."""
        # Given: A response where items fit exactly in one page
        response = PaginatedResponse(
            items=[{"id": 1}] * 10,
            limit=10,
            offset=0,
            total=10,
        )

        # When/Then: has_more is False
        assert response.has_more is False

    def test_next_offset(self):
        """Verify next_offset calculation."""
        # Given: A paginated response
        response = PaginatedResponse(
            items=[{"id": 1}] * 10,
            limit=10,
            offset=20,
            total=100,
        )

        # When/Then: next_offset is correctly calculated
        assert response.next_offset == 30

    def test_total_pages(self):
        """Verify total_pages calculation."""
        # Given: A response with 47 total items and limit of 10
        response = PaginatedResponse(
            items=[],
            limit=10,
            offset=0,
            total=47,
        )

        # When/Then: total_pages is 5 (ceiling of 47/10)
        assert response.total_pages == 5

    def test_total_pages_exact_division(self):
        """Verify total_pages when total divides evenly."""
        # Given: A response where total divides evenly by limit
        response = PaginatedResponse(
            items=[],
            limit=10,
            offset=0,
            total=50,
        )

        # When/Then: total_pages is exactly 5
        assert response.total_pages == 5

    def test_total_pages_zero_limit(self):
        """Verify total_pages returns 0 when limit is 0."""
        # Given: A response with zero limit
        response = PaginatedResponse(
            items=[],
            limit=0,
            offset=0,
            total=47,
        )

        # When/Then: total_pages is 0 to avoid division by zero
        assert response.total_pages == 0

    def test_current_page_first(self):
        """Verify current_page returns 1 for first page."""
        # Given: A response on the first page
        response = PaginatedResponse(
            items=[],
            limit=10,
            offset=0,
            total=47,
        )

        # When/Then: current_page is 1
        assert response.current_page == 1

    def test_current_page_middle(self):
        """Verify current_page calculation for middle pages."""
        # Given: A response on the third page
        response = PaginatedResponse(
            items=[],
            limit=10,
            offset=20,
            total=47,
        )

        # When/Then: current_page is 3
        assert response.current_page == 3

    def test_current_page_last(self):
        """Verify current_page for last page."""
        # Given: A response on the last page
        response = PaginatedResponse(
            items=[],
            limit=10,
            offset=40,
            total=47,
        )

        # When/Then: current_page is 5
        assert response.current_page == 5

    def test_current_page_zero_limit(self):
        """Verify current_page returns 0 when limit is 0."""
        # Given: A response with zero limit
        response = PaginatedResponse(
            items=[],
            limit=0,
            offset=0,
            total=47,
        )

        # When/Then: current_page is 0 to avoid division by zero
        assert response.current_page == 0
