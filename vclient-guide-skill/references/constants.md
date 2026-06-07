# vclient Constants Reference

All Literal types, configuration defaults, and header constants.

## Literal Types (API Enums)

These are the valid values for typed fields throughout the models. Import from `vclient.constants`.

### Character Types

```python
CharacterClass = Literal["VAMPIRE", "WEREWOLF", "MAGE", "HUNTER", "GHOUL", "MORTAL"]
CharacterType = Literal["PLAYER", "NPC", "STORYTELLER"]
CharacterStatus = Literal["ALIVE", "DEAD"]
GameVersion = Literal["V4", "V5"]
```

### Character Creation / Autogen

```python
AutoGenExperienceLevel = Literal["NEW", "INTERMEDIATE", "ADVANCED", "ELITE"]
AbilityFocus = Literal["JACK_OF_ALL_TRADES", "BALANCED", "SPECIALIST"]
```

### Character Inventory

```python
CharacterInventoryType = Literal["BOOK", "CONSUMABLE", "ENCHANTED", "EQUIPMENT", "OTHER", "WEAPON"]
```

### Traits

```python
TraitModifyCurrency = Literal["XP", "STARTING_POINTS", "NO_COST"]
BlueprintTraitOrderBy = Literal["NAME", "SHEET"]
SpecialtyType = Literal["ACTION", "OTHER", "PASSIVE", "RITUAL", "SPELL"]
```

### Werewolf

```python
WerewolfRenown = Literal["HONOR", "GLORY", "WISDOM"]
```

### Hunter

```python
HunterCreed = Literal["ENTREPRENEURIAL", "FAITHFUL", "INQUISITIVE", "MARTIAL", "UNDERGROUND"]
HunterEdgeType = Literal["ASSETS", "APTITUDES", "ENDOWMENTS"]
```

### Dice

```python
DiceSize = Literal[4, 6, 8, 10, 20, 100]
RollResultType = Literal["SUCCESS", "FAILURE", "BOTCH", "CRITICAL", "OTHER"]
```

### Users & Permissions

```python
UserRole = Literal["ADMIN", "STORYTELLER", "PLAYER", "UNAPPROVED", "DEACTIVATED"]
PermissionLevel = Literal["USER", "ADMIN", "OWNER", "REVOKE"]
```

### Identity

These constants are client-side only and are **not** validated against the `/options` endpoint.

```python
IdentityProvider = Literal["apple", "google", "discord", "github"]
IdentityResolutionType = Literal["matched", "linked", "created"]
```

`IdentityProvider` is the credential source passed to `IdentityService.identify()` and `UsersService.link_identity()`. `IdentityResolutionType` is the outcome reported in `IdentityResolution.resolution`.

### Company Settings Permissions

```python
ManageCampaignPermission = Literal["UNRESTRICTED", "STORYTELLER"]
ManageNPCPermission = Literal["UNRESTRICTED", "STORYTELLER"]
GrantXPPermission = Literal["UNRESTRICTED", "PLAYER", "STORYTELLER"]
FreeTraitChangesPermission = Literal["UNRESTRICTED", "WITHIN_24_HOURS", "STORYTELLER"]
RecoupXPPermission = Literal["UNRESTRICTED", "DENIED", "WITHIN_SESSION"]
```

### Assets

```python
AssetType = Literal["image", "text", "audio", "video", "document", "archive", "other"]
```

### Include Parameters

```python
CharacterInclude = Literal["traits", "inventory", "notes", "assets"]
BookInclude = Literal["chapters", "notes", "assets"]
ChapterInclude = Literal["notes", "assets"]
UserInclude = Literal["quickrolls", "notes", "assets", "characters"]
```

### Audit Logs

```python
AuditEntityType = Literal[
    "ASSET", "BOOK", "CAMPAIGN", "CHAPTER", "CHARACTER",
    "CHARACTER_INVENTORY", "CHARACTER_TRAIT", "CHARGEN_SESSION",
    "COMPANY", "DEVELOPER", "DICTIONARY_TERM", "EXPERIENCE",
    "NOTE", "QUICKROLL", "USER",
]
AuditOperation = Literal["CREATE", "UPDATE", "DELETE"]
AuditLogInclude = Literal["request_details"]
```

### Server Logs

```python
LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
```

## Configuration Constants

```python
# Defaults
DEFAULT_TIMEOUT = 30.0          # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0       # seconds
DEFAULT_PAGE_LIMIT = 10
MAX_PAGE_LIMIT = 100             # cap for most list endpoints
MAX_REFERENCE_PAGE_LIMIT = 1000  # cap for reference/catalog endpoints (blueprint, dictionary)
DEFAULT_LOG_TAIL_LIMIT = 100
MIN_LOG_TAIL_LIMIT = 1
MAX_LOG_TAIL_LIMIT = 500
DEFAULT_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
IDEMPOTENT_HTTP_METHODS = frozenset({"GET", "PUT", "DELETE"})

# Headers
API_KEY_HEADER = "X-API-KEY"
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"
ON_BEHALF_OF_HEADER = "On-Behalf-Of"
REQUEST_ID_HEADER = "X-Request-Id"
RATE_LIMIT_HEADER = "RateLimit"
RATE_LIMIT_POLICY_HEADER = "RateLimit-Policy"

# Environment Variables
ENV_BASE_URL = "VALENTINA_CLIENT_BASE_URL"
ENV_API_KEY = "VALENTINA_CLIENT_API_KEY"
ENV_DEFAULT_COMPANY_ID = "VALENTINA_CLIENT_DEFAULT_COMPANY_ID"
```
