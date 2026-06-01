---
icon: lucide/user
---

# Characters Service

Manage characters within a campaign, including their statistics, assets, notes, inventory, and supernatural abilities.

## Usage

```python
from vclient import characters_service

characters = characters_service(
    on_behalf_of="USER_ID",
    company_id="COMPANY_ID"
)
```

The `on_behalf_of` user ID is required and is sent on every request, including reads. The acting user's role determines what is visible.

## Access control

Visibility of `STORYTELLER` characters depends on the acting user's role:

- `PLAYER` and `NPC` characters are visible to every approved company member.
- `STORYTELLER` characters are visible only to `STORYTELLER` and `ADMIN` roles. For a `PLAYER`:
  - List results omit `STORYTELLER` characters (filtering with `character_type="STORYTELLER"` returns an empty page).
  - Fetching a `STORYTELLER` character by ID, or any of its sub-resources (traits, inventory, notes, assets, statistics), raises `AuthorizationError` (403).
- Only `STORYTELLER` and `ADMIN` roles may `create()` a character with `type="STORYTELLER"` or `update()` an existing character's `type` to `STORYTELLER`. A `PLAYER` attempting either raises `AuthorizationError` (403).

## Methods

### CRUD Operations

| Method                                            | Returns     | Description            |
| ------------------------------------------------- | ----------- | ---------------------- |
| `get(character_id)`                               | `Character` | Get a character by ID  |
| `create(CharacterCreate, **kwargs)`               | `Character` | Create a new character |
| `update(character_id, CharacterUpdate, **kwargs)` | `Character` | Update a character     |
| `delete(character_id)`                            | `None`      | Delete a character     |

### Pagination

| Method                                                                                                              | Returns                        | Description                                    |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------ | ---------------------------------------------- |
| `get_page(limit?, offset?, campaign_id?, user_player_id?, character_class?, character_type?, status?, is_temporary?)` | `PaginatedResponse[Character]` | Get a page of characters with optional filters |
| `list_all(...)`                                                                                                  | `list[Character]`              | Get all characters (supports same filters)     |
| `iter_all(limit?, ...)`                                                                                          | `AsyncIterator[Character]`     | Iterate through all characters                 |

### Statistics

| Method                                          | Returns          | Description              |
| ----------------------------------------------- | ---------------- | ------------------------ |
| `get_statistics(character_id, num_top_traits?)` | `RollStatistics` | Get dice roll statistics |

!!! info "Roll Analytics"

    Statistics include success rates, critical frequencies, and most-used traits. Use this data to understand how a character performs in gameplay.

### Full Sheet

| Method                                                                          | Returns                  | Description                                      |
| ------------------------------------------------------------------------------- | ------------------------ | ------------------------------------------------ |
| `get_full_sheet(character_id, include_available_traits?)`                       | `CharacterFullSheet`     | Get hierarchical character sheet with all traits |
| `get_full_sheet_category(character_id, category_id, include_available_traits?)` | `FullSheetTraitCategory` | Get a single category slice of the full sheet    |

!!! info "Sheet Structure"

    The full sheet returns all traits organized as sections > categories > subcategories > character traits. The skeleton includes all structures for the character's class and game version, even if empty. Use this to render a complete character sheet UI.

!!! info "Available Traits"

    Set `include_available_traits=True` to populate the `available_traits` field on each category and subcategory with standard traits the character could add. When not set, these lists are always empty. Custom traits are excluded.

### Assets

| Method                                           | Returns                    | Description            |
| ------------------------------------------------ | -------------------------- | ---------------------- |
| `get_assets_page(character_id, limit?, offset?)` | `PaginatedResponse[Asset]` | Get a page of assets   |
| `list_all_assets(character_id)`                  | `list[Asset]`              | Get all assets         |
| `iter_all_assets(character_id, limit?)`          | `AsyncIterator[Asset]`     | Iterate through assets |
| `get_asset(character_id, asset_id)`              | `Asset`                    | Get an asset           |
| `upload_asset(character_id, filename, content)`  | `Asset`                    | Upload an asset        |
| `delete_asset(character_id, asset_id)`           | `None`                     | Delete an asset        |

### Notes

| Method                                                     | Returns                   | Description           |
| ---------------------------------------------------------- | ------------------------- | --------------------- |
| `get_notes_page(character_id, limit?, offset?)`            | `PaginatedResponse[Note]` | Get a page of notes   |
| `list_all_notes(character_id)`                             | `list[Note]`              | Get all notes         |
| `iter_all_notes(character_id, limit?)`                     | `AsyncIterator[Note]`     | Iterate through notes |
| `get_note(character_id, note_id)`                          | `Note`                    | Get a note            |
| `create_note(character_id, NoteCreate, **kwargs)`          | `Note`                    | Create a note         |
| `update_note(character_id, note_id, NoteUpdate, **kwargs)` | `Note`                    | Update a note         |
| `delete_note(character_id, note_id)`                       | `None`                    | Delete a note         |

### Inventory

| Method                                                                        | Returns                            | Description                   |
| ----------------------------------------------------------------------------- | ---------------------------------- | ----------------------------- |
| `get_inventory_page(character_id, limit?, offset?)`                           | `PaginatedResponse[InventoryItem]` | Get a page of inventory items |
| `list_all_inventory(character_id)`                                            | `list[InventoryItem]`              | Get all inventory items       |
| `iter_all_inventory(character_id, limit?)`                                    | `AsyncIterator[InventoryItem]`     | Iterate through items         |
| `get_inventory_item(character_id, item_id)`                                   | `InventoryItem`                    | Get an item                   |
| `create_inventory_item(character_id, InventoryItemCreate, **kwargs)`          | `InventoryItem`                    | Create an item                |
| `update_inventory_item(character_id, item_id, InventoryItemUpdate, **kwargs)` | `InventoryItem`                    | Update an item                |
| `delete_inventory_item(character_id, item_id)`                                | `None`                             | Delete an item                |

## Example

```python
from vclient.models import CharacterCreate, CharacterUpdate, InventoryItemCreate, NoteCreate

# Create a vampire character (preferred method: use model object)
request = CharacterCreate(
    campaign_id="campaign_id",
    character_class="VAMPIRE",
    game_version="V5",
    name_first="Marcus",
    name_last="Blackwood",
    user_player_id="player_user_id"
)
character = await characters.create(request)

# Alternative: pass fields as keyword arguments
character = await characters.create(
    campaign_id="campaign_id",
    character_class="VAMPIRE",
    game_version="V5",
    name_first="Marcus",
    name_last="Blackwood",
    user_player_id="player_user_id"
)

# Update character details
update = CharacterUpdate(name_first="Marcus", name_last="Black")
updated = await characters.update(character.id, update)

# Retrieve roll statistics
stats = await characters.get_statistics(character.id)
print(f"Total rolls: {stats.total_rolls}")
print(f"Success rate: {stats.success_percentage}%")

# Add an inventory item
item_request = InventoryItemCreate(
    name="Silver Dagger",
    type="weapon",
    description="An ornate blade"
)
item = await characters.create_inventory_item(character.id, item_request)

# Create a character note
note_request = NoteCreate(title="Background", content="Born in Victorian London...")
note = await characters.create_note(character.id, note_request)
```

See [Response Models](../models/characters.md) for `Character` and related types.
