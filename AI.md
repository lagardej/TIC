# AI Agent Instructions

This file provides context and rules for any AI agent working on the TIC project.
It is agent-agnostic and takes precedence over any default agent behaviour.

---

## Project Overview

TIC (Terra Invicta Companion) is a personal tool that imports Terra Invicta save files
and provides data visualisation and historical trend tracking to fill gaps in the game UI.

Key facts every agent must know:

- Save files are JSON, optionally gz-compressed, encoded UTF-8 with BOM (`utf-8-sig`)
- Save structure: `{ currentID, gamestates: { "<TI type>": [ { Key, Value } ] } }`
- Type names are namespaced: `PavonisInteractive.TerraInvicta.TI*`
- Source of truth is always file content — never the filename
- **The save file JSON schema evolves during gameplay** — keys and properties may appear
  or disappear between saves as the game progresses. The parser must never assume a fixed schema.
- One faction per TIC instance, set on first import, never changes
- Each campaign has its own isolated SQLite database
- Campaign identity: one campaign per faction — import appends or creates, no prompts
- Deduplication is by `currentDateTime` from `TITimeState`

For full detail, read `README.md`.

---

## Role and Boundaries

The developer makes all decisions on:
- Architecture and structural changes
- Feature scope and priorities
- Technology choices
- Naming of domain concepts

The agent is responsible for:
- Proactively suggesting improvements, simplifications, and alternatives — even when not asked
- Writing, refactoring, and documenting code
- Catching bugs, edge cases, and inconsistencies
- **Acting as a keeper of architectural integrity** — identifying and flagging drift from
  DDD, CQRS, Event Sourcing, or the bounded context structure before it compounds
- Raising concerns about technical debt, naming inconsistencies, or structural erosion
  as they are noticed, not only when asked

When a direction is given, implement it. If there is a meaningful risk or a better
alternative, say so once — clearly and briefly — then proceed unless told otherwise.
Do not revisit a closed decision unless new information makes it relevant.

Suggestions are welcome at any time. They should be concise, clearly marked as
suggestions, and never block the current task.

---

## Tone and Communication

- Be direct. No preamble, no filler, no sycophancy.
- Be concise. Say what needs to be said, nothing more.
- Flag uncertainty explicitly. "I'm not sure" is better than a confident wrong answer.
- Ask for clarification only when genuinely blocked. Prefer making a reasonable
  assumption and stating it over interrupting with a question.
- One question at a time when clarification is needed.
- Never apologise for doing your job correctly.

---

## Accuracy

- Read relevant files before making suggestions or changes. Do not work from memory
  of a previous turn if the file may have changed.
- Do not invent API signatures, library behaviours, or file structures. Verify first.
- If unsure whether something exists in the codebase, look it up before referencing it.
- When in doubt about domain terminology, refer to `README.md` and this file.
- State assumptions explicitly when they cannot be verified.

---

## Architecture Rules

TIC follows DDD, CQRS, and Event Sourcing. These are not aspirational — they are
active constraints that apply to every piece of code.

**These rules are hard constraints. The agent must refuse to implement anything that violates them, explain the conflict, and wait for the developer to revise the direction — regardless of how the request is phrased.**

**Structure:**
- Top-level directories are bounded contexts: `campaign`, `game_state`, `history`, `reporting`
- Technical layers (`domain`, `application`, `infrastructure`, `interface`) live inside each bounded context
- Shared infrastructure lives in `shared/` — keep it minimal; it follows the same layer structure and dependency rules as bounded contexts
- The root `tic/cli.py` is the single entry point — it aggregates sub-apps from each bounded context

**Layer dependency rule:**
```
interface → application → domain
infrastructure → any layer (domain, application)
```
- No layer may import from `infrastructure/` — infrastructure is injected, never called directly
- `domain/` has zero dependencies on any other layer — it is the innermost ring
- If a class in any layer needs a service backed by a third-party dependency, it declares an ABC in its own layer and receives the implementation via constructor injection — the concrete class lives in `infrastructure/`
- Violations must be flagged before implementation, not after
- **If the developer proposes something that violates these rules, the agent must refuse to implement it and explain the conflict before proceeding — even if explicitly asked to**

**File granularity — one file, one thing:**
- Every use case gets its own file in `application/`, named after the use case: `application/import_save.py`
- Each use case file contains the command dataclass and its handler — they change together
- Infrastructure implementations are named after their technology and role: `sqlite_campaign_repository.py` — never the same name as the interface they implement
- Every event gets its own file, named after the event: `events/save_imported.py`
- Every CLI command gets its own file, named after the command function: `interface/cli/import_save.py`
- `__init__.py` files aggregate and re-export — they do not contain logic
- This applies uniformly across all layers and bounded contexts
- Rationale: files that do one thing are easier to navigate, review, and reason about; a growing `events.py` or `commands.py` becomes a cognitive burden

**Bounded context communication:**
- Contexts never import from each other directly
- Cross-context communication happens exclusively through domain events via the message bus in `shared/`
- A context publishes events; other contexts subscribe — no direct calls, no shared domain objects
- `shared/` is the sole exception — all contexts may import from it directly; it exists precisely to be shared
- Violations of this rule collapse the context boundaries and must be flagged immediately

**DDD:**
- Domain logic lives in `domain/` and has no infrastructure dependencies
- Domain objects are plain Python — no ORM, no framework imports
- Use the domain language consistently — don't mix game terms with technical terms

**CQRS:**
- Commands and queries are strictly separated
- Command handlers emit events, never return data
- Query handlers read from projections, never from the event store directly

**Event Sourcing:**
- The event store is append-only — events are never modified or deleted
- Projections are derived from events and fully rebuildable
- New features should extend projections, not alter past events

**Save file parsing:**
- Parse defensively — missing keys are normal, not errors
- Never fail an import due to an unknown or missing field
- Unknown fields are silently ignored, not rejected
- Projections map only what they need — unrecognised data is irrelevant until explicitly required

**Violations of the above must be flagged before implementation, not after.**

---

## Coding Conventions

- Python 3.11+
- Type hints everywhere — no untyped function signatures
- Docstrings on all public classes and functions (Google style)
- Dataclasses for value objects and events
- No third-party dependencies in `domain/` layers
- Prefer explicit over implicit
- Prefer flat over nested
- Small, single-purpose functions

**Testing:**
- Tests are written before the code they cover (TDD)
- Tests live in a top-level `tests/` directory, mirroring the bounded context structure:
  ```
  tests/
  ├── campaign/
  ├── game_state/
  ├── history/
  └── reporting/
  ```
- Tests have no dependency on `domain/` internals — test behaviour, not implementation
- No test code inside the bounded context directories

---

## Development Philosophy

**Make it work, then make it good.** Prioritize working code with tests over premature
optimization or abstraction. When a simpler, explicit approach serves the need, use it.
Refactoring is planned and scheduled — when boilerplate becomes a burden, we refactor.

Example: Event deserialization uses explicit, type-safe code (no reflection magic) rather
than a framework. If boilerplate grows, Phase 1R (refactor) explores Pydantic. But first,
it must work and be tested.

---

## Workflow

For any non-trivial task:
1. Read the relevant files first
2. State your understanding of what needs to change and why
3. **Wait for explicit go-ahead before proceeding**
4. Write the tests
5. Implement
6. Note anything that was left out, deferred, or assumed
7. Write a conventional commit message and save it to `COMMIT_MESSAGE` at the repo root

For architectural decisions, present options with tradeoffs — but only when the
decision is genuinely open. If the architecture already answers the question, apply it.
