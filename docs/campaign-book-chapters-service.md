# Campaign Chapters Service

Manage chapters within a campaign book, including their notes and assets.

## Usage

```python
from vclient import chapters_service

chapters = chapters_service(
    user_id="USER_ID",
    campaign_id="CAMPAIGN_ID",
    book_id="BOOK_ID",
    company_id="COMPANY_ID"
)
```

## Methods

### CRUD Operations

| Method                                        | Returns           | Description                 |
| --------------------------------------------- | ----------------- | --------------------------- |
| `get(chapter_id)`                             | `CampaignChapter` | Get a chapter by ID         |
| `create(ChapterCreate, **kwargs)`             | `CampaignChapter` | Create a new chapter        |
| `update(chapter_id, ChapterUpdate, **kwargs)` | `CampaignChapter` | Update a chapter            |
| `delete(chapter_id)`                          | `None`            | Delete a chapter            |
| `renumber(chapter_id, number)`                | `CampaignChapter` | Change a chapter's position |

### Pagination

| Method                      | Returns                              | Description                  |
| --------------------------- | ------------------------------------ | ---------------------------- |
| `get_page(limit?, offset?)` | `PaginatedResponse[CampaignChapter]` | Get a page of chapters       |
| `list_all()`                | `list[CampaignChapter]`              | Get all chapters             |
| `iter_all(limit?)`          | `AsyncIterator[CampaignChapter]`     | Iterate through all chapters |

### Assets

| Method                                                       | Returns                      | Description         |
| ------------------------------------------------------------ | ---------------------------- | ------------------- |
| `list_assets(chapter_id, limit?, offset?)`                   | `PaginatedResponse[S3Asset]` | List chapter assets |
| `get_asset(chapter_id, asset_id)`                            | `S3Asset`                    | Get an asset        |
| `upload_asset(chapter_id, filename, content, content_type?)` | `S3Asset`                    | Upload an asset     |
| `delete_asset(chapter_id, asset_id)`                         | `None`                       | Delete an asset     |

### Notes

| Method                                                   | Returns                   | Description           |
| -------------------------------------------------------- | ------------------------- | --------------------- |
| `get_notes_page(chapter_id, limit?, offset?)`            | `PaginatedResponse[Note]` | Get a page of notes   |
| `list_all_notes(chapter_id)`                             | `list[Note]`              | Get all notes         |
| `iter_all_notes(chapter_id, limit?)`                     | `AsyncIterator[Note]`     | Iterate through notes |
| `get_note(chapter_id, note_id)`                          | `Note`                    | Get a note            |
| `create_note(chapter_id, NoteCreate, **kwargs)`          | `Note`                    | Create a note         |
| `update_note(chapter_id, note_id, NoteUpdate, **kwargs)` | `Note`                    | Update a note         |
| `delete_note(chapter_id, note_id)`                       | `None`                    | Delete a note         |

## Example

```python
from vclient.models import ChapterCreate, ChapterUpdate, NoteCreate

# Create a chapter (preferred: use model object)
request = ChapterCreate(
    name="The First Night",
    description="Characters meet for the first time"
)
chapter = await chapters.create(request)

# Alternative: pass fields as kwargs
chapter = await chapters.create(
    name="The First Night",
    description="Characters meet for the first time"
)

# Update a chapter
update = ChapterUpdate(name="The First Night: Introductions")
updated = await chapters.update(chapter.id, update)

# Reorder the chapter
await chapters.renumber(chapter.id, number=3)

# Create a note
note_request = NoteCreate(title="Scene Notes", content="...")
note = await chapters.create_note(chapter.id, note_request)
```

See [Response Models](models.md) for `CampaignChapter`, `S3Asset`, `Note`, and related types.
