"""Export parsed .env data to various formats (JSON, YAML, shell script)."""

from __future__ import annotations

import json
from typing import Dict, Optional


SUPPORTED_FORMATS = ("json", "yaml", "shell")


def export_to_json(env: Dict[str, Optional[str]], indent: int = 2) -> str:
    """Serialize env dict to a JSON string."""
    return json.dumps(env, indent=indent, default=str)


def export_to_yaml(env: Dict[str, Optional[str]]) -> str:
    """Serialize env dict to a simple YAML string (no external dependency)."""
    lines = []
    for key, value in env.items():
        if value is None:
            lines.append(f"{key}: null")
        elif any(c in str(value) for c in (":", "#", "'", '"', "\n")):
            escaped = str(value).replace('"', '\\"')
            lines.append(f'{key}: "{escaped}"')
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def export_to_shell(env: Dict[str, Optional[str]]) -> str:
    """Serialize env dict to an exportable shell script."""
    lines = ["#!/usr/bin/env sh"]
    for key, value in env.items():
        if value is None:
            lines.append(f"export {key}=''")
        else:
            escaped = str(value).replace("'", "'\"'\"'")
            lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines)


def export_env(
    env: Dict[str, Optional[str]],
    fmt: str,
) -> str:
    """Dispatch export to the requested format.

    Args:
        env: Parsed key/value mapping.
        fmt: One of 'json', 'yaml', or 'shell'.

    Returns:
        Formatted string representation.

    Raises:
        ValueError: If *fmt* is not supported.
    """
    fmt = fmt.lower()
    if fmt == "json":
        return export_to_json(env)
    if fmt == "yaml":
        return export_to_yaml(env)
    if fmt == "shell":
        return export_to_shell(env)
    raise ValueError(
        f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
    )
