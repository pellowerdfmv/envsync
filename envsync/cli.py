"""Command-line interface for envsync."""

from __future__ import annotations

import argparse
import sys

from envsync.parser import parse_env_file
from envsync.validator import validate
from envsync.differ import diff_envs
from envsync.auditor import audit_env


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envsync",
        description="Sync and validate .env files across environments.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # check
    check_p = sub.add_parser("check", help="Validate a .env file against a reference template.")
    check_p.add_argument("reference", help="Reference / template .env file")
    check_p.add_argument("target", help="Target .env file to validate")

    # diff
    diff_p = sub.add_parser("diff", help="Show differences between two .env files.")
    diff_p.add_argument("source", help="Source .env file")
    diff_p.add_argument("target", help="Target .env file")
    diff_p.add_argument("--values", action="store_true", help="Include value differences")

    # audit  <-- new sub-command
    audit_p = sub.add_parser("audit", help="Audit a .env file for security and quality issues.")
    audit_p.add_argument("target", help=".env file to audit")

    return parser


def cmd_check(args: argparse.Namespace) -> int:
    ref = parse_env_file(args.reference)
    tgt = parse_env_file(args.target)
    result = validate(ref, tgt, args.target)
    print(result.summary())
    return 0 if result.is_valid else 1


def cmd_diff(args: argparse.Namespace) -> int:
    src = parse_env_file(args.source)
    tgt = parse_env_file(args.target)
    result = diff_envs(src, tgt, compare_values=args.values)
    print(result.summary())
    return 0 if not result.has_differences else 1


def cmd_audit(args: argparse.Namespace) -> int:
    env = parse_env_file(args.target)
    result = audit_env(args.target, env)
    print(result.summary())
    return 0 if not result.has_issues else 1


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "check": cmd_check,
        "diff": cmd_diff,
        "audit": cmd_audit,
    }

    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    sys.exit(handler(args))


if __name__ == "__main__":
    main()
