# Campaigns Service

The Campaigns Service provides methods to create, retrieve, update, and delete campaigns within a company, as well as access campaign statistics, assets, and notes.

## Usage

The campaigns service is scoped to a specific company and user context at creation time:

```python
from vclient import VClient

async with VClient(base_url="...", api_key="...") as client:
    # Get a campaigns service scoped to a company and user
    campaigns = client.campaigns("company_id", "user_id")

    # All operations use this context
    all_campaigns = await campaigns.list_all()
    campaign = await campaigns.get("campaign_id")
```

Or using the factory function:

```python
from vclient import campaigns_service

# Requires a default client to be configured
campaigns = campaigns_service("company_id", "user_id")
all_campaigns = await campaigns.list_all()
```

## Available Methods

### Campaign CRUD

- `get(campaign_id)` - Retrieve a campaign by ID
- `create(name, description?, asset_ids?, desperation?, danger?)` - Create a new campaign
- `update(campaign_id, name?, description?, asset_ids?, desperation?, danger?)` - Update a campaign
- `delete(campaign_id)` - Delete a campaign
- `get_page(limit?, offset?)` - Get a paginated page of campaigns
- `list_all()` - Get all campaigns
- `iter_all(limit?)` - Iterate through all campaigns

### Statistics

- `get_statistics(campaign_id, num_top_traits?)` - Get roll statistics for a campaign

### Assets

- `list_assets(campaign_id, limit?, offset?)` - List campaign assets
- `get_asset(campaign_id, asset_id)` - Get a specific asset
- `upload_asset(campaign_id, filename, content, content_type?)` - Upload an asset
- `delete_asset(campaign_id, asset_id)` - Delete an asset

### Notes

- `get_notes_page(campaign_id, limit?, offset?)` - Get a paginated page of notes
- `list_all_notes(campaign_id)` - Get all notes
- `iter_all_notes(campaign_id, limit?)` - Iterate through all notes
- `get_note(campaign_id, note_id)` - Get a specific note
- `create_note(campaign_id, title, content)` - Create a note
- `update_note(campaign_id, note_id, title?, content?)` - Update a note
- `delete_note(campaign_id, note_id)` - Delete a note

## Method Details

### `get()`

Retrieve detailed information about a specific campaign.

**Parameters:**

| Parameter     | Type  | Description                        |
| ------------- | ----- | ---------------------------------- |
| `campaign_id` | `str` | The ID of the campaign to retrieve |

**Returns:** `Campaign`

**Example:**

```python
campaign = await campaigns.get("campaign_id")
print(f"Campaign: {campaign.name}")
print(f"Danger Level: {campaign.danger}")
```

### `create()`

Create a new campaign within the company.

**Parameters:**

| Parameter     | Type               | Description                                |
| ------------- | ------------------ | ------------------------------------------ |
| `name`        | `str`              | Campaign name (3-50 characters)            |
| `description` | `str \| None`      | Optional description (min 3 chars)         |
| `asset_ids`   | `list[str] \| None`| Optional list of asset IDs to associate    |
| `desperation` | `int`              | Desperation level (0-5, default 0)         |
| `danger`      | `int`              | Danger level (0-5, default 0)              |

**Returns:** `Campaign`

**Example:**

```python
campaign = await campaigns.create(
    name="Dark Chronicles",
    description="A gothic horror campaign",
    desperation=2,
    danger=3,
)
print(f"Created: {campaign.id}")
```

### `update()`

Modify a campaign's properties. Only include fields that need to be changed.

**Parameters:**

| Parameter     | Type               | Description                           |
| ------------- | ------------------ | ------------------------------------- |
| `campaign_id` | `str`              | The ID of the campaign to update      |
| `name`        | `str \| None`      | New campaign name (3-50 characters)   |
| `description` | `str \| None`      | New description (min 3 chars)         |
| `asset_ids`   | `list[str] \| None`| New list of asset IDs                 |
| `desperation` | `int \| None`      | New desperation level (0-5)           |
| `danger`      | `int \| None`      | New danger level (0-5)                |

**Returns:** `Campaign`

### `delete()`

Remove a campaign from the system. Associated characters, books, and other content will no longer be accessible.

**Parameters:**

| Parameter     | Type  | Description                      |
| ------------- | ----- | -------------------------------- |
| `campaign_id` | `str` | The ID of the campaign to delete |

**Returns:** `None`

### `get_statistics()`

Retrieve aggregated dice roll statistics for a specific campaign.

**Parameters:**

| Parameter        | Type  | Description                                 |
| ---------------- | ----- | ------------------------------------------- |
| `campaign_id`    | `str` | The ID of the campaign                      |
| `num_top_traits` | `int` | Number of top traits to include (default 5) |

