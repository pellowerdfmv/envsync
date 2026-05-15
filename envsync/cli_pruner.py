"""cli_pruner.py – CLI sub-command for pruning keys from a .env file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pruner import prune_file


def build_prune_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser("prune", help="Remove keys from a .env file by name or pattern")
    p.add_argument("env_file", type=Path, help="Path to the .env file")
    p.add_argument(
        "-k", "--key",
        dest="keys",
        metavar="KEY",
        action="append",
        default=[],
        help="Exact key name to remove (repeatable)",
    )
    p.add_argument(
        "-p", "--pattern",
        dest="patterns",
        metavar="REGEX",
        action="append",
        default=[],
        help="Regex pattern; matching keys are removed (repeatable)",
    )
    p.add_argument("-q", "--quiet", action="store_true", help="Suppress output")
    return p


def cmd_prune(args: argparse.Namespace) -> int:
    """Entry point for the *prune* sub-command."""
    path: Path = args.env_file
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    result = prune_file(path, keys=args.keys, patterns=args.patterns)

    if not args.quiet:
        print(result.summary())
        if result.has_removals():
            for k in result.removed_keys:
                print(f"  - {k}")

    return 0


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(prog="envsync-prune")
    sub = parser.add_subparsers(dest="command")
    build_prune_parser(sub)
    args = parser.parse_args()
    sys.exit(cmd_prune(args))
