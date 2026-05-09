"""CLI interface for the flatten command."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envsync.flattener import flatten_env
from envsync.parser import parse_env_file


def build_flatten_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *flatten* sub-command and return its parser."""
    p = sub.add_parser(
        "flatten",
        help="Collapse delimiter-separated key segments into single keys.",
    )
    p.add_argument("env_file", help="Path to the .env file to flatten.")
    p.add_argument(
        "--delimiter",
        default="__",
        metavar="SEP",
        help="Segment separator to detect compound keys (default: '__').",
    )
    p.add_argument(
        "--no-expand",
        action="store_true",
        default=False,
        help="Disable key expansion; keys are reported but left unchanged.",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress summary output.",
    )
    p.set_defaults(func=cmd_flatten)
    return p


def cmd_flatten(args: argparse.Namespace) -> int:
    """Execute the flatten command.  Return exit code."""
    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    result = flatten_env(
        env,
        delimiter=args.delimiter,
        expand=not args.no_expand,
    )

    if not args.quiet:
        print(result.summary())

    if result.has_expansions():
        print("\nExpanded keys:")
        for original in result.expanded:
            collapsed = "_".join(original.split(args.delimiter))
            print(f"  {original!r:30s} -> {collapsed!r}")

    print("\nFlattened env:")
    for key, value in result.flattened.items():
        display = value if value is not None else ""
        print(f"  {key}={display}")

    return 0
