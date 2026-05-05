"""Command-line interface for envsync."""

import argparse
import sys

from envsync.differ import diff_envs
from envsync.parser import parse_env_file
from envsync.validator import validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envsync",
        description="Sync and validate .env files across environments.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # check subcommand
    check = sub.add_parser("check", help="Validate a .env file against a reference.")
    check.add_argument("reference", help="Reference env file (e.g. .env.example)")
    check.add_argument("target", help="Target env file to validate (e.g. .env)")

    # diff subcommand
    diff = sub.add_parser("diff", help="Show differences between two .env files.")
    diff.add_argument("source", help="Source env file")
    diff.add_argument("target", help="Target env file")
    diff.add_argument(
        "--values",
        action="store_true",
        default=False,
        help="Also compare values, not just keys.",
    )

    return parser


def cmd_check(args: argparse.Namespace) -> int:
    reference = parse_env_file(args.reference)
    target = parse_env_file(args.target)
    result = validate(reference, target)
    print(result.summary())
    return 0 if result.is_valid else 1


def cmd_diff(args: argparse.Namespace) -> int:
    source = parse_env_file(args.source)
    target = parse_env_file(args.target)
    result = diff_envs(source, target, compare_values=args.values)
    if result.has_differences:
        print(f"Differences between {args.source!r} and {args.target!r}:")
        print(result.summary())
        return 1
    print("No differences found.")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "check":
        sys.exit(cmd_check(args))
    elif args.command == "diff":
        sys.exit(cmd_diff(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
