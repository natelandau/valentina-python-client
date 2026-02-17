"""Validate client constants against the API options endpoint.

Compare the Literal type constants defined in constants.py against the
values returned by the API's /options endpoint to detect drift between
client and server.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConstantMapping:
    """Map a local constant name to its location in the API options response.

    Args:
        api_category: Top-level key in the options response (e.g., "characters").
        api_option: Option name within that category (e.g., "CharacterClass").
    """

    api_category: str
    api_option: str


@dataclass
class ConstantMismatch:
    """Record of a single constant that differs between client and API.

    Args:
        constant_name: The local constant name in constants.py.
        api_category: The API category this constant maps to.
        api_option: The API option name this constant maps to.
        missing_from_client: Values present in the API but not in the local Literal.
        extra_in_client: Values present in the local Literal but not in the API.
    """

    constant_name: str
    api_category: str
    api_option: str
    missing_from_client: set[str | int] = field(default_factory=set)
    extra_in_client: set[str | int] = field(default_factory=set)


@dataclass
class ValidationResult:
    """Result of validating client constants against the API.

    Args:
        is_valid: True if all mapped constants match and no unmapped API options exist.
        mismatches: Constants with value differences between client and API.
        unmapped_api_options: API option keys that have no corresponding local constant.
    """

    is_valid: bool
    mismatches: list[ConstantMismatch] = field(default_factory=list)
    unmapped_api_options: dict[str, list[str]] = field(default_factory=dict)


CONSTANT_MAP: dict[str, ConstantMapping] = {
    "AbilityFocus": ConstantMapping("characters", "AbilityFocus"),
    "AutoGenExperienceLevel": ConstantMapping("characters", "AutoGenExperienceLevel"),
    "BlueprintTraitOrderBy": ConstantMapping("characters", "BlueprintTraitOrderBy"),
    "CharacterClass": ConstantMapping("characters", "CharacterClass"),
    "CharacterInventoryType": ConstantMapping("characters", "InventoryItemType"),
    "CharacterStatus": ConstantMapping("characters", "CharacterStatus"),
    "CharacterType": ConstantMapping("characters", "CharacterType"),
    "DiceSize": ConstantMapping("gameplay", "DiceSize"),
    "FreeTraitChangesPermission": ConstantMapping("companies", "PermissionsFreeTraitChanges"),
    "GameVersion": ConstantMapping("characters", "GameVersion"),
    "GrantXPPermission": ConstantMapping("companies", "PermissionsGrantXP"),
    "HunterCreed": ConstantMapping("characters", "HunterCreed"),
    "HunterEdgeType": ConstantMapping("characters", "HunterEdgeType"),
    "ManageCampaignPermission": ConstantMapping("companies", "PermissionManageCampaign"),
    "PermissionLevel": ConstantMapping("companies", "CompanyPermission"),
    "RollResultType": ConstantMapping("gameplay", "RollResultType"),
    "S3AssetParentType": ConstantMapping("assets", "AssetParentType"),
    "S3AssetType": ConstantMapping("assets", "AssetType"),
    "SpecialtyType": ConstantMapping("characters", "SpecialtyType"),
    "TraitModifyCurrency": ConstantMapping("characters", "TraitModifyCurrency"),
    "UserRole": ConstantMapping("users", "UserRole"),
    "WerewolfRenown": ConstantMapping("characters", "WerewolfRenown"),
}
