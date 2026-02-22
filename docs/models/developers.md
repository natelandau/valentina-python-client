---
icon: lucide/code
---

# Developer Models

Models for developer accounts, API key management, and company permission grants.

## Developer

| Field             | Type                               | Description             |
| ----------------- | ---------------------------------- | ----------------------- |
| `id`              | `str`                              | Unique identifier       |
| `date_created`    | `datetime`                         | Creation timestamp      |
| `date_modified`   | `datetime`                         | Last modified timestamp |
| `username`        | `str`                              | Username                |
| `email`           | `str`                              | Email address           |
| `key_generated`   | `datetime \| None`                 | API key generation time |
| `is_global_admin` | `bool`                             | Global admin status     |
| `companies`       | `list[DeveloperCompanyPermission]` | Company permissions     |

## MeDeveloper

Your own developer profile. Contains the same fields as `Developer` but excludes the `is_global_admin` field for security.

## MeDeveloperWithApiKey

Extends `MeDeveloper` with the generated API key. Only returned when regenerating your API key — save it immediately as it can't be retrieved again.

| Field     | Type  | Description                                    |
| --------- | ----- | ---------------------------------------------- |
| `api_key` | `str` | Generated API key (shown only at creation time) |

All other fields are inherited from `MeDeveloper`.

## MeDeveloperUpdate

Request body for updating your developer profile.

| Field      | Type          | Description        |
| ---------- | ------------- | ------------------ |
| `username` | `str \| None` | Updated username   |
| `email`    | `str \| None` | Updated email      |
