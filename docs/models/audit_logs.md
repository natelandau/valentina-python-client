---
icon: lucide/scroll-text
---

# Audit Log Models

Models for audit log entries, which record entity changes within a company.

## AuditLog

Default response model for audit log entries.

| Field               | Type                     | Description                          |
| ------------------- | ------------------------ | ------------------------------------ |
| `id`                | `str`                    | Unique identifier                    |
| `date_created`      | `datetime`               | When the action occurred             |
| `entity_type`       | `AuditEntityType`        | Type of entity affected              |
| `operation`         | `AuditOperation`         | CREATE, UPDATE, or DELETE            |
| `target_entity_id`  | `str`                    | ID of the affected entity            |
| `description`       | `str`                    | Human-readable description           |
| `changes`           | `dict[str, Any] \| None` | Field changes as `{field: {old, new}}` |
| `company_id`        | `str`                    | Company context                      |
| `acting_user_id`    | `str \| None`            | User who performed the action        |
| `user_id`           | `str \| None`            | User being acted upon                |
| `campaign_id`       | `str \| None`            | Campaign context                     |
| `book_id`           | `str \| None`            | Book context                         |
| `chapter_id`        | `str \| None`            | Chapter context                      |
| `character_id`      | `str \| None`            | Character context                    |
| `request_id`        | `str \| None`            | Request ID for tracing               |

## AuditLogDetail

Extends `AuditLog` with raw request forensic data. Returned when `include=["request_details"]` is passed.

| Field           | Type                      | Description                   |
| --------------- | ------------------------- | ----------------------------- |
| `method`        | `str \| None`             | HTTP method (GET, POST, etc.) |
| `url`           | `str \| None`             | Request URL path              |
| `request_json`  | `dict[str, Any] \| None`  | Parsed JSON request body      |
| `request_body`  | `str \| None`             | Raw request body string       |
| `path_params`   | `dict[str, str] \| None`  | URL path parameters           |
| `query_params`  | `dict[str, str] \| None`  | URL query parameters          |
| `operation_id`  | `str \| None`             | API operation identifier      |
| `handler_name`  | `str \| None`             | Server handler name           |
| `name`          | `str \| None`             | Operation display name        |
| `summary`       | `str \| None`             | Operation summary             |
