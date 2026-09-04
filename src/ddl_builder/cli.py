"""Command-line entry point.

Generate valid SQL from a YAML data model and, only if it is valid, write the composite YAML
artifact and the documentation. Validation failures are reported verbosely (all
problems at once) to stderr and cause a non-zero exit code with no output
written, so the tool can gate a deployment pipeline.
"""
import argparse
from pathlib import Path

from yaml import safe_dump

import ddl_builder as dlb


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ddl-builder",
        description="Take a validated YAML data model and write valid SQL.",
    )
    parser.add_argument("entry", help="Path to the YAML file.")
    parser.add_argument("-o", "--output", required=True, help="Path for the composite output SQL.")
    parser.add_argument("-d", "--docs", required=True, default="./docs", help="Path for the documentation output.")
    return parser

def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Returns the process exit code (0 success, 1 on validation failure)."""
    args = _build_parser().parse_args(argv)

    yamlPath = Path(args.entry)

    outcome = dlb.read_yaml(yamlPath)
    newDB = dlb.ddl_from_dict(outcome)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as handle:
        safe_dump(newDB.model_dump(by_alias=True, mode = "json"), handle)
    print(f"Wrote {args.output} and documentation to {args.docs}")
    return 0
