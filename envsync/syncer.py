"""Sync .env files by generating a template from a reference file."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from envsync.parser import parse_env_file


def generate_template(
    reference_path: str | Path,
    strip_values: bool = True,
    comment_char: str = "#",
) -> str:
    """
    Generate a .env.example template from a reference .env file.

    Args:
        reference_path: Path to the source .env file.
        strip_values: If True, replace values with empty strings.
        comment_char: Character used to denote comment lines.

    Returns:
        A string containing the template content.
    """
    lines: List[str] = []
    reference_path = Path(reference_path)

    with reference_path.open("r", encoding="utf-8") as fh:
        raw_lines = fh.readlines()

    for raw in raw_lines:
        stripped = raw.strip()
        # Preserve blank lines and comments as-is
        if not stripped or stripped.startswith(comment_char):
            lines.append(raw.rstrip("\n"))
            continue

        if "=" in stripped:
            key, _, _ = stripped.partition("=")
            if strip_values:
                lines.append(f"{key.strip()}=")
            else:
                lines.append(stripped)
        else:
            lines.append(stripped)

    return "\n".join(lines) + "\n"


def sync_missing_keys(
    reference_path: str | Path,
    target_path: str | Path,
    default_value: Optional[str] = None,
) -> Dict[str, str]:
    """
    Append keys present in reference but missing from target.

    Args:
        reference_path: Path to the authoritative .env file.
        target_path: Path to the .env file to be updated.
        default_value: Value to assign to newly added keys.

    Returns:
        A dict of keys that were added.
    """
    ref_vars = parse_env_file(reference_path)
    target_vars = parse_env_file(target_path)

    missing: Dict[str, str] = {
        key: (default_value if default_value is not None else "")
        for key in ref_vars
        if key not in target_vars
    }

    if missing:
        with open(target_path, "a", encoding="utf-8") as fh:
            fh.write("\n# Added by envsync\n")
            for key, value in missing.items():
                fh.write(f"{key}={value}\n")

    return missing
