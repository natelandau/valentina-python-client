---
icon: lucide/user
---

# Character Models

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
| `name`                | `str`                        | Display name                                   |
| `name_full`           | `str`                        | Full name                                      |
| `age`                 | `int \| None`                | Age                                            |
| `biography`           | `str \| None`                | Biography                                      |
| `user_creator_id`     | `str`                        | Creator user ID                                |
| `user_player_id`      | `str`                        | Player user ID                                 |
| `company_id`          | `str`                        | Company ID                                     |
| `campaign_id`         | `str`                        | Campaign ID                                    |
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
| `edges` | `list[HunterEdge]` | Hunter edges |

## MageAttributes

| Field       | Type          | Description            |
| ----------- | ------------- | ---------------------- |
| `sphere`    | `str \| None` | Primary sphere of magic |
| `tradition` | `str \| None` | Mage tradition          |
