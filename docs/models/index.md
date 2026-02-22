---
icon: lucide/database
---

# Response Models

All API responses return as strongly-typed Pydantic models with automatic validation. Import models from `vclient.models` to access request and response types.

```python
from vclient.models import Company, User, Campaign, Character
```

!!! info "Type Safety"

    All models provide full type hints for IDE autocomplete and static type checking with mypy or pyright.

## Using Models

Models serve two primary purposes: creating requests and handling responses.

```python
from vclient import users_service
from vclient.models import UserCreate, User

# Create a request model
request = UserCreate(
    name="Alice Johnson",
    email="alice@example.com",
    role="PLAYER",
    requesting_user_id="admin_id"
)

# Send request and receive response model
users = users_service(company_id="company_123")
user: User = await users.create(request)

# Access response data with full type hints
print(f"Created user: {user.name} (ID: {user.id})")
print(f"Role: {user.role}")
```

## Common Models

These models appear across multiple services and provide shared functionality.

### Asset

Represents a file stored in cloud storage. Use this model to manage uploaded files like character portraits, campaign handouts, and other assets.

| Field               | Type        | Description                   |
| ------------------- | ----------- | ----------------------------- |
| `id`                | `str`       | Unique identifier             |
| `date_created`      | `datetime`  | Creation timestamp            |
| `date_modified`     | `datetime`  | Last modified timestamp       |
| `file_type`         | `AssetType` | File type (image, text, etc.) |
| `original_filename` | `str`       | Original filename             |
| `public_url`        | `str`       | Public URL to access the file |
| `uploaded_by`       | `str`       | ID of uploader                |

### Note

Represents a markdown-formatted note. Store session notes, character backstories, and campaign information with full markdown support.

| Field           | Type       | Description             |
| --------------- | ---------- | ----------------------- |
| `id`            | `str`      | Unique identifier       |
| `date_created`  | `datetime` | Creation timestamp      |
| `date_modified` | `datetime` | Last modified timestamp |
| `title`         | `str`      | Note title              |
| `content`       | `str`      | Note content (markdown) |

### RollStatistics

Aggregated dice roll statistics for a user. Track success rates, critical rolls, botches, and identify patterns in player performance.

| Field                  | Type    | Description              |
| ---------------------- | ------- | ------------------------ |
| `botches`              | `int`   | Total botched rolls      |
| `successes`            | `int`   | Total successful rolls   |
| `failures`             | `int`   | Total failed rolls       |
| `criticals`            | `int`   | Total critical successes |
| `total_rolls`          | `int`   | Total number of rolls    |
| `success_percentage`   | `float` | Success rate             |
| `failure_percentage`   | `float` | Failure rate             |
| `botch_percentage`     | `float` | Botch rate               |
| `criticals_percentage` | `float` | Critical rate            |

### Quickroll

Pre-configured dice pool for frequently used trait combinations. Speed up gameplay by saving common rolls like "Strength + Brawl" or "Wits + Investigation".

| Field           | Type          | Description                |
| --------------- | ------------- | -------------------------- |
| `id`            | `str`         | Unique identifier          |
| `date_created`  | `datetime`    | Creation timestamp         |
| `date_modified` | `datetime`    | Last modified timestamp    |
| `name`          | `str`         | Quickroll name             |
| `description`   | `str \| None` | Optional description       |
| `user_id`       | `str`         | Owner user ID              |
| `trait_ids`     | `list[str]`   | Trait IDs in the dice pool |

## Enumerations

### Character Enums

| Enum              | Values                                         |
| ----------------- | ---------------------------------------------- |
| `CharacterClass`  | VAMPIRE, WEREWOLF, MAGE, HUNTER, GHOUL, MORTAL |
| `CharacterType`   | PLAYER, NPC, STORYTELLER, DEVELOPER            |
| `CharacterStatus` | ALIVE, DEAD                                    |
| `GameVersion`     | V4, V5                                         |

### User Enums

| Enum              | Values                     |
| ----------------- | -------------------------- |
| `UserRole`        | ADMIN, STORYTELLER, PLAYER |
| `PermissionLevel` | USER, ADMIN, OWNER, REVOKE |

### Other Enums

| Enum             | Values                            |
| ---------------- | --------------------------------- |
| `WerewolfRenown` | HONOR, GLORY, WISDOM              |
| `HunterEdgeType` | ASSETS, APTITUDES, ENDOWMENTS     |
| `DiceSize`       | 4, 6, 8, 10, 20, 100             |
| `RollResultType` | SUCCESS, FAILURE, BOTCH, CRITICAL |
