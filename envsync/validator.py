"""Validator — compares a .env file against a .env.example template."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from envsync.parser import parse_env_file


@dataclass
class ValidationResult:
    missing_keys: List[str] = field(default_factory=list)
    extra_keys: List[str] = field(default_factory=list)
    empty_required_keys: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not (self.missing_keys or self.empty_required_keys)

    def summary(self) -> str:
        lines = []
        if self.missing_keys:
            lines.append(f"Missing keys ({len(self.missing_keys)}): {', '.join(sorted(self.missing_keys))}")
        if self.empty_required_keys:
            lines.append(f"Empty required keys ({len(self.empty_required_keys)}): {', '.join(sorted(self.empty_required_keys))}")
        if self.extra_keys:
            lines.append(f"Extra keys not in template ({len(self.extra_keys)}): {', '.join(sorted(self.extra_keys))}")
        if not lines:
            return "All checks passed."
        return "\n".join(lines)


def validate(
    env_path: str,
    example_path: str,
    strict: bool = False,
) -> ValidationResult:
    """
    Validate *env_path* against *example_path*.

    Args:
        env_path:     Path to the actual .env file.
        example_path: Path to the .env.example template.
        strict:       If True, extra keys in env_path are treated as an error.
    """
    env_vars: Dict[str, Optional[str]] = parse_env_file(env_path)
    template_vars: Dict[str, Optional[str]] = parse_env_file(example_path)

    template_keys: Set[str] = set(template_vars.keys())
    env_keys: Set[str] = set(env_vars.keys())

    result = ValidationResult()
    result.missing_keys = sorted(template_keys - env_keys)
    result.extra_keys = sorted(env_keys - template_keys)

    for key in template_keys & env_keys:
        template_has_value = template_vars[key] not in (None, '')
        env_value = env_vars[key]
        if template_has_value and env_value in (None, ''):
            result.empty_required_keys.append(key)

    result.empty_required_keys.sort()
    return result
