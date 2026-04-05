"""Polyfactory model factories for all vclient response models."""

from polyfactory.factories.pydantic_factory import ModelFactory

from vclient.models import (
    Asset,
    BulkAssignTraitFailure,
    BulkAssignTraitResponse,
    BulkAssignTraitSuccess,
    Campaign,
    CampaignBook,
    CampaignChapter,
    Character,
    CharacterConcept,
    CharacterDetail,
    CharacterFullSheet,
    CharacterTrait,
    CharacterTraitValueOptionsResponse,
    Company,
    CompanyPermissions,
    Developer,
    DeveloperWithApiKey,
    Diceroll,
    DictionaryTerm,
    FullSheetTraitCategory,
    FullSheetTraitSection,
    FullSheetTraitSubcategory,
    GitHubProfile,
    GoogleProfile,
    InventoryItem,
    MeDeveloper,
    MeDeveloperWithApiKey,
    NewCompanyResponse,
    Note,
    Quickroll,
    RollStatistics,
    SheetSection,
    SystemHealth,
    Trait,
    TraitCategory,
    TraitSubcategory,
    User,
    VampireClan,
    WerewolfAuspice,
    WerewolfTribe,
)
from vclient.models.character_autogen import ChargenSessionResponse
from vclient.models.users import CampaignExperience


class AssetFactory(ModelFactory[Asset]):
    __model__ = Asset
    __use_defaults__ = True


class BulkAssignTraitFailureFactory(ModelFactory[BulkAssignTraitFailure]):
    __model__ = BulkAssignTraitFailure
    __use_defaults__ = True


class BulkAssignTraitResponseFactory(ModelFactory[BulkAssignTraitResponse]):
    __model__ = BulkAssignTraitResponse
    __use_defaults__ = True


class BulkAssignTraitSuccessFactory(ModelFactory[BulkAssignTraitSuccess]):
    __model__ = BulkAssignTraitSuccess
    __use_defaults__ = True


class CampaignFactory(ModelFactory[Campaign]):
    __model__ = Campaign
    __use_defaults__ = True


class CampaignBookFactory(ModelFactory[CampaignBook]):
    __model__ = CampaignBook
    __use_defaults__ = True


class CampaignChapterFactory(ModelFactory[CampaignChapter]):
    __model__ = CampaignChapter
    __use_defaults__ = True


class CampaignExperienceFactory(ModelFactory[CampaignExperience]):
    __model__ = CampaignExperience
    __use_defaults__ = True


class CharacterFactory(ModelFactory[Character]):
    __model__ = Character
    __use_defaults__ = True


class CharacterDetailFactory(ModelFactory[CharacterDetail]):
    __model__ = CharacterDetail
    __use_defaults__ = True


class CharacterConceptFactory(ModelFactory[CharacterConcept]):
    __model__ = CharacterConcept
    __use_defaults__ = True


class CharacterFullSheetFactory(ModelFactory[CharacterFullSheet]):
    __model__ = CharacterFullSheet
    __use_defaults__ = True


class CharacterTraitFactory(ModelFactory[CharacterTrait]):
    __model__ = CharacterTrait
    __use_defaults__ = True


class CharacterTraitValueOptionsResponseFactory(
    ModelFactory[CharacterTraitValueOptionsResponse],
):
    __model__ = CharacterTraitValueOptionsResponse
    __use_defaults__ = True


class ChargenSessionResponseFactory(ModelFactory[ChargenSessionResponse]):
    __model__ = ChargenSessionResponse
    __use_defaults__ = True


class CompanyFactory(ModelFactory[Company]):
    __model__ = Company
    __use_defaults__ = True


class CompanyPermissionsFactory(ModelFactory[CompanyPermissions]):
    __model__ = CompanyPermissions
    __use_defaults__ = True


class DeveloperFactory(ModelFactory[Developer]):
    __model__ = Developer
    __use_defaults__ = True


class DeveloperWithApiKeyFactory(ModelFactory[DeveloperWithApiKey]):
    __model__ = DeveloperWithApiKey
    __use_defaults__ = True


class DicerollFactory(ModelFactory[Diceroll]):
    __model__ = Diceroll
    __use_defaults__ = True


class DictionaryTermFactory(ModelFactory[DictionaryTerm]):
    __model__ = DictionaryTerm
    __use_defaults__ = True


class FullSheetTraitCategoryFactory(ModelFactory[FullSheetTraitCategory]):
    __model__ = FullSheetTraitCategory
    __use_defaults__ = True


