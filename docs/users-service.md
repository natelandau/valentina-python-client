# Users Service

The Users Service provides methods to create, retrieve, update, and delete users within a company, as well as access user statistics and assets.

## Usage

```python
from vclient import users_service

users = users_service()
```

## Available Methods

This service supports all [common CRUD and pagination methods](../README.md#common-service-methods):

- `get(company_id, user_id)` - Retrieve a user by ID
- `create(company_id, name, email, role, requesting_user_id, discord_profile?)` - Create a new user
- `update(company_id, user_id, requesting_user_id, name?, email?, role?, discord_profile?)` - Update a user
- `delete(company_id, user_id, requesting_user_id)` - Delete a user
- `get_page(company_id, user_role?, limit?, offset?)` - Get a paginated page of users
- `list_all(company_id, user_role?)` - Get all users
- `iter_all(company_id, user_role?, limit?)` - Iterate through all users

## Service-Specific Methods

### `get_statistics()`

Retrieve aggregated dice roll statistics for a specific user.

**Parameters:**

| Parameter        | Type  | Description                                 |
| ---------------- | ----- | ------------------------------------------- |
| `company_id`     | `str` | The ID of the company containing the user   |
| `user_id`        | `str` | The ID of the user to get statistics for    |
| `num_top_traits` | `int` | Number of top traits to include (default 5) |

**Returns:** `RollStatistics`

**Example:**

```python
stats = await users.get_statistics("company_id", "user_id", num_top_traits=10)
print(f"Success rate: {stats.success_percentage}%")
print(f"Total rolls: {stats.total_rolls}")
```

### `list_assets()`

Retrieve a paginated list of assets for a user.

**Parameters:**

| Parameter    | Type  | Description                               |
| ------------ | ----- | ----------------------------------------- |
| `company_id` | `str` | The ID of the company containing the user |
| `user_id`    | `str` | The ID of the user whose assets to list   |
| `limit`      | `int` | Maximum items to return (default 10)      |
| `offset`     | `int` | Number of items to skip (default 0)       |

**Returns:** `PaginatedResponse[S3Asset]`

### `get_asset()`

Retrieve details of a specific asset including its URL and metadata.

**Parameters:**

| Parameter    | Type  | Description                     |
| ------------ | ----- | ------------------------------- |
| `company_id` | `str` | The ID of the company           |
| `user_id`    | `str` | The ID of the user who owns it  |
| `asset_id`   | `str` | The ID of the asset to retrieve |

**Returns:** `S3Asset`

### `delete_asset()`

Delete an asset from a user. This action cannot be undone.

**Parameters:**

| Parameter    | Type  | Description                    |
| ------------ | ----- | ------------------------------ |
| `company_id` | `str` | The ID of the company          |
| `user_id`    | `str` | The ID of the user who owns it |
| `asset_id`   | `str` | The ID of the asset to delete  |

**Returns:** `None`

### `get_experience()`

Retrieve a user's experience points and cool points for a specific campaign. Creates the experience record automatically if it doesn't exist.

**Parameters:**

| Parameter     | Type  | Description                               |
| ------------- | ----- | ----------------------------------------- |
| `company_id`  | `str` | The ID of the company containing the user |
| `user_id`     | `str` | The ID of the user                        |
| `campaign_id` | `str` | The ID of the campaign                    |

**Returns:** `CampaignExperience`

**Example:**

```python
experience = await client.users.get_experience("company_id", "user_id", "campaign_id")
print(f"Current XP: {experience.xp_current}")
print(f"Total XP: {experience.xp_total}")
print(f"Cool Points: {experience.cool_points}")
```

### `add_xp()`

Award experience points to a user for a specific campaign. The XP is added to both the current XP pool (available for spending) and the total XP tracker (lifetime earned).

**Parameters:**

| Parameter     | Type  | Description                               |
| ------------- | ----- | ----------------------------------------- |
| `company_id`  | `str` | The ID of the company containing the user |
| `user_id`     | `str` | The ID of the user to award XP to         |
| `campaign_id` | `str` | The ID of the campaign                    |
| `amount`      | `int` | The amount of XP to add                   |

**Returns:** `CampaignExperience`

**Example:**

```python
experience = await client.users.add_xp("company_id", "user_id", "campaign_id", amount=50)
print(f"New current XP: {experience.xp_current}")
```

### `remove_xp()`

Deduct experience points from a user's current XP pool. Returns an error if the user has insufficient XP.

**Parameters:**

| Parameter     | Type  | Description                               |
| ------------- | ----- | ----------------------------------------- |
| `company_id`  | `str` | The ID of the company containing the user |
| `user_id`     | `str` | The ID of the user to remove XP from      |
| `campaign_id` | `str` | The ID of the campaign                    |
| `amount`      | `int` | The amount of XP to remove                |

**Returns:** `CampaignExperience`

**Example:**

```python
experience = await client.users.remove_xp("company_id", "user_id", "campaign_id", amount=25)
print(f"Remaining XP: {experience.xp_current}")
```

### `add_cool_points()`

Award cool points to a user for a specific campaign. Cool points are converted to XP automatically based on the company's configured exchange rate.

**Parameters:**

| Parameter     | Type  | Description                               |
| ------------- | ----- | ----------------------------------------- |
| `company_id`  | `str` | The ID of the company containing the user |
| `user_id`     | `str` | The ID of the user to award cool points   |
| `campaign_id` | `str` | The ID of the campaign                    |
| `amount`      | `int` | The amount of cool points to add          |

**Returns:** `CampaignExperience`

**Example:**

```python
experience = await client.users.add_cool_points("company_id", "user_id", "campaign_id", amount=3)
print(f"Total cool points: {experience.cool_points}")
```

## Response Models

### `User`

Represents a user entity returned from the API.

| Field                 | Type                       | Description                              |
| --------------------- | -------------------------- | ---------------------------------------- |
| `id`                  | `str`                      | MongoDB document ObjectID                |
| `date_created`        | `datetime`                 | Timestamp when the user was created      |
| `date_modified`       | `datetime`                 | Timestamp when the user was modified     |
| `name`                | `str`                      | User's display name                      |
| `email`               | `str`                      | User's email address                     |
| `role`                | `UserRole \| None`         | User's role (ADMIN, STORYTELLER, PLAYER) |
| `company_id`          | `str`                      | ID of the company the user belongs to    |
| `discord_profile`     | `DiscordProfile \| None`   | Discord profile information              |
| `campaign_experience` | `list[CampaignExperience]` | Experience points per campaign           |
| `asset_ids`           | `list[str]`                | List of asset IDs owned by the user      |

### `DiscordProfile`

Discord account information for integration with Discord bots.

| Field           | Type           | Description                       |
| --------------- | -------------- | --------------------------------- |
| `id`            | `str \| None`  | Discord user ID                   |
| `username`      | `str \| None`  | Discord username                  |
| `global_name`   | `str \| None`  | Discord global display name       |
| `avatar_id`     | `str \| None`  | Discord avatar ID                 |
| `avatar_url`    | `str \| None`  | Full URL to avatar image          |
| `discriminator` | `str \| None`  | Discord discriminator             |
| `email`         | `str \| None`  | Discord email                     |
| `verified`      | `bool \| None` | Whether Discord email is verified |

### `CampaignExperience`

Experience points and cool points for a specific campaign.

| Field         | Type  | Description                           |
| ------------- | ----- | ------------------------------------- |
| `campaign_id` | `str` | The campaign ID                       |
| `xp_current`  | `int` | XP available for spending (default 0) |
| `xp_total`    | `int` | Total lifetime XP earned (default 0)  |
| `cool_points` | `int` | Cool points earned (default 0)        |

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

## User Roles

| Role          | Description                              |
| ------------- | ---------------------------------------- |
| `ADMIN`       | Administrative access within the company |
| `STORYTELLER` | Game master / storyteller role           |
| `PLAYER`      | Regular player role                      |

## Example Usage

```python
from vclient import VClient

async with VClient(base_url="...", api_key="...") as client:
    # List all users in a company
    users = await client.users.list_all("company_id")

    # Create a new user
    new_user = await client.users.create(
        company_id="company_id",
        name="John Doe",
        email="john@example.com",
        role="PLAYER",
        requesting_user_id="admin_user_id",
    )

    # Get user statistics
    stats = await client.users.get_statistics("company_id", new_user.id)
    print(f"Total rolls: {stats.total_rolls}")

    # List user assets
    assets = await client.users.list_assets("company_id", new_user.id)
    for asset in assets.items:
        print(f"Asset: {asset.original_filename}")
```
