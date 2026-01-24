# System Service

The System Service provides health checks and system status operations. This service does not require authentication.

## Usage

```python
from vclient import system_service

system = system_service()
```

## Methods

### `health()`

Check the health status of the API and its dependencies.

**Returns:** `SystemHealth`

**Example:**

```python
health = await system.health()
print(f"Database: {health.database_status}")
print(f"Cache: {health.cache_status}")
print(f"API Version: {health.version}")
```

## Response Models

### `SystemHealth`

Represents the health status of the API and its dependencies.

| Field | Type | Description |
|-------|------|-------------|
| `database_status` | `str` | Current status of the database connection |
| `cache_status` | `str` | Current status of the cache connection |
| `version` | `str` | Current API version |

### `ServiceStatus`

Enum for service status values.

| Value | Description |
|-------|-------------|
| `ONLINE` | Service is operational |
| `OFFLINE` | Service is unavailable |
