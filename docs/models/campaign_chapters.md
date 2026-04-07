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

## CampaignChapterDetail

Subclass of `CampaignChapter` returned by `get()` when the `include` query parameter is used. All base fields are inherited; the two embed fields default to `None` when the corresponding resource was not requested.

Use the `ChapterInclude` type alias from `vclient.constants` to get editor autocompletion for valid include values.

| Field    | Type                  | Description                                  |
| -------- | --------------------- | -------------------------------------------- |
| `notes`  | `list[Note] \| None`  | Embedded notes, present only when requested  |
| `assets` | `list[Asset] \| None` | Embedded assets, present only when requested |
