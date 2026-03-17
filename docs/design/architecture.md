# TIC Architecture Reference

This document centralises the architectural design of TIC.
It explains the "why" behind structural decisions and provides a reference for implementing features consistently.

---

## Overview

TIC is built using *Domain-Driven Design (DDD)*, *Command Query Responsibility Segregation (CQRS)*, and *Event Sourcing*, organised by modules.

**Core philosophy:** Architecture is a constraint that keeps the codebase coherent as it grows.
Every decision is enforced at the module level and validated at build time.

## Framework Boundary

`abcdef` is an extracted framework dependency, not part of the TIC codebase structure.

- Source repository: <https://github.com/lagardej/abcdef-py>
- TIC application code imports `abcdef` only through its published package API.
- Framework evolution happens in the `abcdef` repository; TIC pins to a git commit via `uv.lock`.
- TIC architecture rules in this document apply to TIC modules only.

## Spring Modulith Philosophy

TIC adopts the *Spring Modulith* philosophy: modules are first-class design units with enforced boundaries, explicit public APIs, and automated verification.

### Core Principles

#### 1. Modules as Design Boundaries

* Each module has strict rules about what can be imported from outside.
* Accidental violations are caught at build time, not discovered during maintenance.

#### 2. Explicit Public API Contracts

* **Module-to-module boundaries:** Modules communicate through events (publish/subscribe) or SPIs (Service Provider Interfaces—public ABCs with internal implementations). Cross-module imports use root exports only.
* **Infrastructure exemption:** Infrastructure packages (`shared/`, composition root) are not subject to public API rules. They can import from any layer as needed for dependency injection and framework concerns.
* **Domain layer:** Always internal. Never exported from `__init__.py`. Domain objects (aggregates, value objects) remain encapsulated within their module.
* Sub-packages are allowed if structurally necessary (e.g., `interface/cli/`, `interface/web/`) as long as their exports are explicitly declared in `__init__.py`.
* A module's `__init__.py` declares what other *modules* may import—events for cross-module communication, or ABCs for service provider interfaces.
* Package facades may only re-export symbols from their own namespace. Do not re-export symbols from sibling packages.

#### 3. Event-Driven Communication

* Modules primarily communicate through domain events on a message bus.
* Alternatively, modules may expose Service Provider Interfaces (SPIs)—public ABCs that other modules can depend on, with implementations remaining internal.
* No direct imports between module internals; no shared mutable state.
* Event subscriptions and SPI contracts decouple modules from each other.

#### 4. Automated Verification and Documentation

TODO: Define the automated verification and documentation process.

This section is intentionally left as a placeholder. Suggested next steps (to be approved and executed by the
developer):

- Define a verification tool or script that enforces module boundaries and layer dependency rules.
- Add documentation generation steps (optional) and a CI job that validates documentation links.
- Document the verification process here once implemented.

### Benefits

* **Resilience to refactoring:** Module names and responsibilities may change; the rules remain constant.
* **Early detection of drift:** Architects don't discover structural violations months later during a code review.
* **Clarity for new contributors:** The explicit public API makes it obvious what each module exposes.
* **Maintainability:** As the codebase grows, clear boundaries prevent it from becoming a tangled monolith.

## Modules (Abstract)

A module is an organisational boundary within which domain language and models are consistent.
TIC uses modules to partition responsibilities and enforce strict separation.

Modules fall into two categories:

* *Command modules* (write side) — Maintain aggregates, enforce invariants, emit events
* *Query modules* (read side) — Project events into read models, serve queries

Each follows a layered structure (details in "Command Modules vs Query Modules" section below).
All modules share common layers:

* *application* — Use case handlers (commands for write modules, queries for read modules)
* *infrastructure* — Concrete implementations (repositories, stores, external services)
* *interface* — User-facing entry points (CLI, web routes)

**Module independence:** Module names and responsibilities may change over time. The rules below apply to every module regardless of its concrete domain.

## Shared Package (Non-Module)

`shared/` is *not* a module.
It is a place to keep abstract classes and common services that other modules may extend or consume.

**Rules for shared/:**

* Still follows the same layer separation: `domain`, `application`, `infrastructure`, `interface`.
* Still obeys the dependency rules below.
* May be imported by any module.
* Contains no domain-specific models or logic.

## Module Structure (Abstract)

```
tic/
├── <module_command>/                 # Command Module (write side)
│   ├── domain
│   ├── application
│   ├── infrastructure
│   └── interface
├── <module_query>/                   # Query Module (read side)
│   ├── projection
│   ├── application
│   ├── infrastructure
│   └── interface
└── shared/                           # Shared abstractions and services (non-module)
    ├── domain
    ├── application
    ├── infrastructure
    └── interface
```

**Key insight:** Modules follow a layered structure. Command modules use domain for write-side aggregates; query modules use projection for read-side materialisation. Layers communicate downward (interface → application → domain/projection). Infrastructure can call any layer but is never called directly (always injected).

