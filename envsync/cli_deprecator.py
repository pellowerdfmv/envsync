"""cli_deprecator.py – CLI sub-commands for the deprecation feature."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envsync.deprecator import deprecate_file


def build_deprecate_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # noqa: F821
    p = sub.add_parser(
        "deprecate",
        help="Report (or remove) deprecated keys from an env file.",
    )
    p.add_argument("env_file", type=Path, help="Path to the .env file to scan.")
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY=MSG",
        default=[],
        help="Deprecated keys with optional messages, e.g. OLD_KEY='Use NEW_KEY instead'.",
    )
    p.add_argument(
        "--schema",
        type=Path,
        default=None,
        help="JSON file mapping deprecated key names to messages.",
    )
    p.add_argument(
        "--remove",
        action="store_true",
        help="Remove deprecated keys from the output.",
    )
    return p


def _parse_key_args(raw: list[str]) -> dict[str, str]:
    """Parse ``KEY=Message`` pairs from CLI arguments."""
    result: dict[str, str] = {}
    for item in raw:
        if "=" in item:
            key, _, msg = item.partition("=")
            result[key.strip()] = msg.strip()
        else:
            result[item.strip()] = f"{item.strip()} is deprecated."
    return result


def cmd_deprecate(args: argparse.Namespace) -> int:
    if not args.env_file.exists():
        print(f"error: file not found: {args.env_file}", file=sys.stderr)
        return 1

    deprecated: dict[str, str] = {}

    if args.schema:
        if not args.schema.exists():
            print(f"error: schema not found: {args.schema}", file=sys.stderr)
            return 1
        try:
            deprecated.update(json.loads(args.schema.read_text()))
        except json.JSONDecodeError as exc:
            print(f"error: invalid JSON schema – {exc}", file=sys.stderr)
            return 1

    deprecated.update(_parse_key_args(args.keys))

    result = deprecate_file(args.env_file, deprecated, remove=args.remove)

    print(result.summary())
    if result.has_deprecated():
        for key in result.present:
            msg = deprecated.get(key, "deprecated")
            print(f"  [DEPRECATED] {key}: {msg}")
        return 1

    return 0
