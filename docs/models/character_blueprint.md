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

| Field                     | Type                   | Description                |
| ------------------------- | ---------------------- | -------------------------- |
| `id`                      | `str`                  | Unique identifier          |
| `name`                    | `str`                  | Category name              |
| `description`             | `str \| None`          | Description                |
| `game_versions`           | `list[GameVersion]`    | Available game versions    |
| `parent_sheet_section_id` | `str`                  | Parent section ID          |
| `initial_cost`            | `int`                  | XP cost to acquire         |
| `upgrade_cost`            | `int`                  | XP cost per upgrade        |
| `show_when_empty`         | `bool`                 | Whether to show when empty |
| `character_classes`       | `list[CharacterClass]` | Applicable classes         |
| `order`                   | `int`                  | Display order              |

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

| Field           | Type                | Description             |
| --------------- | ------------------- | ----------------------- |
| `id`            | `str`               | Unique identifier       |
| `name`          | `str`               | Tribe name              |
| `description`   | `str \| None`       | Description             |
| `game_versions` | `list[GameVersion]` | Available game versions |
| `renown`        | `WerewolfRenown`    | HONOR, GLORY, or WISDOM |
| `gift_ids`      | `list[str]`         | Native gift IDs         |
| `link`          | `str \| None`       | Link to tribe page      |
| `patron_spirit` | `str \| None`       | Patron spirit name      |
| `favor`         | `str \| None`       | Favor name              |
| `ban`           | `str \| None`       | Ban name                |

## WerewolfAuspice

| Field           | Type                | Description             |
| --------------- | ------------------- | ----------------------- |
| `id`            | `str`               | Unique identifier       |
| `name`          | `str`               | Auspice name            |
| `description`   | `str \| None`       | Description             |
| `game_versions` | `list[GameVersion]` | Available game versions |
| `gift_ids`      | `list[str]`         | Native gift IDs         |
| `link`          | `str \| None`       | Link to auspice page    |

## WerewolfGift

| Field            | Type                | Description             |
| ---------------- | ------------------- | ----------------------- |
| `id`             | `str`               | Unique identifier       |
| `name`           | `str`               | Gift name               |
| `description`    | `str \| None`       | Description             |
| `game_versions`  | `list[GameVersion]` | Available game versions |
| `renown`         | `WerewolfRenown`    | HONOR, GLORY, or WISDOM |
| `cost`           | `str \| None`       | Activation cost         |
| `minimum_renown` | `int \| None`       | Required renown level   |

## WerewolfRite

| Field           | Type                | Description             |
| --------------- | ------------------- | ----------------------- |
| `id`            | `str`               | Unique identifier       |
| `name`          | `str`               | Rite name               |
| `description`   | `str \| None`       | Description             |
| `game_versions` | `list[GameVersion]` | Available game versions |
| `pool`          | `str \| None`       | Dice pool               |

## HunterEdge

| Field           | Type                     | Description                      |
| --------------- | ------------------------ | -------------------------------- |
| `id`            | `str`                    | Unique identifier                |
| `name`          | `str`                    | Edge name                        |
| `description`   | `str \| None`            | Description                      |
| `type`          | `HunterEdgeType \| None` | ASSETS, APTITUDES, or ENDOWMENTS |
| `pool`          | `str \| None`            | Dice pool                        |
| `system`        | `str \| None`            | System rules                     |
| `game_versions` | `list[GameVersion]`      | Available game versions          |
| `perk_ids`      | `list[str]`              | Perk IDs                         |

## HunterEdgePerk

| Field           | Type                | Description             |
| --------------- | ------------------- | ----------------------- |
| `id`            | `str`               | Unique identifier       |
| `name`          | `str`               | Perk name               |
| `description`   | `str \| None`       | Description             |
| `game_versions` | `list[GameVersion]` | Available game versions |
| `edge_id`       | `str \| None`       | Parent Edge ID          |
