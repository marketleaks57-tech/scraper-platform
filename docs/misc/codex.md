# Coding Codex

This codex summarizes conventions for the scraper platform codebase. When in doubt, prefer the style guides in `docs/misc/documentation_index.md` and component-specific READMEs.

## Conventions
- Use type hints across new Python modules.
- Keep optional dependencies (e.g., `psycopg2`, `selenium`) isolated to modules that require them.
- Prefer small, testable functions and document non-obvious behavior.

## Contribution checklist
- Run linters and unit tests relevant to your changes.
- Update configuration and DAGs when introducing new agents or processors.
- Refresh the status documents in this directory before releases.
