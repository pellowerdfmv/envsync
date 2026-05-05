"""Command-line interface for envsync."""

import argparse
import sys

from envsync.validator import validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='envsync',
        description='Sync and validate .env files across project environments.',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    check_cmd = subparsers.add_parser(
        'check',
        help='Validate a .env file against a .env.example template.',
    )
    check_cmd.add_argument(
        '--env', default='.env', metavar='FILE',
        help='Path to the .env file (default: .env)',
    )
    check_cmd.add_argument(
        '--example', default='.env.example', metavar='FILE',
        help='Path to the template file (default: .env.example)',
    )
    check_cmd.add_argument(
        '--strict', action='store_true',
        help='Fail if the .env file contains keys not present in the template.',
    )
    return parser


def cmd_check(args: argparse.Namespace) -> int:
    try:
        result = validate(args.env, args.example, strict=args.strict)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"parse error: {exc}", file=sys.stderr)
        return 2

    print(result.summary())

    if not result.is_valid:
        return 1
    if args.strict and result.extra_keys:
        return 1
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    handlers = {'check': cmd_check}
    sys.exit(handlers[args.command](args))


if __name__ == '__main__':
    main()
