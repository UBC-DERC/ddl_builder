# Contributing to `ddl_builder`

We want to make contributing to this project as easy and transparent as
possible. We also want to support broader community adoption of this tool, and transparent adoption of the data standards.

## Pull Requests

We actively welcome your pull requests.

### For new validation or class structures

1. Most of the class structures are adopted from the [`data_model` project](https://github.com/UBC-DERC/data_model). To change the underlying structure (as opposed to the DDL translation) check there first.
2. Create a GitHub issue proposing a change to a class definition (you can stop here if you'd like).
3. Fork the repo and create your branch from `main`.
4. Modify the code as needed and add new tests to ensure your code runs as expected.
5. If you've added an example, it should be validated. You can do this by running:
     `uv run ddl_builder`
     (once you've followed the installation guidelines).
6. Verify that there are no issues in your doc build. You can check the preview locally by entering your virtual environment and running `mkdocs serve`.
7. Run `pytest`.
8. Address any feedback in code review promptly.

## For bug fixes

1. Create a GitHub issue identifying a bug (you can stop here if you'd like).
2. Fork the repo and create your branch from `main`.
3. Install `uv` and run `uv sync`
4. Make your code change and ensure `ruff`, `ty` and `pytest` checks run cleanly.
5. Address any feedback in code review promptly.

## Issues

We use [GitHub issues](https://github.com/UBC-DERC/ddl_builder) to track public bugs. Please ensure your description is
clear and has sufficient instructions to be able to reproduce the issue.

## License

By contributing to this projects code, documentation and examples you agree that your contributions will be licensed
under the [LICENSE file](LICENSE.md) in the root directory of this source tree.
