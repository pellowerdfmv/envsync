"""Type-casting utilities for .env values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


_BOOL_TRUE = {"1", "true", "yes", "on"}
_BOOL_FALSE = {"0", "false", "no", "off"}


@dataclass
class CastResult:
    """Outcome of casting an env mapping to typed values."""

    values: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)

    def has_errors(self) -> bool:
        return bool(self.errors)

    def __len__(self) -> int:
        return len(self.values)

    def summary(self) -> str:
        lines = [f"Cast {len(self.values)} key(s)."]
        if self.errors:
            lines.append(f"{len(self.errors)} casting error(s):")
            for key, msg in self.errors.items():
                lines.append(f"  {key}: {msg}")
        return "\n".join(lines)


def _cast_value(raw: Optional[str], type_hint: str) -> Any:
    """Cast *raw* string to the requested *type_hint*."""
    if raw is None:
        return None

    hint = type_hint.lower().strip()

    if hint in ("str", "string"):
        return raw

    if hint in ("int", "integer"):
        return int(raw)

    if hint in ("float",):
        return float(raw)

    if hint in ("bool", "boolean"):
        lower = raw.lower()
        if lower in _BOOL_TRUE:
            return True
        if lower in _BOOL_FALSE:
            return False
        raise ValueError(f"Cannot coerce {raw!r} to bool")

    if hint in ("list",):
        return [item.strip() for item in raw.split(",") if item.strip()]

    raise ValueError(f"Unknown type hint {type_hint!r}")


def cast_env(
    env: Dict[str, Optional[str]],
    schema: Dict[str, str],
) -> CastResult:
    """Cast values in *env* according to *schema* (key -> type string).

    Keys absent from *schema* are passed through as-is (str).
    """
    values: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    for key, raw in env.items():
        type_hint = schema.get(key, "str")
        try:
            values[key] = _cast_value(raw, type_hint)
        except (ValueError, TypeError) as exc:
            errors[key] = str(exc)
            values[key] = raw  # keep original on failure

    return CastResult(values=values, errors=errors)