## Command Modules vs Query Modules

TIC enforces strict separation between write-side (command) and read-side (query) modules.

### Command Modules

**Purpose:** Maintain aggregates, enforce invariants, emit events.

**Structure:**

```
<command_module>/
├── domain               # Aggregate, Repository ABC, value objects, invariants
├── application          # Command handlers (use cases)
├── infrastructure       # Concrete implementations (repositories, external services)
└── interface            # CLI/web entry points
```

**Strict rules:**

* Domain always internal (no exports)
* Events exported at module root
* Cross-module boundaries: events or SPIs only
* No shared mutable state

### Query Modules

**Purpose:** Project events into read models, serve queries without modifying state.

**Structure:**

```
<query_module>/
├── projection           # Projection documents, read model stores
├── application          # Query handlers (read use cases)
├── infrastructure       # Concrete projection stores
└── interface            # CLI/web entry points
```

**Pragmatic approach:**

* Projections are always internal (denormalised views, not aggregates)
* Query DTOs exported at root for cross-module queries
* Cross-module queries allowed for performance (read models can aggregate data from multiple modules)
* No modification of state; queries are side-effect-free
* Read model stores may be shared if performance or consistency requires it

**Key distinction:** Query modules prioritise *performance and usability* over strict isolation because reads never corrupt domain invariants. Command modules maintain *absolute rigour* to protect the write side.

## Layer Dependencies

Strict module hierarchy is enforced at import time:

```
interface → application → domain
infrastructure → any layer (never the reverse)
```

### Domain Layer (`domain`)

* *Zero external dependencies.* No imports from other layers, no third-party libraries.
* Defines aggregates, value objects, and ABCs.
* Encodes business logic and invariants.

### Application Layer (`application`)

* *No infrastructure imports.* Depends only on domain ABCs.
* Defines use cases as command/query handlers.
* Orchestrates: call domain logic → call injected ABCs → return minimal result DTOs.
* No business logic here — that lives in the domain.

### Infrastructure Layer (`infrastructure`)

* *Concrete implementations of domain ABCs.*
* Database access, file I/O, external services.
* Injected into application handlers; never called directly.

### Interface Layer (`interface`)

* *User-facing entry points.* CLI commands, web routes, API endpoints.
* Parses user input, calls application handlers, formats output.
* Depends only on application handlers (no domain logic here).

## Data Flow (Abstract Example)

```
1. User input via CLI or web
   ↓
2. Interface layer parses input and builds a command/query
   ↓
3. Application handler orchestrates domain logic
   ↓
4. Domain aggregate validates invariants and emits events
   ↓
5. Repository persists events and publishes them
   ↓
6. Subscribers project events into read models
   ↓
7. Handler returns a minimal result DTO
```

**Key points:**

* Aggregates decide what happened, not handlers.
* Repositories persist and dispatch events.
* Events are the bridge between modules.

## Data Storage (Abstract)

### Append-Only Event Store

**Properties:**

* Append-only: events are never modified or deleted.
* Immutable: event type and data are frozen at insert time.
* Registry-based deserialisation to avoid reflection magic.

### Projections

Projections are read models derived from events. They are fully rebuildable and optimised for query patterns.

## Dependency Injection

All dependencies are injected through a single composition root. Infrastructure types are instantiated only there and never imported directly elsewhere.

**Pattern (abstract):**

* Domain/Application depend on ABCs.
* Infrastructure provides concrete implementations.
* Composition root wires handlers with concrete instances.

## Command Query Responsibility Segregation (CQRS)

Commands and queries are strictly separated at the module level.

* *Command handlers* orchestrate state changes; aggregates decide what happened and emit events.
* *Query handlers* read from projections only, never the event store.
* Handlers return minimal result DTOs, not full aggregates.

## Event Sourcing

The event store is the system of records. All state changes are captured as immutable events.

**Event design (abstract):**

* Events are plain classes with no behaviour (not dataclasses).

### Event Immutability

`Event` enforces immutability via `__setattr__` and `__delattr__` overrides,
using the same pattern as `AggregateId`. Any attempt to assign or delete an
attribute after construction raises `AttributeError`.

Because `Event` is not a dataclass, subclasses must initialise their own
attributes using `object.__setattr__(self, name, value)` in `__init__` —
normal assignment (`self.x = y`) is blocked by the override.

```python
class ThingHappened(DomainEvent):
    event_type = "thing_happened"

    def __init__(self, value: str, *, occurred_at: datetime, aggregate_id: str) -> None:
        super().__init__(occurred_at=occurred_at, aggregate_id=aggregate_id)
        object.__setattr__(self, "value", value)  # required
```

Plain-class subclasses that use `self.x = y` in `__init__` will raise
`AttributeError` at construction time — the convention must be followed
manually.

