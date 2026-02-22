---
icon: lucide/users
---

# User Models

Models for users, their Discord profiles, campaign experience, and quickrolls.

## User

| Field                 | Type                       | Description                       |
| --------------------- | -------------------------- | --------------------------------- |
| `id`                  | `str`                      | Unique identifier                 |
| `date_created`        | `datetime`                 | Creation timestamp                |
| `date_modified`       | `datetime`                 | Last modified timestamp           |
| `name`                | `str`                      | Display name                      |
| `email`               | `str`                      | Email address                     |
| `role`                | `UserRole \| None`         | Role (ADMIN, STORYTELLER, PLAYER) |
| `company_id`          | `str`                      | Company ID                        |
| `discord_profile`     | `DiscordProfile \| None`   | Discord information               |
| `campaign_experience` | `list[CampaignExperience]` | XP per campaign                   |
| `asset_ids`           | `list[str]`                | Owned asset IDs                   |

## CampaignExperience

| Field         | Type  | Description        |
| ------------- | ----- | ------------------ |
| `campaign_id` | `str` | Campaign ID        |
| `xp_current`  | `int` | Available XP       |
| `xp_total`    | `int` | Lifetime XP earned |
| `cool_points` | `int` | Cool points earned |

## DiscordProfile

| Field         | Type          | Description      |
| ------------- | ------------- | ---------------- |
| `id`          | `str \| None` | Discord user ID  |
| `username`    | `str \| None` | Discord username |
| `global_name` | `str \| None` | Display name     |
| `avatar_url`  | `str \| None` | Avatar URL       |

## Quickroll

Pre-configured dice pool for frequently used trait combinations. Speed up gameplay by saving common rolls like "Strength + Brawl" or "Wits + Investigation".

| Field           | Type          | Description                |
| --------------- | ------------- | -------------------------- |
| `id`            | `str`         | Unique identifier          |
| `date_created`  | `datetime`    | Creation timestamp         |
| `date_modified` | `datetime`    | Last modified timestamp    |
| `name`          | `str`         | Quickroll name             |
| `description`   | `str \| None` | Optional description       |
| `user_id`       | `str`         | Owner user ID              |
| `trait_ids`     | `list[str]`   | Trait IDs in the dice pool |

## QuickrollCreate

Request body for creating a new quickroll.

| Field         | Type          | Description                       |
| ------------- | ------------- | --------------------------------- |
| `name`        | `str`         | Quickroll name (3-50 characters)  |
| `description` | `str \| None` | Optional description              |
| `trait_ids`   | `list[str]`   | Trait IDs to include in dice pool |

## QuickrollUpdate

Request body for updating a quickroll. Only include fields that need to change.

| Field         | Type               | Description           |
| ------------- | ------------------ | --------------------- |
| `name`        | `str \| None`      | Updated name          |
| `description` | `str \| None`      | Updated description   |
| `trait_ids`   | `list[str] \| None`| Updated trait IDs     |
