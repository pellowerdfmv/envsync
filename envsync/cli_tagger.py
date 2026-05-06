"""CLI sub-commands for the tagger module."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

from envsync.parser import parse_env_file
from envsync.tagger import tag_env


def build_tag_parser(subparsers: argparse.Action) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p: argparse.ArgumentParser = subparsers.add_parser(
        "tag",
        help="Apply metadata tags to .env keys and display a summary.",
    )
    p.add_argument("env_file", help="Path to the .env file.")
    p.add_argument(
        "--tag-file",
        metavar="FILE",
        help="JSON file mapping key names to lists of tags.",
        required=True,
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Reject tags that are not in the built-in allowed set.",
    )
    p.add_argument(
        "--filter",
        metavar="TAG",
        dest="filter_tag",
        help="Only show keys that carry this tag.",
    )
    p.set_defaults(func=cmd_tag)
    return p


def cmd_tag(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    tag_path = Path(args.tag_file)

    if not env_path.exists():
        print(f"error: env file not found: {env_path}", file=sys.stderr)
        return 1
    if not tag_path.exists():
        print(f"error: tag file not found: {tag_path}", file=sys.stderr)
        return 1

    env: Dict[str, object] = parse_env_file(env_path)
    tag_map: Dict[str, List[str]] = json.loads(tag_path.read_text())

    result = tag_env(env, tag_map, strict=args.strict)

    if args.filter_tag:
        keys = result.keys_with_tag(args.filter_tag)
        if keys:
            print(f"Keys tagged '{args.filter_tag}':")
            for k in sorted(keys):
                print(f"  {k}")
        else:
            print(f"No keys carry tag '{args.filter_tag}'.")
    else:
        print(result.summary())

    if result.unknown_tags:
        print(f"Warning: unknown tags ignored: {', '.join(result.unknown_tags)}", file=sys.stderr)

    return 0
