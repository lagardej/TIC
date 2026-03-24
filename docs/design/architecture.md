# Architecture Reference

This document centralises the architectural design of this project. It explains the "why" behind structural decisions and provides a reference for implementing features consistently.

______________________________________________________________________

## Overview

The project is built using *Domain-Driven Design (DDD)*, *Command Query Responsibility Segregation (CQRS)*, and *Event Sourcing*, organised by modules.

**Core philosophy:** Architecture is a constraint that keeps the codebase coherent as it grows. Every decision is enforced at the module level and validated at build time.

## Modular Philosophy

This project adopts a modular philosophy: modules are first-class design units with enforced boundaries, explicit public APIs, and automated verification where practical.

### Core Principles

#### 1. Modules as Design Boundaries

- Each module has strict rules about what can be imported from outside.
- Accidental violations are caught at build time, not discovered during maintenance.

#### 2. Explicit Public API Contracts

- **Module-to-module boundaries:** Modules communicate through events (publish/subscribe) or SPIs (Service Provider Interfaces—public ABCs with internal implementations). Cross-module imports use root exports only.
- **Infrastructure exemption:** Infrastructure packages (`shared/`, composition root) are not subject to public API rules. They can import from any layer as needed for dependency injection and framework concerns.
- **Domain layer:** Always internal. Domain objects (aggregates, value objects) remain encapsulated within their module. A module's public API must be explicitly declared in a clear, language-appropriate place (for example: a module export file, package manifest, or public API declaration). Avoid implicitly exporting internals.
- Sub-packages are allowed if structurally necessary (for example, `endpoint/cli/` or `endpoint/web/`) provided their public exports are explicitly declared.
- Package facades should only re-export symbols from their own module boundary. Do not re-export symbols from sibling modules without explicit intent.

#### 3. Event-Driven Communication

- Modules primarily communicate through domain events on a message bus.
- Alternatively, modules may expose Service Provider Interfaces (SPIs)—public ABCs that other modules can depend on, with implementations remaining internal.
- No direct imports between module internals; no shared mutable state.
- Event subscriptions and SPI contracts decouple modules from each other.

#### 4. Automated Verification and Documentation

TODO: Define the automated verification and documentation process.

This section is intentionally left as a placeholder. Suggested next steps (to be approved and executed by the developer):

- Define a verification tool or script that enforces module boundaries and layer dependency rules.
- Add documentation generation steps (optional) and a CI job that validates documentation links.
- Document the verification process here once implemented.

### Benefits

- **Resilience to refactoring:** Module names and responsibilities may change; the rules remain constant.
- **Early detection of drift:** Architects don't discover structural violations months later during a code review.
- **Clarity for new contributors:** The explicit public API makes it obvious what each module exposes.
- **Maintainability:** As the codebase grows, clear boundaries prevent it from becoming a tangled monolith.

## Modules (Abstract)

A module is an organisational boundary within which domain language and models are consistent. This project uses modules to partition responsibilities and enforce strict separation.

Modules fall into two categories:

- *Command modules* (write side) — Maintain aggregates, enforce invariants, emit events
- *Query modules* (read side) — Project events into read models, serve queries

Each follows a layered structure (details in "Command Modules vs Query Modules" section below). All modules share common layers:

- *application* — Use case handlers (commands for write modules, queries for read modules)
- *endpoint* — User-facing entry points (CLI, web routes)
- *infrastructure* — Concrete implementations (repositories, stores, external services)

**Module independence:** Module names and responsibilities may change over time. The rules below apply to every module regardless of its concrete domain.

## Shared Package (Non-Module)

`shared/` is *not* a module. It is a place to keep abstract classes and common services that other modules may extend or consume.

**Rules for shared/:**

- Still follows the same layer separation: `domain`, `application`, `endpoint`, `infrastructure`.
- Still obeys the dependency rules below.
- May be imported by any module.
- Contains no domain-specific models or logic.

## Module Structure (Abstract)

```
project_root/
├── <module_command>/                 # Command Module (write side)
│   ├── domain
│   ├── application
│   ├── endpoint
│   └── infrastructure
├── <module_query>/                   # Query Module (read side)
│   ├── projection
│   ├── application
│   ├── endpoint
│   └── infrastructure
└── shared/                           # Shared abstractions and services (non-module)
    ├── domain
    ├── application
    ├── endpoint
    └── infrastructure
```

**Key insight:** Modules follow a layered structure. Command modules use domain for write-side aggregates; query modules use projection for read-side materialisation. Layers communicate downward (endpoint → application → domain/projection). Infrastructure can call any layer but is never called directly (always injected).

## Command Modules vs Query Modules

This project enforces strict separation between write-side (command) and read-side (query) modules.

### Command Modules

**Purpose:** Maintain aggregates, enforce invariants, emit events.

**Structure:**

