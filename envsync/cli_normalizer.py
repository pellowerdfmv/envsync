"""CLI sub-command: envsync normalize."""
from __future__ import annotations

import argparse
from pathlib import Path

from .normalizer import normalize_file


def build_normalize_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *normalize* sub-command on *sub*."""
    p = sub.add_parser(
        "normalize",
        help="Normalize .env key names to UPPER_SNAKE_CASE",
    )
    p.add_argument("env_file", type=Path, help="Path to the .env file")
    p.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output when no changes are detected",
    )
    p.add_argument(
        "--show-renamed",
        action="store_true",
        help="List every renamed key",
    )
    return p


def cmd_normalize(args: argparse.Namespace) -> int:
    """Execute the *normalize* sub-command.  Returns an exit code."""
    path: Path = args.env_file

    if not path.exists():
        print(f"error: file not found: {path}")
        return 1

    result = normalize_file(path)

    if result.has_changes or not args.quiet:
        print(result.summary())

    if args.show_renamed:
        for original, canon in result.renamed:
            print(f"  {original!r} -> {canon!r}")

    return 0
