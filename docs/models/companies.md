---
icon: lucide/building-2
---

# Company Models

Models for managing companies, their settings, and developer access permissions.

## Company

| Field                   | Type                      | Description                                 |
| ----------------------- | ------------------------- | ------------------------------------------- |
| `id`                    | `str`                     | Unique identifier                           |
| `date_created`          | `datetime`                | Creation timestamp                          |
| `date_modified`         | `datetime`                | Last modified timestamp                     |
| `name`                  | `str`                     | Company name                                |
| `description`           | `str \| None`             | Company description                         |
| `email`                 | `str`                     | Contact email                               |
| `user_ids`              | `list[str]`               | Associated user IDs                         |
| `resources_modified_at` | `datetime`                | Last modified timestamp for child resources |
| `settings`              | `CompanySettings \| None` | Company configuration                       |

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

| Field                           | Type          | Description                    |
| ------------------------------- | ------------- | ------------------------------ |
| `character_autogen_xp_cost`     | `int \| None` | XP cost to autogen (0-100)     |
| `character_autogen_num_choices` | `int \| None` | Number of choices (1-10)       |
| `permission_manage_campaign`    | `str \| None` | Campaign management permission |
| `permission_grant_xp`           | `str \| None` | XP granting permission         |
| `permission_free_trait_changes` | `str \| None` | Free trait changes permission  |
