"""CLI sub-commands for the aliaser module."""
from __future__ import annotations

import argparse
import sys
from typing import Dict

from envsync.aliaser import alias_env
from envsync.parser import parse_env_file


def build_alias_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *alias* sub-command."""
    p = sub.add_parser(
        "alias",
        help="Create aliased copies of env keys.",
    )
    p.add_argument("env_file", help="Path to the .env file.")
    p.add_argument(
        "mapping",
        nargs="+",
        metavar="NEW=ORIGINAL",
        help="One or more alias mappings in NEW_KEY=ORIGINAL_KEY format.",
    )
    p.add_argument(
        "--drop-original",
        action="store_true",
        default=False,
        help="Remove the original key after aliasing.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 when any source key is missing.",
    )
    return p


def _parse_mappings(raw: list[str]) -> Dict[str, str]:
    """Parse ``NEW=ORIGINAL`` strings into a dict."""
    result: Dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                f"Invalid mapping {item!r}. Expected NEW_KEY=ORIGINAL_KEY."
            )
        new, _, original = item.partition("=")
        result[new.strip()] = original.strip()
    return result


def cmd_alias(args: argparse.Namespace) -> int:
    """Execute the *alias* command.  Returns an exit code."""
    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    try:
        aliases = _parse_mappings(args.mapping)
    except argparse.ArgumentTypeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = alias_env(env, aliases, keep_original=not args.drop_original)

    for key, value in sorted(result.env.items()):
        display = value if value is not None else ""
        print(f"{key}={display}")

    if result.has_missing():
        for src in result.missing:
            print(f"Warning: source key not found: {src}", file=sys.stderr)
        if args.strict:
            return 1

    print(f"\n# {result.summary()}", file=sys.stderr)
    return 0
