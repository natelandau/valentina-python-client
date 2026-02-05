# Valentina Python Client

Async Python client library for accessing the Valentina Noir API.

## Features

-   **Async-first design** - Built on httpx for efficient async HTTP operations
-   **Type-safe** - Full type hints with Pydantic models for request/response validation
-   **Convenient factory pattern** - Create a client once, access services from anywhere
-   **Automatic pagination** - Stream through large datasets with `iter_all()` or fetch everything with `list_all()`
-   **Robust error handling** - Specific exception types for different error conditions
-   **Idempotency support** - Optional automatic idempotency keys for safe retries
-   **Rate limit handling** - Built-in support for automatic rate limit retries

This client is a supported and up-to-date reference implementation for the Valentina Noir API. The full documentation for is available at https://docs.valentina-noir.com/python-api-client/.

## Documentation

For complete documentation including configuration options, all available services, response models, and error handling, see the **[Full Documentation](https://docs.valentina-noir.com/python-api-client/)**.

## Resources

-   [Full Client Documentation](https://docs.valentina-noir.com/python-api-client/)
-   [API Concepts](https://docs.valentina-noir.com/concepts/)
-   [API Reference](https://api.valentina-noir.com/docs)
