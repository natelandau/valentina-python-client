# Users Service

Manage users within a company, including their experience points, assets, notes, and quickrolls.

## Usage

```python
from vclient import users_service

users = users_service(company_id="COMPANY_ID")
```

## Methods

### CRUD Operations

| Method                                  | Returns | Description       |
| --------------------------------------- | ------- | ----------------- |
| `get(user_id)`                          | `User`  | Get a user by ID  |
| `create(UserCreate, **kwargs)`          | `User`  | Create a new user |
| `update(user_id, UserUpdate, **kwargs)` | `User`  | Update a user     |
| `delete(user_id, requesting_user_id)`   | `None`  | Delete a user     |

### Pagination

| Method                                  | Returns                   | Description               |
| --------------------------------------- | ------------------------- | ------------------------- |
| `get_page(user_role?, limit?, offset?)` | `PaginatedResponse[User]` | Get a page of users       |
| `list_all(user_role?)`                  | `list[User]`              | Get all users             |
| `iter_all(user_role?, limit?)`          | `AsyncIterator[User]`     | Iterate through all users |

### Statistics

| Method                                     | Returns          | Description              |
| ------------------------------------------ | ---------------- | ------------------------ |
| `get_statistics(user_id, num_top_traits?)` | `RollStatistics` | Get dice roll statistics |

### Experience Points

| Method                                          | Returns              | Description            |
| ----------------------------------------------- | -------------------- | ---------------------- |
| `get_experience(user_id, campaign_id)`          | `CampaignExperience` | Get XP and cool points |
| `add_xp(user_id, campaign_id, amount)`          | `CampaignExperience` | Award XP               |
| `remove_xp(user_id, campaign_id, amount)`       | `CampaignExperience` | Deduct XP              |
| `add_cool_points(user_id, campaign_id, amount)` | `CampaignExperience` | Award cool points      |

### Assets

| Method                                                    | Returns                      | Description      |
| --------------------------------------------------------- | ---------------------------- | ---------------- |
| `list_assets(user_id, limit?, offset?)`                   | `PaginatedResponse[S3Asset]` | List user assets |
| `get_asset(user_id, asset_id)`                            | `S3Asset`                    | Get an asset     |
| `upload_asset(user_id, filename, content, content_type?)` | `S3Asset`                    | Upload an asset  |
| `delete_asset(user_id, asset_id)`                         | `None`                       | Delete an asset  |

### Notes

| Method                                                | Returns                   | Description           |
| ----------------------------------------------------- | ------------------------- | --------------------- |
| `get_notes_page(user_id, limit?, offset?)`            | `PaginatedResponse[Note]` | Get a page of notes   |
| `list_all_notes(user_id)`                             | `list[Note]`              | Get all notes         |
| `iter_all_notes(user_id, limit?)`                     | `AsyncIterator[Note]`     | Iterate through notes |
| `get_note(user_id, note_id)`                          | `Note`                    | Get a note            |
| `create_note(user_id, NoteCreate, **kwargs)`          | `Note`                    | Create a note         |
| `update_note(user_id, note_id, NoteUpdate, **kwargs)` | `Note`                    | Update a note         |
| `delete_note(user_id, note_id)`                       | `None`                    | Delete a note         |

### Quickrolls

| Method | Returns | Description |
| --- | --- | --- |
| `get_quickrolls_page(user_id, limit?, offset?)` | `PaginatedResponse[Quickroll]` | Get a page of quickrolls |
| `list_all_quickrolls(user_id)` | `list[Quickroll]` | Get all quickrolls |
| `iter_all_quickrolls(user_id, limit?)` | `AsyncIterator[Quickroll]` | Iterate through quickrolls |
| `get_quickroll(user_id, quickroll_id)` | `Quickroll` | Get a quickroll |
| `create_quickroll(user_id, QuickrollCreate, **kwargs)` | `Quickroll` | Create a quickroll |
| `update_quickroll(user_id, quickroll_id, QuickrollUpdate, **kwargs)` | `Quickroll` | Update a quickroll |
| `delete_quickroll(user_id, quickroll_id)` | `None` | Delete a quickroll |

## User Roles

| Role          | Description           |
| ------------- | --------------------- |
| `ADMIN`       | Administrative access |
| `STORYTELLER` | Game master role      |
| `PLAYER`      | Regular player        |

## Example

```python
from vclient.models import UserCreate, NoteCreate, QuickrollCreate

# Create a user (preferred: use model object)
request = UserCreate(
    name="John Doe",
    email="john@example.com",
    role="PLAYER",
    requesting_user_id="admin_user_id"
)
user = await users.create(request)

# Alternative: pass fields as kwargs
user = await users.create(
    name="John Doe",
    email="john@example.com",
    role="PLAYER",
    requesting_user_id="admin_user_id"
)

# Award XP
experience = await users.add_xp(user.id, "campaign_id", amount=50)
print(f"Current XP: {experience.xp_current}")

# Create a quickroll
quickroll_request = QuickrollCreate(
    name="Strength + Brawl",
    trait_ids=["trait_strength_id", "trait_brawl_id"]
)
quickroll = await users.create_quickroll(user.id, quickroll_request)

# Create a note
note_request = NoteCreate(title="Session Notes", content="...")
note = await users.create_note(user.id, note_request)
```

See [Response Models](models.md) for `User`, `CampaignExperience`, `S3Asset`, `Note`, `Quickroll`, and related types.
