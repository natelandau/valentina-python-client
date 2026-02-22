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
    "AssetParentType": ConstantMapping("assets", "AssetParentType"),
    "AssetType": ConstantMapping("assets", "AssetType"),
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


def _print_status_lines(mismatched_names: set[str]) -> None:
    """Print OK/FAIL status line for each constant in the mapping table."""
    for constant_name in sorted(CONSTANT_MAP):
        status = "FAIL" if constant_name in mismatched_names else "OK  "
        print(f"  {status}  {constant_name}")


def _print_mismatches(mismatches: list[ConstantMismatch]) -> None:
    """Print detailed mismatch information for each failing constant."""
    print()
    print("-" * 60)
    print("Mismatches:")
    print("-" * 60)
    for mismatch in mismatches:
        print(f"\n  {mismatch.constant_name}")
        print(f"    API: {mismatch.api_category}.{mismatch.api_option}")
        if mismatch.missing_from_client:
            print(f"    Missing from client: {sorted(mismatch.missing_from_client)}")
        if mismatch.extra_in_client:
            print(f"    Extra in client:     {sorted(mismatch.extra_in_client)}")


def _print_unmapped(unmapped_api_options: dict[str, list[str]]) -> None:
    """Print API options that have no corresponding local constant."""
    print()
    print("-" * 60)
    print("Unmapped API options (no local constant):")
    print("-" * 60)
    for category, options in sorted(unmapped_api_options.items()):
        for option in sorted(options):
            print(f"  {category}.{option}")


def _build_summary(
    matched_count: int,
    total: int,
    mismatch_count: int,
    unmapped_api_options: dict[str, list[str]],
) -> str:
    """Build the final summary line for the report."""
    if mismatch_count == 0 and not unmapped_api_options:
        return f"  {matched_count}/{total} constants in sync"

    summary_parts: list[str] = []
    if mismatch_count:
        summary_parts.append(f"{mismatch_count} mismatch(es)")
    if unmapped_api_options:
        unmapped_count = sum(len(v) for v in unmapped_api_options.values())
        summary_parts.append(f"{unmapped_count} unmapped API option(s)")
    return f"  {matched_count}/{total} constants in sync, {', '.join(summary_parts)}"


def print_report(result: ValidationResult) -> None:
    """Print a human-readable validation report to stdout.

    Args:
        result: The ValidationResult from validate().
    """
    total = len(CONSTANT_MAP)
    mismatch_count = len(result.mismatches)
    matched_count = total - mismatch_count
    mismatched_names = {m.constant_name for m in result.mismatches}

    print()
    print("=" * 60)
    print("Constants Validation Report")
    print("=" * 60)

    _print_status_lines(mismatched_names)

    if result.mismatches:
        _print_mismatches(result.mismatches)

    if result.unmapped_api_options:
        _print_unmapped(result.unmapped_api_options)

    print()
    print("=" * 60)
    print(_build_summary(matched_count, total, mismatch_count, result.unmapped_api_options))
    print("=" * 60)
    print()
