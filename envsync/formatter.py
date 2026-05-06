"""Format / normalise .env file content."""
from __future__ import annotations

from typing import Dict, List, Optional


def _quote_value(value: str) -> str:
    """Wrap value in double quotes if it contains spaces or special chars."""
    needs_quoting = any(c in value for c in (' ', '\t', '#', '"', "'", '$', '\\'))
    if needs_quoting:
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return value


def format_env(
    parsed: Dict[str, Optional[str]],
    *,
    sort_keys: bool = False,
    quote_all: bool = False,
    uppercase_keys: bool = False,
) -> str:
    """Return a formatted .env string from a parsed mapping.

    Args:
        parsed: Mapping of key -> value (None means empty/unset).
        sort_keys: Alphabetically sort keys.
        quote_all: Wrap every value in double quotes.
        uppercase_keys: Convert all keys to UPPER_SNAKE_CASE.

    Returns:
        Formatted .env content as a string.
    """
    keys: List[str] = list(parsed.keys())
    if sort_keys:
        keys = sorted(keys)

    lines: List[str] = []
    for key in keys:
        out_key = key.upper() if uppercase_keys else key
        value = parsed[key]

        if value is None:
            lines.append(f"{out_key}=")
        elif quote_all:
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            lines.append(f'{out_key}="{escaped}"')
        else:
            lines.append(f"{out_key}={_quote_value(value)}")

    return '\n'.join(lines) + ('\n' if lines else '')


def normalise_file(
    src_path: str,
    dst_path: str,
    parsed: Dict[str, Optional[str]],
    **fmt_kwargs,
) -> None:
    """Write a normalised version of *parsed* to *dst_path*."""
    content = format_env(parsed, **fmt_kwargs)
    with open(dst_path, 'w', encoding='utf-8') as fh:
        fh.write(content)
