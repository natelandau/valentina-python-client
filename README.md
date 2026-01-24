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

| Service | Factory Function | Description |
|---------|------------------|-------------|
| [System Service](docs/system-service.md) | `system_service()` | Health checks and system status |
| [Companies Service](docs/companies-service.md) | `companies_service()` | Manage companies and permissions |
| [Developers Service](docs/developers-service.md) | `developer_service()` | Manage your own developer profile |
| [Global Admin Service](docs/global-admin-service.md) | `global_admin_service()` | Manage developer accounts (requires admin) |

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

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `APIError` | - | Base class for all API errors |
| `AuthenticationError` | 401 | Invalid or missing API key |
| `AuthorizationError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `ValidationError` | 422 | Invalid request data |
| `ConflictError` | 409 | Resource conflict |
| `RateLimitError` | 429 | Rate limit exceeded |
| `ServerError` | 5xx | Server-side error |

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
