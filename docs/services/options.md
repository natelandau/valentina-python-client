---
icon: lucide/list
---

# Options Service

The Options service retrieves all available enumerations and configuration values used throughout the API. This is useful for populating dropdowns, validating input values, and understanding available options before making API calls.

## Usage

```python
from vclient import options_service

options = options_service(on_behalf_of="USER_ID", company_id="COMPANY_ID")
```

## Methods

| Method          | Returns | Description                      |
| --------------- | ------- | -------------------------------- |
| `get_options()` | `dict`  | Get all options and enumerations |

## Response Structure

The options endpoint returns a dictionary organized by category:

### Companies

Permission settings that control user access:

| Key                           | Values                                           | Description                     |
| ----------------------------- | ------------------------------------------------ | ------------------------------- |
| `PermissionManageCampaign`    | `UNRESTRICTED`, `STORYTELLER`                    | Who can create/edit campaigns   |
| `PermissionsGrantXP`          | `UNRESTRICTED`, `PLAYER`, `STORYTELLER`          | Who can grant experience        |
| `PermissionsFreeTraitChanges` | `UNRESTRICTED`, `WITHIN_24_HOURS`, `STORYTELLER` | Who can make free trait changes |

### Characters

Character-related enumerations:

| Key                      | Description                                                      |
| ------------------------ | ---------------------------------------------------------------- |
| `AbilityFocus`           | Character ability specializations                                |
| `AutoGenExperienceLevel` | Experience levels for auto-generated characters                  |
| `CharacterClass`         | Available character classes (Vampire, Werewolf, etc.)            |
| `CharacterStatus`        | Character status values (ALIVE, DEAD, ARCHIVED)                  |
| `CharacterType`          | Character visibility types (PLAYER, NPC, STORYTELLER)            |
| `GameVersion`            | Supported World of Darkness versions                             |
| `HunterEdgeType`         | Hunter edge categories                                           |
| `InventoryItemType`      | Types of inventory items                                         |
| `TraitModifyCurrency`    | Currency types for trait modifications                           |
| `TrackerAction`          | Actions for trait trackers and health                            |
| `TrackerRules`           | Valid tracker and health actions per game version (a nested dictionary, see below) |
| `TrackerType`            | Tracker types for traits (COUNTER, DAMAGE, STAINS)               |
| `WerewolfRenown`         | Werewolf renown types                                            |
| `_related`               | URLs to related blueprint endpoints                              |

#### TrackerRules

`TrackerRules` is a nested dictionary, not a list. Its shape is `{game_version: {tracker_type: {"actions": [...]}}}`. V4 has the keys `COUNTER` and `DAMAGE`. V5 has the keys `COUNTER`, `STAINS`, and `DAMAGE`. Health uses the `DAMAGE` key, which is its `type`. Look up the actions for a trait tracker or for health with `rules[game_version][tracker.type]`. A rule change on the server then needs no client release.

```python
options = await options_service().get_options()
rules = options["characters"]["TrackerRules"]

rules["V5"]["STAINS"]["actions"]
# Output: ["add_stain", "remove_stain", "reset"]
rules[character.game_version][character.health.type]["actions"]
# Output: ["damage", "heal", "reset"]
```

### Character Autogeneration

| Key                              | Description                                   |
| -------------------------------- | --------------------------------------------- |
| `CharacterClassPercentileChance` | Probability ranges for random class selection |

### Users

| Key                  | Values                                  | Description                                                                          |
| -------------------- | --------------------------------------- | ------------------------------------------------------------------------------------ |
| `UserRole`           | `ADMIN`, `STORYTELLER`, `PLAYER`        | Available user roles                                                                  |
| `IdentityProvider`   | `apple`, `google`, `discord`, `github`  | Providers accepted by [identity verification](identity.md)                            |
| `IdentityResolution` | `matched`, `linked`, `created`          | Resolution outcomes returned by [`identify()`](identity.md#resolution-order)      |

### Gameplay

| Key              | Description                     |
| ---------------- | ------------------------------- |
| `DiceSize`       | Available dice sizes for rolls  |
| `RollResultType` | Possible roll result categories |

### Assets

| Key               | Description                                |
| ----------------- | ------------------------------------------ |
| `AssetType`       | Types of uploadable assets                 |

## Example

```python
options_data = await options.get_options()

# Access company permission options
print(options_data["companies"]["PermissionManageCampaign"])
# Output: ["UNRESTRICTED", "STORYTELLER"]

print(options_data["companies"]["PermissionsGrantXP"])
# Output: ["UNRESTRICTED", "PLAYER", "STORYTELLER"]

# Access character options
print(options_data["characters"]["CharacterClass"])
# Output: ["VAMPIRE", "WEREWOLF", "HUNTER", "MORTAL", "MAGE", "GHOUL"]

print(options_data["characters"]["CharacterStatus"])
# Output: ["ALIVE", "DEAD", "ARCHIVED"]

# Access user roles
print(options_data["users"]["UserRole"])
# Output: ["ADMIN", "STORYTELLER", "PLAYER"]

# Access related blueprint URLs
print(options_data["characters"]["_related"]["vampire_clans"])
# Output: "https://api.valentina-noir.com/api/v1/companies/{company_id}/characterblueprint/vampireclans"
```

!!! tip "Caching"

    The options endpoint response is cached for 10 minutes. Consider caching these values client-side to reduce API calls, as these values rarely change.
