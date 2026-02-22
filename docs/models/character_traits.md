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

## Trait

| Field                  | Type                   | Description             |
| ---------------------- | ---------------------- | ----------------------- |
| `id`                   | `str`                  | Unique identifier       |
| `name`                 | `str`                  | Trait name              |
| `description`          | `str \| None`          | Trait description       |
| `max_value`            | `int`                  | Maximum value           |
| `min_value`            | `int`                  | Minimum value           |
| `is_custom`            | `bool`                 | Whether custom trait    |
| `initial_cost`         | `int`                  | XP cost to acquire      |
| `upgrade_cost`         | `int`                  | XP cost per upgrade     |
| `parent_category_id`   | `str`                  | Parent category ID      |
| `parent_category_name` | `str \| None`          | Parent category name    |
| `game_versions`        | `list[GameVersion]`    | Available game versions |
| `character_classes`    | `list[CharacterClass]` | Applicable classes      |

## CharacterTraitValueOptionsResponse

Returned when querying available value change options for a character trait. Contains the current state and a map of possible changes with their costs.

| Field                    | Type                                      | Description                    |
| ------------------------ | ----------------------------------------- | ------------------------------ |
| `current_value`          | `int`                                     | Current trait value            |
| `min_value`              | `int`                                     | Minimum allowed value          |
| `max_value`              | `int`                                     | Maximum allowed value          |
| `xp_current`             | `int`                                     | Available XP                   |
| `starting_points_current`| `int`                                     | Available starting points      |
| `options`                | `dict[str, CharacterTraitValueOption]`    | Map of value to change options |

## CharacterTraitValueOption

Represents a single value change option for a trait.

| Field                   | Type   | Description                          |
| ----------------------- | ------ | ------------------------------------ |
| `direction`             | `str`  | Direction of change (up/down)        |
| `point_change`          | `int`  | Cost in points for this change       |
| `can_use_xp`            | `bool` | Whether XP can fund this change      |
| `xp_after`              | `int`  | XP remaining after this change       |
| `can_use_starting_points`| `bool`| Whether starting points can be used  |
| `starting_points_after` | `int`  | Starting points remaining after      |
