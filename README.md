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

```python
import asyncio
from vclient import VClient

async def main():
    async with VClient(api_key="your-api-key") as client:
        # Check system health
        health = await client.system.health()
        print(f"API Version: {health.api_version}")
        print(f"Database: {health.database_status}")

        # List companies you have access to
        companies = await client.companies.list_all()
        for company in companies:
            print(f"Company: {company.name}")

asyncio.run(main())
```

## Using VClient Without Context Manager

For applications that need to manage the client lifecycle manually (e.g., long-running services or class-based architectures), you can instantiate `VClient` directly:

```python
from vclient import VClient

# Create the client
client = VClient(base_url="https://api.example.com", api_key="your-api-key")

# Use the client
companies = await client.companies.list_all()

# Always close the client when done to release resources
await client.close()
```

For robust error handling, use a try/finally block:

```python
client = VClient(base_url="https://api.example.com", api_key="your-api-key")
try:
    companies = await client.companies.list_all()
finally:
    await client.close()
```

You can check if the client has been closed using the `is_closed` property:

```python
if not client.is_closed:
    await client.close()
```

> **Note**: The `async with` context manager is the recommended approach as it ensures proper cleanup even when exceptions occur.

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
async with VClient(api_key="...") as client:
    # Check API health (no authentication required)
    health = await client.system.health()
    print(f"Database: {health.database_status}")
    print(f"Cache: {health.cache_status}")
    print(f"API Version: {health.api_version}")
```

### Companies Service

Manage companies and developer access permissions.

```python
async with VClient(api_key="...") as client:
    # List all companies (auto-paginates)
    companies = await client.companies.list_all()

    # Get a single page
    page = await client.companies.get_page(limit=10, offset=0)
    print(f"Total companies: {page.total}")

    # Iterate through all companies (memory-efficient)
    async for company in client.companies.iter_all():
        print(company.name)

    # Get a specific company
    company = await client.companies.get("company-id")

    # Create a company
    new_company = await client.companies.create(
        name="My Company",
        email="contact@example.com",
        description="Optional description",
    )

    # Update a company
    updated = await client.companies.update(
        "company-id",
        name="New Name",
    )

    # Delete a company
    await client.companies.delete("company-id")

    # Grant developer access
    from vclient.api.models import CompanyPermission

    permissions = await client.companies.grant_access(
        company_id="company-id",
        developer_id="developer-id",
        permission=CompanyPermission.ADMIN,
    )
```

### Global Admin Service

Manage developer accounts (requires global admin privileges).

```python
async with VClient(api_key="...") as client:
    # List all developers
    developers = await client.global_admin.list_all()

    # Filter by admin status
    admins = await client.global_admin.list_all(is_global_admin=True)

    # Get a specific developer
    developer = await client.global_admin.get("developer-id")

    # Create a developer
    new_dev = await client.global_admin.create(
        username="newuser",
        email="user@example.com",
        is_global_admin=False,
    )

    # Generate a new API key (invalidates existing key)
    dev_with_key = await client.global_admin.create_api_key("developer-id")
    print(f"New API Key: {dev_with_key.api_key}")  # Save this - only shown once!

    # Update a developer
    updated = await client.global_admin.update(
        "developer-id",
        username="newusername",
    )

    # Delete a developer
    await client.global_admin.delete("developer-id")
```

## Error Handling

The client provides specific exception types for different error conditions:

```python
from vclient import (
    VClient,
    APIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    ConflictError,
    RateLimitError,
    ServerError,
)

async with VClient(api_key="...") as client:
    try:
        company = await client.companies.get("invalid-id")
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
async with VClient(api_key="...") as client:
    company = await client.companies.get("company-id")

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
# Root level imports (most common)
from vclient import VClient, APIConfig, APIError

# Import from api submodule for more classes
from vclient.api import (
    VClient,
    CompaniesService,
    GlobalAdminService,
    SystemService,
    Company,
    Developer,
)

# Import specific models
from vclient.api.models import (
    Company,
    CompanyPermission,
    Developer,
    SystemHealth,
    ServiceStatus,
)
```
