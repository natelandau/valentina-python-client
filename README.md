# Valentina Python Client

Async and sync Python client library for accessing the Valentina Noir API.

## Features

- **Async and sync clients** - Both `VClient` (async) and `SyncVClient` (sync) built on httpx
- **Type-safe** - Full type hints with Pydantic models for request/response validation
- **Convenient factory pattern** - Create a client once, access services from anywhere
- **Automatic pagination** - Stream through large datasets with `iter_all()` or fetch everything with `list_all()`
- **Robust error handling** - Specific exception types for different error conditions
- **Idempotency support** - Optional automatic idempotency keys for safe retries
- **Rate limit handling** - Built-in support for automatic rate limit retries

This client is a supported and up-to-date reference implementation for the [Valentina Noir API](https://docs.valentina-noir.com).

## Documentation

The full documentation is available at https://natelandau.github.io/valentina-python-client/.

## Development Tools

### Validate Constants

Verify that the `Literal` type constants in this package are in sync with the live API's `/options` endpoint. This catches drift between client and server before a release.

```bash
# Via duty task
uv run duty validate_constants

# Via script directly
uv run python scripts/validate_constants.py --api-key <key> --company-id <id>
```

The script reads configuration from (highest precedence first):

1. CLI arguments (`--api-url`, `--api-key`, `--company-id`)
2. System environment variables (`VALENTINA_CLIENT_BASE_URL`, `VALENTINA_CLIENT_API_KEY`, `VALENTINA_CLIENT_DEFAULT_COMPANY_ID`)
3. A `.env.secret` file in the project root

Exit codes: `0` = all constants match, `1` = mismatches found, `2` = missing configuration.
