---
icon: lucide/share-2
---

# Shared Models

These models appear across multiple services and provide shared functionality.

## Asset

Represents a file stored in cloud storage. Use this model to manage uploaded files like character portraits, campaign handouts, and other assets.

| Field               | Type        | Description                   |
| ------------------- | ----------- | ----------------------------- |
| `id`                | `str`       | Unique identifier             |
| `date_created`      | `datetime`  | Creation timestamp            |
| `date_modified`     | `datetime`  | Last modified timestamp       |
| `file_type`         | `AssetType` | File type (image, text, etc.) |
| `original_filename` | `str`       | Original filename             |
| `public_url`        | `str`       | Public URL to access the file |
| `uploaded_by`       | `str`       | ID of uploader                |

## Note

Represents a markdown-formatted note. Store session notes, character backstories, and campaign information with full markdown support.

| Field           | Type       | Description             |
| --------------- | ---------- | ----------------------- |
| `id`            | `str`      | Unique identifier       |
| `date_created`  | `datetime` | Creation timestamp      |
| `date_modified` | `datetime` | Last modified timestamp |
| `title`         | `str`      | Note title              |
| `content`       | `str`      | Note content (markdown) |

## NoteCreate

Request body for creating a new note.

| Field     | Type  | Description                     |
| --------- | ----- | ------------------------------- |
| `title`   | `str` | Note title (3-50 characters)    |
| `content` | `str` | Note content (3+ characters)    |

## NoteUpdate

Request body for updating a note. Only include fields that need to change.

| Field     | Type          | Description                     |
| --------- | ------------- | ------------------------------- |
| `title`   | `str \| None` | Updated title (3-50 characters) |
| `content` | `str \| None` | Updated content (3+ characters) |

## RollStatistics

Aggregated dice roll statistics for a user. Track success rates, critical rolls, botches, and identify patterns in player performance.

| Field                  | Type             | Description                   |
| ---------------------- | ---------------- | ----------------------------- |
| `botches`              | `int`            | Total botched rolls           |
| `successes`            | `int`            | Total successful rolls        |
| `failures`             | `int`            | Total failed rolls            |
| `criticals`            | `int`            | Total critical successes      |
| `total_rolls`          | `int`            | Total number of rolls         |
| `average_difficulty`   | `float \| None`  | Average roll difficulty       |
| `average_pool`         | `float \| None`  | Average dice pool size        |
| `top_traits`           | `list[dict]`     | Most frequently rolled traits |
| `success_percentage`   | `float`          | Success rate                  |
| `failure_percentage`   | `float`          | Failure rate                  |
| `botch_percentage`     | `float`          | Botch rate                    |
| `criticals_percentage` | `float`          | Critical rate                 |

## SystemHealth

Represents the health status of the API and its dependencies. Returned by the [System Service](../services/system.md) health check endpoint.

| Field             | Type  | Description             |
| ----------------- | ----- | ----------------------- |
| `database_status` | `str` | Database connection status |
| `cache_status`    | `str` | Cache connection status    |
| `version`         | `str` | API version string         |
