"""Constants for the API client."""

from typing import Literal

# Authentication
API_KEY_HEADER = "X-API-KEY"

# Environment variable names
ENV_BASE_URL = "VALENTINA_CLIENT_BASE_URL"
ENV_API_KEY = "VALENTINA_CLIENT_API_KEY"
ENV_DEFAULT_COMPANY_ID = "VALENTINA_CLIENT_DEFAULT_COMPANY_ID"

# Request defaults
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_RETRY_STATUSES: frozenset[int] = frozenset({429, 500, 502, 503, 504})
IDEMPOTENT_HTTP_METHODS: frozenset[str] = frozenset({"GET", "PUT", "DELETE"})

# Pagination defaults
DEFAULT_PAGE_LIMIT = 10
MAX_PAGE_LIMIT = 100

# HTTP Status Code Ranges (5xx Server Errors)
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_600_UPPER_BOUND = 600

# Idempotency
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"

# Rate Limiting Headers
RATE_LIMIT_HEADER = "RateLimit"
RATE_LIMIT_POLICY_HEADER = "RateLimit-Policy"

# Valentina API Constants
AbilityFocus = Literal["JACK_OF_ALL_TRADES", "BALANCED", "SPECIALIST"]
AutoGenExperienceLevel = Literal["NEW", "INTERMEDIATE", "ADVANCED", "ELITE"]
CharacterClass = Literal["VAMPIRE", "WEREWOLF", "MAGE", "HUNTER", "GHOUL", "MORTAL"]
CharacterInventoryType = Literal[
    "BOOK",
    "CONSUMABLE",
    "ENCHANTED",
    "EQUIPMENT",
    "OTHER",
    "WEAPON",
]
CharacterStatus = Literal["ALIVE", "DEAD"]
CharacterType = Literal["PLAYER", "NPC", "STORYTELLER", "DEVELOPER"]
DiceSize = Literal[4, 6, 8, 10, 20, 100]
FreeTraitChangesPermission = Literal["UNRESTRICTED", "WITHIN_24_HOURS", "STORYTELLER"]
GameVersion = Literal["V4", "V5"]
GrantXPPermission = Literal["UNRESTRICTED", "PLAYER", "STORYTELLER"]
HunterCreed = Literal["ENTREPRENEURIAL", "FAITHFUL", "INQUISITIVE", "MARTIAL", "UNDERGROUND"]
HunterEdgeType = Literal["ASSETS", "APTITUDES", "ENDOWMENTS"]
ManageCampaignPermission = Literal["UNRESTRICTED", "STORYTELLER"]
PermissionLevel = Literal["USER", "ADMIN", "OWNER", "REVOKE"]
RollResultType = Literal["SUCCESS", "FAILURE", "BOTCH", "CRITICAL", "OTHER"]
AssetParentType = Literal[
    "character", "campaign", "campaignbook", "campaignchapter", "user", "company", "unknown"
]
AssetType = Literal["image", "text", "audio", "video", "document", "archive", "other"]
SpecialtyType = Literal["ACTION", "OTHER", "PASSIVE", "RITUAL", "SPELL"]
UserRole = Literal["ADMIN", "STORYTELLER", "PLAYER"]
WerewolfRenown = Literal["HONOR", "GLORY", "WISDOM"]
BlueprintTraitOrderBy = Literal["NAME", "SHEET"]
TraitModifyCurrency = Literal["XP", "STARTING_POINTS", "NO_COST"]
