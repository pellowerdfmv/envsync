"""Parser for .env files — reads and tokenizes key-value pairs."""

import re
from typing import Dict, Optional

ENV_LINE_PATTERN = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)
COMMENT_PATTERN = re.compile(r'^\s*#.*$')


def parse_env_file(filepath: str) -> Dict[str, Optional[str]]:
    """
    Parse a .env file and return a dict of key -> value.
    Values may be None if the key is declared without a value.
    Blank lines and comments are ignored.
    """
    env_vars: Dict[str, Optional[str]] = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for lineno, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip('\n')

            if not line.strip() or COMMENT_PATTERN.match(line):
                continue

            match = ENV_LINE_PATTERN.match(line)
            if not match:
                raise ValueError(
                    f"Invalid syntax on line {lineno} in '{filepath}': {line!r}"
                )

            key = match.group('key')
            raw_value = match.group('value').strip()
            value = _strip_quotes(raw_value) if raw_value else None
            env_vars[key] = value

    return env_vars


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value string."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value
