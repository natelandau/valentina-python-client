---
icon: lucide/map
---

# Campaigns Service

Manage campaigns within a company, including their statistics, assets, and notes.

The Campaigns service provides full CRUD operations for campaigns, plus specialized methods for managing campaign assets, notes, and viewing dice roll statistics.

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

| Method                                         | Returns                    | Description          |
| ---------------------------------------------- | -------------------------- | -------------------- |
| `get_assets_page(campaign_id, limit?, offset?)`  | `PaginatedResponse[Asset]` | Get a page of assets   |
| `list_all_assets(campaign_id)`                    | `list[Asset]`              | Get all assets         |
| `iter_all_assets(campaign_id, limit?)`            | `AsyncIterator[Asset]`     | Iterate through assets |
| `get_asset(campaign_id, asset_id)`                | `Asset`                    | Get an asset           |
| `upload_asset(campaign_id, filename, content)`    | `Asset`                    | Upload an asset        |
| `delete_asset(campaign_id, asset_id)`             | `None`                     | Delete an asset        |

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

## Examples

### Create and Manage Campaigns

```python
from vclient.models import CampaignCreate, CampaignUpdate

# Create a campaign (preferred: use model object)
request = CampaignCreate(
    name="Dark Metropolis",
    description="A noir vampire chronicle",
    desperation=2,
    danger=3
)
campaign = await campaigns.create(request)
print(f"Created campaign: {campaign.name}")

# Alternative: pass fields as kwargs
campaign = await campaigns.create(
    name="Dark Metropolis",
    description="A noir vampire chronicle"
)

# Update a campaign
update = CampaignUpdate(danger=4)
updated = await campaigns.update(campaign.id, update)
```

### View Statistics

```python
# Get dice roll statistics for a campaign
stats = await campaigns.get_statistics(campaign.id, num_top_traits=10)
print(f"Total rolls: {stats.total_rolls}")
print(f"Success rate: {stats.success_percentage}%")
for trait in stats.top_traits:
    print(f"  {trait.name}: {trait.count} uses")
```

### Manage Campaign Notes

```python
from vclient.models import NoteCreate, NoteUpdate

# Create a note
note_request = NoteCreate(title="Session 1", content="The story begins...")
note = await campaigns.create_note(campaign.id, note_request)

# List all notes
all_notes = await campaigns.list_all_notes(campaign.id)

# Update a note
update = NoteUpdate(content="Updated content")
await campaigns.update_note(campaign.id, note.id, update)

# Delete a note
await campaigns.delete_note(campaign.id, note.id)
```

### Manage Campaign Assets

```python
# Upload an image
with open("map.png", "rb") as f:
    asset = await campaigns.upload_asset(
        campaign.id,
        filename="campaign_map.png",
        content=f.read(),
    )
print(f"Uploaded: {asset.public_url}")

# List all assets
all_assets = await campaigns.list_all_assets(campaign.id)

# Or iterate for memory efficiency
async for asset in campaigns.iter_all_assets(campaign.id):
    print(asset.original_filename)

# Delete an asset
await campaigns.delete_asset(campaign.id, asset.id)
```

See [Response Models](../models/campaigns.md) for `Campaign`, `RollStatistics`, `Asset`, `Note`, and related types.
