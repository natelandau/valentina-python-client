"""Testing utilities for downstream applications using vclient.

Requires the 'testing' extra: pip install vclient[testing]
"""

try:
    import polyfactory  # noqa: F401
except ImportError as e:
    msg = (
        "vclient.testing requires the 'testing' extra. "
        "Install it with: pip install vclient[testing]"
    )
    raise ImportError(msg) from e

from vclient._sync.testing import SyncFakeVClient
from vclient.testing._client import FakeVClient
from vclient.testing._factories import (
    AssetFactory,
    CampaignBookFactory,
    CampaignChapterFactory,
    CampaignExperienceFactory,
    CampaignFactory,
    CharacterConceptFactory,
    CharacterFactory,
    CharacterTraitFactory,
    CharacterTraitValueOptionsResponseFactory,
    ChargenSessionResponseFactory,
    CompanyFactory,
    CompanyPermissionsFactory,
    DeveloperFactory,
    DeveloperWithApiKeyFactory,
    DicerollFactory,
    DictionaryTermFactory,
    EdgeAndPerksFactory,
    HunterEdgeFactory,
    HunterEdgePerkFactory,
    InventoryItemFactory,
    MeDeveloperFactory,
    MeDeveloperWithApiKeyFactory,
    NewCompanyResponseFactory,
    NoteFactory,
    PerkFactory,
    QuickrollFactory,
    RollStatisticsFactory,
    SheetSectionFactory,
    SystemHealthFactory,
    TraitCategoryFactory,
    TraitFactory,
    UserFactory,
    VampireClanFactory,
    WerewolfAuspiceFactory,
    WerewolfGiftFactory,
    WerewolfRiteFactory,
    WerewolfTribeFactory,
)
from vclient.testing._routes import Routes, RouteSpec

__all__ = [
    "AssetFactory",
    "CampaignBookFactory",
    "CampaignChapterFactory",
    "CampaignExperienceFactory",
    "CampaignFactory",
    "CharacterConceptFactory",
    "CharacterFactory",
    "CharacterTraitFactory",
    "CharacterTraitValueOptionsResponseFactory",
    "ChargenSessionResponseFactory",
    "CompanyFactory",
    "CompanyPermissionsFactory",
    "DeveloperFactory",
    "DeveloperWithApiKeyFactory",
    "DicerollFactory",
    "DictionaryTermFactory",
    "EdgeAndPerksFactory",
    "FakeVClient",
    "HunterEdgeFactory",
    "HunterEdgePerkFactory",
    "InventoryItemFactory",
    "MeDeveloperFactory",
    "MeDeveloperWithApiKeyFactory",
    "NewCompanyResponseFactory",
    "NoteFactory",
    "PerkFactory",
    "QuickrollFactory",
    "RollStatisticsFactory",
    "RouteSpec",
    "Routes",
    "SheetSectionFactory",
    "SyncFakeVClient",
    "SystemHealthFactory",
    "TraitCategoryFactory",
    "TraitFactory",
    "UserFactory",
    "VampireClanFactory",
    "WerewolfAuspiceFactory",
    "WerewolfGiftFactory",
    "WerewolfRiteFactory",
    "WerewolfTribeFactory",
]
