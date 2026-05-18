"""CLI commands for the archiver module."""
from __future__ import annotations

import argparse
from pathlib import Path

from envsync.archiver import archive_envs, restore_archive


def build_archive_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("archive", help="Bundle .env files into a compressed archive")
    p.add_argument("files", nargs="+", help=".env files to archive")
    p.add_argument("--out", required=True, help="Destination .gz archive path")
    p.set_defaults(func=cmd_archive)

    r = sub.add_parser("restore", help="List entries stored in an archive")
    r.add_argument("archive", help="Archive file to inspect")
    r.set_defaults(func=cmd_restore)


def cmd_archive(args: argparse.Namespace) -> int:
    paths = [Path(f) for f in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"[error] File not found: {m}")
        return 1

    dest = Path(args.out)
    result = archive_envs(paths, dest)
    print(result.summary())
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    archive = Path(args.archive)
    if not archive.exists():
        print(f"[error] Archive not found: {archive}")
        return 1

    entries = restore_archive(archive)
    if not entries:
        print("Archive is empty.")
        return 0

    for entry in entries:
        key_count = len(entry.env)
        print(f"  {entry.path}  ({key_count} keys)")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="envsync-archive")
    sub = parser.add_subparsers(dest="command")
    build_archive_parser(sub)
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        raise SystemExit(1)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