class FullSheetTraitSectionFactory(ModelFactory[FullSheetTraitSection]):
    __model__ = FullSheetTraitSection
    __use_defaults__ = True


class FullSheetTraitSubcategoryFactory(ModelFactory[FullSheetTraitSubcategory]):
    __model__ = FullSheetTraitSubcategory
    __use_defaults__ = True


class GitHubProfileFactory(ModelFactory[GitHubProfile]):
    __model__ = GitHubProfile
    __use_defaults__ = True


class GoogleProfileFactory(ModelFactory[GoogleProfile]):
    __model__ = GoogleProfile
    __use_defaults__ = True


class InventoryItemFactory(ModelFactory[InventoryItem]):
    __model__ = InventoryItem
    __use_defaults__ = True


class MeDeveloperFactory(ModelFactory[MeDeveloper]):
    __model__ = MeDeveloper
    __use_defaults__ = True


class MeDeveloperWithApiKeyFactory(ModelFactory[MeDeveloperWithApiKey]):
    __model__ = MeDeveloperWithApiKey
    __use_defaults__ = True


class NewCompanyResponseFactory(ModelFactory[NewCompanyResponse]):
    __model__ = NewCompanyResponse
    __use_defaults__ = True


class NoteFactory(ModelFactory[Note]):
    __model__ = Note
    __use_defaults__ = True


class QuickrollFactory(ModelFactory[Quickroll]):
    __model__ = Quickroll
    __use_defaults__ = True


class RollStatisticsFactory(ModelFactory[RollStatistics]):
    __model__ = RollStatistics
    __use_defaults__ = True


class SheetSectionFactory(ModelFactory[SheetSection]):
    __model__ = SheetSection
    __use_defaults__ = True


class SystemHealthFactory(ModelFactory[SystemHealth]):
    __model__ = SystemHealth
    __use_defaults__ = True


class TraitCategoryFactory(ModelFactory[TraitCategory]):
    __model__ = TraitCategory
    __use_defaults__ = True


class TraitSubcategoryFactory(ModelFactory[TraitSubcategory]):
    __model__ = TraitSubcategory
    __use_defaults__ = True


class TraitFactory(ModelFactory[Trait]):
    __model__ = Trait
    __use_defaults__ = True


class UserFactory(ModelFactory[User]):
    __model__ = User
    __use_defaults__ = True
    role = "PLAYER"


class VampireClanFactory(ModelFactory[VampireClan]):
    __model__ = VampireClan
    __use_defaults__ = True


class WerewolfAuspiceFactory(ModelFactory[WerewolfAuspice]):
    __model__ = WerewolfAuspice
    __use_defaults__ = True


class WerewolfTribeFactory(ModelFactory[WerewolfTribe]):
    __model__ = WerewolfTribe
    __use_defaults__ = True


__all__ = [
    "AssetFactory",
    "BulkAssignTraitFailureFactory",
    "BulkAssignTraitResponseFactory",
    "BulkAssignTraitSuccessFactory",
    "CampaignBookFactory",
    "CampaignChapterFactory",
    "CampaignExperienceFactory",
    "CampaignFactory",
    "CharacterConceptFactory",
    "CharacterDetailFactory",
    "CharacterFactory",
    "CharacterFullSheetFactory",
    "CharacterTraitFactory",
    "CharacterTraitValueOptionsResponseFactory",
    "ChargenSessionResponseFactory",
    "CompanyFactory",
    "CompanyPermissionsFactory",
    "DeveloperFactory",
    "DeveloperWithApiKeyFactory",
    "DicerollFactory",
    "DictionaryTermFactory",
    "FullSheetTraitCategoryFactory",
    "FullSheetTraitSectionFactory",
    "FullSheetTraitSubcategoryFactory",
    "GitHubProfileFactory",
    "GoogleProfileFactory",
    "InventoryItemFactory",
    "MeDeveloperFactory",
    "MeDeveloperWithApiKeyFactory",
    "NewCompanyResponseFactory",
    "NoteFactory",
    "QuickrollFactory",
    "RollStatisticsFactory",
    "SheetSectionFactory",
    "SystemHealthFactory",
    "TraitCategoryFactory",
    "TraitFactory",
    "TraitSubcategoryFactory",
    "UserFactory",
    "VampireClanFactory",
    "WerewolfAuspiceFactory",
    "WerewolfTribeFactory",
]
