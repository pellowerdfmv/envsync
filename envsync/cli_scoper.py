"""CLI sub-command: envsync scope — filter an env file to a named scope."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envsync.parser import parse_env_file
from envsync.scoper import scope_env


def build_scope_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *scope* sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "scope",
        help="Filter an .env file to a declared set of allowed keys.",
    )
    p.add_argument("env_file", help="Path to the .env file to filter.")
    p.add_argument(
        "keys",
        nargs="+",
        help="Allowed key names that belong to this scope.",
    )
    p.add_argument(
        "--scope",
        default="default",
        help="Label for the scope (default: 'default').",
    )
    p.add_argument(
        "--show-excluded",
        action="store_true",
        help="Also print the excluded keys.",
    )
    p.set_defaults(func=cmd_scope)


def cmd_scope(args: argparse.Namespace) -> int:
    """Execute the *scope* sub-command. Returns an exit code."""
    path = Path(args.env_file)
    if not path.exists():
        print(f"[error] File not found: {path}", file=sys.stderr)
        return 1

    env = parse_env_file(path)
    result = scope_env(env, args.keys, scope=args.scope)

    print(result.summary())
    print()

    if result.included:
        print("Included:")
        for key, value in result.included.items():
            display = value if value is not None else "<unset>"
            print(f"  {key}={display}")
    else:
        print("  (no keys included)")

    if args.show_excluded and result.excluded:
        print()
        print("Excluded:")
        for key in result.excluded:
            print(f"  {key}")

    return 0
