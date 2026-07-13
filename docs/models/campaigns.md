---
icon: lucide/map
---

# Campaign Models

Models for campaigns, which organize gameplay sessions within a company.

## Campaign

| Field                          | Type          | Description                                      |
| ------------------------------ | ------------- | ------------------------------------------------ |
| `id`                           | `str`         | Unique identifier                                |
| `date_created`                 | `datetime`    | Creation timestamp                               |
| `date_modified`                | `datetime`    | Last modified timestamp                          |
| `name`                         | `str`         | Campaign name                                    |
| `description`                  | `str \| None` | Campaign description                             |
| `in_game_date`                 | `date \| None`| In-game calendar date (ISO 8601 `YYYY-MM-DD`)    |
| `desperation`                  | `int`         | Desperation level (0-5)                          |
| `danger`                       | `int`         | Danger level (0-5)                               |
| `company_id`                   | `str`         | Company ID                                       |
| `asset_ids`                    | `list[str]`   | Associated asset IDs                             |
| `num_books`                    | `int`         | Active book count (excludes archived)            |
| `num_chapters`                 | `int`         | Active chapter count across active books         |
| `num_notes`                    | `int`         | Active note count on the campaign                |
| `num_player_characters`        | `int`         | Active player character count                    |
| `num_storyteller_characters`   | `int`         | Active storyteller character count               |
| `num_npc_characters`           | `int`         | Active NPC character count                       |
