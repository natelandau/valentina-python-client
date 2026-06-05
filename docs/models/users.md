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
| `apple_profile`        | `AppleProfile \| None`     | Apple account information                     |
| `campaign_experience`  | `list[CampaignExperience]` | XP per campaign                               |
| `asset_ids`            | `list[str]`                | Owned asset IDs                               |
| `lifetime_xp`          | `int`                      | Lifetime XP earned                            |
| `lifetime_cool_points` | `int`                      | Lifetime cool points earned                   |
| `num_quickrolls`       | `int`                      | Active quick-roll count owned by the user     |
| `num_notes`            | `int`                      | Active note count authored by the user        |
| `num_assets`           | `int`                      | Active asset count owned by the user          |
| `num_characters`       | `int`                      | Active character count played by the user     |

## UserDetail

Subclass of `User` returned by `get()` when the `include` query parameter is used. All base fields are inherited; the four embed fields default to `None` when the corresponding resource was not requested.

Use the `UserInclude` type alias from `vclient.constants` to get editor autocompletion for valid include values.

!!! note "Semantic nuances"

    - `assets` returns assets **attached to** the user, not assets the user uploaded.
    - `characters` returns only the characters the user **plays** (not characters they created for others).

| Field        | Type                    | Description                                                     |
| ------------ | ----------------------- | --------------------------------------------------------------- |
| `quickrolls` | `list[Quickroll] \| None` | Embedded quickrolls, present only when requested              |
| `notes`      | `list[Note] \| None`    | Embedded notes, present only when requested                     |
| `assets`     | `list[Asset] \| None`   | Assets attached to the user, present only when requested        |
| `characters` | `list[Character] \| None` | Characters the user plays, present only when requested        |

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

## AppleProfile

| Field      | Type          | Description         |
| ---------- | ------------- | ------------------- |
| `id`       | `str \| None` | Apple user ID       |
| `email`    | `str \| None` | Apple email address |
| `fullname` | `str \| None` | Full name           |

## UserRegisterDTO

Request body for registering a user via SSO onboarding.

| Field             | Type                     | Description              |
| ----------------- | ------------------------ | ------------------------ |
| `username`        | `str`                    | Username (required)      |
| `email`           | `str`                    | Email address (required) |
| `name_first`      | `str \| None`            | First name               |
| `name_last`       | `str \| None`            | Last name                |
| `discord_profile` | `DiscordProfile \| None` | Discord information      |
| `google_profile`  | `GoogleProfile \| None`  | Google account info      |
| `github_profile`  | `GitHubProfile \| None`  | GitHub account info      |
| `apple_profile`   | `AppleProfile \| None`   | Apple account info       |

## UserMergeDTO

Request body for merging an unapproved user into an existing primary user.

| Field               | Type  | Description                          |
| ------------------- | ----- | ------------------------------------ |
| `primary_user_id`   | `str` | ID of the primary user to merge into |
| `secondary_user_id` | `str` | ID of the unapproved user to merge   |

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

| Field  | Type       | Description                         |
| ------ | ---------- | ----------------------------------- |
| `role` | `UserRole` | Role to assign to the approved user |

## AdminUser

Returned by all `GlobalAdminService` user methods. Extends `User` with an `is_archived` field that is always present, allowing global admins to see and restore soft-deleted users.

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
| `apple_profile`        | `AppleProfile \| None`     | Apple account information                     |
| `campaign_experience`  | `list[CampaignExperience]` | XP per campaign                               |
| `asset_ids`            | `list[str]`                | Owned asset IDs                               |
| `lifetime_xp`          | `int`                      | Lifetime XP earned                            |
| `lifetime_cool_points` | `int`                      | Lifetime cool points earned                   |
| `num_quickrolls`       | `int`                      | Active quick-roll count owned by the user     |
| `num_notes`            | `int`                      | Active note count authored by the user        |
| `num_assets`           | `int`                      | Active asset count owned by the user          |
| `num_characters`       | `int`                      | Active character count played by the user     |
| `is_archived`          | `bool`                     | Whether the user has been soft-deleted        |

## AdminUserCreate

Request body for creating a user via the global-admin service. Requires a `company_id` because the global-admin service operates across all companies.

| Field             | Type                     | Description                                   |
| ----------------- | ------------------------ | --------------------------------------------- |
| `company_id`      | `str`                    | Company the user belongs to (required)        |
| `username`        | `str`                    | Username (required)                           |
| `email`           | `str`                    | Email address (required)                      |
| `role`            | `UserRole`               | Role (ADMIN, STORYTELLER, PLAYER, UNAPPROVED) |
| `name_first`      | `str \| None`            | First name                                    |
| `name_last`       | `str \| None`            | Last name                                     |
| `discord_profile` | `DiscordProfile \| None` | Discord information                           |
| `google_profile`  | `GoogleProfile \| None`  | Google account information                    |
| `github_profile`  | `GitHubProfile \| None`  | GitHub account information                    |
| `apple_profile`   | `AppleProfile \| None`   | Apple account information                     |

## AdminUserUpdate

Request body for updating a user via the global-admin service. All fields are optional; include only the fields that need to change. Set `is_archived=False` to restore a soft-deleted user.

| Field             | Type                     | Description                                          |
| ----------------- | ------------------------ | ---------------------------------------------------- |
| `name_first`      | `str \| None`            | Updated first name                                   |
| `name_last`       | `str \| None`            | Updated last name                                    |
| `username`        | `str \| None`            | Updated username                                     |
| `email`           | `str \| None`            | Updated email address                                |
| `role`            | `UserRole \| None`       | Updated role                                         |
| `discord_profile` | `DiscordProfile \| None` | Updated Discord information                          |
| `google_profile`  | `GoogleProfile \| None`  | Updated Google account information                   |
| `github_profile`  | `GitHubProfile \| None`  | Updated GitHub account information                   |
| `apple_profile`   | `AppleProfile \| None`   | Updated Apple account information                    |
| `is_archived`     | `bool \| None`           | Set to `False` to restore a soft-deleted user        |
