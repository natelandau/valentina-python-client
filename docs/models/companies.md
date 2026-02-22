---
icon: lucide/building-2
---

# Company Models

## Company

| Field           | Type                      | Description             |
| --------------- | ------------------------- | ----------------------- |
| `id`            | `str`                     | Unique identifier       |
| `date_created`  | `datetime`                | Creation timestamp      |
| `date_modified` | `datetime`                | Last modified timestamp |
| `name`          | `str`                     | Company name            |
| `description`   | `str \| None`             | Company description     |
| `email`         | `str`                     | Contact email           |
| `user_ids`      | `list[str]`               | Associated user IDs     |
| `settings`      | `CompanySettings \| None` | Company configuration   |

## CompanySettings

| Field                           | Type          | Description                    |
| ------------------------------- | ------------- | ------------------------------ |
| `character_autogen_xp_cost`     | `int \| None` | XP cost to autogen (0-100)     |
| `character_autogen_num_choices` | `int \| None` | Number of choices (1-10)       |
| `permission_manage_campaign`    | `str \| None` | Campaign management permission |
| `permission_grant_xp`           | `str \| None` | XP granting permission         |
| `permission_free_trait_changes` | `str \| None` | Free trait changes permission  |
