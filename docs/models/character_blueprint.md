---
icon: lucide/file-text
---

# Character Blueprint Models

Blueprint models define the structure and rules for character creation across different game versions and character types.

## SheetSection

Top-level character sheet section. Organizes traits into logical groups like "Attributes", "Skills", or "Disciplines".

| Field               | Type                   | Description                |
| ------------------- | ---------------------- | -------------------------- |
| `id`                | `str`                  | Unique identifier          |
| `name`              | `str`                  | Section name               |
| `description`       | `str \| None`          | Description                |
| `game_versions`     | `list[GameVersion]`    | Available game versions    |
| `character_classes` | `list[CharacterClass]` | Applicable classes         |
| `order`             | `int`                  | Display order              |
| `show_when_empty`   | `bool`                 | Whether to show when empty |

## TraitCategory

Category within a sheet section. Groups related traits together, like "Physical Attributes" or "Social Skills".

| Field                         | Type                   | Description                            |
| ----------------------------- | ---------------------- | -------------------------------------- |
| `id`                          | `str`                  | Unique identifier                      |
| `name`                        | `str`                  | Category name                          |
| `description`                 | `str \| None`          | Description                            |
| `game_versions`               | `list[GameVersion]`    | Available game versions                |
| `parent_sheet_section_id`     | `str`                  | Parent section ID                      |
| `initial_cost`                | `int`                  | XP cost to acquire                     |
| `upgrade_cost`                | `int`                  | XP cost per upgrade                    |
| `count_based_cost_multiplier` | `int \| None`          | Count-based cost multiplier for traits |
| `show_when_empty`             | `bool`                 | Whether to show when empty             |
| `character_classes`           | `list[CharacterClass]` | Applicable classes                     |
| `order`                       | `int`                  | Display order                          |

## TraitSubcategory

Subcategory within a trait category. Groups related traits together, like "Allies" or "Resources" within "Backgrounds".

| Field                         | Type                   | Description                                     |
| ----------------------------- | ---------------------- | ----------------------------------------------- |
| `id`                          | `str`                  | Unique identifier                               |
| `name`                        | `str`                  | Subcategory name                                |
| `description`                 | `str \| None`          | Description                                     |
| `date_created`                | `datetime`             | Creation timestamp                              |
| `date_modified`               | `datetime`             | Last modified timestamp                         |
| `game_versions`               | `list[GameVersion]`    | Available game versions                         |
| `character_classes`           | `list[CharacterClass]` | Applicable classes                              |
| `show_when_empty`             | `bool`                 | Whether to show when empty                      |
| `initial_cost`                | `int`                  | Default initial cost for traits                 |
| `upgrade_cost`                | `int`                  | Default upgrade cost multiplier                 |
| `count_based_cost_multiplier` | `int \| None`          | Count-based cost multiplier for traits          |
| `requires_parent`             | `bool`                 | Whether subcategory must be added before traits |
| `pool`                        | `str \| None`          | Dice pool description                           |
| `system`                      | `str \| None`          | System/mechanical rules                         |
| `parent_category_id`          | `str`                  | Parent category ID                              |
| `parent_category_name`        | `str`                  | Parent category name                            |

## CharacterConcept

| Field             | Type          | Description             |
| ----------------- | ------------- | ----------------------- |
| `id`              | `str`         | Unique identifier       |
| `name`            | `str`         | Concept name            |
| `description`     | `str \| None` | Description             |
| `examples`        | `list[str]`   | Example concepts        |
| `max_specialties` | `int`         | Max specialties allowed |

## VampireClan

| Field           | Type                | Description             |
| --------------- | ------------------- | ----------------------- |
| `id`            | `str`               | Unique identifier       |
| `name`          | `str`               | Clan name               |
| `description`   | `str \| None`       | Description             |
| `game_versions` | `list[GameVersion]` | Available game versions |

## WerewolfTribe

| Field            | Type                | Description             |
| ---------------- | ------------------- | ----------------------- |
| `id`             | `str`               | Unique identifier       |
| `name`           | `str`               | Tribe name              |
| `description`    | `str \| None`       | Description             |
| `game_versions`  | `list[GameVersion]` | Available game versions |
| `renown`         | `WerewolfRenown`    | HONOR, GLORY, or WISDOM |
| `gift_trait_ids` | `list[str]`         | Native gift trait IDs   |
| `link`           | `str \| None`       | Link to tribe page      |
| `patron_spirit`  | `str \| None`       | Patron spirit name      |
| `favor`          | `str \| None`       | Favor name              |
| `ban`            | `str \| None`       | Ban name                |

## WerewolfAuspice

| Field            | Type                | Description             |
| ---------------- | ------------------- | ----------------------- |
| `id`             | `str`               | Unique identifier       |
| `name`           | `str`               | Auspice name            |
| `description`    | `str \| None`       | Description             |
| `game_versions`  | `list[GameVersion]` | Available game versions |
| `gift_trait_ids` | `list[str]`         | Native gift trait IDs   |
| `link`           | `str \| None`       | Link to auspice page    |

## GiftAttributes

Werewolf gift-specific attributes embedded on a `Trait`. Present on traits that represent werewolf gifts; `None` on all other traits.

| Field            | Type             | Description              |
| ---------------- | ---------------- | ------------------------ |
| `renown`         | `WerewolfRenown` | HONOR, GLORY, or WISDOM  |
| `cost`           | `str \| None`    | Activation cost          |
| `duration`       | `str \| None`    | Effect duration          |
| `dice_pool`      | `list[str]`      | Dice pool components     |
| `opposing_pool`  | `list[str]`      | Opposing pool components |
| `minimum_renown` | `int \| None`    | Required renown level    |
| `is_native_gift` | `bool`           | Whether gift is native   |
| `notes`          | `str \| None`    | Additional notes         |
| `tribe_id`       | `str \| None`    | Associated tribe ID      |
| `auspice_id`     | `str \| None`    | Associated auspice ID    |
