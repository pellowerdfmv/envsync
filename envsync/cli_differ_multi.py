"""CLI sub-command: multi-diff — compare several .env files against a reference."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envsync.differ_multi import diff_multi


def build_multi_diff_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "multi-diff",
        help="Diff multiple .env files against a reference file.",
    )
    p.add_argument("reference", type=Path, help="Reference .env file (source of truth).")
    p.add_argument(
        "targets",
        type=Path,
        nargs="+",
        help="One or more .env files to compare against the reference.",
    )
    p.add_argument(
        "--values",
        action="store_true",
        default=False,
        help="Also report value differences (not just missing / extra keys).",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any target differs from the reference.",
    )
    return p


def cmd_multi_diff(args: argparse.Namespace) -> int:
    reference: Path = args.reference
    targets: list[Path] = args.targets

    if not reference.exists():
        print(f"error: reference file not found: {reference}", file=sys.stderr)
        return 1

    missing = [t for t in targets if not t.exists()]
    if missing:
        for m in missing:
            print(f"error: target file not found: {m}", file=sys.stderr)
        return 1

    result = diff_multi(reference, targets, compare_values=args.values)
    print(result.summary())

    if args.strict and result.has_differences():
        return 1
    return 0


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(prog="envsync-multi-diff")
    sub = parser.add_subparsers(dest="command")
    build_multi_diff_parser(sub)
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    sys.exit(cmd_multi_diff(args))
