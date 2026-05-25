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

## ServerLogEntry

A single parsed server log entry returned by `tail_logs()` on the [Global Admin Service](../services/global_admin.md). Every field is nullable because individual log lines may omit values or fail to parse as structured JSON. When a line is not valid JSON, the original text is available on `raw`.

| Field       | Type             | Description                                  |
| ----------- | ---------------- | -------------------------------------------- |
| `timestamp` | `str \| None`    | Log entry timestamp                          |
| `level`     | `str \| None`    | Log level                                    |
| `name`      | `str \| None`    | Logger name                                  |
| `message`   | `str \| None`    | Log message                                  |
| `exception` | `str \| None`    | Formatted exception traceback, if any        |
| `extra`     | `dict[str, Any]` | Additional structured fields (defaults to `{}`) |
| `raw`       | `str \| None`    | Original line when the entry is not valid JSON |

## ServerLogArchive

A downloaded server-log zip archive returned by `download_logs()` on the [Global Admin Service](../services/global_admin.md). This is a frozen dataclass rather than a Pydantic model. Pair the server-provided filename with the raw zip bytes to write the archive straight to disk.

| Field      | Type    | Description                                          |
| ---------- | ------- | --------------------------------------------------- |
| `filename` | `str`   | Filename parsed from the server's `Content-Disposition` |
| `content`  | `bytes` | Raw zip archive bytes                               |
