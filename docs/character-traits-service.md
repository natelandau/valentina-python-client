# Character Traits Service

The Character Traits Service provides methods to retrieve and assign traits to characters within a campaign.

## Usage

The character traits service is scoped to a specific company, user, campaign, and character context at creation time:

```python
from vclient import VClient

async with VClient(base_url="...", api_key="...") as client:
    # Get a character traits service scoped to a specific character
    character_traits = client.character_traits("company_id", "user_id", "campaign_id", "character_id")

    # All operations use this context
    all_traits = await character_traits.list_all()
    trait = await character_traits.get("character_trait_id")
```

Or using the factory function:

```python
from vclient import character_traits_service

character_traits = character_traits_service("company_id", "user_id", "campaign_id", "character_id")
all_traits = await character_traits.list_all()
```

## Available Methods

### Character Trait CRUD

-   `get(character_trait_id)` - Retrieve a specific character trait by ID
-   `assign(trait_id, value)` - Assign an existing trait to the character with a specified value
-   `create(name, parent_category_id, ...)` - Create a new custom trait for the character
-   `delete(character_trait_id)` - Delete a character trait
-   `get_page(limit?, offset?, parent_category_id?)` - Get a paginated page of character traits with optional filter
-   `list_all(parent_category_id?)` - Get all character traits
-   `iter_all(limit?, parent_category_id?)` - Iterate through all character traits

### Trait Value Modification

-   `get_value_options(character_trait_id)` - Get the value options for a character trait
-   `change_value(character_trait_id, new_value)` - Change the value of a character trait

### Create Method Parameters

| Parameter            | Type          | Required | Default | Description                         |
| -------------------- | ------------- | -------- | ------- | ----------------------------------- |
| `name`               | `str`         | Yes      | -       | Name of the custom trait            |
| `parent_category_id` | `str`         | Yes      | -       | ID of the parent category           |
| `description`        | `str \| None` | No       | `None`  | Description of the trait            |
| `max_value`          | `int`         | No       | `5`     | Maximum value for the trait (0-100) |
| `min_value`          | `int`         | No       | `0`     | Minimum value for the trait (0-100) |
| `show_when_zero`     | `bool`        | No       | `True`  | Display trait when value is zero    |
| `initial_cost`       | `int \| None` | No       | `None`  | XP cost to acquire the trait        |
| `upgrade_cost`       | `int \| None` | No       | `None`  | XP cost per level upgrade           |
| `value`              | `int \| None` | No       | `None`  | Initial value for the trait         |

## Response Models

### `CharacterTrait`

Represents a trait assigned to a character, including the trait definition and the character's current value.

| Field          | Type    | Description                               |
| -------------- | ------- | ----------------------------------------- |
| `id`           | `str`   | MongoDB document ObjectID                 |
| `character_id` | `str`   | ID of the character this trait belongs to |
| `value`        | `int`   | Current value of the trait (0-5 typical)  |
| `trait`        | `Trait` | The trait definition                      |

### `Trait`

Represents a trait definition from the game system.

| Field                     | Type                   | Description                        |
| ------------------------- | ---------------------- | ---------------------------------- |
| `id`                      | `str`                  | MongoDB document ObjectID          |
| `name`                    | `str`                  | Trait name                         |
| `description`             | `str \| None`          | Trait description                  |
| `date_created`            | `datetime`             | Timestamp when created             |
| `date_modified`           | `datetime`             | Timestamp when modified            |
| `link`                    | `str \| None`          | External link for more information |
| `show_when_zero`          | `bool`                 | Display trait when value is zero   |
| `max_value`               | `int`                  | Maximum allowed value (default 5)  |
| `min_value`               | `int`                  | Minimum allowed value (default 0)  |
| `is_custom`               | `bool`                 | Whether this is a custom trait     |
| `initial_cost`            | `int`                  | XP cost to acquire                 |
| `upgrade_cost`            | `int`                  | XP cost per level upgrade          |
| `sheet_section_name`      | `str \| None`          | Character sheet section name       |
| `sheet_section_id`        | `str \| None`          | Character sheet section ID         |
| `parent_category_name`    | `str \| None`          | Parent category name               |
| `parent_category_id`      | `str`                  | Parent category ID                 |
| `custom_for_character_id` | `str \| None`          | Character ID if custom trait       |
| `advantage_category_id`   | `str \| None`          | Advantage category ID              |
| `advantage_category_name` | `str \| None`          | Advantage category name            |
| `character_classes`       | `list[CharacterClass]` | Applicable character classes       |
| `game_versions`           | `list[GameVersion]`    | Applicable game versions           |

### `CharacterTraitValueOptionsResponse`

Represents the value options for a character trait.

| Field                     | Type                                   | Description                                |
| ------------------------- | -------------------------------------- | ------------------------------------------ |
| `current_value`           | `int`                                  | Current value of the trait                 |
| `min_value`               | `int`                                  | Minimum value for the trait                |
| `max_value`               | `int`                                  | Maximum value for the trait                |
| `xp_current`              | `int`                                  | Current XP cost for the trait              |
| `starting_points_current` | `int`                                  | Current starting points cost for the trait |
| `options`                 | `dict[str, CharacterTraitValueOption]` | Value options for the trait                |

### `CharacterTraitValueOption`

Represents a value option for a character trait.

| Field                     | Type   | Description                                      |
| ------------------------- | ------ | ------------------------------------------------ |
| `direction`               | `str`  | Direction of the value option                    |
| `point_change`            | `int`  | Number of points to change                       |
| `can_use_xp`              | `bool` | Whether the value option can use XP              |
| `xp_after`                | `int`  | XP cost after the value option                   |
| `can_use_starting_points` | `bool` | Whether the value option can use starting points |
