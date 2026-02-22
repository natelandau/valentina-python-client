---
icon: lucide/package
---

# Valentina Noir Python Client

The `valentina-python-client` package is an async Python client for the [Valentina Noir REST API](https://docs.valentina-noir.com). It wraps the API in type-safe Pydantic models, handles pagination and retries automatically, and lets you focus on building your application instead of managing HTTP requests.

!!! note

    This client library is a convenience for Python developers. It isn't required to use the Valentina Noir API — you can integrate with any HTTP client in any language by following the [full API documentation](https://docs.valentina-noir.com).

## Why Use This Client?

You can call the Valentina Noir API directly with any HTTP library, but this client removes the boilerplate:

- **Type safety** — Every request and response is validated through Pydantic models, catching errors early and giving you full IDE autocompletion.
- **Automatic pagination** — Stream through large result sets with `iter_all()` or fetch everything at once with `list_all()`, without writing pagination logic yourself.
- **Built-in retries** — Rate limits (429), server errors (5xx), and network failures are retried automatically with exponential backoff.
- **Async-first** — Built on httpx for efficient, non-blocking HTTP operations that integrate naturally into async Python applications.
- **Idempotency support** — Enable automatic idempotency keys so retried writes don't create duplicate resources.
- **Structured logging** — Optional Loguru-based logging with a stdlib bridge for debugging and observability.

## Requirements

- Python 3.13+
- A [Valentina API key](https://docs.valentina-noir.com/technical/authentication/)

## Installation

```bash
# Using uv
uv add valentina-python-client

# Using pip
pip install valentina-python-client
```

## Quick Start

Create a client once at application startup, then access API services from anywhere in your code.

### 1. Create the Client

```python
from vclient import VClient

client = VClient(
    base_url="https://api.valentina-noir.com",
    api_key="YOUR_API_KEY",
)
```

You can also set `VALENTINA_CLIENT_BASE_URL` and `VALENTINA_CLIENT_API_KEY` as [environment variables](configuration.md#environment-variables) and create the client with no arguments:

```python
client = VClient()
```

### 2. Use Services

The preferred way to interact with the API is through factory functions like `companies_service()` and `campaigns_service()`. Once a `VClient` is created, these functions are available from any module — you don't need to pass the client around or instantiate service classes directly.

```python
import asyncio
from vclient import VClient, companies_service, campaigns_service

async def main():
    async with VClient() as client:
        # List all companies you have access to
        companies = companies_service()
        for company in await companies.list_all():
            print(f"Company: {company.name}")

        # Fetch campaigns for a specific user
        campaigns = campaigns_service(
            user_id="USER_ID",
            company_id="COMPANY_ID",
        )
        for campaign in await campaigns.list_all():
            print(f"Campaign: {campaign.name}")

asyncio.run(main())
```

## Learn More

Detailed guides are available for each aspect of the client:

| Topic                              | Description                                                             |
| ---------------------------------- | ----------------------------------------------------------------------- |
| [Configuration](configuration.md)  | Timeouts, retries, environment variables, idempotency, and logging      |
| [Services](services/index.md)      | Available services, method signatures, scoping, and pagination patterns |
| [Response Models](models/index.md) | Pydantic model specifications for all API resources                     |
| [Error Handling](errors.md)        | Exception hierarchy, HTTP status mapping, and usage examples            |

## Resources

- [Valentina Noir API Documentation](https://docs.valentina-noir.com)
- [Source Code on GitHub](https://github.com/natelandau/valentina-python-client)
