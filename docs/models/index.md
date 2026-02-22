---
icon: lucide/database
---

# Models

Every API request and response uses strongly-typed Pydantic models with automatic validation. Import them from `vclient.models`.

```python
from vclient.models import Company, User, Campaign, Character
```

## Naming Conventions

Models follow a consistent naming pattern that indicates their purpose.

| Pattern          | Purpose        | Example         |
| ---------------- | -------------- | --------------- |
| `{Entity}`       | Response model | `Company`       |
| `{Entity}Create` | Create request | `CompanyCreate` |
| `{Entity}Update` | Update request | `CompanyUpdate` |

## Request and Response Models

Use `Create` and `Update` models to build requests, and receive entity models in responses. All models provide full type hints for IDE autocomplete and static type checking.

```python
from vclient import VClient
from vclient.models import UserCreate, User

async with VClient() as client:
    # Build a request with a Create model
    request = UserCreate(
        name="Alice Johnson",
        email="alice@example.com",
        role="PLAYER",
        requesting_user_id="admin_id",
    )

    # Send the request and receive a typed response model
    users = client.users(company_id="company_123")
    user: User = await users.create(request)

    # Access fields with full type hints
    print(f"Created user: {user.name} (ID: {user.id})")
    print(f"Role: {user.role}")
```

## Enumerations

The API uses `Literal` type constants to represent fixed sets of values. Import them from `vclient.constants`.

```python
from vclient.constants import CharacterClass, UserRole, GameVersion
```

### Character Enums

| Enum                     | Values                                                            |
| ------------------------ | ----------------------------------------------------------------- |
| `CharacterClass`         | `VAMPIRE`, `WEREWOLF`, `MAGE`, `HUNTER`, `GHOUL`, `MORTAL`        |
| `CharacterType`          | `PLAYER`, `NPC`, `STORYTELLER`, `DEVELOPER`                       |
| `CharacterStatus`        | `ALIVE`, `DEAD`                                                   |
| `CharacterInventoryType` | `BOOK`, `CONSUMABLE`, `ENCHANTED`, `EQUIPMENT`, `OTHER`, `WEAPON` |

### Game Enums

| Enum          | Values     |
| ------------- | ---------- |
| `GameVersion` | `V4`, `V5` |

### User and Permission Enums

| Enum                         | Values                                           |
| ---------------------------- | ------------------------------------------------ |
| `UserRole`                   | `ADMIN`, `STORYTELLER`, `PLAYER`                 |
| `PermissionLevel`            | `USER`, `ADMIN`, `OWNER`, `REVOKE`               |
| `ManageCampaignPermission`   | `UNRESTRICTED`, `STORYTELLER`                    |
| `GrantXPPermission`          | `UNRESTRICTED`, `PLAYER`, `STORYTELLER`          |
| `FreeTraitChangesPermission` | `UNRESTRICTED`, `WITHIN_24_HOURS`, `STORYTELLER` |

### Dice Roll Enums

| Enum             | Values                                             |
| ---------------- | -------------------------------------------------- |
| `DiceSize`       | `4`, `6`, `8`, `10`, `20`, `100`                   |
| `RollResultType` | `SUCCESS`, `FAILURE`, `BOTCH`, `CRITICAL`, `OTHER` |

### Werewolf Enums

| Enum             | Values                     |
| ---------------- | -------------------------- |
| `WerewolfRenown` | `HONOR`, `GLORY`, `WISDOM` |

### Hunter Enums

| Enum             | Values                                                                 |
| ---------------- | ---------------------------------------------------------------------- |
| `HunterCreed`    | `ENTREPRENEURIAL`, `FAITHFUL`, `INQUISITIVE`, `MARTIAL`, `UNDERGROUND` |
| `HunterEdgeType` | `ASSETS`, `APTITUDES`, `ENDOWMENTS`                                    |

### Auto-Generation Enums

| Enum                     | Values                                         |
| ------------------------ | ---------------------------------------------- |
| `AutoGenExperienceLevel` | `NEW`, `INTERMEDIATE`, `ADVANCED`, `ELITE`     |
| `AbilityFocus`           | `JACK_OF_ALL_TRADES`, `BALANCED`, `SPECIALIST` |

### Asset Enums

| Enum              | Values                                                                                   |
| ----------------- | ---------------------------------------------------------------------------------------- |
| `AssetType`       | `image`, `text`, `audio`, `video`, `document`, `archive`, `other`                        |
| `AssetParentType` | `character`, `campaign`, `campaignbook`, `campaignchapter`, `user`, `company`, `unknown` |

### Trait Enums

| Enum                    | Values                                          |
| ----------------------- | ----------------------------------------------- |
| `SpecialtyType`         | `ACTION`, `OTHER`, `PASSIVE`, `RITUAL`, `SPELL` |
| `BlueprintTraitOrderBy` | `NAME`, `SHEET`                                 |
| `TraitModifyCurrency`   | `XP`, `STARTING_POINTS`, `NO_COST`              |
