"""CLI sub-command: filter — print .env keys matching a pattern or prefix."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envsync.filter import filter_env
from envsync.parser import parse_env_file


def build_filter_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "filter",
        help="Filter .env keys by pattern, prefix, or value presence.",
    )
    p.add_argument("env_file", help="Path to the .env file to filter.")
    p.add_argument("-p", "--pattern", default=None, help="Regex pattern applied to key names.")
    p.add_argument("--prefix", default=None, help="Only keys that start with this prefix.")
    p.add_argument(
        "--set-only",
        action="store_true",
        default=False,
        help="Only include keys with a non-empty value.",
    )
    p.add_argument(
        "--unset-only",
        action="store_true",
        default=False,
        help="Only include keys with a None value.",
    )
    p.add_argument(
        "--show-excluded",
        action="store_true",
        default=False,
        help="Also print excluded keys.",
    )
    return p


def cmd_filter(args: argparse.Namespace) -> int:
    path = Path(args.env_file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    env = parse_env_file(path)

    try:
        result = filter_env(
            env,
            pattern=args.pattern,
            prefix=args.prefix,
            set_only=args.set_only,
            unset_only=args.unset_only,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.summary())
    print()

    if result.matched:
        print("Matched:")
        for key, value in result.matched.items():
            display = value if value is not None else "<unset>"
            print(f"  {key}={display}")
    else:
        print("Matched: (none)")

    if args.show_excluded and result.excluded:
        print()
        print("Excluded:")
        for key in result.excluded:
            print(f"  {key}")

    return 0