```
<command_module>/
├── domain               # Aggregate, Repository ABC, value objects, invariants
├── application          # Command handlers (use cases)
├── endpoint             # CLI/web entry points
└── infrastructure       # Concrete implementations (repositories, external services)
```

**Strict rules:**

- Domain always internal (no exports)
- Events exported at module root
- Cross-module boundaries: events or SPIs only
- No shared mutable state

### Query Modules

**Purpose:** Project events into read models, serve queries without modifying state.

**Structure:**

```
<query_module>/
├── projection           # Projection documents, read model stores
├── application          # Query handlers (read use cases)
├── endpoint             # CLI/web entry points
└── infrastructure       # Concrete projection stores
```

**Pragmatic approach:**

- Projections are always internal (denormalised views, not aggregates)
- Query DTOs exported at root for cross-module queries
- Cross-module queries allowed for performance (read models can aggregate data from multiple modules)
- No modification of state; queries are side-effect-free
- Read model stores may be shared if performance or consistency requires it

**Key distinction:** Query modules prioritise *performance and usability* over strict isolation because reads never corrupt domain invariants. Command modules maintain *absolute rigour* to protect the write side.

## Layer Dependencies

Strict module hierarchy is an architectural constraint and should be enforced by conventions, verification scripts, or build-time checks where possible:

```
endpoint → application → domain
infrastructure → any layer (never the reverse)
```

### Domain Layer (`domain`)

- Minimise external dependencies. Domain code should not depend on infrastructure or other modules; keep the core model and invariants isolated from implementation concerns.
- Define aggregates, value objects, and abstract contracts appropriate to the project's language.
- Encapsulate business logic and invariants in the domain.

### Application Layer (`application`)

- *No infrastructure imports.* Depends only on domain ABCs.
- Defines use cases as command/query handlers.
- Orchestrates: call domain logic → call injected ABCs → return minimal result DTOs.
- No business logic here — that lives in the domain.

### Endpoint Layer (`endpoint`)

- *User-facing entry points.* CLI commands, web routes, API endpoints.
- Parses user input, calls application handlers, formats output.
- Depends only on application handlers (no domain logic here).

### Infrastructure Layer (`infrastructure`)

- Concrete implementations of domain/application contracts.
- Responsible for persistence, external APIs, and platform-specific concerns.
- Provide implementations that are wired into higher layers at the composition root; avoid direct imports of infrastructure from domain code.

### Dependency Placement (Guidance)

Dependency placement and module-coupling rules are an architectural concern and live here. Language-specific implementation details (for example, how to express interfaces or perform dependency injection in a particular language) belong in language convention documents.

- Core/domain modules should avoid direct dependencies on infrastructure or external libraries whenever practical.
- Define abstract interfaces or contracts in the appropriate higher-level layer (domain or application) and provide concrete implementations in `infrastructure/` or adapter modules.
- Wire concrete implementations at the composition root; do not import infrastructure implementations directly from domain modules.
- Document and justify any exceptions in the architecture decision log or PR description.

## Data Flow (Abstract Example)

```
1. User input via CLI or web
   ↓
2. Endpoint layer parses input and builds a command/query
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

- Aggregates decide what happened, not handlers.
- Repositories persist and dispatch events.
- Events are the bridge between modules.

## Data Storage (Abstract)

### Append-Only Event Store

**Properties:**

- Append-only: events are never modified or deleted.
- Immutable: event type and data are frozen at insert time.
- Registry-based deserialisation to avoid reflection magic.

### Projections

Projections are read models derived from events. They are fully rebuildable and optimised for query patterns.

## Dependency Injection

All dependencies are injected through a single composition root. Infrastructure types are instantiated only there and never imported directly elsewhere.

**Pattern (abstract):**

- Domain/Application depend on ABCs.
- Infrastructure provides concrete implementations.
- Composition root wires handlers with concrete instances.

## Command Query Responsibility Segregation (CQRS)

Commands and queries are strictly separated at the module level.

- *Command handlers* orchestrate state changes; aggregates decide what happened and emit events.
- *Query handlers* read from projections only, never the event store.
- Handlers return minimal result DTOs, not full aggregates.

## Event Sourcing

The event store is the system of records. All state changes are captured as immutable events.

**Event design (abstract):**

- Events are immutable data records representing facts that have occurred. Prefer simple, serialisable data structures with no behavioural logic.

### Event Immutability

Events must be treated as immutable once created. Enforce immutability using the language's facilities or clear conventions (for example, read-only data types, immutable value objects, or defensive copying). The implementation details will vary by language; document language-specific patterns in the language convention documents.

### Abstract Event Types

Every concrete event type should declare a stable identifier (an "event type") and a well-defined schema. Intermediate base event types may be used for grouping and should be clearly marked as abstract in the language-appropriate way. Document the event registry and deserialisation strategy in an implementation guide.

**Aggregate rehydration:**

- Aggregates are rebuilt by replaying event history in order.
- Consider snapshotting when replay cost becomes significant.

## Message Bus

Events are published to a message bus, allowing modules to react without direct coupling.

- Subscribers are registered at the composition root.
- A synchronous in-memory bus is acceptable for local development.
- An async bus can replace it without changing modules.

## Service Provider Interfaces (SPIs)

**Purpose:** Modules export abstract interfaces (SPIs) to allow other modules to depend on the abstraction without tight coupling to implementations.

**Ownership and visibility:**

- Each SPI is **defined and owned by a single module** (the module that exports it).
- The SPI interface itself is **exported publicly** in the module's public API so other modules can import and depend on it.
- Concrete implementations of the SPI **remain internal** to the defining module—they live in that module's infrastructure or domain layers.
- No other module may provide or implement an SPI defined by another module.

**Example:**

```
Inventory module exports: InventoryRepository (abstract interface)
 ├─ Exported in: inventory/__init__.py
 ├─ Other modules depend on: InventoryRepository
 └─ Concrete implementation: inventory/infrastructure/postgres_inventory_repository.py
    (owned by Inventory, never exported)

