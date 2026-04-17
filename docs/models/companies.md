---
icon: lucide/building-2
---

# Company Models

Models for managing companies, their settings, and developer access permissions.

## Company

| Field                   | Type              | Description                                 |
| ----------------------- | ----------------- | ------------------------------------------- |
| `id`                    | `str`             | Unique identifier                           |
| `date_created`          | `datetime`        | Creation timestamp                          |
| `date_modified`         | `datetime`        | Last modified timestamp                     |
| `name`                  | `str`             | Company name                                |
| `description`           | `str \| None`     | Company description                         |
| `email`                 | `str`             | Contact email                               |
| `resources_modified_at` | `datetime`        | Last modified timestamp for child resources |
| `num_campaigns`         | `int`             | Number of active campaigns (excludes archived) |
| `num_player_characters` | `int`             | Number of active player characters (excludes archived) |
| `num_storyteller_characters` | `int`        | Number of active storyteller characters (excludes archived) |
| `num_npc_characters`    | `int`             | Number of active NPC characters (excludes archived) |
| `num_users`             | `int`             | Number of active users (excludes archived)  |
| `settings`              | `CompanySettings` | Company configuration                       |

## NewCompanyResponse

Returned when creating a new company. Contains both the created company and the admin user automatically generated for it.

| Field        | Type      | Description                        |
| ------------ | --------- | ---------------------------------- |
| `company`    | `Company` | The newly created company          |
| `admin_user` | `User`    | Admin user created for the company |

## CompanyPermissions

Returned when granting or modifying developer access to a company.

| Field        | Type              | Description              |
| ------------ | ----------------- | ------------------------ |
| `company_id` | `str`             | Company ID               |
| `name`       | `str \| None`     | Company name             |
| `permission` | `PermissionLevel` | Granted permission level |

## CompanySettings

Response model for company configuration. All fields are always populated by the server.

| Field                             | Type                          | Description                                             |
| --------------------------------- | ----------------------------- | ------------------------------------------------------- |
| `character_autogen_xp_cost`       | `int`                         | XP cost to autogenerate a character (0-100)             |
| `character_autogen_num_choices`   | `int`                         | Number of autogen choices presented (1-10)              |
| `character_autogen_starting_points` | `int`                       | Starting-points budget copied onto finalized chargen characters (0-100) |
| `permission_manage_campaign`      | `ManageCampaignPermission`    | Who may manage campaigns                                |
| `permission_grant_xp`             | `GrantXPPermission`           | Who may grant XP                                        |
| `permission_free_trait_changes`   | `FreeTraitChangesPermission`  | When trait changes are free                             |
| `permission_recoup_xp`            | `RecoupXPPermission`          | When XP may be recouped                                 |

## CompanySettingsCreate

Request payload for `POST /companies`. All fields optional — the server applies defaults for anything omitted.

| Field                             | Type                                    | Description                              |
| --------------------------------- | --------------------------------------- | ---------------------------------------- |
| `character_autogen_xp_cost`       | `int \| None`                           | Override default XP cost                 |
| `character_autogen_num_choices`   | `int \| None`                           | Override default number of choices       |
| `character_autogen_starting_points` | `int \| None`                         | Override default starting-points budget  |
| `permission_manage_campaign`      | `ManageCampaignPermission \| None`      | Override default                         |
| `permission_grant_xp`             | `GrantXPPermission \| None`             | Override default                         |
| `permission_free_trait_changes`   | `FreeTraitChangesPermission \| None`    | Override default                         |
| `permission_recoup_xp`            | `RecoupXPPermission \| None`            | Override default                         |

## CompanySettingsUpdate

Request payload for `PATCH /companies/{id}`. All fields optional — omitted fields remain unchanged.

| Field                             | Type                                    | Description                              |
| --------------------------------- | --------------------------------------- | ---------------------------------------- |
| `character_autogen_xp_cost`       | `int \| None`                           | New XP cost value                        |
| `character_autogen_num_choices`   | `int \| None`                           | New number of choices                    |
| `character_autogen_starting_points` | `int \| None`                         | New starting-points budget               |
| `permission_manage_campaign`      | `ManageCampaignPermission \| None`      | New value                                |
| `permission_grant_xp`             | `GrantXPPermission \| None`             | New value                                |
| `permission_free_trait_changes`   | `FreeTraitChangesPermission \| None`    | New value                                |
| `permission_recoup_xp`            | `RecoupXPPermission \| None`            | New value                                |
