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


@pytest.fixture
def user_response_data() -> dict:
    """Return sample user response data."""
    return {
        "id": "507f1f77bcf86cd799439011",
        "date_created": "2024-01-15T10:30:00Z",
        "date_modified": "2024-01-15T10:30:00Z",
        "name": "Test User",
        "email": "test@example.com",
        "role": "PLAYER",
        "company_id": "company123",
        "discord_profile": {
            "id": "discord123",
            "username": "testuser",
        },
        "campaign_experience": [
            {"campaign_id": "campaign1", "xp_current": 50, "xp_total": 100, "cool_points": 5}
        ],
        "asset_ids": ["asset1"],
    }
