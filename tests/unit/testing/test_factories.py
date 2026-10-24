"""Tests for polyfactory model factories."""

import pytest

from vclient.models import CounterTracker, DamageTracker, Health, StainsTracker
from vclient.testing._factories import (
    AssetFactory,
    CampaignBookFactory,
    CampaignChapterFactory,
    CampaignExperienceFactory,
    CampaignFactory,
    CharacterConceptFactory,
    CharacterDetailFactory,
    CharacterFactory,
    CharacterTraitFactory,
    CharacterTraitValueOptionsResponseFactory,
    ChargenSessionResponseFactory,
    CompanyFactory,
    CompanyPermissionsFactory,
    CounterTrackerFactory,
    DamageTrackerFactory,
    DeveloperFactory,
    DeveloperWithApiKeyFactory,
    DicerollFactory,
    DictionaryTermFactory,
    HealthFactory,
    HealthLevelFactory,
    IdentityResolutionFactory,
    InventoryItemFactory,
    MeDeveloperFactory,
    MeDeveloperWithApiKeyFactory,
    NewCompanyResponseFactory,
    NoteFactory,
    QuickrollFactory,
    RollStatisticsFactory,
    SheetSectionFactory,
    StainsTrackerFactory,
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
            IdentityResolutionFactory,
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


class TestTrackerFactories:
    """Tracker and health factories should round-trip through their models."""

    @pytest.mark.parametrize(
        "factory_cls",
        [
            CounterTrackerFactory,
            DamageTrackerFactory,
            StainsTrackerFactory,
            HealthLevelFactory,
            HealthFactory,
        ],
    )
    def test_tracker_factory_round_trips(self, factory_cls):
        """Verify built instances survive JSON serialization and validation."""
        instance = factory_cls.build()
        model = factory_cls.__model__
        assert model.model_validate(instance.model_dump(mode="json")) == instance

    @pytest.mark.parametrize("factory_cls", [CharacterTraitFactory, CharacterFactory])
    def test_models_with_tracker_fields_round_trip(self, factory_cls):
        """Verify built characters and traits survive JSON serialization and validation."""
        for _ in range(20):
            instance = factory_cls.build()
            model = factory_cls.__model__
            assert model.model_validate(instance.model_dump(mode="json")) == instance

    @pytest.mark.parametrize("factory_cls", [CharacterFactory, CharacterDetailFactory])
    def test_character_factory_always_has_health(self, factory_cls):
        """Verify fake characters carry health, as the API always sends it."""
        for _ in range(20):
            assert isinstance(factory_cls.build().health, Health)

    def test_character_trait_factory_varies_tracker(self):
        """Verify fake traits produce more than one tracker variant."""
        kinds = {type(CharacterTraitFactory.build().tracker) for _ in range(200)}
        assert {CounterTracker, DamageTracker, StainsTracker} <= kinds

    @pytest.mark.parametrize("factory_cls", [DamageTrackerFactory, HealthFactory])
    def test_damage_factory_boxes_match_size(self, factory_cls):
        """Verify fake damage tracks render one box per point of size."""
        for _ in range(20):
            tracker = factory_cls.build()
            assert len(tracker.boxes) == tracker.size

    @pytest.mark.parametrize("factory_cls", [DamageTrackerFactory, HealthFactory])
    def test_damage_factory_marks_match_counts(self, factory_cls):
        """Verify fake damage tracks mark boxes that agree with their counts."""
        for _ in range(50):
            tracker = factory_cls.build()
            assert tracker.superficial + tracker.aggravated <= tracker.size
            assert tracker.boxes.count("AGGRAVATED") == tracker.aggravated
            assert tracker.boxes.count("SUPERFICIAL") == tracker.superficial
            assert tracker.is_impaired == (tracker.superficial + tracker.aggravated >= tracker.size)

    def test_damage_factory_keeps_overrides(self):
        """Verify overridden fields are kept and the rest derive from them."""
        tracker = DamageTrackerFactory.build(size=5, aggravated=2, superficial=1)
        assert tracker.boxes == ["AGGRAVATED", "AGGRAVATED", "SUPERFICIAL", None, None]
        assert tracker.is_impaired is False

    def test_counter_and_stains_factories_stay_in_range(self):
        """Verify fake counters and stains respect their capacity."""
        for _ in range(50):
            counter = CounterTrackerFactory.build()
            assert 0 <= counter.current <= counter.size
            stains = StainsTrackerFactory.build()
            assert stains.stain_capacity == 10 - stains.humanity
            assert 0 <= stains.stains <= stains.stain_capacity

    @pytest.mark.parametrize(
        "factory_cls", [CounterTrackerFactory, DamageTrackerFactory, StainsTrackerFactory]
    )
    def test_tracker_factories_honor_seed(self, factory_cls):
        """Verify seed_random makes tracker factories reproducible."""
        factory_cls.seed_random(42)
        first = factory_cls.build()
        factory_cls.seed_random(42)
        assert factory_cls.build() == first
