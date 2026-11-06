"""Wire-format helpers: the API speaks camelCase, the SDK accepts snake_case params."""

from __future__ import annotations

from typing import Any, Mapping

# Keys whose values are free-form user data and must be sent verbatim.
_OPAQUE_KEYS = frozenset({"metadata"})


def to_camel(key: str) -> str:
    """Convert ``snake_case`` to ``camelCase``; keys without underscores are unchanged."""
    if "_" not in key:
        return key
    head, *rest = key.split("_")
    return head + "".join(part[:1].upper() + part[1:] for part in rest)


def camelize(value: Any) -> Any:
    """Recursively convert dict keys to camelCase, leaving ``metadata`` values untouched."""
    if isinstance(value, Mapping):
        return {
            to_camel(k): (v if k in _OPAQUE_KEYS else camelize(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [camelize(v) for v in value]
    return value
