---
icon: lucide/map
---

# Campaign Models

Models for campaigns, which organize gameplay sessions within a company.

## Campaign

| Field           | Type          | Description             |
| --------------- | ------------- | ----------------------- |
| `id`            | `str`         | Unique identifier       |
| `date_created`  | `datetime`    | Creation timestamp      |
| `date_modified` | `datetime`    | Last modified timestamp |
| `name`          | `str`         | Campaign name           |
| `description`   | `str \| None` | Campaign description    |
| `desperation`   | `int`         | Desperation level (0-5) |
| `danger`        | `int`         | Danger level (0-5)      |
| `company_id`    | `str`         | Company ID              |
| `asset_ids`     | `list[str]`   | Associated asset IDs    |
