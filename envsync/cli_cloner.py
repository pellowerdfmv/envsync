"""CLI sub-command: clone — copy an .env file with optional remap/override."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Optional

from envsync.parser import parse_env_file
from envsync.cloner import clone_env
from envsync.formatter import format_env


def build_clone_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *clone* sub-command on *sub*."""
    p = sub.add_parser(
        "clone",
        help="Clone an .env file with optional key remapping and value overrides.",
    )
    p.add_argument("src", help="Source .env file.")
    p.add_argument(
        "-o", "--output",
        default=None,
        help="Destination file (default: print to stdout).",
    )
    p.add_argument(
        "--remap",
        metavar="OLD=NEW",
        nargs="*",
        default=[],
        help="Rename keys during clone, e.g. --remap DB_HOST=DATABASE_HOST.",
    )
    p.add_argument(
        "--override",
        metavar="KEY=VALUE",
        nargs="*",
        default=[],
        help="Override values after cloning, e.g. --override DEBUG=false.",
    )
    p.add_argument("--sort", action="store_true", help="Sort keys alphabetically.")
    p.set_defaults(func=cmd_clone)
    return p


def _parse_pairs(pairs: list[str]) -> Dict[str, Optional[str]]:
    """Parse ``KEY=VALUE`` strings into a dict; VALUE may be empty (-> None)."""
    out: Dict[str, Optional[str]] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Expected KEY=VALUE, got: {pair!r}")
        key, _, value = pair.partition("=")
        out[key.strip()] = value or None
    return out


def cmd_clone(args: argparse.Namespace) -> int:
    """Entry-point for the *clone* sub-command."""
    src = Path(args.src)
    if not src.exists():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 1

    try:
        remap = _parse_pairs(args.remap or [])
        overrides = _parse_pairs(args.override or [])
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    env = parse_env_file(src)
    result = clone_env(env, remap=remap, overrides=overrides)

    output = format_env(result.cloned, sort_keys=args.sort)

    if args.output:
        Path(args.output).write_text(output)
        print(result.summary())
    else:
        print(output, end="")

    return 0
