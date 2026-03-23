"""Tests for polyfactory model factories."""

import pytest

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
    InventoryItemFactory,
    MeDeveloperFactory,
    MeDeveloperWithApiKeyFactory,
    NewCompanyResponseFactory,
    NoteFactory,
    QuickrollFactory,
    RollStatisticsFactory,
    SheetSectionFactory,
    SystemHealthFactory,
    TraitCategoryFactory,
    TraitFactory,
    UserFactory,
    VampireClanFactory,
    WerewolfAuspiceFactory,
    WerewolfTribeFactory,
)


class TestFactoriesBuildValidModels:
    """Each factory should produce a valid model instance."""

    @pytest.mark.parametrize(
        "factory_cls",
        [
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
            InventoryItemFactory,
            MeDeveloperFactory,
            MeDeveloperWithApiKeyFactory,
            NewCompanyResponseFactory,
            NoteFactory,
            QuickrollFactory,
            RollStatisticsFactory,
            SheetSectionFactory,
            SystemHealthFactory,
            TraitCategoryFactory,
            TraitFactory,
            UserFactory,
            VampireClanFactory,
            WerewolfAuspiceFactory,
            WerewolfTribeFactory,
        ],
    )
    def test_factory_builds_valid_instance(self, factory_cls):
        """Each factory should produce a valid instance of its model."""
        instance = factory_cls.build()
        assert instance is not None
        assert isinstance(instance, factory_cls.__model__)

    def test_factory_accepts_overrides(self):
        """Factories should accept field overrides."""
        campaign = CampaignFactory.build(name="Custom Name")
        assert campaign.name == "Custom Name"

    def test_factory_batch(self):
        """Factories should support batch creation."""
        campaigns = CampaignFactory.batch(3)
        assert len(campaigns) == 3
        assert all(isinstance(c, CampaignFactory.__model__) for c in campaigns)
