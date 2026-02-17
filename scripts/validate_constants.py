"""Validate client constants against the live Valentina API.

Usage:
    uv run python scripts/validate_constants.py --company-id <id>

Environment variables:
    VALENTINA_API_URL: Base URL for the API (default: https://api.valentina-noir.com)
    VALENTINA_API_KEY: API key for authentication
    VALENTINA_COMPANY_ID: Company ID (alternative to --company-id flag)
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys


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


def cli() -> int:
    """Parse CLI arguments and run validation.

    Returns:
        Exit code: 0 if valid, 1 if mismatches, 2 if configuration error.
    """
    parser = argparse.ArgumentParser(
        description="Validate vclient constants against the live API.",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("VALENTINA_API_URL", "https://api.valentina-noir.com"),
        help="Base URL for the API (env: VALENTINA_API_URL)",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("VALENTINA_API_KEY"),
        help="API key (env: VALENTINA_API_KEY)",
    )
    parser.add_argument(
        "--company-id",
        default=os.environ.get("VALENTINA_COMPANY_ID"),
        help="Company ID (env: VALENTINA_COMPANY_ID)",
    )
    args = parser.parse_args()

    if not args.api_key:
        print("Error: --api-key or VALENTINA_API_KEY environment variable is required.")
        return 2

    if not args.company_id:
        print("Error: --company-id or VALENTINA_COMPANY_ID environment variable is required.")
        return 2

    return asyncio.run(main(args.api_url, args.api_key, args.company_id))


if __name__ == "__main__":
    sys.exit(cli())
