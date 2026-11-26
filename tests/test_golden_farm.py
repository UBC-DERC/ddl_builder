"""The SQL generated for the test model matches the saved copy.

Any change to the generated SQL, intended or not, shows up here as a diff. When
the change is intended, regenerate the saved copy and review it with `git diff`:

    UPDATE_GOLDEN=1 uv run pytest tests/test_sql_matches_golden.py
"""

import os
from pathlib import Path

import ddl_builder as dlb

MODEL = Path("tests/models/farm.yaml")
GOLDEN = Path("tests/golden/farm.sql")


def test_golden_farm(tmp_path):
    output: Path = tmp_path / "farm.sql"
    # Through the CLI, so the --sql option is tested too.
    dlb.main(
        [
            str(MODEL),
            "--output",
            str(tmp_path / "output.yaml"),
            "--docs",
            str(tmp_path / "docs"),
            "--sql",
            str(output),
        ]
    )
    produced: str = output.read_text()

    if os.environ.get("UPDATE_GOLDEN"):
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(produced)

    assert produced == GOLDEN.read_text()