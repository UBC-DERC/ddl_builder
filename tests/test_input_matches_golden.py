# tests/test_output_yaml.py
import os
import subprocess
from pathlib import Path
import yaml
import hashlib

EXAMPLE = Path("examples/output.yaml")
GOLDEN = Path("tests/golden/output.yaml")

def test_input_yaml_matches_golden(tmp_path):
    output = tmp_path / "output.yaml"
    subprocess.run(
        ["data-model", str(EXAMPLE),
         "--docs", str(tmp_path / "docs"),
         "--output", str(output)],
        check=True,
    )

    hashed_new = hashlib.md5()
    produced = hashed_new.update(output.read_text().encode("utf-8"))

    if os.environ.get("UPDATE_GOLDEN"):
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(yaml.safe_dump(produced, sort_keys=True))

    expected = yaml.safe_load(GOLDEN.read_text())
    assert produced == expected