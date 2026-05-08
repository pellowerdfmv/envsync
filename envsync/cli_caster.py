"""CLI sub-commands for the env caster."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

from envsync.parser import parse_env_file
from envsync.caster import cast_env


def build_cast_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "cast",
        help="Cast .env values to typed Python objects using a JSON schema.",
    )
    p.add_argument("env_file", help="Path to the .env file.")
    p.add_argument(
        "--schema",
        metavar="JSON",
        default="{}",
        help='JSON object mapping key names to types, e.g. \'{"PORT":"int","DEBUG":"bool"}\'',
    )
    p.add_argument(
        "--output",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary).",
    )
    p.set_defaults(func=cmd_cast)
    return p


def cmd_cast(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 1

    try:
        schema: Dict[str, str] = json.loads(args.schema)
    except json.JSONDecodeError as exc:
        print(f"error: invalid schema JSON: {exc}", file=sys.stderr)
        return 1

    env = parse_env_file(env_path)
    result = cast_env(env, schema)

    if args.output == "json":
        print(json.dumps(result.values, indent=2, default=str))
    else:
        print(result.summary())

    return 1 if result.has_errors() else 0
