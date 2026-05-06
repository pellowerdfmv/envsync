"""Command-line interface for envsync."""

from __future__ import annotations

import argparse
import sys

from envsync.auditor import audit
from envsync.differ import diff_envs
from envsync.exporter import export_env
from envsync.merger import merge_envs
from envsync.reporter import Report
from envsync.validator import validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envsync",
        description="Sync and validate .env files across environments.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # check
    chk = sub.add_parser("check", help="Validate env files against a reference.")
    chk.add_argument("reference", help="Reference .env file.")
    chk.add_argument("targets", nargs="+", help="Target .env files to validate.")

    # diff
    dif = sub.add_parser("diff", help="Show differences between two env files.")
    dif.add_argument("source", help="Source .env file.")
    dif.add_argument("target", help="Target .env file.")
    dif.add_argument("--values", action="store_true", help="Include value differences.")

    # audit
    aud = sub.add_parser("audit", help="Audit an env file for security issues.")
    aud.add_argument("file", help=".env file to audit.")

    # merge
    mrg = sub.add_parser("merge", help="Merge multiple env files.")
    mrg.add_argument("files", nargs="+", help=".env files to merge (in order).")
    mrg.add_argument(
        "--strategy",
        choices=["last_wins", "first_wins"],
        default="last_wins",
        help="Conflict resolution strategy (default: last_wins).",
    )
    mrg.add_argument("--output", help="Write merged result to this file.")
    mrg.add_argument(
        "--format",
        dest="fmt",
        choices=["env", "json", "yaml", "shell"],
        default="env",
        help="Output format (default: env).",
    )

    return parser


def cmd_check(args: argparse.Namespace) -> int:
    results = [validate(args.reference, t) for t in args.targets]
    report = Report._build(list(zip(args.targets, results)), [])
    print(render := report.render())
    return 0 if not report.has_issues() else 1


def cmd_diff(args: argparse.Namespace) -> int:
    result = diff_envs(args.source, args.target, compare_values=args.values)
    print(result.summary())
    return 0 if not result.has_differences() else 1


def cmd_audit(args: argparse.Namespace) -> int:
    result = audit(args.file)
    for issue in result.issues:
        level = "ERROR" if issue.level == "error" else "WARN "
        print(f"[{level}] {issue.key}: {issue.message}")
    if not result.has_issues():
        print("No issues found.")
    return 0 if not result.errors() else 1


def cmd_merge(args: argparse.Namespace) -> int:
    result = merge_envs(*args.files, strategy=args.strategy)
    print(result.summary(), file=sys.stderr)

    if args.fmt == "env":
        lines = [
            f"{k}={v}" if v is not None else f"{k}="
            for k, v in result.merged.items()
        ]
        output = "\n".join(lines) + "\n"
    else:
        output = export_env(result.merged, fmt=args.fmt)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output)
        print(f"Merged env written to {args.output}")
    else:
        print(output, end="")

    return 1 if result.has_conflicts() else 0


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {
        "check": cmd_check,
        "diff": cmd_diff,
        "audit": cmd_audit,
        "merge": cmd_merge,
    }
    sys.exit(dispatch[args.command](args))


if __name__ == "__main__":
    main()
