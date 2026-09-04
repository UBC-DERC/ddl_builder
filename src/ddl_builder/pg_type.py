"""Validation and canonicalisation of PostgreSQL data types.

`pg_type()` is the public entry point. It checks a user-supplied type string
against a whitelist (the bundled ``pg_types.yaml`` plus an optional project
override) and returns the *canonical* spelling to emit into generated DDL.

Because every accepted type is drawn from the whitelist, and the only
free-form parts (a ``(...)`` modifier and a ``[]`` array suffix) are checked
to contain nothing but digits, commas and brackets, the returned string is
safe to inject verbatim with ``psycopg.sql.SQL``.
"""

import os
import re
from functools import lru_cache
from pathlib import Path

import yaml

#: The type registry that ships with the package.
BUNDLED_TYPES_PATH: Path = Path(__file__).with_name("pg_types.yaml")

#: Filename looked for in the project root to extend the registry.
OVERRIDE_FILENAME: str = "pg_types.yaml"

#: Environment variable that, when set, points at the override file directly.
OVERRIDE_ENV_VAR: str = "DDL_BUILDER_PG_TYPES"

# A trailing array suffix: one or more ``[]`` / ``[n]`` groups at the end.
_ARRAY_RE: re.Pattern[str] = re.compile(r"((?:\s*\[\s*\d*\s*\])+)\s*$")

# A ``(...)`` type modifier group.
_MODIFIER_RE: re.Pattern[str] = re.compile(r"\(([^()]*)\)")

# Contents allowed inside a modifier: digits, commas and whitespace only.
_MODIFIER_CONTENT_RE: re.Pattern[str] = re.compile(r"^[\d\s,]+$")

# Collapse runs of whitespace.
_WS_RE: re.Pattern[str] = re.compile(r"\s+")

# Temporal types carry their modifier *before* this suffix, e.g.
# ``timestamp(3) with time zone`` rather than ``timestamp with time zone(3)``.
_TZ_SUFFIX: str = " with time zone"


def _load_yaml(path: Path) -> dict[str, list[str]]:
    """Load a type-registry YAML file, tolerating an empty (comment-only) file."""
    with open(path) as fp:
        data = yaml.safe_load(fp)
    return data or {}


def _merge(
    bundled: dict[str, list[str]], override: dict[str, list[str]]
) -> dict[str, list[str]]:
    """Merge an override registry additively on top of the bundled one.

    The override may add new canonical types or append aliases to existing
    ones; it can never remove a bundled built-in.
    """
    merged: dict[str, list[str]] = {k: list(v or []) for k, v in bundled.items()}
    for canonical, aliases in override.items():
        existing: list[str] = merged.setdefault(canonical, [])
        for alias in aliases or []:
            if alias not in existing:
                existing.append(alias)
    return merged


def _override_path() -> Path | None:
    """Resolve the project-level override file, if one exists."""
    env: str | None = os.environ.get(OVERRIDE_ENV_VAR)
    candidate: Path = Path(env) if env else Path.cwd() / OVERRIDE_FILENAME
    return candidate if candidate.is_file() else None


@lru_cache(maxsize=None)
def _lookup(bundled_path: str, override_path: str | None) -> dict[str, str]:
    """Build a case-insensitive ``spelling -> canonical`` lookup table."""
    bundled: dict[str, list[str]] = _load_yaml(Path(bundled_path))
    override: dict[str, list[str]] = (
        _load_yaml(Path(override_path)) if override_path else {}
    )
    merged: dict[str, list[str]] = _merge(bundled, override)

    lookup: dict[str, str] = {}
    for canonical, aliases in merged.items():
        lookup[canonical.lower()] = canonical
        for alias in aliases:
            lookup[alias.lower()] = canonical
    return lookup


def _apply_modifier(canonical: str, modifier: str) -> str:
    """Re-attach a ``(...)`` modifier to a canonical type in the right place."""
    if not modifier:
        return canonical
    if canonical.endswith(_TZ_SUFFIX):
        head: str = canonical[: -len(_TZ_SUFFIX)]
        return f"{head}{modifier}{_TZ_SUFFIX}"
    return f"{canonical}{modifier}"


def pg_type(type: str) -> str:
    """Validate a PostgreSQL data type and return its canonical spelling.

    Args:
        type: The type as written by the user, e.g. ``int4``, ``numeric(10,2)``
            or ``text[]``.

    Raises:
        ValueError: If the type is empty, malformed, or not present in the
            (bundled + override) whitelist.

    Returns:
        The canonical spelling to emit into DDL, e.g. ``integer``,
        ``numeric(10,2)`` or ``text[]``.
    """
    if not isinstance(type, str):
        raise ValueError("A column type must be a string.")

    raw: str = type.strip()
    if not raw:
        raise ValueError("A column type must be a non-empty string.")

    working: str = raw

    # 1. Peel off a trailing array suffix, e.g. ``[]`` or ``[3][3]``.
    array_suffix: str = ""
    array_match: re.Match[str] | None = _ARRAY_RE.search(working)
    if array_match:
        array_suffix = re.sub(r"\s+", "", array_match.group(1))
        working = working[: array_match.start()].rstrip()

    # 2. Peel off an optional ``(...)`` modifier and check it is safe.
    modifier: str = ""
    mods: list[str] = _MODIFIER_RE.findall(working)
    if len(mods) > 1:
        raise ValueError(f"'{raw}' has more than one type modifier.")
    if mods:
        content: str = mods[0].strip()
        if not _MODIFIER_CONTENT_RE.match(content):
            raise ValueError(
                f"Invalid type modifier '({mods[0]})' in '{raw}'; "
                "only digits and commas are allowed."
            )
        modifier = "(" + re.sub(r"\s+", "", content) + ")"
        working = _MODIFIER_RE.sub("", working)

    # 3. Normalise the remaining base name and look up its canonical form.
    base: str = _WS_RE.sub(" ", working).strip().lower()
    lookup: dict[str, str] = _lookup(str(BUNDLED_TYPES_PATH), _override_path_str())
    canonical: str | None = lookup.get(base)
    if canonical is None:
        raise ValueError(
            f"'{raw}' is not a recognised PostgreSQL data type. "
            f"Add it to a project-level '{OVERRIDE_FILENAME}' if it is provided "
            "by an extension."
        )

    return _apply_modifier(canonical, modifier) + array_suffix


def _override_path_str() -> str | None:
    """String form of the override path (or ``None``) for cache keying."""
    path: Path | None = _override_path()
    return str(path) if path else None
