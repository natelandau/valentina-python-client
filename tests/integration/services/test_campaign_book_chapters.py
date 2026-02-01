"""Tests for vclient.services.campaign_book_chapters."""

import pytest
import respx

from vclient.endpoints import Endpoints
from vclient.exceptions import NotFoundError
from vclient.models import CampaignChapter, Note, PaginatedResponse, S3Asset

pytestmark = pytest.mark.anyio


@pytest.fixture
def chapter_response_data() -> dict:
    """Return sample chapter response data."""
    return {
        "id": "507f1f77bcf86cd799439011",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "name": "Test Chapter",
        "description": "A test chapter description",
        "asset_ids": ["asset1", "asset2"],
        "number": 1,
        "book_id": "book123",
    }


@pytest.fixture
def paginated_chapters_response(chapter_response_data) -> dict:
    """Return sample paginated chapters response."""
    return {
        "items": [chapter_response_data],
        "limit": 10,
        "offset": 0,
        "total": 1,
    }


@pytest.fixture
def asset_response_data() -> dict:
    """Return sample asset response data."""
    return {
        "id": "asset123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "file_type": "image",
        "original_filename": "chapter.png",
        "public_url": "https://example.com/chapter.png",
        "uploaded_by": "user123",
        "parent_type": "campaignchapter",
    }


@pytest.fixture
def note_response_data() -> dict:
    """Return sample note response data."""
    return {
        "id": "note123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "title": "Test Note",
        "content": "This is test content",
    }


class TestChaptersServiceGetPage:
    """Tests for ChaptersService.get_page method."""

    @respx.mock
    async def test_get_page_chapters(self, vclient, base_url, paginated_chapters_response):
        """Verify get_page returns paginated CampaignChapter objects."""
        # Given: A mocked chapters list endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        route = respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTERS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id)}",
            params={"limit": "10", "offset": "0"},
        ).respond(200, json=paginated_chapters_response)

        # When: Getting a page of chapters
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).get_page()

        # Then: Returns PaginatedResponse with CampaignChapter objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], CampaignChapter)
        assert result.items[0].name == "Test Chapter"
        assert result.total == 1

    @respx.mock
    async def test_get_page_with_pagination(self, vclient, base_url, chapter_response_data):
        """Verify get_page accepts pagination parameters."""
        # Given: A mocked endpoint expecting custom pagination
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        route = respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTERS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id)}",
            params={"limit": "25", "offset": "50"},
        ).respond(
            200,
            json={
                "items": [chapter_response_data],
                "limit": 25,
                "offset": 50,
                "total": 100,
            },
        )

        # When: Getting a page with custom pagination
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).get_page(limit=25, offset=50)

        # Then: Request was made with correct params
        assert route.called
        assert result.limit == 25
        assert result.offset == 50


class TestChaptersServiceListAll:
    """Tests for ChaptersService.list_all method."""

    @respx.mock
    async def test_list_all_chapters(self, vclient, base_url, chapter_response_data):
        """Verify list_all returns all chapters across pages."""
        # Given: Mocked endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTERS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id)}",
            params={"limit": "100", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [chapter_response_data],
                "limit": 100,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Calling list_all
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).list_all()

        # Then: Returns list of CampaignChapter objects
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], CampaignChapter)


class TestChaptersServiceIterAll:
    """Tests for ChaptersService.iter_all method."""

    @respx.mock
    async def test_iter_all_chapters(self, vclient, base_url, chapter_response_data):
        """Verify iter_all yields CampaignChapter objects across pages."""
        # Given: Mocked endpoints for multiple pages
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter2 = {
            **chapter_response_data,
            "id": "507f1f77bcf86cd799439012",
            "name": "Chapter 2",
            "number": 2,
        }
        respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTERS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id)}",
            params={"limit": "1", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [chapter_response_data],
                "limit": 1,
                "offset": 0,
                "total": 2,
            },
        )
        respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTERS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id)}",
            params={"limit": "1", "offset": "1"},
        ).respond(
            200,
            json={
                "items": [chapter2],
                "limit": 1,
                "offset": 1,
                "total": 2,
            },
        )

        # When: Iterating through all chapters
        chapters = [
            c
            async for c in vclient.chapters(
                user_id, campaign_id, book_id, company_id=company_id
            ).iter_all(limit=1)
        ]

        # Then: All chapters are yielded as CampaignChapter objects
        assert len(chapters) == 2
        assert all(isinstance(c, CampaignChapter) for c in chapters)
        assert chapters[0].name == "Test Chapter"
        assert chapters[1].name == "Chapter 2"


