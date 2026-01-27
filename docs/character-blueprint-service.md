# Character Blueprint Service

The Character Blueprint Service provides read-only access to character sheet blueprints, including sections, categories, and traits that define the structure of character sheets for different game versions.

## Usage

The character blueprint service is scoped to a specific company context at creation time:

```python
from vclient import VClient

async with VClient(base_url="...", api_key="...") as client:
    # Get a character blueprint service scoped to a company
    blueprint = client.character_blueprint("company_id")

    # Get all sections for a game version
    sections = await blueprint.list_all_sections(game_version="V5")

    # Get categories within a section
    categories = await blueprint.list_all_categories(
        game_version="V5",
        section_id="section_id"
    )

    # Get traits within a category
    traits = await blueprint.list_all_traits(
        game_version="V5",
        section_id="section_id",
        category_id="category_id"
    )
```

Or using the factory function:

```python
from vclient import character_blueprint_service

blueprint = character_blueprint_service("company_id")
sections = await blueprint.list_all_sections(game_version="V5")
```

## Available Methods

### Sections

Sections are the top-level organization of a character sheet (e.g., "Attributes", "Skills", "Disciplines").

- `get_sections_page(game_version, limit?, offset?, character_class?)` - Get a paginated page of character blueprint sections
- `list_all_sections(game_version, character_class?)` - Get all sections for a game version
- `iter_all_sections(game_version, character_class?)` - Iterate through all sections
- `get_section(game_version, section_id)` - Get a specific section by ID

### Categories

Categories are nested within sections (e.g., "Physical", "Social", "Mental" within "Attributes").

- `get_categories_page(game_version, section_id, limit?, offset?, character_class?)` - Get a paginated page of categories within a section
- `list_all_categories(game_version, section_id, character_class?)` - Get all categories within a section
- `iter_all_categories(game_version, section_id, character_class?)` - Iterate through all categories
- `get_category(game_version, section_id, category_id)` - Get a specific category by ID

### Category Traits

- `get_category_traits_page(game_version, section_id, category_id, limit?, offset?, character_class?, character_id?)` - Get a paginated page of traits within a category
- `list_all_category_traits(game_version, section_id, category_id, character_class?, character_id?)` - Get all traits within a category
- `iter_all_category_traits(game_version, section_id, category_id, character_class?, character_id?)` - Iterate through all traits within a category

### Traits

Traits are the individual attributes, skills, or abilities within categories (e.g., "Strength", "Brawl", "Dominate").

- `get_traits_page(game_version, section_id, category_id, limit?, offset?, character_class?, character_id?)` - Get a paginated page of traits within a category
- `list_all_traits(game_version, section_id, category_id, character_class?, character_id?)` - Get all traits within a category
- `iter_all_traits(game_version, section_id, category_id, character_class?, character_id?)` - Iterate through all traits
- `get_trait(game_version, section_id, category_id, trait_id)` - Get a specific trait by ID

### Character Concepts

- `get_concepts_page(limit?, offset?)` - Get a paginated page of character concepts
- `list_all_concepts()` - Get all character concepts
- `iter_all_concepts()` - Iterate through all character concepts
- `get_concept(concept_id)` - Get a specific concept by ID

### Vampire Clans

- `get_vampire_clans_page(limit?, offset?)` - Get a paginated page of vampire clans
- `list_all_vampire_clans()` - Get all vampire clans
- `iter_all_vampire_clans()` - Iterate through all vampire clans
- `get_vampire_clan(vampire_clan_id)` - Get a specific vampire clan by ID

### Werewolf Tribes

- `get_werewolf_tribes_page(limit?, offset?)` - Get a paginated page of werewolf tribes
- `list_all_werewolf_tribes()` - Get all werewolf tribes
- `iter_all_werewolf_tribes()` - Iterate through all werewolf tribes
- `get_werewolf_tribe(werewolf_tribe_id)` - Get a specific werewolf tribe by ID

### Werewolf Auspices

- `get_werewolf_auspices_page(limit?, offset?)` - Get a paginated page of werewolf auspices
- `list_all_werewolf_auspices()` - Get all werewolf auspices
- `iter_all_werewolf_auspices()` - Iterate through all werewolf auspices
- `get_werewolf_auspice(werewolf_auspice_id)` - Get a specific werewolf auspice by ID

### Werewolf Gifts