Orders module may depend on:
 └─ InventoryRepository (the abstraction only)
```

**Benefit:** Modules decouple from each other's implementations while still depending on shared contracts.

## File Granularity

*One concept per file.* This is a hard constraint.

Physical location follows clear patterns. Aggregates and value objects live in `domain` and are not exported as part of other modules' internals. Application handlers follow their layer structure. Sub-packages are allowed if they reflect structural needs (for example, `endpoint/cli` for CLI commands, `endpoint/web` for web routes), but public exports must be declared explicitly in a module's public API declaration.

- **Aggregate** — `domain/<aggregate>`
- **Aggregate repository/ABC** — `domain/<aggregate>_repository`
- **Use case command + handler** — `application/<use_case>`
- **Concrete implementation** — `infrastructure/<tech>_<concept>`
- **Query handler** — `application/<query>`
- **CLI command** — `endpoint/cli/<command>`
- **Web route** — `endpoint/web/<route>`
- **Module public API** — module root export / public API file

## Defensive Parsing (Abstract)

When ingesting evolving external data:

- Missing keys are normal.
- Unknown fields are ignored.
- Only extract what is needed for the current feature.
- Fail fast on corrupted data (e.g., invalid JSON).

### Testing Strategy (Abstract)

### Fakes, Not Mocks

For each module interface or abstract contract, provide in-memory fakes for unit testing where practical.

### Test Structure

- Tests should live in a dedicated top-level `tests/` area and mirror the project's module structure where practical.
- Keep test code separate from production module code.
- Avoid external I/O in unit tests; use in-memory databases or test doubles when appropriate.
- Boundary checks should validate runtime import rules and module public API contracts.

## Code Style and Conventions

This document describes architectural rules. Language- and tool-specific coding conventions belong in the language-specific convention documents (for example, `docs/design/python_conventions.md`). High-level expectations:

### General

- Prefer explicit and clear code over clever or implicit constructs.
- Avoid circular dependencies between modules.
- Infrastructure implementations should be provided by the composition root and not imported into domain logic.

### Encoding & I/O

- Treat UTF-8 as the canonical encoding for text content. When reading or writing files, specify encoding explicitly if the platform or language requires it.

## Design Principles

### Explicit Over Implicit

Code should say what it is doing. Avoid magic, reflection, and implicit conventions.

### Fail Fast

Validate early and raise descriptive errors.

### Immutability

Domain entities and events should be treated as immutable where practical. Use the appropriate language-level mechanisms (for example, read-only data structures, immutable value objects, or explicit freezing patterns) to enforce immutability for state objects and events. Document any language-specific enforcement techniques in the language convention documents.

### No Surprises

If code looks like it does X, it does X. No side effects, no hidden state mutations.

### Cohesion Over Abstraction

Keep related code together. Separate only when there is a genuine reason.

## Glossary

- ***Aggregate Root*** — the entry point to an aggregate; all state changes go through it
- ***CQRS*** — Command Query Responsibility Segregation; separate write (commands) from read (queries)
- ***DDD*** — Domain-Driven Design; organise code around domain language and boundaries
- ***DTO*** — Data Transfer Object; minimal data carrier (no business logic)
- ***Event Sourcing*** — store changes as events; derive state by replaying; events are the system of record
- ***Event*** — an immutable record of something that happened; source of truth for state changes
- ***Message Bus*** — publish/subscribe for events; decouples modules
- ***Module*** — a boundary within which models are consistent; no cross-module imports
- ***Projection*** — a materialised read model derived from events; optimised for queries
- ***Repository*** — abstracts persistence; loads/saves aggregates; handles event dispatch
- ***SPI*** — Service Provider Interface; an abstract interface exported by a module for other modules to depend on, with implementation remaining internal
- ***Use Case*** — an application-layer operation (command or query handler)