class TestChaptersServiceGet:
    """Tests for ChaptersService.get method."""

    @respx.mock
    async def test_get_chapter(self, vclient, base_url, chapter_response_data):
        """Verify getting a chapter returns CampaignChapter object."""
        # Given: A mocked chapter endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "507f1f77bcf86cd799439011"
        route = respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTER.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}"
        ).respond(200, json=chapter_response_data)

        # When: Getting the chapter
        result = await vclient.chapters(user_id, campaign_id, book_id, company_id=company_id).get(
            chapter_id
        )

        # Then: Returns CampaignChapter object with correct data
        assert route.called
        assert isinstance(result, CampaignChapter)
        assert result.id == chapter_id
        assert result.name == "Test Chapter"
        assert result.number == 1

    @respx.mock
    async def test_get_chapter_not_found(self, vclient, base_url):
        """Verify getting non-existent chapter raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "nonexistent"
        respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTER.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}"
        ).respond(404, json={"detail": "Chapter not found"})

        # When/Then: Getting the chapter raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.chapters(user_id, campaign_id, book_id, company_id=company_id).get(
                chapter_id
            )


class TestChaptersServiceCreate:
    """Tests for ChaptersService.create method."""

    @respx.mock
    async def test_create_chapter_minimal(self, vclient, base_url, chapter_response_data):
        """Verify creating chapter with minimal data."""
        # Given: A mocked create endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        route = respx.post(
            f"{base_url}{Endpoints.BOOK_CHAPTERS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id)}"
        ).respond(201, json=chapter_response_data)

        # When: Creating a chapter with minimal data
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).create(name="Test Chapter")

        # Then: Returns created CampaignChapter object
        assert route.called
        assert isinstance(result, CampaignChapter)
        assert result.name == "Test Chapter"

        # Verify request body
        request = route.calls.last.request
        import json

        body = json.loads(request.content)
        assert body["name"] == "Test Chapter"

    @respx.mock
    async def test_create_chapter_with_description(self, vclient, base_url, chapter_response_data):
        """Verify creating chapter with all fields."""
        # Given: A mocked create endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        route = respx.post(
            f"{base_url}{Endpoints.BOOK_CHAPTERS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id)}"
        ).respond(201, json=chapter_response_data)

        # When: Creating a chapter with all fields
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).create(
            name="Test Chapter",
            description="A test chapter description",
        )

        # Then: Returns created CampaignChapter object
        assert route.called
        assert isinstance(result, CampaignChapter)

        # Verify request body
        request = route.calls.last.request
        import json

        body = json.loads(request.content)
        assert body["name"] == "Test Chapter"
        assert body["description"] == "A test chapter description"


class TestChaptersServiceUpdate:
    """Tests for ChaptersService.update method."""

    @respx.mock
    async def test_update_chapter_name(self, vclient, base_url, chapter_response_data):
        """Verify updating chapter name."""
        # Given: A mocked update endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "507f1f77bcf86cd799439011"
        updated_data = {**chapter_response_data, "name": "Updated Name"}
        route = respx.patch(
            f"{base_url}{Endpoints.BOOK_CHAPTER.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}"
        ).respond(200, json=updated_data)

        # When: Updating the chapter name
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).update(chapter_id, name="Updated Name")

        # Then: Returns updated CampaignChapter object
        assert route.called
        assert isinstance(result, CampaignChapter)
        assert result.name == "Updated Name"

        # Verify request body
        request = route.calls.last.request
        import json

        body = json.loads(request.content)
        assert body["name"] == "Updated Name"

    @respx.mock
    async def test_update_chapter_not_found(self, vclient, base_url):
        """Verify updating non-existent chapter raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "nonexistent"
        respx.patch(
            f"{base_url}{Endpoints.BOOK_CHAPTER.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}"
        ).respond(404, json={"detail": "Chapter not found"})

        # When/Then: Updating raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.chapters(user_id, campaign_id, book_id, company_id=company_id).update(
                chapter_id, name="New Name"
            )


