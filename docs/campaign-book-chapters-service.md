# Campaign Books Service

The Chapter service provides methods to create, retrieve, update, and delete campaign book chapters within a campaign book, as well as access chapter notes and assets.

## Usage

The chapter service is scoped to a specific company, user, campaign, and book context at creation time:

```python
from vclient import VClient

async with VClient(base_url="...", api_key="...") as client:
    # Get a campaign books service scoped to a company, user, and campaign
    books = client.chapters("company_id", "user_id", "campaign_id", "book_id")

    # All operations use this context
    all_chapters = await chapters.list_all()
    chapter = await chapters.get("chapter_id")
```

Or using the factory function:

```python
from vclient import chapters_service

# Requires a default client to be configured
chapters = chapters_service("company_id", "user_id", "campaign_id", "book_id")
all_chapters = await chapters.list_all()
```

## Available Methods

### Book CRUD

- `get(chapter_id)` - Retrieve a chapter by ID
- `create(name, description?)` - Create a new book
- `update(chapter_id, name?, description?)` - Update a chapter
- `delete(chapter_id)` - Delete a chapter
- `renumber(chapter_id, number)` - Change a chapter's position number
- `get_page(limit?, offset?)` - Get a paginated page of chapters
- `list_all()` - Get all chapters
- `iter_all(limit?)` - Iterate through all chapters

### Notes

- `get_notes_page(chapter_id, limit?, offset?)` - Get a paginated page of notes
- `list_all_notes(chapter_id)` - Get all notes
- `iter_all_notes(chapter_id, limit?)` - Iterate through all notes
- `get_note(chapter_id, note_id)` - Get a specific note
- `create_note(chapter_id, title, content)` - Create a note
- `update_note(chapter_id, note_id, title?, content?)` - Update a note
- `delete_note(chapter_id, note_id)` - Delete a note

### Assets

- `list_assets(chapter_id, limit?, offset?)` - List chapter assets
- `get_asset(chapter_id, asset_id)` - Get a specific asset
- `upload_asset(chapter_id, filename, content, content_type?)` - Upload an asset
- `delete_asset(chapter_id, asset_id)` - Delete an asset

## Response Models

### `CampaignChapter`

Represents a campaign chapter entity returned from the API.

| Field           | Type          | Description                             |
| --------------- | ------------- | --------------------------------------- |
| `id`            | `str \| None` | MongoDB document ObjectID               |
| `date_created`  | `datetime`    | Timestamp when the chapter was created  |
| `date_modified` | `datetime`    | Timestamp when the chapter was modified |
| `name`          | `str`         | Chapter name (3-50 characters)          |
| `description`   | `str \| None` | Chapter description                     |
| `asset_ids`     | `list[str]`   | List of associated asset IDs            |
| `number`        | `int`         | Chapter number within the campaign      |
| `book_id`       | `str`         | ID of the parent book                   |

### `S3Asset`

Represents a file asset stored in S3.

| Field               | Type                        | Description                      |
| ------------------- | --------------------------- | -------------------------------- |
| `id`                | `str`                       | MongoDB document ObjectID        |
| `date_created`      | `datetime`                  | Timestamp when created           |
| `date_modified`     | `datetime`                  | Timestamp when modified          |
| `file_type`         | `S3AssetType`               | Type of file (image, text, etc.) |
| `original_filename` | `str`                       | Original filename when uploaded  |
| `public_url`        | `str`                       | Public URL to access the file    |
| `uploaded_by`       | `str`                       | ID of user who uploaded          |
| `parent_type`       | `S3AssetParentType \| None` | Type of parent entity            |

### `Note`

Represents a note attached to a chapter.

| Field           | Type       | Description                      |
| --------------- | ---------- | -------------------------------- |
| `id`            | `str`      | MongoDB document ObjectID        |
| `date_created`  | `datetime` | Timestamp when created           |
| `date_modified` | `datetime` | Timestamp when modified          |
| `title`         | `str`      | Note title (3-50 characters)     |
| `content`       | `str`      | Note content (supports markdown) |
