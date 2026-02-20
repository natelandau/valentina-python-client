# External Integrations

**Analysis Date:** 2026-02-20

## APIs & External Services

**Valentina Noir API:**
- REST API - The primary Valentina Noir backend API for accessing game management, characters, campaigns, users, etc.
  - SDK/Client: httpx 0.28.1+ (async HTTP client)
  - Auth: Custom header `X-API-KEY` (via `API_KEY_HEADER` constant in `src/vclient/constants.py`)
  - Configuration: Base URL set via `VALENTINA_CLIENT_BASE_URL` env var or `base_url` constructor parameter
  - Entry point: `src/vclient/client.py` - VClient class initializes httpx.AsyncClient with base_url and headers

**Internal Options Endpoint:**
- Purpose: Runtime validation of API enum constants
- Used by: `src/vclient/validate_constants.py` and `scripts/validate_constants.py`
- Validates that local Literal type constants match live API options
- No SDK wrapper needed - called directly via httpx

## Data Storage

**Databases:**
- None - This is a client library only. It does not manage databases.
- All data persistence is handled by the Valentina Noir API server.

**File Storage:**
- AWS S3 (referenced, not integrated) - The API manages S3 asset storage
  - Referenced in constants: `S3AssetParentType`, `S3AssetType` (in `src/vclient/constants.py`)
  - Client library provides type definitions but does not directly integrate with S3
  - Asset management is abstracted through the Valentina API

**Caching:**
- None - No built-in caching layer. Callers should implement caching as needed.

## Authentication & Identity

**Auth Provider:**
- Custom API Key Authentication
  - Implementation: Header-based API key (X-API-KEY header)
  - Key location: Environment variable `VALENTINA_CLIENT_API_KEY` or constructor parameter `api_key`
  - Validation: Required at client initialization; raises ValueError if missing
  - Scoping: Global to the VClient instance; applies to all requests
  - Configuration in `src/vclient/client.py` lines 126-129

## Monitoring & Observability

**Error Tracking:**
- None built-in - Application errors are propagated as exceptions
- RFC 9457 Problem Details format used for API errors (`src/vclient/exceptions.py`)
- Error classes: `APIError`, `AuthenticationError`, `AuthorizationError`, `NotFoundError`, `ValidationError`, `ConflictError`, `RateLimitError`, `ServerError`, `RequestValidationError`
- Exceptions include status_code, title, detail, instance properties for debugging

**Logs:**
- Structured logging via loguru 0.7.3+ (`src/vclient/__init__.py`)
  - Automatically disabled on import (`logger.disable("vclient")`) to avoid spam
  - Can be enabled by caller with `logger.enable("vclient")`
  - Integration with stdlib logging for pytest caplog compatibility
  - Structured fields support for context binding (base_url, timeout, max_retries, etc.)
  - Log entries prefixed with "vclient" namespace for filtering

**Rate Limiting:**
- Response header parsing for rate limit info: `RateLimit-Policy` and `RateLimit` headers
- Auto-retry on 429 status code when `auto_retry_rate_limit=True` (default)
- Rate limit errors raise `RateLimitError` exception with `retry_after` and `remaining` properties

## CI/CD & Deployment

**Hosting:**
- Not applicable - This is a client library distributed via PyPI, not a hosted service
- Package info: `valentina-python-client` on PyPI (https://pypi.org/project/valentina-python-client/)
- Distribution via uv/pip

**CI Pipeline:**
- GitHub Actions (referenced in `.github/` directory, pre-commit config aware of GitHub workflows)
- Pre-commit hooks configured via `.pre-commit-config.yaml`:
  - commitizen for conventional commits validation
  - ruff for linting and formatting
  - typos for spell checking
  - gitleaks for secret detection
  - pytest integration for test validation
  - ty for type checking
  - shellcheck for shell script linting
  - yamllint for YAML validation

## Environment Configuration

**Required env vars:**
- `VALENTINA_CLIENT_API_KEY` - API authentication key (required at runtime)
- `VALENTINA_CLIENT_BASE_URL` - Valentina API base URL (required at runtime)

**Optional env vars:**
- `VALENTINA_CLIENT_DEFAULT_COMPANY_ID` - Default company scope for service factory functions

**Secrets location:**
- `.env.secret` file (in project root, git-ignored, contains API credentials)
- Environment variables (for deployment)
- Constructor arguments (for programmatic initialization, highest precedence)

**Reading secrets:**
- Secrets are NOT read automatically from .env files
- Callers must:
  1. Use constructor parameters: `VClient(api_key="...", base_url="...")`
  2. Set environment variables: `export VALENTINA_CLIENT_API_KEY=...`
  3. Use a dotenv loader if needed (not included)

## Idempotency & Idempotent Requests

**Feature:**
- Optional automatic idempotency key generation
- Configuration: `auto_idempotency_keys=False` (default) in VClient constructor
- Header: `Idempotency-Key` header with UUID v4 values (`src/vclient/constants.py`)
- Use case: POST/PUT/PATCH requests can optionally include idempotency keys for safe retry logic
- Implementation: `BaseService._generate_idempotency_key()` in `src/vclient/services/base.py`

## Webhooks & Callbacks

**Incoming:**
- Not applicable - This is a client library. The Valentina API may send webhooks but that's server-side.

**Outgoing:**
- Not applicable - Client library does not initiate webhooks or callbacks.

## Export and Documentation Integration

**Documentation:**
- External: Published documentation at https://docs.valentina-noir.com/python-api-client/
- Repository: Separate repo (`../valentina-noir/docs/python-api-client/`)
- Sync requirement: Changes to client API must be reflected in external documentation
- Documentation is managed by zensical and navigation in `../valentina-noir/zensical.toml`

---

*Integration audit: 2026-02-20*
