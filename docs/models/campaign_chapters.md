---
icon: lucide/bookmark
---

# Campaign Chapter Models

Models for campaign chapters, which organize content within a campaign book.

## CampaignChapter

| Field           | Type          | Description             |
| --------------- | ------------- | ----------------------- |
| `id`            | `str`         | Unique identifier       |
| `date_created`  | `datetime`    | Creation timestamp      |
| `date_modified` | `datetime`    | Last modified timestamp |
| `name`          | `str`         | Chapter name            |
| `description`   | `str \| None` | Chapter description     |
| `number`        | `int`         | Position in book        |
| `book_id`       | `str`         | Parent book ID          |
| `asset_ids`     | `list[str]`   | Associated asset IDs    |
