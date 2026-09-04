"""Tests for `ddl_builder.pg_type.pg_type` type validation/canonicalisation."""

import pytest

from ddl_builder import pg_type as pg_type_mod
from ddl_builder.pg_type import OVERRIDE_ENV_VAR, pg_type


@pytest.fixture(autouse=True)
def _clear_registry_cache():
    """Ensure each test sees a freshly-built registry (override files vary)."""
    pg_type_mod._lookup.cache_clear()
    yield
    pg_type_mod._lookup.cache_clear()


# --- 1. Built-in canonicalisation + alias resolution -----------------------

@pytest.mark.parametrize(
    ("written", "canonical"),
    [
        ("integer", "integer"),
        ("int", "integer"),
        ("int4", "integer"),
        ("int8", "bigint"),
        ("int2", "smallint"),
        ("bool", "boolean"),
        ("float8", "double precision"),
        ("float4", "real"),
        ("decimal", "numeric"),
        ("varchar", "character varying"),
        ("char", "character"),
        ("timestamptz", "timestamp with time zone"),
        ("timetz", "time with time zone"),
        ("text", "text"),
    ],
)
def test_aliases_resolve_to_canonical(written, canonical):
    assert pg_type(written) == canonical


def test_lookup_is_case_insensitive():
    assert pg_type("INT4") == "integer"
    assert pg_type("Integer") == "integer"


def test_surrounding_whitespace_is_trimmed():
    assert pg_type("  bigint  ") == "bigint"


# --- 2. Modifiers ----------------------------------------------------------

@pytest.mark.parametrize(
    ("written", "expected"),
    [
        ("numeric(10,2)", "numeric(10,2)"),
        ("decimal(10,2)", "numeric(10,2)"),
        ("varchar(50)", "character varying(50)"),
        ("character varying(255)", "character varying(255)"),
        ("bit(8)", "bit(8)"),
    ],
)
def test_modifiers_are_preserved_and_canonicalised(written, expected):
    assert pg_type(written) == expected


def test_modifier_internal_whitespace_is_normalised():
    assert pg_type("decimal(10, 2)") == "numeric(10,2)"
    assert pg_type("numeric( 10 , 2 )") == "numeric(10,2)"


# --- 3. Arrays -------------------------------------------------------------

@pytest.mark.parametrize(
    ("written", "expected"),
    [
        ("text[]", "text[]"),
        ("int4[]", "integer[]"),
        ("character varying(255)[]", "character varying(255)[]"),
        ("integer[][]", "integer[][]"),
    ],
)
def test_array_suffixes(written, expected):
    assert pg_type(written) == expected


# --- 4. Infix timezone types ----------------------------------------------

@pytest.mark.parametrize(
    ("written", "expected"),
    [
        ("timestamp with time zone", "timestamp with time zone"),
        ("timestamptz(3)", "timestamp(3) with time zone"),
        ("timestamp(3) with time zone", "timestamp(3) with time zone"),
        ("time with time zone", "time with time zone"),
        ("timestamp(6)", "timestamp(6)"),
    ],
)
def test_timezone_modifier_placement(written, expected):
    assert pg_type(written) == expected


# --- 5. Injection / malformed rejection ------------------------------------

@pytest.mark.parametrize(
    "bad",
    [
        "",
        "   ",
        "notatype",
        "int; DROP TABLE users",
        "integer(5); drop",
        "numeric(10,2); drop",
        "varchar(50) foo",
        "text; --",
        "integer[1]; drop",
        "numeric(a,b)",
        "numeric(10)(2)",
        "integer'",
        'integer"',
    ],
)
def test_rejects_unknown_or_malformed(bad):
    with pytest.raises(ValueError):
        pg_type(bad)


def test_non_string_input_is_rejected():
    with pytest.raises(ValueError):
        pg_type(123)  # ty: ignore[invalid-argument-type]


# --- 6. Project override adds a new type -----------------------------------

def test_override_adds_new_type(tmp_path, monkeypatch):
    # An extension type is unknown by default...
    with pytest.raises(ValueError):
        pg_type("geometry")

    override = tmp_path / "pg_types.yaml"
    override.write_text("geometry: []\n")
    monkeypatch.setenv(OVERRIDE_ENV_VAR, str(override))
    pg_type_mod._lookup.cache_clear()

    # ...and accepted once declared in the project override.
    assert pg_type("geometry") == "geometry"


def test_override_appends_alias_to_builtin(tmp_path, monkeypatch):
    override = tmp_path / "pg_types.yaml"
    override.write_text("bigint:\n  - int64\n")
    monkeypatch.setenv(OVERRIDE_ENV_VAR, str(override))
    pg_type_mod._lookup.cache_clear()

    assert pg_type("int64") == "bigint"
    # Bundled aliases still work.
    assert pg_type("int8") == "bigint"


def test_comment_only_override_is_a_noop(tmp_path, monkeypatch):
    override = tmp_path / "pg_types.yaml"
    override.write_text("# only comments here\n")
    monkeypatch.setenv(OVERRIDE_ENV_VAR, str(override))
    pg_type_mod._lookup.cache_clear()

    assert pg_type("integer") == "integer"
    with pytest.raises(ValueError):
        pg_type("geometry")
