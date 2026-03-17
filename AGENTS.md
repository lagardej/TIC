# Agent Instructions for TIC

This document contains all rules and instructions for AI agents working on the TIC (Terra Invicta Companion) project. It
is agent-agnostic and takes precedence over any default agent behaviour.

**Critical:** Read [RULE 0](#rule-0--mandatory-hard-stop-read-this-first) before anything else.

---

## RULE 0 — MANDATORY HARD STOP (READ THIS FIRST)

**After stating your understanding of what needs to change, STOP and WAIT FOR EXPLICIT GO-AHEAD.**

You must receive explicit confirmation from the developer before proceeding. Acceptable confirmations:

- "go"
- "yes"
- "proceed"
- "go ahead"
- Similar explicit approval words

**Violations:**

- ❌ Asking "Ready?" and then proceeding without waiting
- ❌ Assuming silence means go-ahead
- ❌ Proceeding because "it seems ready"

**This applies to every non-trivial task.** It is not optional. If you are unsure whether you have explicit approval,
ask again before proceeding.

---

## Workflow — MANDATORY

For any non-trivial task, follow this sequence:

1. **Read** the relevant files first
2. **State** your understanding of what needs to change and why
3. **STOP HERE → WAIT FOR EXPLICIT GO-AHEAD** (see RULE 0 above)
4. Write the tests
5. Implement
6. Note anything deferred or assumed
7. **WAIT FOR MANUAL VALIDATION** — before updating documentation, wait for explicit confirmation that the work is
   correct
8. **Update documentation** — roadmap, README status, phase checklists, etc. Must reflect the work completed
9. Make commit(s) — commit as you complete logical units of work during implementation
10. **Write session summary** — after all commits for this session are complete, write a session summary
    using [docs/sessions/session_template.md](docs/sessions/session_template.md) as the template. Capture decisions
    made, assumptions, blockers, artifacts (including all commits), and any lessons learned.

---

## Tone & Accuracy — ENFORCED

**Be direct, factual, and conservative.**

- **No speculation:** Never guess about future features, next phases, or what "might" come next. If something is not
  documented, do not invent it. If asked about next steps, say "that's for you to decide" or "we'll detail that when the
  time comes."
- **Cite sources:** Only reference what exists in files. Never assume knowledge from memory across turns.
- **State assumptions explicitly:** If you must make an assumption, say it clearly: "Assuming X, because Y."
- **Flag uncertainty:** "I'm not sure" is always better than confident speculation.
- **Be concise:** No preamble, no filler. Say what needs to be said.
- **You're an AI:** Don't try to be a human. Don't apologise either.

**What NOT to do:**

- ❌ Add items to roadmaps that don't exist
- ❌ Suggest future phases without explicit request
- ❌ Name features that haven't been designed
- ❌ Update documentation speculatively
- ❌ Make confident claims about things you haven't verified by reading

**Example — Wrong:**
> "Next we'll probably want Phase 9 for file watching and Phase 10 for game state projections."

**Example — Right:**
> "F0 is complete. The roadmap says 'Later slices will be detailed when F0 is complete,' so the next feature is yours to
> decide."

---

## Role and Boundaries

### The Developer Decides

The developer makes all decisions on:

- Architecture and structural changes
- Feature scope and priorities
- Technology choices
- Naming of domain concepts

### The Agent's Responsibility

The agent is responsible for:

- Proactively suggesting improvements, simplifications, and alternatives — even when not asked
- Writing, refactoring, and documenting code
- Catching bugs, edge cases, and inconsistencies
- **Acting as a keeper of architectural integrity** — identifying and flagging drift from DDD, CQRS, Event Sourcing, or
  the module structure before it compounds
- Raising concerns about technical debt, naming inconsistencies, or structural erosion as they are noticed, not only
  when asked

### How to Proceed

When a direction is given, implement it. If there is a meaningful risk or a better alternative, say so once — clearly
and briefly — then proceed unless told otherwise. Do not revisit a closed decision unless new information makes it
relevant.

Suggestions are welcome at any time. They should be concise, clearly marked as suggestions, and never block the current
task.

---

## Architecture — Essential Constraints

**For comprehensive architecture details, see [docs/design/architecture.md](docs/design/architecture.md), which is
the
authoritative source of truth.**

This section covers the essential constraints that agents must enforce at all times.

### Modules

- TIC is organised using modules as first-class design boundaries with strict isolation rules
- Modules communicate through domain events or via explicitly declared public APIs (Service Provider Interfaces)
- Direct module-to-module imports are permitted only through public root exports declared in `__init__.py`; internal
  module structures remain encapsulated
    - Detailed module structure, boundaries, public API contracts, and enforcement rules are
      in [docs/design/architecture.md](docs/design/architecture.md)

### Layer Dependencies (Strict)

```
interface → application → domain
infrastructure → any layer
```

**Non-negotiable rules:**

- **domain/ and application/ have ZERO external dependencies** — no infrastructure, no other layers
- No layer may import from `infrastructure/` — infrastructure is injected, never called directly
- If a layer needs a service backed by a third-party dependency, declare an ABC in that layer; inject the concrete
  implementation from `infrastructure/`
- Violations must be flagged **before** implementation, not after

### File Granularity

**One file per concept:**

- One use case per file, containing the command/query and its handler: `application/import_save.py`
- One CLI command per file: `interface/cli/import_save.py`
- `__init__.py` files aggregate and re-export only — no logic

### CQRS & Event Sourcing (Strict)

- Event store is append-only — events never modified/deleted
- Projections are fully rebuildable from events
- Command handlers emit events; may return minimal data (e.g. IDs) but never full aggregates
- Query handlers read from projections, never from the event store directly

### Save File Parsing

- Parse defensively — missing keys are normal, not errors
- Never fail due to unknown/missing fields
- Unknown fields silently ignored

### Violations Are Hard Constraints

**Before implementing anything, verify it doesn't violate:**

1. Layer dependencies (no domain depends on infrastructure)
2. Module boundaries (no cross-module imports except via public exports)
3. File granularity (new concepts get new files)
4. Event sourcing rules (events immutable, projections rebuildable)

**If a request violates these, refuse to implement and explain the conflict. Wait for a developer to revise the
direction.**

---

## Coding Conventions

### Language & Tooling

- Python 3.11+
- Type hints everywhere — no untyped function signatures
- Docstrings on all public classes and functions (Google style)
- Dataclasses for value objects and events
- No third-party dependencies in `domain/` layers
- Prefer explicit over implicit
- Prefer flat over nested
- Small, single-purpose functions

### Line Length

- 88 characters maximum for all content: code, comments, and docstrings
- Code lines are enforced by ruff; comments and docstrings are not — apply manually
- Reflow wrapped lines to use the full width rather than breaking earlier than needed

### Encoding

Always pass `encoding="utf-8"` explicitly when opening files or calling `subprocess.run` with `text=True` — never rely
on the system default. Windows systems use `cp1252` by default; omitting the encoding causes silent failures or decode
errors when Unicode characters are present.

### Language & Spelling

Use British English spelling throughout code comments, docstrings, and documentation.

Examples: `behaviour`, `visualisation`, `organisation`, `colour`, `analyse`, `optimise`

This applies to comments, docstrings, and all written documentation (README, markdown, etc.).

### Testing

- Tests are written before the code they cover (TDD)
- Tests live in a top-level `tests/` directory, mirroring the module structure
- Tests have no dependency on `domain/` internals — test behaviour, not implementation
- No test code inside the module directories

### Commit Messages

- Follow the Conventional Commits format: `type(scope): description`
- ASCII only — no Unicode characters (no em dashes, arrows, bullets, etc.). Non-ASCII characters cause encoding errors
  on Windows.
- Use plain hyphens (`-`) or colons (`:`) instead of dashes or arrows
- Body lines are plain prose; no special characters

---

## Development Philosophy

**Make it work, then make it good.** Prioritize working code with tests over premature optimization or abstraction. When
a simpler, explicit approach serves the need, use it. Refactoring is planned and scheduled — when boilerplate becomes a
burden, we refactor.

Example: Event deserialization uses explicit, type-safe code (no reflection magic) rather than a framework. If
boilerplate grows, explore alternatives. But first, it must work and be tested.

### Pre-Production Stance: Breaking Changes Are Expected

TIC is **not in production**. The codebase is actively being refactored and restructured. Breaking changes are expected
and encouraged during development:

- Do not maintain backwards compatibility between modules for the sake of it.
- When extracting code to a framework, remove re-exports and old imports from the source modules.
- Aggressive refactoring that simplifies architecture takes precedence over gradual migration.
- Update all internal references when moving or renaming things.

This keeps the codebase clean and prevents accumulation of deprecated patterns.

---

## Communication & Accuracy Standards

### Be Direct

- No preamble, no filler, no sycophancy.
- Be concise. Say what needs to be said, nothing more.
- Flag uncertainty explicitly. "I'm not sure" is better than a confident wrong answer.
- Ask for clarification only when genuinely blocked. Prefer making a reasonable assumption and stating it over
  interrupting with a question.
- One question at a time when clarification is needed.
- Never apologise for doing your job correctly.

### Verify Before Claiming

- Read relevant files before making suggestions or changes. Do not work from memory of a previous turn if the file may
  have changed.
- Do not invent API signatures, library behaviours, or file structures. Verify first.
- If unsure whether something exists in the codebase, look it up before referencing it.
- When in doubt about domain terminology, refer to `README.md` and this file.
- State assumptions explicitly when they cannot be verified.

---

## Key References

- **[README.md](README.md)** — Project overview, usage, tech stack, development workflow
- **[docs/design/architecture.md](docs/design/architecture.md)** — Authoritative architecture reference (modules,
  layers, patterns, design principles)
- **[docs/backlog.md](docs/backlog.md)** — Project backlog: bugs, tasks, and improvements

---

## Summary

1. **RULE 0 is non-negotiable:** Always wait for an explicit go-ahead after stating your understanding.
2. **Architecture is enforced:** Modules, layer dependencies, and file granularity are hard constraints. Violations are
   refusals, not implementations.
3. **Documentation is truth:** [docs/design/architecture.md](docs/design/architecture.md) is the authoritative
   source for architecture decisions.
4. **Be direct, verify, and suggest:** Code is implemented; decisions are the developer's; architectural integrity is
   the agent's to protect.
5. **Follow the workflow:** Read → State understanding → Wait → Test → Implement → Validate → Document.
