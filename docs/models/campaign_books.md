---
icon: lucide/book-open
---

# Campaign Book Models

Models for campaign books, which organize campaign content into sequentially numbered volumes.

## CampaignBook

| Field           | Type          | Description                              |
| --------------- | ------------- | ---------------------------------------- |
| `id`            | `str`         | Unique identifier                        |
| `date_created`  | `datetime`    | Creation timestamp                       |
| `date_modified` | `datetime`    | Last modified timestamp                  |
| `name`          | `str`         | Book name                                |
| `description`   | `str \| None` | Book description                         |
| `number`        | `int`         | Position in campaign                     |
| `campaign_id`   | `str`         | Parent campaign ID                       |
| `asset_ids`     | `list[str]`   | Associated asset IDs                     |
| `character_ids` | `list[str]`   | Read-only. Distinct union of character IDs across the book's chapters (archived characters excluded) |
| `num_chapters`  | `int`         | Active chapter count (excludes archived) |
| `num_notes`     | `int`         | Active note count (excludes archived)    |
| `num_assets`    | `int`         | Active asset count (excludes archived)   |

## CampaignBookDetail

Subclass of `CampaignBook` returned by `get()` when the `include` query parameter is used. All base fields are inherited; the three embed fields default to `None` when the corresponding resource was not requested.

Use the `BookInclude` type alias from `vclient.constants` to get editor autocompletion for valid include values.

| Field      | Type                       | Description                                        |
| ---------- | -------------------------- | -------------------------------------------------- |
| `chapters` | `list[CampaignChapter] \| None` | Embedded chapters, present only when requested |
| `notes`    | `list[Note] \| None`       | Embedded notes, present only when requested        |
| `assets`   | `list[Asset] \| None`      | Embedded assets, present only when requested       |
