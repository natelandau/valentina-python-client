# Campaign Books Service

The Campaign Books Service provides methods to create, retrieve, update, and delete campaign books within a campaign, as well as access book notes and assets.

## Usage

The campaign books service is scoped to a specific company, user, and campaign context at creation time:

```python
from vclient import VClient

async with VClient(base_url="...", api_key="...") as client:
    # Get a campaign books service scoped to a company, user, and campaign
    books = client.books("company_id", "user_id", "campaign_id")

    # All operations use this context
    all_books = await books.list_all()
    book = await books.get("book_id")
```

Or using the factory function:

```python
from vclient import books_service

# Requires a default client to be configured
books = books_service("company_id", "user_id", "campaign_id")
all_books = await books.list_all()
```

## Available Methods

### Book CRUD

- `get(book_id)` - Retrieve a book by ID
- `create(name, description?)` - Create a new book
- `update(book_id, name?, description?)` - Update a book
- `delete(book_id)` - Delete a book
- `renumber(book_id, number)` - Change a book's position number
- `get_page(limit?, offset?)` - Get a paginated page of books
- `list_all()` - Get all books
- `iter_all(limit?)` - Iterate through all books

### Notes

- `get_notes_page(book_id, limit?, offset?)` - Get a paginated page of notes
- `list_all_notes(book_id)` - Get all notes
- `iter_all_notes(book_id, limit?)` - Iterate through all notes
- `get_note(book_id, note_id)` - Get a specific note
- `create_note(book_id, title, content)` - Create a note
- `update_note(book_id, note_id, title?, content?)` - Update a note
- `delete_note(book_id, note_id)` - Delete a note

### Assets

- `list_assets(book_id, limit?, offset?)` - List book assets
- `get_asset(book_id, asset_id)` - Get a specific asset
- `upload_asset(book_id, filename, content, content_type?)` - Upload an asset
- `delete_asset(book_id, asset_id)` - Delete an asset

## Method Details

### `get()`

Retrieve detailed information about a specific campaign book.

**Parameters:**

| Parameter | Type  | Description                    |
| --------- | ----- | ------------------------------ |
| `book_id` | `str` | The ID of the book to retrieve |

**Returns:** `CampaignBook`

**Example:**

```python
book = await books.get("book_id")
print(f"Book: {book.name}")
print(f"Number: {book.number}")
```

### `create()`

Create a new campaign book within the campaign.

**Parameters:**

| Parameter     | Type          | Description                        |
| ------------- | ------------- | ---------------------------------- |
| `name`        | `str`         | Book name (3-50 characters)        |
| `description` | `str \| None` | Optional description (min 3 chars) |

**Returns:** `CampaignBook`

**Example:**

```python
book = await books.create(
    name="The Dark Forest",
    description="A haunting chapter in the story",
)
print(f"Created: {book.id}")
```

### `update()`

Modify a campaign book's properties. Only include fields that need to be changed.

**Parameters:**

| Parameter     | Type          | Description                     |
| ------------- | ------------- | ------------------------------- |
| `book_id`     | `str`         | The ID of the book to update    |
| `name`        | `str \| None` | New book name (3-50 characters) |
| `description` | `str \| None` | New description (min 3 chars)   |

**Returns:** `CampaignBook`

### `delete()`

Remove a campaign book from the system. Associated notes and assets will no longer be accessible.

**Parameters:**

| Parameter | Type  | Description                  |
| --------- | ----- | ---------------------------- |
| `book_id` | `str` | The ID of the book to delete |

**Returns:** `None`

### `renumber()`

Change the book's position number within the campaign.

**Parameters:**

| Parameter | Type  | Description                    |
| --------- | ----- | ------------------------------ |
| `book_id` | `str` | The ID of the book             |
| `number`  | `int` | New book number (must be >= 1) |

**Returns:** `CampaignBook`

**Example:**

```python
book = await books.renumber("book_id", number=3)
print(f"Book now at position: {book.number}")
```

### `upload_asset()`

Upload a new asset for a book.

**Parameters:**

| Parameter      | Type    | Description                                                   |
| -------------- | ------- | ------------------------------------------------------------- |
| `book_id`      | `str`   | The ID of the book                                            |
| `filename`     | `str`   | The original filename of the asset                            |
| `content`      | `bytes` | The raw bytes of the file to upload                           |
| `content_type` | `str`   | The MIME type of the file (default: application/octet-stream) |

**Returns:** `S3Asset`

**Example:**

```python
with open("map.png", "rb") as f:
    content = f.read()

asset = await books.upload_asset(
    book_id="book_id",
    filename="map.png",
    content=content,
    content_type="image/png",
)
print(f"Uploaded: {asset.public_url}")
```

### `create_note()`

Create a new note for a book. Notes support markdown formatting.

**Parameters:**

| Parameter | Type  | Description                                       |
| --------- | ----- | ------------------------------------------------- |
| `book_id` | `str` | The ID of the book                                |
| `title`   | `str` | The note title (3-50 characters)                  |
| `content` | `str` | The note content (min 3 chars, supports markdown) |

**Returns:** `Note`

**Example:**

```python
note = await books.create_note(
    book_id="book_id",
    title="Chapter 1 Notes",
    content="## Summary\n\nThe story begins with...",
)
print(f"Created note: {note.title}")
```

## Response Models

### `CampaignBook`

Represents a campaign book entity returned from the API.

| Field           | Type          | Description                          |
| --------------- | ------------- | ------------------------------------ |
| `id`            | `str \| None` | MongoDB document ObjectID            |
| `date_created`  | `datetime`    | Timestamp when the book was created  |
| `date_modified` | `datetime`    | Timestamp when the book was modified |
| `name`          | `str`         | Book name (3-50 characters)          |
| `description`   | `str \| None` | Book description                     |
| `asset_ids`     | `list[str]`   | List of associated asset IDs         |
| `number`        | `int`         | Book number within the campaign      |
| `campaign_id`   | `str`         | ID of the parent campaign            |

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

Represents a note attached to a book.

| Field           | Type       | Description                      |
| --------------- | ---------- | -------------------------------- |
| `id`            | `str`      | MongoDB document ObjectID        |
| `date_created`  | `datetime` | Timestamp when created           |
| `date_modified` | `datetime` | Timestamp when modified          |
| `title`         | `str`      | Note title (3-50 characters)     |
| `content`       | `str`      | Note content (supports markdown) |

## Example Usage

```python
from vclient import VClient

async with VClient(base_url="...", api_key="...") as client:
    # Get campaign books service for a specific context
    books = client.books("company_id", "user_id", "campaign_id")

    # List all books
    all_books = await books.list_all()
    for b in all_books:
        print(f"Book {b.number}: {b.name}")

    # Create a new book
    new_book = await books.create(
        name="The Lost City",
        description="An adventure into ancient ruins",
    )
    print(f"Created: {new_book.id}")

    # Add a chapter note
    note = await books.create_note(
        book_id=new_book.id,
        title="Opening Scene",
        content="The expedition begins at dawn...",
    )

    # Upload a book illustration
    with open("ruins_map.png", "rb") as f:
        asset = await books.upload_asset(
            book_id=new_book.id,
            filename="ruins_map.png",
            content=f.read(),
            content_type="image/png",
        )

    # Renumber the book to position 1
    updated = await books.renumber(new_book.id, number=1)
    print(f"Moved to position: {updated.number}")

    # Update the book name
    updated = await books.update(new_book.id, name="The Lost City of Zara")
    print(f"Renamed to: {updated.name}")
```
