---
icon: lucide/users
---

# User Models

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
