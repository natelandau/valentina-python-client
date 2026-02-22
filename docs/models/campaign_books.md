---
icon: lucide/book-open
---

# Campaign Book Models

## CampaignBook

| Field           | Type          | Description             |
| --------------- | ------------- | ----------------------- |
| `id`            | `str`         | Unique identifier       |
| `date_created`  | `datetime`    | Creation timestamp      |
| `date_modified` | `datetime`    | Last modified timestamp |
| `name`          | `str`         | Book name               |
| `description`   | `str \| None` | Book description        |
| `number`        | `int`         | Position in campaign    |
| `campaign_id`   | `str`         | Parent campaign ID      |
| `asset_ids`     | `list[str]`   | Associated asset IDs    |
