---
icon: lucide/users
---

# User Models

Models for users, their Discord profiles, campaign experience, and quickrolls.

## User

| Field                  | Type                       | Description                                   |
| ---------------------- | -------------------------- | --------------------------------------------- |
| `id`                   | `str`                      | Unique identifier                             |
| `date_created`         | `datetime`                 | Creation timestamp                            |
| `date_modified`        | `datetime`                 | Last modified timestamp                       |
| `name_first`           | `str`                      | First name                                    |
| `name_last`            | `str`                      | Last name                                     |
| `username`             | `str`                      | Username                                      |
| `email`                | `str`                      | Email address                                 |
| `role`                 | `UserRole`                 | Role (ADMIN, STORYTELLER, PLAYER, UNAPPROVED) |
| `company_id`           | `str`                      | Company ID                                    |
| `discord_profile`      | `DiscordProfile \| None`   | Discord information                           |
| `google_profile`       | `GoogleProfile \| None`    | Google account information                    |
| `github_profile`       | `GitHubProfile \| None`    | GitHub account information                    |
| `campaign_experience`  | `list[CampaignExperience]` | XP per campaign                               |
| `asset_ids`            | `list[str]`                | Owned asset IDs                               |
| `lifetime_xp`          | `int`                      | Lifetime XP earned                            |
| `lifetime_cool_points` | `int`                      | Lifetime cool points earned                   |

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

## GoogleProfile

| Field            | Type           | Description               |
| ---------------- | -------------- | ------------------------- |
| `id`             | `str \| None`  | Google user ID            |
| `email`          | `str \| None`  | Google email address      |
| `verified_email` | `bool \| None` | Whether email is verified |
| `username`       | `str \| None`  | Google username           |
| `name_first`     | `str \| None`  | First name                |
| `name_last`      | `str \| None`  | Last name                 |
| `avatar_url`     | `str \| None`  | Avatar URL                |
| `locale`         | `str \| None`  | Locale setting            |

## GitHubProfile

| Field         | Type          | Description        |
| ------------- | ------------- | ------------------ |
| `id`          | `str \| None` | GitHub user ID     |
| `login`       | `str \| None` | GitHub login name  |
| `username`    | `str \| None` | GitHub username    |
| `avatar_url`  | `str \| None` | Avatar URL         |
| `email`       | `str \| None` | GitHub email       |
| `profile_url` | `str \| None` | GitHub profile URL |

## UserRegisterDTO

Request body for registering a user via SSO onboarding. Unlike `UserCreate`, no `requesting_user_id` is required.

| Field             | Type                     | Description              |
| ----------------- | ------------------------ | ------------------------ |
| `username`        | `str`                    | Username (required)      |
| `email`           | `str`                    | Email address (required) |
| `name_first`      | `str \| None`            | First name               |
| `name_last`       | `str \| None`            | Last name                |
| `discord_profile` | `DiscordProfile \| None` | Discord information      |
| `google_profile`  | `GoogleProfile \| None`  | Google account info      |
| `github_profile`  | `GitHubProfile \| None`  | GitHub account info      |

## UserMergeDTO

Request body for merging an unapproved user into an existing primary user.

| Field                | Type  | Description                          |
| -------------------- | ----- | ------------------------------------ |
| `primary_user_id`    | `str` | ID of the primary user to merge into |
| `secondary_user_id`  | `str` | ID of the unapproved user to merge   |
| `requesting_user_id` | `str` | ID of the user making the request    |

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

| Field         | Type                | Description         |
| ------------- | ------------------- | ------------------- |
| `name`        | `str \| None`       | Updated name        |
| `description` | `str \| None`       | Updated description |
| `trait_ids`   | `list[str] \| None` | Updated trait IDs   |

## UserApproveDTO

Request body for approving an unapproved user.

| Field                | Type       | Description                         |
| -------------------- | ---------- | ----------------------------------- |
| `role`               | `UserRole` | Role to assign to the approved user |
| `requesting_user_id` | `str`      | ID of the user making the request   |

## UserDenyDTO

Request body for denying an unapproved user.

| Field                | Type  | Description                       |
| -------------------- | ----- | --------------------------------- |
| `requesting_user_id` | `str` | ID of the user making the request |
