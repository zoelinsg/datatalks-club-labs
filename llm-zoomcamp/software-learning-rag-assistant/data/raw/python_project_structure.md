# Python Project Structure

A good Python project structure helps developers separate application logic, configuration, tests, and scripts.

A common layout includes:

- `src/` for reusable application code
- `tests/` for automated tests
- `data/` for input or generated data
- `README.md` for documentation
- `pyproject.toml` for dependencies and project metadata
- `.env` for local environment variables

Application code should not be mixed directly with notebooks or one-off scripts. Keeping code in `src/` makes it easier to test, reuse, and package.

Environment variables should be used for secrets such as API keys. They should be loaded from `.env` locally but never committed to GitHub.

For reproducibility, dependencies should be locked using tools such as Poetry, uv, or pip-tools. A project should include clear setup and run instructions so another developer can run it without guessing.

A maintainable project usually has small modules with clear responsibilities. For example, a RAG application may have separate files for ingestion, search, prompting, monitoring, and the user interface.