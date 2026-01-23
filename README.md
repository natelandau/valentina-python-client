# vclient

Async Python client library for the Valentina API.

## Installation

### From Git

```bash
# Using uv
uv add git+https://github.com/username/valentina-api-client.git

# Using pip
pip install git+https://github.com/username/valentina-api-client.git
```

### From Local Path (Development)

```bash
# Using uv
uv add ../valentina-api-client

# Using pip (editable install)
pip install -e ../valentina-api-client
```

## Quick Start

Create a client once at application startup, then use service factory functions from any module.

### 1. Create the Client (once at startup)

```python
from vclient import VClient

# Client automatically registers itself as the default
client = VClient(api_key="your-api-key")
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

### Available Factory Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `companies_service()` | `CompaniesService` | Get a service for company operations |
| `global_admin_service()` | `GlobalAdminService` | Get a service for admin operations |
| `system_service()` | `SystemService` | Get a service for system operations |

> **Note**: Calling factory functions before creating a `VClient` raises a `RuntimeError`.

## Alternative: Using Context Manager

For simple scripts or when you prefer explicit client management, use the async context manager:

```python
import asyncio
from vclient import VClient

async def main():
    async with VClient(api_key="your-api-key") as client:
        health = await client.system.health()
        companies = await client.companies.list_all()

asyncio.run(main())
```

For manual lifecycle management without the context manager:

```python
from vclient import VClient

client = VClient(api_key="your-api-key")
try:
    companies = await client.companies.list_all()
finally:
    await client.close()
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

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `base_url` | `str` | `https://api.valentina-noir.com` | Base URL for the API |
| `api_key` | `str \| None` | `None` | API key for authentication |
| `timeout` | `float` | `30.0` | Request timeout in seconds |
| `max_retries` | `int` | `3` | Maximum retry attempts for failed requests |
| `retry_delay` | `float` | `1.0` | Base delay between retries in seconds |
| `auto_retry_rate_limit` | `bool` | `True` | Automatically retry rate-limited requests |

## Available Services

### System Service

Health checks and system status operations.

```python
from vclient import system_service

system = system_service()

# Check API health (no authentication required)
health = await system.health()
print(f"Database: {health.database_status}")
print(f"Cache: {health.cache_status}")
print(f"API Version: {health.api_version}")
```

### Companies Service

Manage companies and developer access permissions.

```python
from vclient import companies_service
from vclient.api.models import CompanyPermission

companies = companies_service()

# List all companies (auto-paginates)
all_companies = await companies.list_all()

# Get a single page
page = await companies.get_page(limit=10, offset=0)
print(f"Total companies: {page.total}")

# Iterate through all companies (memory-efficient)
async for company in companies.iter_all():
    print(company.name)

# Get a specific company
company = await companies.get("company-id")

# Create a company
new_company = await companies.create(
    name="My Company",
    email="contact@example.com",
    description="Optional description",
)

# Update a company
updated = await companies.update(
    "company-id",
    name="New Name",
)

# Delete a company
await companies.delete("company-id")

# Grant developer access
permissions = await companies.grant_access(
    company_id="company-id",
    developer_id="developer-id",
    permission=CompanyPermission.ADMIN,
)
```

### Global Admin Service

Manage developer accounts (requires global admin privileges).

```python
from vclient import global_admin_service

admins = global_admin_service()

# List all developers
developers = await admins.list_all()

# Filter by admin status
global_admins = await admins.list_all(is_global_admin=True)

# Get a specific developer
developer = await admins.get("developer-id")

# Create a developer
new_dev = await admins.create(
    username="newuser",
    email="user@example.com",
    is_global_admin=False,
)

# Generate a new API key (invalidates existing key)
dev_with_key = await admins.create_api_key("developer-id")
print(f"New API Key: {dev_with_key.api_key}")  # Save this - only shown once!

# Update a developer
updated = await admins.update(
    "developer-id",
    username="newusername",
)

# Delete a developer
await admins.delete("developer-id")
```

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

# Access nested models
if company.settings:
    print(company.settings.permission_grant_xp)
```

### Available Models

| Model | Description |
|-------|-------------|
| `Company` | Company entity with name, email, settings, and metadata |
| `CompanySettings` | Configuration options for a company |
| `CompanyPermission` | Enum for permission levels (USER, ADMIN, OWNER, REVOKE) |
| `CompanyPermissions` | Response from granting developer access |
| `Developer` | Developer account with username, email, and admin status |
| `SystemHealth` | API health status including database and cache status |
| `ServiceStatus` | Enum for service status (ONLINE, OFFLINE) |

## Type Hints

This package includes PEP 561 type hint support via the `py.typed` marker. Type checkers like mypy and pyright will automatically use the package's type annotations.

## Imports

```python
# Factory functions for service access (recommended)
from vclient import (
    VClient,
    configure_default_client,
    default_client,
    companies_service,
    global_admin_service,
    system_service,
)

# Configuration and exceptions
from vclient import APIConfig, APIError, NotFoundError, ValidationError

# Import specific models
from vclient.api.models import (
    Company,
    CompanyPermission,
    Developer,
    SystemHealth,
    ServiceStatus,
)

# Import service classes directly (for type hints or manual instantiation)
from vclient.api import (
    CompaniesService,
    GlobalAdminService,
    SystemService,
)
```
