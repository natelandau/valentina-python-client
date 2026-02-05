# System Service

Check API health and system status. This service doesn't require authentication.

## Usage

```python
from vclient import system_service

system = system_service()
```

## Methods

| Method     | Returns        | Description                     |
| ---------- | -------------- | ------------------------------- |
| `health()` | `SystemHealth` | Check API and dependency health |

## Example

```python
health = await system.health()
print(f"API Version: {health.version}")
print(f"Database: {health.database_status}")
print(f"Cache: {health.cache_status}")
```
