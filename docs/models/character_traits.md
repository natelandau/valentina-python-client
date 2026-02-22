---
icon: lucide/list
---

# Character Trait Models

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
