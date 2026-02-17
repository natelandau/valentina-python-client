"""Validate client constants against the live Valentina API.

Usage:
    uv run python scripts/validate_constants.py --company-id <id>

Configuration (highest precedence wins):
    1. CLI arguments (--api-url, --api-key, --company-id)
    2. System environment variables
    3. .env.secrets file in the project root

Environment variables:
    VALENTINA_CLIENT_BASE_URL: Base URL for the API (default: https://api.valentina-noir.com)
    VALENTINA_CLIENT_API_KEY: API key for authentication
    VALENTINA_CLIENT_DEFAULT_COMPANY_ID: Company ID (alternative to --company-id flag)
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path


async def main(api_url: str, api_key: str, company_id: str) -> int:
    """Run validation and return exit code.

    Args:
        api_url: Base URL for the Valentina API.
        api_key: API key for authentication.
        company_id: Company ID to use for the options endpoint.

    Returns:
        0 if all constants match, 1 if mismatches found.
    """
    from vclient import VClient
    from vclient.validate_constants import print_report, validate

    async with VClient(api_key=api_key, base_url=api_url) as client:
        options = client.options(company_id)
        api_options = await options.get_options()

    result = validate(api_options)
    print_report(result)

    return 0 if result.is_valid else 1


def _load_env_secrets() -> dict[str, str]:
    """Load variables from .env.secrets file if it exists.

    Reads KEY=VALUE pairs from .env.secrets in the project root. Ignores
    blank lines, comments (#), and inline comments. Strips optional quotes
    from values.

    Returns:
        Dictionary of variable names to values.
    """
    secrets_path = Path(__file__).resolve().parent.parent / ".env.secrets"
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
    """Get a configuration value with precedence: system env > .env.secrets > default.

    Args:
        key: The environment variable name.
        secrets: Values loaded from .env.secrets.
        default: Fallback value if not found elsewhere.

    Returns:
        The resolved value, or None if not found.
    """
    return os.environ.get(key) or secrets.get(key) or default


def cli() -> int:
    """Parse CLI arguments and run validation.

    Returns:
        Exit code: 0 if valid, 1 if mismatches, 2 if configuration error.
    """
    secrets = _load_env_secrets()

    parser = argparse.ArgumentParser(
        description="Validate vclient constants against the live API.",
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

    return asyncio.run(main(args.api_url, args.api_key, args.company_id))


if __name__ == "__main__":
    sys.exit(cli())
