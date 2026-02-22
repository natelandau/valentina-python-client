---
icon: lucide/code
---

# Developer Models

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

## DeveloperWithApiKey

Extends `Developer` with an `api_key` field. Only returned when generating a new API key - save it immediately as it cannot be retrieved again.
