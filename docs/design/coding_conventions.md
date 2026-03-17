# Coding Conventions

This document describes language-agnostic coding conventions, style expectations, and development practices for this
project. It is intentionally general so teams can map the guidance to the project's chosen language(s) and tools.

> The conventions here are guidelines. When the project's technology or context requires deviation, note the
> exception and the rationale in the change set or PR.

## Purpose

- Provide a consistent baseline for code quality, readability, and maintainability across modules and languages.
- Document expectations for tests, commits, formatting, and dependency usage.

## Key Principles

- Clarity over cleverness: prefer simple, explicit code that is easy to read and reason about.
- Small functions and modules: each function or module should have a single responsibility.
- Encapsulation: modules should expose a clear, minimal public API and hide internal details.
- Minimise cross-module coupling: prefer well-defined interfaces or abstractions for interactions between modules.

## Style & Formatting

- Adopt the project's chosen formatter and linter for the implementation language. Configure and run them as part of
  the development workflow.
- Use a consistent maximum line length agreed by the team; default recommendation: 88 characters.
- Use a consistent comment and documentation style appropriate for the language (e.g., Javadoc-style, docblocks,
  reStructuredText, Markdown). Document public APIs.

## Typing and Interfaces

- Where the language supports static or optional typing, prefer explicit types or interfaces for public APIs.
- Define language-appropriate interfaces or abstract types for dependencies that cross module boundaries.

## Testing

- Tests should be clear, deterministic, and focused on behaviour rather than implementation details.
- Locate tests in a dedicated top-level `tests/` area or the language-appropriate equivalent; mirror module structure
  where practical.
- Tests should not rely on private internals of modules; prefer testing through public interfaces.
- Prefer automated tests that run quickly. Use integration tests sparingly and clearly distinguish them from unit tests.

## Commit Messages & Reviews

- Use a consistent commit message format (for example, Conventional Commits) and keep messages focused and actionable.
- Include a descriptive PR title and summary explaining motivation, key changes, and any migration or upgrade notes.
- Keep review comments specific and constructive; capture important decisions in the PR description or linked issue.

## Encoding & I/O

- Treat UTF-8 as the canonical encoding for text content. When reading or writing files, specify encoding explicitly if the
  platform or language requires it.
- Be defensive when parsing external or user-generated data: validate inputs and fail gracefully.

## Internationalisation & Localisation

- Store user-visible strings in a single place to ease translation where applicable. Avoid hardcoding UI strings in code
  logic.

## Exceptions

- If a rule must be broken for a good reason, document the exception in the change and get explicit approval from the
  reviewer.

## References

- Architecture document: `docs/design/architecture.md` (authoritative for architecture and module boundaries)
- This file is intentionally generic; map its guidance to the team's chosen tools and languages when implementing.

