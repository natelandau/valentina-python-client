---
icon: lucide/list
---

# Character Trait Models

Models for character traits, trait definitions, and trait value modification options.

## CharacterTrait

| Field          | Type    | Description         |
| -------------- | ------- | ------------------- |
| `id`           | `str`   | Unique identifier   |
| `character_id` | `str`   | Parent character ID |
| `value`        | `int`   | Current trait value |
| `trait`        | `Trait` | Trait definition    |

## CharacterTraitAdd

Request model for assigning a trait to an already-created character. Used by the `assign()` method on the character traits service.

| Field      | Type                  | Description                          |
| ---------- | --------------------- | ------------------------------------ |
| `trait_id` | `str`                 | ID of the trait to assign            |
| `value`    | `int`                 | Value to set for the trait           |
| `currency` | `TraitModifyCurrency` | Currency to use to pay for the trait |

## BulkAssignTraitResponse

Response from `bulk_assign()`. Contains results grouped by outcome.

| Field       | Type                           | Description                       |
| ----------- | ------------------------------ | --------------------------------- |
| `succeeded` | `list[BulkAssignTraitSuccess]` | Successfully assigned traits      |
| `failed`    | `list[BulkAssignTraitFailure]` | Traits that failed to be assigned |

## BulkAssignTraitSuccess

| Field             | Type             | Description                            |
| ----------------- | ---------------- | -------------------------------------- |
| `trait_id`        | `str`            | ID of the trait that was assigned      |
| `character_trait` | `CharacterTrait` | The resulting character trait instance |

## BulkAssignTraitFailure

| Field      | Type  | Description                  |
| ---------- | ----- | ---------------------------- |
| `trait_id` | `str` | ID of the trait that failed  |
| `error`    | `str` | Human-readable error message |

## Trait

| Field                    | Type                     | Description                        |
| ------------------------ | ------------------------ | ---------------------------------- |
| `id`                     | `str`                    | Unique identifier                  |
| `name`                   | `str`                    | Trait name                         |
| `description`            | `str \| None`            | Trait description                  |
| `max_value`              | `int`                    | Maximum value                      |
| `min_value`              | `int`                    | Minimum value                      |
| `is_custom`              | `bool`                   | Whether custom trait               |
| `initial_cost`           | `int`                    | XP cost to acquire                 |
| `upgrade_cost`           | `int`                    | XP cost per upgrade                |
| `parent_category_id`     | `str`                    | Parent category ID                 |
| `parent_category_name`   | `str \| None`            | Parent category name               |
| `trait_subcategory_id`   | `str \| None`            | Trait subcategory ID               |
| `trait_subcategory_name` | `str \| None`            | Trait subcategory name             |
| `pool`                   | `str \| None`            | Traits that contribute to the pool |
| `opposing_pool`          | `str \| None`            | Traits to counter this trait       |
| `system`                 | `str \| None`            | System rules                       |
| `sheet_section_id`       | `str`                    | Sheet section ID                   |
| `sheet_section_name`     | `str \| None`            | Sheet section name                 |
| `game_versions`          | `list[GameVersion]`      | Available game versions            |
| `character_classes`      | `list[CharacterClass]`   | Applicable classes                 |
| `gift_attributes`        | `GiftAttributes \| None` | Werewolf gift attributes           |

## CharacterTraitValueOptionsResponse

Returned when querying available value change options for a character trait. Contains the current state and a map of possible changes with their costs.

| Field                     | Type                                   | Description                    |
| ------------------------- | -------------------------------------- | ------------------------------ |
| `name`                    | `str`                                  | Name of the trait              |
| `current_value`           | `int`                                  | Current trait value            |
| `trait`                   | `Trait`                                | Full Trait definition          |
| `xp_current`              | `int`                                  | Available XP                   |
| `starting_points_current` | `int`                                  | Available starting points      |
| `options`                 | `dict[str, CharacterTraitValueOption]` | Map of value to change options |

## CharacterTraitValueOption

Represents a single value change option for a trait.

| Field                     | Type   | Description                         |
| ------------------------- | ------ | ----------------------------------- |
| `direction`               | `str`  | Direction of change (up/down)       |
| `point_change`            | `int`  | Cost in points for this change      |
| `can_use_xp`              | `bool` | Whether XP can fund this change     |
| `xp_after`                | `int`  | XP remaining after this change      |
| `can_use_starting_points` | `bool` | Whether starting points can be used |
| `starting_points_after`   | `int`  | Starting points remaining after     |
