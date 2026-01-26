# Characters Service

The Characters Service provides methods to create, retrieve, update, and delete characters within a campaign.

## Usage

The characters service is scoped to a specific company, user, and campaign context at creation time:

```python
from vclient import VClient

async with VClient(base_url="...", api_key="...") as client:
    # Get a characters service scoped to a company, user, and campaign
    characters = client.characters("company_id", "user_id", "campaign_id")

    # All operations use this context
    all_characters = await characters.list_all()
    character = await characters.get("character_id")
```

Or using the factory function:

```python
from vclient import characters_service

characters = characters_service("company_id", "user_id", "campaign_id")
all_characters = await characters.list_all()
```

## Available Methods

### Character CRUD

- `get(character_id)` - Retrieve a character by ID
- `create(character_class, game_version, name_first, name_last, ...)` - Create a new character
- `update(character_id, ...)` - Update a character
- `delete(character_id)` - Delete a character
- `get_page(limit?, offset?, user_player_id?, user_creator_id?, character_class?, character_type?, status?)` - Get a paginated page of characters with optional filters
- `list_all(...)` - Get all characters (supports same filters as get_page)
- `iter_all(limit?, ...)` - Iterate through all characters

### Statistics

- `get_statistics(character_id, num_top_traits?)` - Get roll statistics for a character

### Assets

- `list_assets(character_id, limit?, offset?)` - List character assets
- `get_asset(character_id, asset_id)` - Get a specific asset
- `upload_asset(character_id, filename, content, content_type?)` - Upload an asset
- `delete_asset(character_id, asset_id)` - Delete an asset

### Notes

- `get_notes_page(character_id, limit?, offset?)` - Get a paginated page of notes
- `list_all_notes(character_id)` - Get all notes
- `iter_all_notes(character_id, limit?)` - Iterate through all notes
- `get_note(character_id, note_id)` - Get a specific note
- `create_note(character_id, title, content)` - Create a note
- `update_note(character_id, note_id, title?, content?)` - Update a note
- `delete_note(character_id, note_id)` - Delete a note

### Inventory

- `get_inventory_page(character_id, limit?, offset?)` - Get a paginated page of inventory items
- `list_all_inventory(character_id)` - Get all inventory items
- `iter_all_inventory(character_id, limit?)` - Iterate through all inventory items
- `get_inventory_item(character_id, item_id)` - Get a specific inventory item
- `create_inventory_item(character_id, name, type, description)` - Create an inventory item
- `update_inventory_item(character_id, item_id, name?, type?, description?)` - Update an inventory item
- `delete_inventory_item(character_id, item_id)` - Delete an inventory item

### Werewolf Gifts

- `get_gifts_page(character_id, limit?, offset?)` - Get a paginated page of werewolf gifts
- `list_all_gifts(character_id)` - Get all werewolf gifts
- `iter_all_gifts(character_id, limit?)` - Iterate through all werewolf gifts
- `get_gift(character_id, werewolf_gift_id)` - Get a specific werewolf gift
- `add_gift(character_id, werewolf_gift_id)` - Add a werewolf gift to a character
- `remove_gift(character_id, werewolf_gift_id)` - Remove a werewolf gift from a character

### Werewolf Rites

- `get_rites_page(character_id, limit?, offset?)` - Get a paginated page of werewolf rites
- `list_all_rites(character_id)` - Get all werewolf rites
- `iter_all_rites(character_id, limit?)` - Iterate through all werewolf rites
- `get_rite(character_id, werewolf_rite_id)` - Get a specific werewolf rite
- `add_rite(character_id, werewolf_rite_id)` - Add a werewolf rite to a character
- `remove_rite(character_id, werewolf_rite_id)` - Remove a werewolf rite from a character

## Response Models

### `Character`

Represents a character entity returned from the API.

| Field                 | Type                         | Description                              |
| --------------------- | ---------------------------- | ---------------------------------------- |
| `id`                  | `str \| None`                | MongoDB document ObjectID                |
| `date_created`        | `datetime \| None`           | Timestamp when created                   |
| `date_modified`       | `datetime \| None`           | Timestamp when last modified             |
| `date_killed`         | `datetime \| None`           | Timestamp when killed (if dead)          |
| `character_class`     | `CharacterClass`             | Character class                          |
| `type`                | `CharacterType`              | Character type (PLAYER, NPC, etc.)       |
| `game_version`        | `GameVersion`                | Game version (V4 or V5)                  |
| `status`              | `CharacterStatus`            | Character status (ALIVE or DEAD)         |
| `starting_points`     | `int`                        | Starting experience points               |
| `name_first`          | `str`                        | Character's first name                   |
| `name_last`           | `str`                        | Character's last name                    |
| `name_nick`           | `str \| None`                | Character's nickname                     |
| `name`                | `str`                        | Character's display name                 |
| `name_full`           | `str`                        | Character's full name                    |
| `age`                 | `int \| None`                | Character's age                          |
| `biography`           | `str \| None`                | Character biography                      |
| `demeanor`            | `str \| None`                | Character's demeanor                     |
| `nature`              | `str \| None`                | Character's nature                       |
| `concept_id`          | `str \| None`                | ID of the character concept              |
| `user_creator_id`     | `str`                        | ID of the user who created the character |
| `user_player_id`      | `str`                        | ID of the user who plays the character   |
| `company_id`          | `str`                        | ID of the company                        |
| `campaign_id`         | `str`                        | ID of the campaign                       |
| `asset_ids`           | `list[str]`                  | List of associated asset IDs             |
| `character_trait_ids` | `list[str]`                  | List of character trait IDs              |
| `specialties`         | `list[CharacterSpecialty]`   | List of character specialties            |
| `vampire_attributes`  | `VampireAttributes \| None`  | Vampire-specific attributes              |
| `werewolf_attributes` | `WerewolfAttributes \| None` | Werewolf-specific attributes             |
| `mage_attributes`     | `MageAttributes \| None`     | Mage-specific attributes                 |
| `hunter_attributes`   | `HunterAttributes \| None`   | Hunter-specific attributes               |

