---
icon: lucide/user
---

# Character Models

Models for player and non-player characters, including class-specific attributes for vampires, werewolves, mages, and hunters.

## Character

| Field                 | Type                         | Description                                    |
| --------------------- | ---------------------------- | ---------------------------------------------- |
| `id`                  | `str`                        | Unique identifier                              |
| `date_created`        | `datetime`                   | Creation timestamp                             |
| `date_modified`       | `datetime`                   | Last modified timestamp                        |
| `character_class`     | `CharacterClass`             | VAMPIRE, WEREWOLF, MAGE, HUNTER, GHOUL, MORTAL |
| `type`                | `CharacterType`              | PLAYER, NPC, STORYTELLER, DEVELOPER            |
| `game_version`        | `GameVersion`                | V4 or V5                                       |
| `status`              | `CharacterStatus`            | ALIVE or DEAD                                  |
| `name_first`          | `str`                        | First name                                     |
| `name_last`           | `str`                        | Last name                                      |
| `name_nick`           | `str \| None`                | Nickname                                       |
| `name`                | `str`                        | First and last name                            |
| `name_full`           | `str`                        | First, last, and nickname                      |
| `age`                 | `int \| None`                | Age                                            |
| `biography`           | `str \| None`                | Biography                                      |
| `user_creator_id`     | `str`                        | Creator user ID                                |
| `user_player_id`      | `str`                        | Player user ID                                 |
| `company_id`          | `str`                        | Company ID                                     |
| `campaign_id`         | `str`                        | Campaign ID                                    |
| `concept_id`          | `str \| None`                | Concept ID                                     |
| `starting_points`     | `int`                        | Starting experience points                     |
| `demeanor`            | `str \| None`                | demeanor                                       |
| `nature`              | `str \| None`                | nature                                         |
| `asset_ids`           | `list[str]`                  | Asset IDs                                      |
| `specialties`         | `list[CharacterSpecialty]`   | Character specialties                          |
| `character_trait_ids` | `list[str]`                  | Character trait IDs                            |
| `vampire_attributes`  | `VampireAttributes \| None`  | Vampire-specific data                          |
| `werewolf_attributes` | `WerewolfAttributes \| None` | Werewolf-specific data                         |
| `hunter_attributes`   | `HunterAttributes \| None`   | Hunter-specific data                           |
| `mage_attributes`     | `MageAttributes \| None`     | Mage-specific data                             |

## VampireAttributes

| Field        | Type          | Description |
| ------------ | ------------- | ----------- |
| `clan_id`    | `str \| None` | Clan ID     |
| `clan_name`  | `str \| None` | Clan name   |
| `generation` | `int \| None` | Generation  |
| `sire`       | `str \| None` | Sire name   |

## WerewolfAttributes

| Field          | Type          | Description  |
| -------------- | ------------- | ------------ |
| `tribe_id`     | `str \| None` | Tribe ID     |
| `tribe_name`   | `str \| None` | Tribe name   |
| `auspice_id`   | `str \| None` | Auspice ID   |
| `auspice_name` | `str \| None` | Auspice name |
| `pack_name`    | `str \| None` | Pack name    |

## HunterAttributes

| Field   | Type               | Description  |
| ------- | ------------------ | ------------ |
| `creed` | `str \| None`      | Hunter creed |

## MageAttributes

| Field       | Type          | Description             |
| ----------- | ------------- | ----------------------- |
| `sphere`    | `str \| None` | Primary sphere of magic |
| `tradition` | `str \| None` | Mage tradition          |

## InventoryItem

Represents an item in a character's inventory.

| Field           | Type                     | Description             |
| --------------- | ------------------------ | ----------------------- |
| `id`            | `str`                    | Unique identifier       |
| `character_id`  | `str`                    | Parent character ID     |
| `name`          | `str`                    | Item name               |
| `type`          | `CharacterInventoryType` | Item type               |
| `description`   | `str \| None`            | Item description        |
| `date_created`  | `datetime`               | Creation timestamp      |
| `date_modified` | `datetime`               | Last modified timestamp |

## CharacterFullSheet

Top-level response for the full character sheet endpoint.

| Field       | Type                          | Description                            |
| ----------- | ----------------------------- | -------------------------------------- |
| `character` | `Character`                   | The character data                     |
| `sections`  | `list[FullSheetTraitSection]` | Hierarchical trait sections            |

## FullSheetTraitSection

A section on the character sheet (e.g., "Physical", "Social", "Mental").

| Field             | Type                            | Description                       |
| ----------------- | ------------------------------- | --------------------------------- |
| `id`              | `str`                           | Unique identifier                 |
| `name`            | `str`                           | Section name                      |
| `description`     | `str \| None`                   | Section description               |
| `order`           | `int`                           | Display order                     |
| `show_when_empty` | `bool`                          | Whether to show when no traits    |
| `categories`      | `list[FullSheetTraitCategory]`  | Trait categories in this section  |

## FullSheetTraitCategory

A trait category within a section (e.g., "Attributes", "Skills").

| Field              | Type                               | Description                              |
| ------------------ | ---------------------------------- | ---------------------------------------- |
| `id`               | `str`                              | Unique identifier                        |
| `name`             | `str`                              | Category name                            |
| `description`      | `str \| None`                      | Category description                     |
| `initial_cost`     | `int`                              | XP cost for initial dot                  |
| `upgrade_cost`     | `int`                              | XP cost per additional dot               |
| `show_when_empty`  | `bool`                             | Whether to show when no traits           |
| `order`            | `int`                              | Display order                            |
| `subcategories`    | `list[FullSheetTraitSubcategory]`  | Subcategories in this category           |
| `character_traits` | `list[CharacterTrait]`             | Direct traits (no subcategory)           |

## FullSheetTraitSubcategory

A trait subcategory within a category (e.g., "Celerity", "Potence").

| Field              | Type                        | Description                               |
| ------------------ | --------------------------- | ----------------------------------------- |
| `id`               | `str`                       | Unique identifier                         |
| `name`             | `str`                       | Subcategory name                          |
| `description`      | `str \| None`               | Subcategory description                   |
| `initial_cost`     | `int`                       | XP cost for initial dot                   |
| `upgrade_cost`     | `int`                       | XP cost per additional dot                |
| `show_when_empty`  | `bool`                      | Whether to show when no traits            |
| `requires_parent`  | `bool`                      | Whether a parent trait is required         |
| `pool`             | `str \| None`               | Dice pool formula                         |
| `system`           | `str \| None`               | System rules description                  |
| `hunter_edge_type` | `HunterEdgeType \| None`    | Hunter edge type (ASSETS, APTITUDES, etc) |
| `character_traits` | `list[CharacterTrait]`      | Traits in this subcategory                |

