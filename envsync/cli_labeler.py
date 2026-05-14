"""CLI sub-command: envsync label — label env keys by category."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .labeler import label_env_file


def build_label_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *label* sub-command on *sub*."""
    p = sub.add_parser(
        "label",
        help="Label env keys with category tags defined in a JSON rules file.",
    )
    p.add_argument("env_file", type=Path, help="Path to the .env file.")
    p.add_argument(
        "--rules",
        type=Path,
        required=True,
        metavar="RULES_JSON",
        help=(
            "Path to a JSON file mapping label names to lists of key names. "
            'Example: {"database": ["DB_HOST", "DB_PORT"]}"\''
        ),
    )
    p.add_argument(
        "--label",
        metavar="LABEL",
        dest="filter_label",
        default=None,
        help="Show only keys that carry this specific label.",
    )
    p.add_argument(
        "--show-unlabeled",
        action="store_true",
        default=False,
        help="Also print keys that received no label.",
    )
    return p


def cmd_label(args: argparse.Namespace) -> int:
    """Execute the *label* sub-command; return an exit code."""
    env_path: Path = args.env_file
    rules_path: Path = args.rules

    if not env_path.exists():
        print(f"error: env file not found: {env_path}", file=sys.stderr)
        return 1

    if not rules_path.exists():
        print(f"error: rules file not found: {rules_path}", file=sys.stderr)
        return 1

    try:
        rules = json.loads(rules_path.read_text())
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in rules file: {exc}", file=sys.stderr)
        return 1

    result = label_env_file(env_path, rules)
    print(result.summary())

    if args.filter_label:
        keys = result.keys_with_label(args.filter_label)
        if keys:
            print(f"\nKeys with label '{args.filter_label}':")
            for k in sorted(keys):
                print(f"  {k}")
        else:
            print(f"\nNo keys carry label '{args.filter_label}'.")
    else:
        if result.labeled:
            print("\nLabeled keys:")
            for key, labels in sorted(result.labeled.items()):
                print(f"  {key}: {', '.join(labels)}")

    if args.show_unlabeled and result.unlabeled:
        print("\nUnlabeled keys:")
        for k in sorted(result.unlabeled):
            print(f"  {k}")

    return 0
