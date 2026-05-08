"""CLI sub-command: ``envsync pin`` — pin keys to fixed values in an env file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from envsync.parser import parse_env_file
from envsync.pinner import pin_env


def build_pin_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *pin* sub-command on *sub*."""
    p = sub.add_parser(
        "pin",
        help="Force specific keys to fixed values in an env file.",
    )
    p.add_argument("env_file", help="Path to the .env file to update.")
    p.add_argument(
        "assignments",
        nargs="+",
        metavar="KEY=VALUE",
        help="One or more KEY=VALUE pairs to pin.",
    )
    p.add_argument(
        "--allow-new",
        action="store_true",
        default=False,
        help="Add keys that are not already present in the file.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print the result without writing to disk.",
    )
    return p


def _parse_assignments(assignments: List[str]) -> dict:
    pins: dict = {}
    for item in assignments:
        if "=" not in item:
            print(f"[error] Invalid assignment (expected KEY=VALUE): {item!r}", file=sys.stderr)
            sys.exit(1)
        key, _, value = item.partition("=")
        pins[key.strip()] = value if value != "" else None
    return pins


def cmd_pin(args: argparse.Namespace) -> int:
    """Execute the *pin* command; return an exit code."""
    path = Path(args.env_file)
    if not path.exists():
        print(f"[error] File not found: {path}", file=sys.stderr)
        return 1

    pins = _parse_assignments(args.assignments)
    env = parse_env_file(path)
    result = pin_env(env, pins, source_path=str(path), allow_new=args.allow_new)

    print(result.summary())

    if result.has_skipped():
        for key in result.skipped:
            print(f"  [skip] {key} — not found in {path}")

    if not args.dry_run:
        lines = []
        for key, value in result._merged.items():  # type: ignore[attr-defined]
            lines.append(f"{key}={value if value is not None else ''}")
        path.write_text("\n".join(lines) + "\n")
        print(f"Written to {path}")

    return 0
