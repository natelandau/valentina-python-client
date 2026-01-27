"""Shared response fixtures."""

import pytest


@pytest.fixture
def character_response_data() -> dict:
    """Return sample character response data."""
    return {
        "id": "char123",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "date_killed": None,
        "character_class": "VAMPIRE",
        "type": "PLAYER",
        "game_version": "V5",
        "status": "ALIVE",
        "starting_points": 0,
        "name_first": "John",
        "name_last": "Doe",
        "name_nick": "Johnny",
        "name": "Johnny",
        "name_full": "John Doe",
        "age": 35,
        "biography": "A mysterious vampire.",
        "demeanor": "Friendly",
        "nature": "Warrior",
        "concept_id": "concept123",
        "user_creator_id": "user123",
        "user_player_id": "user456",
        "company_id": "company123",
        "campaign_id": "campaign123",
        "asset_ids": ["asset1", "asset2"],
        "character_trait_ids": ["trait1", "trait2"],
        "specialties": [{"id": "spec1", "name": "Brawl: Kindred", "type": "ACTION"}],
        "vampire_attributes": {
            "clan_id": "clan123",
            "clan_name": "Ventrue",
            "generation": 10,
            "sire": "Ancient One",
            "bane": {"name": "Rarefied Tastes", "description": "Feeds only on specific blood"},
            "compulsion": None,
        },
        "werewolf_attributes": None,
        "mage_attributes": None,
        "hunter_attributes": None,
    }
