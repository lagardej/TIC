# Python Conventions

This document captures Python-specific conventions for this project. It exists to record rules that apply only to
Python code and that were intentionally removed from the language-agnostic `coding_conventions.md` during a
refactor.

Treat this file as the authoritative reference for Python idioms and practices in the repository. If the project uses a
language other than Python in a module, map these rules to the language-specific equivalents or ignore them for that
module.

## Python Version

- Supported Python minor versions and the project's chosen interpreter must be documented in the project `README` or
  dependency manifests (for example, `pyproject.toml`). Use the project's documented Python version when writing or
  updating Python code.

## Typing & Structures

- Prefer explicit typing for public APIs and module boundaries (use typing, Protocols, or ABCs where appropriate).
- Use dataclasses or language-appropriate value-object patterns for simple immutable data carriers when they improve
  clarity.

## Dependency Rule (migrated from coding conventions)

- Minimise direct third-party dependencies in `domain/` (core) modules. Domain modules should depend only on the
  standard library and small, stable, purpose-specific utilities where strictly necessary.
- When a domain module needs functionality provided by an external library (I/O, persistence, external APIs), define an
  explicit interface (for example an abstract base class or Protocol) in the domain or application layer and provide the
  concrete implementation in an `infrastructure/` or `adapters/` module.
- Inject concrete implementations from infrastructure/adapters into the domain/application at runtime (dependency
  injection or explicit factory wiring). Do not import infrastructure implementations directly from domain modules.
- Document any exception to this rule in the PR and explain why the dependency is necessary in the domain layer.

## Linting & Formatting

- Use the project's configured formatter and linter toolchain for Python (for example, Black, Ruff, isort). Configure
  them consistently and run them as part of the developer workflow and CI.
- Follow the project's agreed maximum line length; default recommendation: 88 characters for Python code.

## Docstrings & Comments

- Document public modules, classes, and functions with clear docstrings. Adopt a consistent docstring style (the project
  may prefer Google-style, NumPy-style, or reStructuredText) and document the chosen style in the project's contributor
  guide.

## Encoding & I/O

- Explicitly specify `encoding="utf-8"` when opening files. When invoking subprocesses with text output, ensure
  encoding is handled explicitly by the chosen API.

## Testing

- Follow the project's testing conventions for Python. Prefer unit tests that exercise behaviour via public interfaces.
- Test files should live under the top-level `tests/` directory and mirror the module layout where practical.

## Exceptions

- Any exception to these conventions must be documented in the PR and approved by reviewers.

## References

- Language-agnostic coding guidance: `docs/design/coding_conventions.md`
- Architecture and module boundaries: `docs/design/architecture.md` (authoritative for dependency rules and boundaries)