class TestChaptersServiceDelete:
    """Tests for ChaptersService.delete method."""

    @respx.mock
    async def test_delete_chapter(self, vclient, base_url):
        """Verify deleting a chapter."""
        # Given: A mocked delete endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "507f1f77bcf86cd799439011"
        route = respx.delete(
            f"{base_url}{Endpoints.BOOK_CHAPTER.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}"
        ).respond(204)

        # When: Deleting the chapter
        await vclient.chapters(user_id, campaign_id, book_id, company_id=company_id).delete(
            chapter_id
        )

        # Then: Request was made
        assert route.called

    @respx.mock
    async def test_delete_chapter_not_found(self, vclient, base_url):
        """Verify deleting non-existent chapter raises NotFoundError."""
        # Given: A mocked endpoint returning 404
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "nonexistent"
        respx.delete(
            f"{base_url}{Endpoints.BOOK_CHAPTER.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}"
        ).respond(404, json={"detail": "Chapter not found"})

        # When/Then: Deleting raises NotFoundError
        with pytest.raises(NotFoundError):
            await vclient.chapters(user_id, campaign_id, book_id, company_id=company_id).delete(
                chapter_id
            )


class TestChaptersServiceRenumber:
    """Tests for ChaptersService.renumber method."""

    @respx.mock
    async def test_renumber_chapter(self, vclient, base_url, chapter_response_data):
        """Verify renumbering a chapter."""
        # Given: A mocked renumber endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "507f1f77bcf86cd799439011"
        updated_data = {**chapter_response_data, "number": 3}
        route = respx.put(
            f"{base_url}{Endpoints.BOOK_CHAPTER_NUMBER.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}"
        ).respond(200, json=updated_data)

        # When: Renumbering the chapter
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).renumber(chapter_id, number=3)

        # Then: Returns updated CampaignChapter object
        assert route.called
        assert isinstance(result, CampaignChapter)
        assert result.number == 3

        # Verify request body
        request = route.calls.last.request
        import json

        body = json.loads(request.content)
        assert body == {"number": 3}


class TestChaptersServiceNotes:
    """Tests for ChaptersService note methods."""

    @respx.mock
    async def test_get_notes_page(self, vclient, base_url, note_response_data):
        """Verify getting a page of notes."""
        # Given: A mocked notes endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "chapter123"
        route = respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTER_NOTES.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}",
            params={"limit": "10", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [note_response_data],
                "limit": 10,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Getting a page of notes
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).get_notes_page(chapter_id)

        # Then: Returns paginated Note objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], Note)

    @respx.mock
    async def test_list_all_notes(self, vclient, base_url, note_response_data):
        """Verify list_all_notes returns all notes."""
        # Given: A mocked notes endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "chapter123"
        respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTER_NOTES.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}",
            params={"limit": "100", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [note_response_data],
                "limit": 100,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Calling list_all_notes
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).list_all_notes(chapter_id)

        # Then: Returns list of Note objects
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Note)

    @respx.mock
    async def test_get_note(self, vclient, base_url, note_response_data):
        """Verify getting a specific note."""
        # Given: A mocked note endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "chapter123"
        note_id = "note123"
        route = respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTER_NOTE.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id, note_id=note_id)}"
        ).respond(200, json=note_response_data)

        # When: Getting the note
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).get_note(chapter_id, note_id)

        # Then: Returns Note object
        assert route.called
        assert isinstance(result, Note)
        assert result.id == "note123"
        assert result.title == "Test Note"

    @respx.mock
    async def test_create_note(self, vclient, base_url, note_response_data):
        """Verify creating a note."""
        # Given: A mocked create endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "chapter123"
        route = respx.post(
            f"{base_url}{Endpoints.BOOK_CHAPTER_NOTES.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}"
        ).respond(201, json=note_response_data)

        # When: Creating a note
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).create_note(chapter_id, title="Test Note", content="This is test content")

        # Then: Returns Note object
        assert route.called
        assert isinstance(result, Note)
        assert result.title == "Test Note"

    @respx.mock
    async def test_update_note(self, vclient, base_url, note_response_data):
        """Verify updating a note."""
        # Given: A mocked update endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "chapter123"
        note_id = "note123"
        updated_data = {**note_response_data, "title": "Updated Title"}
        route = respx.patch(
            f"{base_url}{Endpoints.BOOK_CHAPTER_NOTE.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id, note_id=note_id)}"
        ).respond(200, json=updated_data)

        # When: Updating the note
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).update_note(chapter_id, note_id, title="Updated Title")

        # Then: Returns updated Note object
        assert route.called
        assert isinstance(result, Note)
        assert result.title == "Updated Title"

    @respx.mock
    async def test_delete_note(self, vclient, base_url):
        """Verify deleting a note."""
        # Given: A mocked delete endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "chapter123"
        note_id = "note123"
        route = respx.delete(
            f"{base_url}{Endpoints.BOOK_CHAPTER_NOTE.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id, note_id=note_id)}"
        ).respond(204)

        # When: Deleting the note
        await vclient.chapters(user_id, campaign_id, book_id, company_id=company_id).delete_note(
            chapter_id, note_id
        )

        # Then: Request was made
        assert route.called


