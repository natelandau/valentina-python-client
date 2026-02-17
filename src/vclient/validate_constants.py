"""Validate client constants against the API options endpoint.

Compare the Literal type constants defined in constants.py against the
values returned by the API's /options endpoint to detect drift between
client and server.
"""

from __future__ import annotations

import typing
from dataclasses import dataclass, field

from vclient import constants


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


def validate(api_options: dict[str, dict[str, list | dict]]) -> ValidationResult:
    """Compare local Literal constants against values from the API options endpoint.

    Args:
        api_options: The raw dictionary returned by OptionsService.get_options().

    Returns:
        ValidationResult with is_valid=True if all constants match, otherwise
        populated with mismatches and unmapped API options.
    """
    mismatches: list[ConstantMismatch] = []
    mapped_api_options: set[tuple[str, str]] = set()

    for constant_name, mapping in CONSTANT_MAP.items():
        mapped_api_options.add((mapping.api_category, mapping.api_option))

        local_values = set(typing.get_args(getattr(constants, constant_name)))

        category_data = api_options.get(mapping.api_category, {})
        api_values_raw = category_data.get(mapping.api_option)
        if api_values_raw is None:
            mismatches.append(
                ConstantMismatch(
                    constant_name=constant_name,
                    api_category=mapping.api_category,
                    api_option=mapping.api_option,
                    missing_from_client=set(),
                    extra_in_client=local_values,
                )
            )
            continue

        api_values = set(api_values_raw)
        missing_from_client = api_values - local_values
        extra_in_client = local_values - api_values

        if missing_from_client or extra_in_client:
            mismatches.append(
                ConstantMismatch(
                    constant_name=constant_name,
                    api_category=mapping.api_category,
                    api_option=mapping.api_option,
                    missing_from_client=missing_from_client,
                    extra_in_client=extra_in_client,
                )
            )

    unmapped_api_options: dict[str, list[str]] = {}
    for category, options in api_options.items():
        if not isinstance(options, dict):
            continue
        for option_name, option_values in options.items():
            if option_name.startswith("_"):
                continue
            if not isinstance(option_values, list):
                continue
            if (category, option_name) not in mapped_api_options:
                unmapped_api_options.setdefault(category, []).append(option_name)

    is_valid = len(mismatches) == 0 and len(unmapped_api_options) == 0

    return ValidationResult(
        is_valid=is_valid,
        mismatches=mismatches,
        unmapped_api_options=unmapped_api_options,
    )
