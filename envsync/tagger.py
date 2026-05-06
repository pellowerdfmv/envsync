"""Tag .env keys with metadata labels (e.g. required, optional, secret)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set

_KNOWN_TAGS: FrozenSet[str] = frozenset({"required", "optional", "secret", "deprecated", "internal"})


@dataclass
class TagResult:
    tags: Dict[str, Set[str]] = field(default_factory=dict)  # key -> set of tags
    unknown_tags: List[str] = field(default_factory=list)

    def keys_with_tag(self, tag: str) -> List[str]:
        """Return all keys that carry *tag*."""
        return [k for k, ts in self.tags.items() if tag in ts]

    def has_tag(self, key: str, tag: str) -> bool:
        return tag in self.tags.get(key, set())

    def summary(self) -> str:
        lines: List[str] = []
        for key, ts in sorted(self.tags.items()):
            lines.append(f"{key}: {', '.join(sorted(ts))}")
        if self.unknown_tags:
            lines.append(f"Unknown tags ignored: {', '.join(sorted(self.unknown_tags))}")
        return "\n".join(lines) if lines else "No tags defined."


def tag_env(
    env: Dict[str, object],
    tag_map: Dict[str, List[str]],
    *,
    strict: bool = False,
) -> TagResult:
    """Apply *tag_map* labels to keys present in *env*.

    Parameters
    ----------
    env:      Parsed environment dict (key -> value).
    tag_map:  Mapping of key -> list of tag strings.
    strict:   When True, only *_KNOWN_TAGS* are accepted; others are recorded
              in ``TagResult.unknown_tags`` and skipped.
    """
    result = TagResult()
    for key, raw_tags in tag_map.items():
        accepted: Set[str] = set()
        for t in raw_tags:
            t = t.strip().lower()
            if strict and t not in _KNOWN_TAGS:
                if t not in result.unknown_tags:
                    result.unknown_tags.append(t)
                continue
            accepted.add(t)
        if accepted:
            result.tags[key] = accepted
    return result
