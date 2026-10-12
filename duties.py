"""Duty tasks for the project."""

from __future__ import annotations

import os
import re
import shlex
import shutil
import sys
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from duty import duty
from rich.console import Console

if TYPE_CHECKING:
    from duty.context import Context


console = Console()
PYPROJECT = Path("pyproject.toml")
PY_SRC_PATHS = (Path(_) for _ in ("src/", "tests/", "duties.py", "scripts/") if Path(_).exists())
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
# Matches gate-cache's rule for when a variable is on, so duty and gate-cache agree on CI
CI = os.environ.get("CI", "").strip().lower() not in {"", "0", "false"}
PROJECT_ROOT = Path(__file__).parent
VERSION = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]
DEV_DIR = PROJECT_ROOT / ".dev"
DEV_DIRECTORIES = [
    DEV_DIR / "logs",
    DEV_DIR / "redis",
    DEV_DIR / "mongodb",
]


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from a string.

    Args:
        text (str): String to remove ANSI escape sequences from.

    Returns:
        str: String without ANSI escape sequences.
    """
    ansi_chars = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")

    # Replace [ with \[ so rich doesn't interpret output as style tags
    return ansi_chars.sub("", text).replace("[", r"\[")


def gated(name: str, cmd: list[str]) -> list[str]:
    """Wrap a gate command in gate-cache so it skips on a tree where it already passed.

    Args:
        name (str): Marker name for the gate.
        cmd (list[str]): Command to run.

    Returns:
        list[str]: The command prefixed with the gate-cache invocation.
    """
    return ["gate-cache", "--name", name, "--", *cmd]


def pyprefix(title: str) -> str:
    """Add a prefix to the title if CI is true.

    Returns:
        str: Title with prefix if CI is true.
    """
    if CI:
        prefix = f"(python{sys.version_info.major}.{sys.version_info.minor})"
        return f"{prefix:14}{title}"
    return title


@duty()
def dev_clean(ctx: Context) -> None:  # noqa: ARG001
    """Clean the development environment."""
    for directory in DEV_DIRECTORIES:
        if directory.exists():
            shutil.rmtree(directory)
            console.print(f"✓ Cleaned dev env in '{directory.name}/'")


@duty(silent=True, post=[dev_clean])
def clean(ctx: Context) -> None:
    """Clean the project."""
    ctx.run("rm -rf .coverage*")
    ctx.run("rm -rf .cache")
    ctx.run("rm -rf build")
    ctx.run("rm -rf dist")
    ctx.run("rm -rf pip-wheel-metadata")
    ctx.run("rm *.log")
    ctx.run("rm *.rdb")
    ctx.run("find . -type d -name __pycache__ | xargs rm -rf")
    ctx.run("find . -name '.DS_Store' -delete")


@duty
def ruff(ctx: Context) -> None:
    """Check the code quality with ruff."""
    ctx.run(
        gated("ruff", ["ruff", "check", "--config", "pyproject.toml", "--no-fix", *PY_SRC_LIST]),
        title=pyprefix("code quality check"),
    )


@duty
def format(ctx: Context) -> None:  # noqa: A001
    """Check the code formatting with ruff."""
    # ruff formats Python fences in Markdown too, so check the whole tree
    ctx.run(
        gated("format", ["ruff", "format", "--check", "--config", "pyproject.toml", "."]),
        title=pyprefix("code formatting"),
    )


@duty
def ty(ctx: Context) -> None:
    """Check the code with ty."""
    ctx.run(
        gated("ty", ["ty", "check", "src/"]),
        title="ty check",
    )


@duty
def typos(ctx: Context) -> None:
    """Check the code with typos."""
    ctx.run(
        gated("typos", ["typos", "--config", ".typos.toml"]),
        title=pyprefix("typos check"),
    )


@duty(skip_if=CI, skip_reason="skip prek in CI environments")
def precommit(ctx: Context) -> None:
    """Run prek hooks."""
    ctx.run(
        "PREK_SKIP=ty,pytest,ruff-check,ruff-format,typos gate-cache --name prek -- prek run --all-files",
        title=pyprefix("prek hooks"),
    )


@duty(pre=[ruff, format, ty, typos, precommit], capture=CI)
def lint(ctx: Context) -> None:
    """Run all linting duties."""


@duty(capture=CI)
def update(ctx: Context) -> None:
    """Update the project."""
    ctx.run(["uv", "lock", "--upgrade"], title="update uv lock")
    ctx.run(["uv", "sync"], title="update uv sync")
    ctx.run(["prek", "autoupdate"], title="prek autoupdate")
    ctx.run(["uvx", "uv-upx", "upgrade", "run"], title="uv-upx upgrade")


@duty()
def test(ctx: Context, *cli_args: str) -> None:
    """Test package and generate coverage reports."""
    cmd = [
        "pytest",
        "tests/",
        "-c",
        "pyproject.toml",
        "--color=yes",
        "--cov",
        "--cov-config=pyproject.toml",
        "--cov-report=xml",
        "--cov-report=term",
        *cli_args,
    ]
    # Each set of arguments gets its own marker, so a filtered pass never skips the full suite
    ctx.run(
        gated(shlex.join(["test", *cli_args]), cmd),
        title=pyprefix("Running tests - this may take a while"),
        capture=CI,
    )


@duty()
def generate_sync(ctx: Context) -> None:
    """Generate synchronous client from async source and format the output."""
    ctx.run(
        [
            "uv",
            "run",
            "python",
            "-c",
            "from vclient._codegen import generate_sync; from pathlib import Path; generate_sync(Path('src/vclient'))",
        ],
        title="generate sync client",
    )
    ctx.run(
        ["uv", "run", "ruff", "format", "--config", "pyproject.toml", "src/vclient/_sync/"],
        title="format generated sync client",
    )
    ctx.run(
        ["uv", "run", "ruff", "check", "--fix", "--config", "pyproject.toml", "src/vclient/_sync/"],
        title="lint generated sync client",
    )


@duty()
def verify_sync(ctx: Context) -> None:
    """Verify the generated sync client is up to date with async source."""
    # Regenerating rewrites _sync/ when it is stale, which changes the tree, so gate-cache
    # writes a marker only when the generated client already matches the async source
    ctx.run(
        gated(
            "verify-sync",
            ["sh", "-c", "duty generate_sync && git diff --exit-code src/vclient/_sync/"],
        ),
        title="verify sync client is up to date",
    )


@duty()
def validate_constants(ctx: Context) -> None:
    """Validate client constants against the live API."""
    ctx.run(
        ["uv", "run", "python", "scripts/validate_constants.py"],
        title="validate constants",
    )
