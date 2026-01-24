# Valentina Python Client

Async Python client library for accessing the Valentina Noir API. Documentation can be found at [https://docs.valentina-noir.com](https://docs.valentina-noir.com) and full API reference can be found at [https://api.valentina-noir.com/docs](https://api.valentina-noir.com/docs).

## Installation

### From Git

```bash
# Using uv
uv add git+https://github.com/natelandau/valentina-python-client.git

# Using pip
pip install git+https://github.com/natelandau/valentina-python-client.git
```

## Quick Start

Create a client once at application startup, then use service factory functions from any module.

### 1. Create the Client (once at startup)

```python
from vclient import VClient

# Client automatically registers itself as the default
client = VClient(
    base_url="https://api.valentina-noir.com",
    api_key="your-api-key",
)
```

### 2. Use Services from Any Module

```python
import asyncio
from vclient import companies_service, system_service

async def main():
    # Check system health
    system = system_service()
    health = await system.health()
    print(f"API Version: {health.version}")
    print(f"Database: {health.database_status}")

    # List companies you have access to
    companies = companies_service()
    for company in await companies.list_all():
        print(f"Company: {company.name}")

asyncio.run(main())
```

## Configuration

### Basic Configuration

```python
from vclient import VClient

# Using constructor parameters
client = VClient(
    base_url="https://api.valentina-noir.com",
    api_key="your-api-key",
    timeout=30.0,
)
```

### Advanced Configuration with APIConfig

```python
from vclient import VClient, APIConfig

config = APIConfig(
    base_url="https://api.valentina-noir.com",
    api_key="your-api-key",
    timeout=30.0,
    max_retries=3,
    retry_delay=1.0,
    auto_retry_rate_limit=True,
)

client = VClient(config=config)
```

### Configuration Options

| Option                  | Type    | Default  | Description                                |
| ----------------------- | ------- | -------- | ------------------------------------------ |
| `base_url`              | `str`   | Required | Base URL for the API                       |
| `api_key`               | `str`   | Required | API key for authentication                 |
| `timeout`               | `float` | `30.0`   | Request timeout in seconds                 |
| `max_retries`           | `int`   | `3`      | Maximum retry attempts for failed requests |
| `retry_delay`           | `float` | `1.0`    | Base delay between retries in seconds      |
| `auto_retry_rate_limit` | `bool`  | `True`   | Automatically retry rate-limited requests  |

## Available Services

| Service | Factory Function | Description |
| --- | --- | --- |
| [System Service](docs/system-service.md) | `system_service()` | Health checks and system status |
| [Companies Service](docs/companies-service.md) | `companies_service()` | Manage companies and permissions |
| [Developers Service](docs/developers-service.md) | `developer_service()` | Manage your own developer profile |
| [Global Admin Service](docs/global-admin-service.md) | `global_admin_service()` | Manage developer accounts (requires admin) |

## Common Service Methods

Services that manage resources (Companies, Global Admin) share a consistent API pattern for CRUD operations and pagination.

### CRUD Operations

| Method            | Description                                   |
| ----------------- | --------------------------------------------- |
| `get(id)`         | Retrieve a single resource by ID              |
| `create(...)`     | Create a new resource                         |
| `update(id, ...)` | Update an existing resource (partial updates) |
| `delete(id)`      | Delete a resource                             |

```python
# Get a single resource
company = await companies.get("507f1f77bcf86cd799439011")

# Create a new resource
company = await companies.create(name="My Company", email="contact@example.com")

# Update (only include fields to change)
updated = await companies.update("507f1f77bcf86cd799439011", name="New Name")

# Delete
await companies.delete("507f1f77bcf86cd799439011")
```

### Pagination

Services that return collections provide three methods for accessing paginated data:

| Method       | Returns                | Description                                     |
| ------------ | ---------------------- | ----------------------------------------------- |
| `get_page()` | `PaginatedResponse[T]` | Retrieve a single page with pagination metadata |
| `list_all()` | `list[T]`              | Fetch all items across all pages into a list    |
| `iter_all()` | `AsyncIterator[T]`     | Memory-efficient streaming through all pages    |

```python
# Get a single page with metadata
page = await companies.get_page(limit=10, offset=0)
print(f"Page {page.current_page} of {page.total_pages}")

for company in page.items:
    print(company.name)

# Check if there are more pages
if page.has_more:
    next_page = await companies.get_page(limit=10, offset=page.next_offset)

# Fetch all items at once
all_companies = await companies.list_all()

# Stream through all items (memory-efficient for large datasets)
async for company in companies.iter_all():
    print(company.name)
```

### PaginatedResponse Model

| Field    | Type      | Description                            |
| -------- | --------- | -------------------------------------- |
| `items`  | `list[T]` | The requested page of results          |
| `limit`  | `int`     | The limit that was applied             |
| `offset` | `int`     | The offset that was applied            |
| `total`  | `int`     | Total number of items across all pages |

**Computed Properties:**

| Property       | Type   | Description                            |
| -------------- | ------ | -------------------------------------- |
| `has_more`     | `bool` | Whether there are more pages available |
| `next_offset`  | `int`  | The offset for the next page           |
| `total_pages`  | `int`  | Total number of pages                  |
| `current_page` | `int`  | Current page number (1-indexed)        |

## Error Handling

The client provides specific exception types for different error conditions:

```python
from vclient import (
    companies_service,
    APIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    ConflictError,
    RateLimitError,
    ServerError,
)

companies = companies_service()

try:
    company = await companies.get("invalid-id")
except NotFoundError:
    print("Company not found")
except AuthorizationError:
    print("You don't have access to this company")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Invalid request: {e}")
except RateLimitError:
    print("Rate limit exceeded, try again later")
except ServerError:
    print("Server error, try again later")
except APIError as e:
    print(f"API error: {e}")
```

### Exception Hierarchy

| Exception             | HTTP Status | Description                   |
| --------------------- | ----------- | ----------------------------- |
| `APIError`            | -           | Base class for all API errors |
| `AuthenticationError` | 401         | Invalid or missing API key    |
| `AuthorizationError`  | 403         | Insufficient permissions      |
| `NotFoundError`       | 404         | Resource not found            |
| `ValidationError`     | 422         | Invalid request data          |
| `ConflictError`       | 409         | Resource conflict             |
| `RateLimitError`      | 429         | Rate limit exceeded           |
| `ServerError`         | 5xx         | Server-side error             |

## Response Models

All API responses are returned as [Pydantic](https://docs.pydantic.dev/) models, providing automatic validation, serialization, and IDE autocompletion support.

```python
from vclient import companies_service

companies = companies_service()
company = await companies.get("company-id")

# Access attributes directly
print(company.name)
print(company.date_created)

# Convert to dictionary
data = company.model_dump()

# Convert to JSON string
json_str = company.model_dump_json()

# Exclude None values when serializing
data = company.model_dump(exclude_none=True)
```

See individual service documentation for detailed response model specifications.
