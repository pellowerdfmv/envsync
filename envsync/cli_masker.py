"""CLI sub-command: mask — display a .env file with sensitive values masked."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envsync.masker import mask_env
from envsync.parser import parse_env_file


def build_mask_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # noqa: SLF001
    p = subparsers.add_parser(
        "mask",
        help="Print a .env file with sensitive values masked.",
    )
    p.add_argument("env_file", help="Path to the .env file to mask.")
    p.add_argument(
        "--visible",
        type=int,
        default=4,
        metavar="N",
        help="Number of trailing characters to keep visible (default: 4).",
    )
    p.add_argument(
        "--char",
        default="*",
        metavar="CHAR",
        help="Masking character (default: '*').",
    )
    p.add_argument(
        "--extra-keys",
        nargs="*",
        default=[],
        metavar="KEY",
        help="Additional key names to treat as sensitive.",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary line after the masked output.",
    )
    return p


def cmd_mask(args: argparse.Namespace) -> int:
    """Execute the *mask* sub-command.  Returns an exit code."""
    path = Path(args.env_file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    env = parse_env_file(path)
    result = mask_env(
        env,
        visible=args.visible,
        char=args.char,
        extra_keys=tuple(args.extra_keys),
    )

    for key, value in result.masked.items():
        display = "" if value is None else value
        print(f"{key}={display}")

    if args.summary:
        print()
        print(result.summary())

    return 0
