---
icon: lucide/shield
---

# Global Admin Service

Manage developer accounts and API keys across the entire system. All operations require global admin privileges.

!!! warning "Global Admin Only"

    This service requires global admin privileges. Regular developers cannot access these endpoints.

## Initialize the Service

```python
from vclient import global_admin_service

admins = global_admin_service()
```

## Available Methods

### CRUD Operations

| Method                                         | Returns     | Description                    |
| ---------------------------------------------- | ----------- | ------------------------------ |
| `get(developer_id)`                            | `Developer` | Retrieve a developer by ID     |
| `create(request=None, **kwargs)`               | `Developer` | Create a new developer account |
| `update(developer_id, request=None, **kwargs)` | `Developer` | Update developer properties    |
| `delete(developer_id)`                         | `None`      | Delete a developer account     |

### Pagination Methods

| Method                                               | Returns                        | Description                    |
| ---------------------------------------------------- | ------------------------------ | ------------------------------ |
| `get_page(limit=10, offset=0, is_global_admin=None)` | `PaginatedResponse[Developer]` | Retrieve a paginated page      |
| `list_all(is_global_admin=None)`                     | `list[Developer]`              | Retrieve all developers        |
| `iter_all(limit=100, is_global_admin=None)`          | `AsyncIterator[Developer]`     | Iterate through all developers |

### API Key Management

| Method                         | Returns               | Description                            |
| ------------------------------ | --------------------- | -------------------------------------- |
| `create_api_key(developer_id)` | `DeveloperWithApiKey` | Generate a new API key for a developer |

### Server Logs

Inspect the API server's on-disk logs without shelling into the host. Both methods require global admin privileges and that file logging is enabled on the server.

| Method                          | Returns                 | Description                                  |
| ------------------------------- | ----------------------- | -------------------------------------------- |
| `tail_logs(level=None, limit=100)` | `list[ServerLogEntry]`  | Return the most recent log entries, newest first |
| `download_logs()`               | `ServerLogArchive`      | Download a zip archive of all log files      |

**`tail_logs` parameters**

- `level`: minimum log level to include. One of `"TRACE"`, `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` (the `LogLevel` type). When omitted, the server uses its configured level.
- `limit`: maximum number of entries to return. Clamped client-side to 1-500, defaulting to 100.

!!! note "File logging required"

    Both methods raise `ConflictError` (HTTP 409) when file logging is not enabled on the server. `download_logs` also raises `ConflictError` when no log files exist. Without global admin privileges, both raise `AuthorizationError` (HTTP 403).

## Examples

### Create a Developer Account

Add a new developer to the system.

```python
from vclient.models import DeveloperCreate

# Option 1: Use a model object (preferred)
request = DeveloperCreate(
    username="newdev",
    email="dev@example.com",
    is_global_admin=False
)
dev = await admins.create(request)

# Option 2: Pass fields as keyword arguments
dev = await admins.create(
    username="newdev",
    email="dev@example.com"
)
```

### Update Developer Settings

Modify a developer account's properties.

```python
from vclient.models import DeveloperUpdate

update = DeveloperUpdate(
    email="newemail@example.com",
    is_global_admin=True
)
updated = await admins.update(dev.id, update)
```

### Generate API Key

Create a new API key for an existing developer.

```python
dev_with_key = await admins.create_api_key(dev.id)
print(f"New API Key: {dev_with_key.api_key}")
```

!!! warning "Save API Keys Immediately"

    API keys are only displayed once during creation. Save the key from the response - it cannot be retrieved later.

### Audit Logs

View audit trail entries for a specific developer across all companies. Requires global admin privileges.

```python
# Get a page of audit logs for a developer
page = await admins.get_audit_log_page(dev.id)

# Filter to a specific company
page = await admins.get_audit_log_page(
    dev.id,
    company_id="company123",
    operation="CREATE",
)

# Include request forensic details
page = await admins.get_audit_log_page(
    dev.id,
    include=["request_details"],
)
```

| Method                                                  | Returns                                          | Description                             |
| ------------------------------------------------------- | ------------------------------------------------ | --------------------------------------- |
| `get_audit_log_page(developer_id, **filters)`           | `PaginatedResponse[AuditLog \| AuditLogDetail]`  | Get a page of audit log entries         |
| `list_all_audit_logs(developer_id, **filters)`          | `list[AuditLog \| AuditLogDetail]`               | Get all audit log entries               |
| `iter_all_audit_logs(developer_id, **filters)`          | `AsyncIterator[AuditLog \| AuditLogDetail]`      | Iterate through all audit log entries   |

The admin endpoint accepts all the same filter parameters as the company audit log (see [Companies Service](companies.md#filter-parameters)), plus `company_id` to narrow results to a specific company.

### Tail Server Logs

Read the most recent server log entries, newest first.

```python
# Get the latest 100 entries at the server's configured level
entries = await admins.tail_logs()
for entry in entries:
    print(f"{entry.timestamp} [{entry.level}] {entry.message}")

# Filter to warnings and above, limited to 50 entries
warnings = await admins.tail_logs(level="WARNING", limit=50)
```

Each `ServerLogEntry` field is nullable. When a log line is not valid JSON, the original line is available on `entry.raw`.

### Download Server Logs

Download a zip archive containing the active log file and any rotated backups.

```python
from pathlib import Path

archive = await admins.download_logs()
Path(archive.filename).write_bytes(archive.content)
```

The `filename` comes from the server's `Content-Disposition` header (for example, `vapi-logs-20260525T120000Z.zip`), and `content` holds the raw zip bytes.

### List Developers

Retrieve all developer accounts with optional filtering.

```python
# Get all developers
all_devs = await admins.list_all()

# Filter by global admin status
admin_devs = await admins.list_all(is_global_admin=True)

# Paginated access
page = await admins.get_page(limit=25, offset=0)
print(f"Total developers: {page.total}")
```

### Iterate Through Developers

Use memory-efficient iteration for large developer lists.

```python
async for developer in admins.iter_all():
    print(f"{developer.username} - {developer.email}")
```

## Related Documentation

- [Response Models](../models/developers.md) - View `Developer`, `DeveloperWithApiKey`, `ServerLogEntry`, and `ServerLogArchive` model schemas