class TestChaptersServiceAssets:
    """Tests for ChaptersService asset methods."""

    @respx.mock
    async def test_list_assets(self, vclient, base_url, asset_response_data):
        """Verify listing chapter assets."""
        # Given: A mocked assets endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "chapter123"
        route = respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTER_ASSETS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}",
            params={"limit": "10", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [asset_response_data],
                "limit": 10,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Listing assets
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).list_assets(chapter_id)

        # Then: Returns paginated S3Asset objects
        assert route.called
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert isinstance(result.items[0], S3Asset)

    @respx.mock
    async def test_get_asset(self, vclient, base_url, asset_response_data):
        """Verify getting a specific asset."""
        # Given: A mocked asset endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "chapter123"
        asset_id = "asset123"
        route = respx.get(
            f"{base_url}{Endpoints.BOOK_CHAPTER_ASSET.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id, asset_id=asset_id)}"
        ).respond(200, json=asset_response_data)

        # When: Getting the asset
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).get_asset(chapter_id, asset_id)

        # Then: Returns S3Asset object
        assert route.called
        assert isinstance(result, S3Asset)
        assert result.id == "asset123"

    @respx.mock
    async def test_delete_asset(self, vclient, base_url):
        """Verify deleting an asset."""
        # Given: A mocked delete endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "chapter123"
        asset_id = "asset123"
        route = respx.delete(
            f"{base_url}{Endpoints.BOOK_CHAPTER_ASSET.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id, asset_id=asset_id)}"
        ).respond(204)

        # When: Deleting the asset
        await vclient.chapters(user_id, campaign_id, book_id, company_id=company_id).delete_asset(
            chapter_id, asset_id
        )

        # Then: Request was made
        assert route.called

    @respx.mock
    async def test_upload_asset(self, vclient, base_url, asset_response_data):
        """Verify uploading an asset."""
        # Given: A mocked upload endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        book_id = "book123"
        chapter_id = "chapter123"
        route = respx.post(
            f"{base_url}{Endpoints.BOOK_CHAPTER_ASSET_UPLOAD.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id, book_id=book_id, chapter_id=chapter_id)}"
        ).respond(201, json=asset_response_data)

        # When: Uploading an asset
        result = await vclient.chapters(
            user_id, campaign_id, book_id, company_id=company_id
        ).upload_asset(
            chapter_id,
            filename="test.png",
            content=b"test content",
            content_type="image/png",
        )

        # Then: Returns S3Asset object
        assert route.called
        assert isinstance(result, S3Asset)
        assert result.id == "asset123"
