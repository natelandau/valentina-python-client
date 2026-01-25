"""Constants for the API client."""

# Authentication
API_KEY_HEADER = "X-API-KEY"


# Request defaults
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0

# Pagination defaults
DEFAULT_PAGE_LIMIT = 10
MAX_PAGE_LIMIT = 100

# HTTP Status Code Ranges (5xx Server Errors)
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_600_UPPER_BOUND = 600

# Idempotency
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"

# Rate Limiting Headers
RATE_LIMIT_HEADER = "RateLimit"
RATE_LIMIT_POLICY_HEADER = "RateLimit-Policy"