- `get_werewolf_gifts_page(limit?, offset?)` - Get a paginated page of werewolf gifts
- `list_all_werewolf_gifts()` - Get all werewolf gifts
- `iter_all_werewolf_gifts()` - Iterate through all werewolf gifts
- `get_werewolf_gift(werewolf_gift_id)` - Get a specific werewolf gift by ID

### Werewolf Rites

- `get_werewolf_rites_page(limit?, offset?)` - Get a paginated page of werewolf rites
- `list_all_werewolf_rites()` - Get all werewolf rites
- `iter_all_werewolf_rites()` - Iterate through all werewolf rites
- `get_werewolf_rite(werewolf_rite_id)` - Get a specific werewolf rite by ID

### Hunter Edges

- `get_hunter_edges_page(limit?, offset?)` - Get a paginated page of hunter edges
- `list_all_hunter_edges()` - Get all hunter edges
- `iter_all_hunter_edges()` - Iterate through all hunter edges
- `get_hunter_edge(hunter_edge_id)` - Get a specific hunter edge by ID

### Hunter Edge Perks

- `get_hunter_edge_perks_page(hunter_edge_id, limit?, offset?)` - Get a paginated page of hunter edge perks
- `list_all_hunter_edge_perks(hunter_edge_id)` - Get all hunter edge perks
- `iter_all_hunter_edge_perks(hunter_edge_id, limit?)` - Iterate through all hunter edge perks
- `get_hunter_edge_perk(hunter_edge_id, hunter_edge_perk_id)` - Get a specific hunter edge perk by ID

## Response Models

### `SheetSection`

Represents a top-level section of the character sheet blueprint.

| Field               | Type                   | Description                                      |
| ------------------- | ---------------------- | ------------------------------------------------ |
| `id`                | `str`                  | MongoDB document ObjectID                        |
| `name`              | `str`                  | Section name (e.g., "Attributes")                |
| `description`       | `str \| None`          | Section description                              |
| `character_classes` | `list[CharacterClass]` | Character classes this section applies to        |
| `date_created`      | `datetime`             | Timestamp when created                           |
| `date_modified`     | `datetime`             | Timestamp when last modified                     |
| `game_version`      | `GameVersion`          | Game version (V4 or V5)                          |
| `show_when_empty`   | `bool`                 | Whether to display section when it has no values |
| `order`             | `int`                  | Display order on the character sheet             |

### `TraitCategory`

Represents a category within a character sheet section.

| Field                     | Type                   | Description                                |
| ------------------------- | ---------------------- | ------------------------------------------ |
| `id`                      | `str`                  | MongoDB document ObjectID                  |
| `name`                    | `str`                  | Category name (e.g., "Physical")           |
| `description`             | `str \| None`          | Category description                       |
| `character_classes`       | `list[CharacterClass]` | Character classes this category applies to |
| `date_created`            | `datetime`             | Timestamp when created                     |
| `date_modified`           | `datetime`             | Timestamp when last modified               |
| `game_version`            | `GameVersion`          | Game version (V4 or V5)                    |
| `parent_sheet_section_id` | `str`                  | ID of the parent section                   |
| `initial_cost`            | `int`                  | XP cost to acquire traits in this category |
| `upgrade_cost`            | `int`                  | XP cost per level upgrade                  |

### `Trait`

Represents a trait definition from the game system.

| Field                     | Type                   | Description                        |
| ------------------------- | ---------------------- | ---------------------------------- |
| `id`                      | `str`                  | MongoDB document ObjectID          |
| `name`                    | `str`                  | Trait name (e.g., "Strength")      |
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

### `CharacterConcept`

Represents a character concept from the game system.

| Field                   | Type                       | Description                               |
| ----------------------- | -------------------------- | ----------------------------------------- |
| `id`                    | `str`                      | MongoDB document ObjectID                 |
| `name`                  | `str`                      | Concept name (e.g., "Physical")           |
| `description`           | `str \| None`              | Concept description                       |
| `date_created`          | `datetime`                 | Timestamp when created                    |
| `date_modified`         | `datetime`                 | Timestamp when modified                   |
| `game_version`          | `GameVersion`              | Game version (V4 or V5)                   |
| `examples`              | `list[str]`                | Example concepts                          |
| `company_id`            | `str \| None`              | Company ID if concept is company-specific |
| `max_specialties`       | `int`                      | Maximum number of specialties             |
| `specialties`           | `list[CharacterSpecialty]` | List of character specialties             |
| `favored_ability_names` | `list[str]`                | List of favored ability names             |