**Returns:** `RollStatistics`

**Example:**

```python
stats = await campaigns.get_statistics("campaign_id", num_top_traits=10)
print(f"Success rate: {stats.success_percentage}%")
print(f"Total rolls: {stats.total_rolls}")
```

### `upload_asset()`

Upload a new asset for a campaign.

**Parameters:**

| Parameter      | Type    | Description                                                   |
| -------------- | ------- | ------------------------------------------------------------- |
| `campaign_id`  | `str`   | The ID of the campaign                                        |
| `filename`     | `str`   | The original filename of the asset                            |
| `content`      | `bytes` | The raw bytes of the file to upload                           |
| `content_type` | `str`   | The MIME type of the file (default: application/octet-stream) |

**Returns:** `S3Asset`

**Example:**

```python
with open("map.png", "rb") as f:
    content = f.read()

asset = await campaigns.upload_asset(
    campaign_id="campaign_id",
    filename="map.png",
    content=content,
    content_type="image/png",
)
print(f"Uploaded: {asset.public_url}")
```

### `create_note()`

Create a new note for a campaign. Notes support markdown formatting.

**Parameters:**

| Parameter     | Type  | Description                                       |
| ------------- | ----- | ------------------------------------------------- |
| `campaign_id` | `str` | The ID of the campaign                            |
| `title`       | `str` | The note title (3-50 characters)                  |
| `content`     | `str` | The note content (min 3 chars, supports markdown) |

**Returns:** `Note`

**Example:**

```python
note = await campaigns.create_note(
    campaign_id="campaign_id",
    title="Session 1 Recap",
    content="## Summary\n\nThe party ventured into...",
)
print(f"Created note: {note.title}")
```

## Response Models

### `Campaign`

Represents a campaign entity returned from the API.

| Field           | Type           | Description                         |
| --------------- | -------------- | ----------------------------------- |
| `id`            | `str`          | MongoDB document ObjectID           |
| `date_created`  | `datetime`     | Timestamp when the campaign was created |
| `date_modified` | `datetime`     | Timestamp when the campaign was modified |
| `name`          | `str`          | Campaign name (3-50 characters)     |
| `description`   | `str \| None`  | Campaign description                |
| `asset_ids`     | `list[str]`    | List of associated asset IDs        |
| `desperation`   | `int`          | Desperation level (0-5)             |
| `danger`        | `int`          | Danger level (0-5)                  |
| `company_id`    | `str`          | ID of the company                   |

### `RollStatistics`

Aggregated dice roll statistics.

| Field                  | Type                   | Description                    |
| ---------------------- | ---------------------- | ------------------------------ |
| `botches`              | `int`                  | Total botched rolls            |
| `successes`            | `int`                  | Total successful rolls         |
| `failures`             | `int`                  | Total failed rolls             |
| `criticals`            | `int`                  | Total critical successes       |
| `total_rolls`          | `int`                  | Total number of rolls          |
| `average_difficulty`   | `float \| None`        | Average difficulty of rolls    |
| `average_pool`         | `float \| None`        | Average dice pool size         |
| `top_traits`           | `list[dict[str, Any]]` | Most frequently used traits    |
| `criticals_percentage` | `float`                | Percentage of critical rolls   |
| `success_percentage`   | `float`                | Percentage of successful rolls |
| `failure_percentage`   | `float`                | Percentage of failed rolls     |
| `botch_percentage`     | `float`                | Percentage of botched rolls    |

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

Represents a note attached to a campaign.

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
    # Get campaigns service for a specific company and user
    campaigns = client.campaigns("company_id", "user_id")

    # List all campaigns
    all_campaigns = await campaigns.list_all()
    for c in all_campaigns:
        print(f"Campaign: {c.name} (Danger: {c.danger})")

    # Create a new campaign
    new_campaign = await campaigns.create(
        name="Blood Moon Rising",
        description="A werewolf-themed horror campaign",
        danger=4,
    )
    print(f"Created: {new_campaign.id}")

    # Get campaign statistics
    stats = await campaigns.get_statistics(new_campaign.id)
    print(f"Total rolls: {stats.total_rolls}")

    # Add a session note
    note = await campaigns.create_note(
        campaign_id=new_campaign.id,
        title="Session 1",
        content="The pack gathered under the full moon...",
    )

    # Upload a campaign map
    with open("forest_map.png", "rb") as f:
        asset = await campaigns.upload_asset(
            campaign_id=new_campaign.id,
            filename="forest_map.png",
            content=f.read(),
            content_type="image/png",
        )

    # Update danger level after a story event
    updated = await campaigns.update(new_campaign.id, danger=5)
    print(f"Updated danger to: {updated.danger}")
```