### Type Aliases

| Type              | Values                                         | Description                   |
| ----------------- | ---------------------------------------------- | ----------------------------- |
| `CharacterClass`  | VAMPIRE, WEREWOLF, MAGE, HUNTER, GHOUL, MORTAL | Character's supernatural type |
| `CharacterType`   | PLAYER, NPC, STORYTELLER, DEVELOPER            | Character ownership type      |
| `CharacterStatus` | ALIVE, DEAD                                    | Character's living status     |
| `GameVersion`     | V4, V5                                         | Game ruleset version          |

### `VampireAttributes`

Vampire-specific character attributes.

| Field        | Type           | Description                |
| ------------ | -------------- | -------------------------- |
| `clan_id`    | `str \| None`  | ID of the vampire clan     |
| `clan_name`  | `str \| None`  | Name of the vampire clan   |
| `generation` | `int \| None`  | Vampire generation         |
| `sire`       | `str \| None`  | Name of the vampire's sire |
| `bane`       | `dict \| None` | Clan bane details          |
| `compulsion` | `dict \| None` | Clan compulsion details    |

### `WerewolfAttributes`

Werewolf-specific character attributes.

| Field          | Type          | Description                  |
| -------------- | ------------- | ---------------------------- |
| `tribe_id`     | `str \| None` | ID of the werewolf tribe     |
| `tribe_name`   | `str \| None` | Name of the werewolf tribe   |
| `auspice_id`   | `str \| None` | ID of the werewolf auspice   |
| `auspice_name` | `str \| None` | Name of the werewolf auspice |
| `pack_name`    | `str \| None` | Name of the werewolf's pack  |

### `HunterAttributes`

Hunter-specific character attributes.

| Field   | Type               | Description          |
| ------- | ------------------ | -------------------- |
| `creed` | `str \| None`      | Hunter creed         |
| `edges` | `list[HunterEdge]` | List of hunter edges |

### `MageAttributes`

Mage-specific character attributes.

| Field    | Type          | Description             |
| -------- | ------------- | ----------------------- |
| `sphere` | `str \| None` | Primary sphere of magic |

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

### `WerewolfGift`

Represents a werewolf gift ability.

| Field             | Type           | Description                              |
| ----------------- | -------------- | ---------------------------------------- |
| `id`              | `str`          | MongoDB document ObjectID                |
| `name`            | `str`          | Gift name                                |
| `description`     | `str \| None`  | Gift description                         |
| `game_version`    | `GameVersion`  | Game version (V4 or V5)                  |
| `date_created`    | `datetime`     | Timestamp when created                   |
| `date_modified`   | `datetime`     | Timestamp when last modified             |
| `renown`          | `WerewolfRenown` | Renown type (HONOR, GLORY, or WISDOM)  |
| `cost`            | `str \| None`  | Cost to activate the gift                |
| `duration`        | `str \| None`  | Duration of the gift effect              |
| `dice_pool`       | `list[str]`    | Dice pool attributes for the gift        |
| `opposing_pool`   | `list[str]`    | Opposing dice pool for contested rolls   |
| `minimum_renown`  | `int \| None`  | Minimum renown level required            |
| `is_native_gift`  | `bool`         | Whether this is a native tribe/auspice gift |
| `notes`           | `str \| None`  | Additional notes about the gift          |
| `tribe_id`        | `str \| None`  | Associated tribe ID (if tribal gift)     |
| `auspice_id`      | `str \| None`  | Associated auspice ID (if auspice gift)  |

### `WerewolfRite`

Represents a werewolf rite ritual.

| Field           | Type          | Description                  |
| --------------- | ------------- | ---------------------------- |
| `id`            | `str`         | MongoDB document ObjectID    |
| `name`          | `str`         | Rite name                    |
| `description`   | `str \| None` | Rite description             |
| `game_version`  | `GameVersion` | Game version (V4 or V5)      |
| `date_created`  | `datetime`    | Timestamp when created       |
| `date_modified` | `datetime`    | Timestamp when last modified |
| `pool`          | `str \| None` | Dice pool for the rite       |

### Type Aliases

| Type             | Values                 | Description                      |
| ---------------- | ---------------------- | -------------------------------- |
| `WerewolfRenown` | HONOR, GLORY, WISDOM   | Werewolf renown type for gifts   |
