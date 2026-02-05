# Campaigns Service

Manage campaigns within a company, including their statistics, assets, and notes.

## Usage

```python
from vclient import campaigns_service

campaigns = campaigns_service(user_id="USER_ID", company_id="COMPANY_ID")
```

## Methods

### CRUD Operations

| Method                                          | Returns    | Description           |
| ----------------------------------------------- | ---------- | --------------------- |
| `get(campaign_id)`                              | `Campaign` | Get a campaign by ID  |
| `create(CampaignCreate, **kwargs)`              | `Campaign` | Create a new campaign |
| `update(campaign_id, CampaignUpdate, **kwargs)` | `Campaign` | Update a campaign     |
| `delete(campaign_id)`                           | `None`     | Delete a campaign     |

### Pagination

| Method                      | Returns                       | Description                   |
| --------------------------- | ----------------------------- | ----------------------------- |
| `get_page(limit?, offset?)` | `PaginatedResponse[Campaign]` | Get a page of campaigns       |
| `list_all()`                | `list[Campaign]`              | Get all campaigns             |
| `iter_all(limit?)`          | `AsyncIterator[Campaign]`     | Iterate through all campaigns |

### Statistics

| Method                                         | Returns          | Description              |
| ---------------------------------------------- | ---------------- | ------------------------ |
| `get_statistics(campaign_id, num_top_traits?)` | `RollStatistics` | Get dice roll statistics |

### Assets

| Method                                                        | Returns                      | Description          |
| ------------------------------------------------------------- | ---------------------------- | -------------------- |
| `list_assets(campaign_id, limit?, offset?)`                   | `PaginatedResponse[S3Asset]` | List campaign assets |
| `get_asset(campaign_id, asset_id)`                            | `S3Asset`                    | Get an asset         |
| `upload_asset(campaign_id, filename, content, content_type?)` | `S3Asset`                    | Upload an asset      |
| `delete_asset(campaign_id, asset_id)`                         | `None`                       | Delete an asset      |

### Notes

| Method                                                    | Returns                   | Description           |
| --------------------------------------------------------- | ------------------------- | --------------------- |
| `get_notes_page(campaign_id, limit?, offset?)`            | `PaginatedResponse[Note]` | Get a page of notes   |
| `list_all_notes(campaign_id)`                             | `list[Note]`              | Get all notes         |
| `iter_all_notes(campaign_id, limit?)`                     | `AsyncIterator[Note]`     | Iterate through notes |
| `get_note(campaign_id, note_id)`                          | `Note`                    | Get a note            |
| `create_note(campaign_id, NoteCreate, **kwargs)`          | `Note`                    | Create a note         |
| `update_note(campaign_id, note_id, NoteUpdate, **kwargs)` | `Note`                    | Update a note         |
| `delete_note(campaign_id, note_id)`                       | `None`                    | Delete a note         |

## Example

```python
from vclient.models import CampaignCreate, CampaignUpdate, NoteCreate

# Create a campaign (preferred: use model object)
request = CampaignCreate(
    name="Dark Metropolis",
    description="A noir vampire chronicle",
    desperation=2,
    danger=3
)
campaign = await campaigns.create(request)

# Alternative: pass fields as kwargs
campaign = await campaigns.create(
    name="Dark Metropolis",
    description="A noir vampire chronicle"
)

# Update a campaign
update = CampaignUpdate(danger=4)
updated = await campaigns.update(campaign.id, update)

# Get statistics
stats = await campaigns.get_statistics(campaign.id)
print(f"Total rolls: {stats.total_rolls}")

# Create a note
note_request = NoteCreate(title="Session 1", content="...")
note = await campaigns.create_note(campaign.id, note_request)
```

See [Response Models](models.md) for `Campaign`, `RollStatistics`, `S3Asset`, `Note`, and related types.
