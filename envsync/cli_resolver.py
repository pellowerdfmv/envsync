"""CLI helpers for the ``resolve`` sub-command."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from envsync.exporter import export_env
from envsync.resolver import has_overrides, resolve_envs, summary


def build_resolve_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *resolve* sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "resolve",
        help="Merge multiple .env files into a single resolved set of variables.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help=".env files in ascending priority order (last file wins).",
    )
    p.add_argument(
        "--first-wins",
        action="store_true",
        default=False,
        help="Reverse priority so that the first file takes precedence.",
    )
    p.add_argument(
        "--format",
        choices=["env", "json", "yaml", "shell"],
        default="env",
        help="Output format for the resolved variables (default: env).",
    )
    p.add_argument(
        "--show-sources",
        action="store_true",
        default=False,
        help="Print the source file for each resolved key.",
    )
    p.set_defaults(func=cmd_resolve)


def cmd_resolve(args: argparse.Namespace) -> int:
    """Execute the *resolve* sub-command.

    Returns an exit code: 0 on success, 1 when overrides were detected and
    ``--strict`` semantics are implied by the caller.
    """
    paths: List[Path] = [Path(f) for f in args.files]

    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"[error] File not found: {m}")
        return 1

    result = resolve_envs(paths, reverse_priority=args.first_wins)

    print(summary(result))
    print()

    if args.show_sources:
        for key, src in sorted(result.sources.items()):
            print(f"  {key} <- {src}")
        print()

    output = export_env(result.resolved, fmt=args.format)
    print(output)

    return 0
