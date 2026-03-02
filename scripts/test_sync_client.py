"""Smoke-test the synchronous client against the live Valentina API.

Mirrors the validate_constants script but uses SyncVClient instead of VClient
to verify the sync client works end-to-end.

Usage:
    uv run python scripts/test_sync_client.py
    uv run python scripts/test_sync_client.py --company-id <id>

Configuration (highest precedence wins):
    1. CLI arguments (--api-url, --api-key, --company-id)
    2. System environment variables
    3. .env.secret file in the project root

Environment variables:
    VALENTINA_CLIENT_BASE_URL: Base URL for the API (default: https://api.valentina-noir.com)
    VALENTINA_CLIENT_API_KEY: API key for authentication
    VALENTINA_CLIENT_DEFAULT_COMPANY_ID: Company ID (alternative to --company-id flag)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    level="DEBUG",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>: <level>{message}</level> | <level>{extra}</level>",
    enqueue=True,
)


def main(api_url: str, api_key: str, company_id: str) -> int:
    """Run sync client smoke tests and return exit code.

    Args:
        api_url: Base URL for the Valentina API.
        api_key: API key for authentication.
        company_id: Company ID to scope requests to.

    Returns:
        0 if all tests pass, 1 on failure.
    """
    from vclient import SyncVClient

    logger.enable("vclient")

    print(f"Testing SyncVClient against {api_url}")
    print(f"Company ID: {company_id}")
    print("-" * 60)

    passed = 0
    failed = 0

    with SyncVClient(api_key=api_key, base_url=api_url) as client:
        # Test 1: List companies
        try:
            companies_svc = client.companies()
            companies = companies_svc.list_all()
            print(f"  PASS  list companies: got {len(companies)} companies")
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  list companies: {e}")
            failed += 1

        # Test 2: Get a single company
        try:
            company = client.companies().get(company_id)
            print(f"  PASS  get company: {company.name!r} (id={company.id})")
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  get company: {e}")
            failed += 1

        # Test 3: Get options/enumerations
        try:
            options_svc = client.options(company_id)
            api_options = options_svc.get_options()
            categories = list(api_options.keys())
            print(
                f"  PASS  get options: {len(categories)} categories ({', '.join(categories[:5])}...)"
            )
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  get options: {e}")
            failed += 1

        # Test 4: List users for the company
        try:
            users_svc = client.users(company_id)
            users = users_svc.list_all()
            print(f"  PASS  list users: got {len(users)} users")
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  list users: {e}")
            failed += 1

        # Test 5: Paginated access
        try:
            page = client.companies().get_page(limit=2, offset=0)
            print(f"  PASS  paginated companies: {page.total} total, got {len(page.items)} items")
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  paginated companies: {e}")
            failed += 1

    print("-" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return 0 if failed == 0 else 1


def _load_env_secrets() -> dict[str, str]:
    """Load variables from .env.secret file if it exists.

    Reads KEY=VALUE pairs from .env.secret in the project root. Ignores
    blank lines, comments (#), and inline comments. Strips optional quotes
    from values.

    Returns:
        Dictionary of variable names to values.
    """
    secrets_path = Path(__file__).resolve().parent.parent / ".env.secret"
    if not secrets_path.is_file():
        return {}

    secrets: dict[str, str] = {}
    for line in secrets_path.read_text().splitlines():
        line = line.strip()  # noqa: PLW2901
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")

        secrets[key] = value

    return secrets


def _get_config_value(key: str, secrets: dict[str, str], default: str | None = None) -> str | None:
    """Get a configuration value with precedence: system env > .env.secret > default.

    Args:
        key: The environment variable name.
        secrets: Values loaded from .env.secret.
        default: Fallback value if not found elsewhere.

    Returns:
        The resolved value, or None if not found.
    """
    return os.environ.get(key) or secrets.get(key) or default


def cli() -> int:
    """Parse CLI arguments and run sync client tests.

    Returns:
        Exit code: 0 if all pass, 1 if failures, 2 if configuration error.
    """
    secrets = _load_env_secrets()

    parser = argparse.ArgumentParser(
        description="Smoke-test the SyncVClient against the live API.",
    )
    parser.add_argument(
        "--api-url",
        default=_get_config_value(
            "VALENTINA_CLIENT_BASE_URL", secrets, "https://api.valentina-noir.com"
        ),
        help="Base URL for the API (env: VALENTINA_CLIENT_BASE_URL)",
    )
    parser.add_argument(
        "--api-key",
        default=_get_config_value("VALENTINA_CLIENT_API_KEY", secrets),
        help="API key (env: VALENTINA_CLIENT_API_KEY)",
    )
    parser.add_argument(
        "--company-id",
        default=_get_config_value("VALENTINA_CLIENT_DEFAULT_COMPANY_ID", secrets),
        help="Company ID (env: VALENTINA_CLIENT_DEFAULT_COMPANY_ID)",
    )
    args = parser.parse_args()

    if not args.api_key:
        print("Error: --api-key or VALENTINA_CLIENT_API_KEY environment variable is required.")
        return 2

    if not args.company_id:
        print(
            "Error: --company-id or VALENTINA_CLIENT_DEFAULT_COMPANY_ID"
            " environment variable is required."
        )
        return 2

    return main(args.api_url, args.api_key, args.company_id)


if __name__ == "__main__":
    sys.exit(cli())
