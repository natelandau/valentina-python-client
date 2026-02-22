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

## RollStatistics

Aggregated dice roll statistics for a user. Track success rates, critical rolls, botches, and identify patterns in player performance.

| Field                  | Type    | Description              |
| ---------------------- | ------- | ------------------------ |
| `botches`              | `int`   | Total botched rolls      |
| `successes`            | `int`   | Total successful rolls   |
| `failures`             | `int`   | Total failed rolls       |
| `criticals`            | `int`   | Total critical successes |
| `total_rolls`          | `int`   | Total number of rolls    |
| `success_percentage`   | `float` | Success rate             |
| `failure_percentage`   | `float` | Failure rate             |
| `botch_percentage`     | `float` | Botch rate               |
| `criticals_percentage` | `float` | Critical rate            |
