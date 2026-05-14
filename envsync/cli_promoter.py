"""CLI interface for the *promote* command.

Usage examples::

    envsync-promote .env.staging .env.production
    envsync-promote .env.staging .env.production --overwrite
    envsync-promote .env.staging .env.production --keys FOO BAR
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envsync.promoter import promote_env


def build_promote_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: E501
    """Build (and optionally register) the *promote* sub-command parser."""
    kwargs = dict(
        prog="envsync-promote",
        description="Promote env values from a source file into a target file.",
    )
    if parent is not None:
        parser = parent.add_parser("promote", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("source", type=Path, help="Source .env file (e.g. .env.staging).")
    parser.add_argument("target", type=Path, help="Target .env file (e.g. .env.production).")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite keys that already exist in the target.",
    )
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        default=None,
        help="Allowlist of key names to promote (default: all).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress summary output.",
    )
    return parser


def cmd_promote(args: argparse.Namespace) -> int:
    """Execute the promote command; return an exit code."""
    if not args.source.exists():
        print(f"error: source file not found: {args.source}", file=sys.stderr)
        return 1
    if not args.target.exists():
        print(f"error: target file not found: {args.target}", file=sys.stderr)
        return 1

    result = promote_env(
        args.source,
        args.target,
        overwrite=args.overwrite,
        keys=args.keys,
    )

    if not args.quiet:
        print(result.summary())

    return 0


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    parser = build_promote_parser()
    args = parser.parse_args(argv)
    sys.exit(cmd_promote(args))


if __name__ == "__main__":  # pragma: no cover
    main()
