# TIC — [FX] Roadmap Template

**Use this template for all feature roadmaps.** Each feature corresponds to one module (bounded context). Replace
`[FX]` with the phase number, `[Module Name]` with the domain concept, and fill in the sections below.

---

## [FX] — [Module Name]

**Objective:** Clear, single-sentence statement of what the user can do with this feature end-to-end. Describe the
working vertical slice: what data enters the system, what processing happens, and what the user sees as output.

**Key architectural decision(s):** Identity model, snapshot vs. incremental tracking, which entities are aggregates, any
major cross-module boundaries, etc. Keep this brief — the detailed decisions live in design sessions.

---

## Phase Overview

Phases are ordered by dependency: each phase assumes prior phases are complete. Each phase has a dedicated design
session before implementation. Phases 1–5 use in-memory implementations provided by the project; Phase 6 swaps in
durable storage.

### Phase 1 — Read Model & Projection

**Goal:** Define what the user will see. Constraint the data scope by designing the read-side output first.

**Outputs:**

- `[EntityDocument]`: read model dataclass, fields optimised for query/display (this is the contract — only data here will be tracked)
- `[EntityStore]` ABC: read-side persistence interface responsible for storing and querying projection documents (`EntityDocument`)
- Event subscriber handler signature: what events will update this projection
- Tests: document construction, field types, constraints (no implementation yet)

---

### Phase 2 — Domain Model: [Aggregate Name] Aggregate

**Goal:** Define the primary aggregate, its events, and invariants. Events must carry at least the data needed for Phase
1's projection.

**Depends on:** Phase 1 (read model defines scope)

**Outputs:**

- `[Aggregate]` aggregate: core identity and state fields, extends the project's `Aggregate` base class
- `[AggregateRepository]` ABC: concrete repository ABC that specifies `get()`, `list_all()`, `save()` signatures
- Domain events: all events the aggregate can emit (e.g. `[EntityCreated]`, `[EntityUpdated]`), each implements the project's `DomainEvent` contract; events carry fields needed to populate Phase 1 document
- Any value objects for sub-domains
- Tests: aggregate creation, state transitions, invariants, event collection

---

### Phase 3 — Application Layer: Commands & Handlers, Queries & Handlers

**Goal:** Wire domain to read-side. Commands change aggregate state; queries and projections serve the read model.

**Depends on:** Phase 1 (read model) and Phase 2 (domain model)

**Outputs:**

- `[Command]` dataclass(es): input contracts for use cases, implementing the project's `CommandHandler` contract
- Command handlers: orchestrate aggregate state changes and repository persistence
- `[Query]` dataclass(es): read contracts, implementing the project's `QueryHandler` contract
- Query handlers: read from `[EntityStore]`, return `[EntityDocument]`
- Event subscriber handler: transforms Phase 2 events into Phase 1 documents
- Tests: command dispatch, state transitions, query results, event → projection mapping (using in-memory repository and store)

---

### Phase 4 — CLI Interface: Commands

**Goal:** Expose commands and queries via Typer/REPL.

**Depends on:** Phase 3 (commands and queries)

**Outputs:**

- Typer command implementations: dispatch to Phase 3 command and query handlers
- Help topics registered in REPL (`_HELP_TOPICS` dict)
- Output formatting (tables, lists, details)
- Manual verification: all commands discoverable via `help`, run correctly with sample data (all using in-memory storage)

---

### Phase 5 — Web UI: Views & Routes

**Goal:** Display entities and their state in the web interface.

**Depends on:** Phase 3 (queries)

**Outputs:**

- FastAPI route handlers: list view, detail view, and any domain-specific views; dispatch to Phase 3 query handlers
- Jinja2 templates: layout, entity list, entity detail
- Navigation integration (links from other pages, if applicable)
- Manual verification: all pages render correctly, new data appears immediately, URLs are user-friendly (all using in-memory storage)

---

### Phase 6 — Infrastructure: Durable Storage

**Goal:** Replace in-memory implementations with durable storage. Ensure full rebuildability from event store.

**Depends on:** Phases 1–5 (all domain, application, query, and interface layers)

**Outputs:**

- `Sqlite[Aggregate]Repository` extends the project's `SqliteRepository` base: persists aggregates to per-aggregate databases
- `Sqlite[Entity]Store`: persists projection to durable storage (same interface as in-memory version)
- Event registry: `dict[str, type[DomainEvent]]` mapping `DomainEvent.NAME` constants to event classes for deserialisation
- SQLite schema: tables for aggregates/events and projections, with isolation by aggregate ID
- Dependency injection: wire the project's `SqliteEventStore`, inject concrete `SqliteRepository` and `SqliteStore` implementations
- Tests: end-to-end persistence, event store append/load, projection rebuildability, isolation
- Manual verification: data persists across application restart, CLI/web UI read from disk correctly

---

## Design Session Workflow

For each phase:

1. **Scope:** Clarify what inputs, outputs, and dependencies this phase has
2. **Design:** Sketch architecture, identify trade-offs, propose structure
3. **Specification:** Write tests, define interfaces
4. **Implementation:** Code
5. **Validation:** Manual verification before documenting

---

## Notes

- Phases are strict dependencies; implementing out of order risks rework
- Each phase should have a dedicated design conversation before implementation
- **Phase 1 constraints scope:** Only data in the read model will be extracted and tracked. This prevents scope creep from 300+ fields to just what users need.
- Phases 2–5 build the full feature on in-memory storage; Phase 6 is infrastructure-only
- Event store is append-only; projections are fully rebuildable from events
- All core contracts (Aggregate, Repository, EventStore, MessageBus, CommandHandler, QueryHandler) are mandatory
- In-memory implementations provided for the project (`InMemoryEventStore`, `InMemoryRepository`, `InMemoryMessageBus`) are production-quality for phases 1–5