### Abstract Event Classes (`_abstract_event`)

`Event.__init_subclass__` enforces that every concrete subclass declares a
non-empty `event_type` directly in its own class body. Intermediate base
classes in the hierarchy (e.g. `DomainEvent`) need to opt out of this check
because they are not themselves concrete events.

They do so by setting `_abstract_event = True` directly in their class body:

```python
class DomainEvent(Event):
    _abstract_event = True  # exempt from event_type enforcement
```

The flag is checked via `cls.__dict__.get("_abstract_event")`, so it must
appear directly on the class — inheriting it from a parent has no effect.
Concrete leaf classes must never set it; they must declare `event_type`.

The underscore prefix marks this as an internal framework convention. It is
not part of the public API and should not appear on application-level event
classes.

**Aggregate rehydration:**

* Aggregates are rebuilt by replaying event history in order.
* A snapshotting system may be needed later.

## Message Bus

Events are published to a message bus, allowing modules to react without direct coupling.

* Subscribers are registered at the composition root.
* A synchronous in-memory bus is acceptable for local development.
* An async bus can replace it without changing modules.

## File Granularity

*One concept per file.* This is a hard constraint.

Physical location follows clear patterns. Aggregates and value objects always live in `domain` and are never exported. Application handlers follow their layer structure. Sub-packages are allowed if they reflect structural needs (e.g., `interface/cli` for CLI commands, `interface/web` for web routes), but all public exports must be declared in `__init__.py`.

| Concept                     | File Pattern                         |
|-----------------------------|--------------------------------------|
| Aggregate                   | `domain/<aggregate>.py`              |
| Aggregate ABC               | `domain/<aggregate>_repository.py`   |
| Use case command + handler  | `application/<use_case>.py`          |
| Concrete ABC implementation | `infrastructure/<tech>_<concept>.py` |
| Query handler               | `application/<query>.py`             |
| CLI command                 | `interface/cli/<command>.py`         |
| Web route                   | `interface/web/<route>.py`           |
| `__init__.py`               | Public API contract; re-exports only |

## Defensive Parsing (Abstract)

When ingesting evolving external data:

* Missing keys are normal.
* Unknown fields are ignored.
* Only extract what is needed for the current feature.
* Fail fast on corrupted data (e.g., invalid JSON).

## Testing Strategy (Abstract)

### Fakes, Not Mocks

For each module ABC, provide in-memory fakes for testing.

### Test Structure

* `tests/` mirrors `tic/`.
* No test code inside module directories.
* No external I/O in tests; use in-memory databases when needed.
* Boundary checks should validate both runtime import rules and package facade
  re-export rules (`__init__.py` imports only from its own namespace).

## Code Style and Conventions

### Type Hints

All function signatures must have type hints.

### Docstrings

Public classes and functions have Google-style docstrings.

### Imports

* No circular imports.
* Infrastructure is never imported directly outside the composition root.
* Cross-module imports use root exports only.

### Encoding

Always specify encoding explicitly when opening files or running subprocesses.

## Design Principles

### Explicit Over Implicit

Code should say what it is doing. Avoid magic, reflection, and implicit conventions.

### Fail Fast

Validate early and raise descriptive errors.

### Immutability

Domain entities and events are immutable where practical.

`AggregateState` is a frozen dataclass. All concrete state classes must be
declared as `@dataclass(frozen=True)`. This enforces immutability at
construction time, provides value-based `__eq__` and `__hash__`, and makes
`__repr__` readable without boilerplate. Plain-class subclasses (not
decorated with `@dataclass`) will compile but will not have immutability
enforced at runtime — the convention must be followed manually.

### No Surprises

If code looks like it does X, it does X. No side effects, no hidden state mutations.

### Cohesion Over Abstraction

Keep related code together. Separate only when there is a genuine reason.

## Glossary

| Term             | Meaning                                                                                  |
|------------------|------------------------------------------------------------------------------------------|
| *Aggregate Root* | The entry point to an aggregate. All state changes go through it.                        |
| *CQRS*           | Command Query Responsibility Segregation. Separate write (commands) from read (queries). |
| *DDD*            | Domain-Driven Design. Organise code around domain language and boundaries.               |
| *DTO*            | Data Transfer Object. Minimal data carrier (no business logic).                          |
| *Event Sourcing* | Store changes as events; derive state by replaying. Events are the system of record.     |
| *Event*          | An immutable record of something that happened. Source of truth for state changes.       |
| *Message Bus*    | Publish/subscribe for events. Decouples modules.                                         |
| *Module*         | A boundary within which models are consistent. No cross-module imports.                  |
| *Projection*     | A materialised read model derived from events. Optimised for queries.                    |
| *Repository*     | Abstracts persistence. Loads/saves aggregates; handles event dispatch.                   |
| *Use Case*       | An application-layer operation (command or query handler).                               |
