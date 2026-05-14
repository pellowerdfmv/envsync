"""stringer.py – Convert an env mapping to various string representations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class StringResult:
    """Result returned by stringify_env."""

    content: str
    format: str
    key_count: int
    source_path: Optional[str] = None
    _env: Dict[str, Optional[str]] = field(default_factory=dict, repr=False)

    def __len__(self) -> int:  # noqa: D105
        return self.key_count

    def summary(self) -> str:  # noqa: D102
        src = f" ({self.source_path})" if self.source_path else ""
        return (
            f"Stringified {self.key_count} key(s) as '{self.format}'{src}."
        )


def _to_dotenv(env: Dict[str, Optional[str]]) -> str:
    """Render env as a .env-style string."""
    lines: list[str] = []
    for key, value in env.items():
        if value is None:
            lines.append(f"{key}=")
        else:
            needs_quotes = any(c in value for c in (" ", "\t", "#", "'", '"'))
            if needs_quotes:
                escaped = value.replace('"', '\\"')
                lines.append(f'{key}="{escaped}"')
            else:
                lines.append(f"{key}={value}")
    return "\n".join(lines)


def _to_export(env: Dict[str, Optional[str]]) -> str:
    """Render env as shell export statements."""
    lines: list[str] = []
    for key, value in env.items():
        if value is None:
            lines.append(f"export {key}=''")
        else:
            escaped = value.replace("'", "'\"'\"'")
            lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines)


def _to_inline(env: Dict[str, Optional[str]]) -> str:
    """Render env as a single-line space-separated KEY=VALUE string."""
    parts: list[str] = []
    for key, value in env.items():
        v = "" if value is None else value
        parts.append(f"{key}={v}")
    return " ".join(parts)


_FORMATS = {
    "dotenv": _to_dotenv,
    "export": _to_export,
    "inline": _to_inline,
}


def stringify_env(
    env: Dict[str, Optional[str]],
    fmt: str = "dotenv",
    source_path: Optional[str] = None,
) -> StringResult:
    """Convert *env* mapping to a string in the requested *fmt*.

    Parameters
    ----------
    env:
        Key/value mapping (values may be ``None``).
    fmt:
        One of ``"dotenv"``, ``"export"``, or ``"inline"``.
    source_path:
        Optional path recorded in the result for traceability.

    Raises
    ------
    ValueError
        If *fmt* is not a recognised format.
    """
    if fmt not in _FORMATS:
        raise ValueError(
            f"Unknown format {fmt!r}. Choose from: {sorted(_FORMATS)}"
        )
    content = _FORMATS[fmt](env)
    return StringResult(
        content=content,
        format=fmt,
        key_count=len(env),
        source_path=source_path,
        _env=dict(env),
    )
