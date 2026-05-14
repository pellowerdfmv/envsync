"""CLI sub-command: envsync extract."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .extractor import extract_env_file


def build_extract_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *extract* sub-command on *sub*."""
    p = sub.add_parser(
        "extract",
        help="Extract a subset of keys from an .env file.",
    )
    p.add_argument("env_file", type=Path, help="Source .env file.")
    p.add_argument(
        "keys",
        nargs="+",
        metavar="KEY",
        help="Keys to extract.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with error if any key is missing.",
    )
    return p


def cmd_extract(args: argparse.Namespace) -> int:
    """Execute the *extract* command; return an exit code."""
    path: Path = args.env_file
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        result = extract_env_file(path, args.keys, strict=args.strict)
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for key, value in result.extracted.items():
        display = value if value is not None else ""
        print(f"{key}={display}")

    if result.has_missing():
        print(
            f"Warning: missing keys: {', '.join(result.missing)}",
            file=sys.stderr,
        )

    print(result.summary(), file=sys.stderr)
    return 0
