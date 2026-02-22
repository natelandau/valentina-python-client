---
icon: lucide/database
---

# Response Models

All API responses return as strongly-typed Pydantic models with automatic validation. Import models from `vclient.models` to access request and response types.

```python
from vclient.models import Company, User, Campaign, Character
```

!!! info "Type Safety"

    All models provide full type hints for IDE autocomplete and static type checking with mypy or pyright.

## Using Models

Models serve two primary purposes: creating requests and handling responses.

```python
from vclient import users_service
from vclient.models import UserCreate, User

# Create a request model
request = UserCreate(
    name="Alice Johnson",
    email="alice@example.com",
    role="PLAYER",
    requesting_user_id="admin_id"
)

# Send request and receive response model
users = users_service(company_id="company_123")
user: User = await users.create(request)

# Access response data with full type hints
print(f"Created user: {user.name} (ID: {user.id})")
print(f"Role: {user.role}")
```

## Enumerations

### Character Enums

| Enum              | Values                                         |
| ----------------- | ---------------------------------------------- |
| `CharacterClass`  | VAMPIRE, WEREWOLF, MAGE, HUNTER, GHOUL, MORTAL |
| `CharacterType`   | PLAYER, NPC, STORYTELLER, DEVELOPER            |
| `CharacterStatus` | ALIVE, DEAD                                    |
| `GameVersion`     | V4, V5                                         |

### User Enums

| Enum              | Values                     |
| ----------------- | -------------------------- |
| `UserRole`        | ADMIN, STORYTELLER, PLAYER |
| `PermissionLevel` | USER, ADMIN, OWNER, REVOKE |

### Other Enums

| Enum             | Values                            |
| ---------------- | --------------------------------- |
| `WerewolfRenown` | HONOR, GLORY, WISDOM              |
| `HunterEdgeType` | ASSETS, APTITUDES, ENDOWMENTS     |
| `DiceSize`       | 4, 6, 8, 10, 20, 100             |
| `RollResultType` | SUCCESS, FAILURE, BOTCH, CRITICAL |
