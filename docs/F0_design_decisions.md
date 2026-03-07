# TIC — Design Decisions

This document records significant design decisions made during development.
Each entry includes the decision, rationale, and any future considerations.

---

## Event Sourcing Pattern (Phase 3R Refactoring)

**Decision:** Aggregates track domain events; repositories extract and persist them.

**Rationale:**
- Aggregate is the source of truth: it decides what happened, not the command handler
- DDD/Event Sourcing: command handler orchestrates, but doesn't create events
- Clear responsibility: handler calls `repository.save(aggregate)`, which handles all persistence

**Correct flow:**
```python
# Command handler (application layer)
campaign = repository.get_by_name(name) or Campaign.create_new(name)
campaign.record_save_import(game_date)  # Aggregate tracks changes
repository.save(campaign)  # Repository extracts events and publishes

# Repository (infrastructure layer)
def save(self, campaign: Campaign) -> None:
    events = campaign.get_pending_changes()  # Extract tracked events
    event_store.append(campaign.id, events)  # Persist
    message_bus.publish(events)  # Dispatch
```

**Current state (Phase 3):** Command handler creates and publishes events (WRONG).
This must be refactored in Phase 3R before Phase 4 infrastructure is implemented.

**Tracking:** Phase 3R is a required refactoring before Phase 4.

---

## Command Handler Return Values (Phase 3+)

**Decision:** Command handlers return a minimal result DTO (aggregate ID + status), not business data.

**Rationale:**
- CQRS separation: commands are for state changes, queries are for reading
- CLI/web layer needs the ID to show user feedback or link to next operation
- Avoids coupling: result DTO carries only what the caller needs immediately
- Business data (full metadata) comes from queries on projections (read-side)

**Pattern:**
```python
@dataclass
class ImportSaveResult:
    campaign_id: UUID
    is_new: bool

class ImportSaveHandler:
    def handle(self, command: ImportSaveCommand) -> ImportSaveResult:
        # ... orchestrate domain logic ...
        return ImportSaveResult(campaign_id=campaign.id, is_new=True)
```

**Note:** After Phase 3R, the pattern remains the same, but events are no longer created here.
Repository.save() handles event extraction and dispatch internally.

---

## Campaign Factory Method (Phase 2)

**Decision:** Use `Campaign.create_new(name, id=None, created_at=None)` as the public factory.

**Rationale:**
- Caller controls both identity and timestamp generation (testability, flexibility)
- No infrastructure dependencies in domain
- Aggregate state only holds what's needed for invariants
- Explicit vs implicit: production code omits optional params, tests inject them

**Pattern:**
```python
# Production: auto-generate UUID and timestamp
campaign = Campaign.create_new("ResistCouncil")

# Tests: deterministic
campaign = Campaign.create_new(
    "ResistCouncil",
    id=uuid4(),
    created_at=datetime(2045, 1, 1)
)

# Flexible: use only what you need
campaign = Campaign.create_new("ResistCouncil", id=fixed_uuid)  # auto timestamp
campaign = Campaign.create_new("ResistCouncil", created_at=fixed_datetime)  # auto id
```

**Design Principle:**
The aggregate doesn't care where its identity comes from. Both `id` and `created_at` are
optional parameters to the factory — the caller decides whether to inject or auto-generate.
This keeps the aggregate agnostic to infrastructure while maximizing testability.

---

## Campaign UUID Generation (Phase 2)

**Decision:** Use UUID4 for campaign identity.

**Rationale:**
- Standard library support (no external dependencies)
- Battle-tested, widely used
- Sufficient for F0 (no natural ordering requirement yet)
- Simple to generate and serialize

**Future Consideration:**
- If historical trend charts or audit logs require chronological ordering of campaigns,
  consider migrating to UUID7 (lexicographically sortable by timestamp).
- UUID7 requires `uuid6` package or Python 3.13+ stdlib.
- Migration path: Add `uuid6` as optional dependency, update `Campaign.create_new()` to use `uuid7.uuid7()`.
- No breaking change: UUIDs are opaque identifiers; storage and API can switch transparently.

**Tracking:** Consider this when implementing F8 (Historical Trends) if campaign ordering becomes relevant.

---

## Event Deserialization (Phase 1)

**Decision:** Explicit, type-safe deserialization without reflection frameworks.

**Rationale:**
- Avoid magic: no automatic reflection, no framework surprises
- Mypy --strict compliance
- Java-style safety: compile-time type checking translates to Python type hints

**Current State:**
- Dynamic import + getattr for event class lookup
- Explicit dataclass validation
- Fail fast on unknown types

**Future Consideration (Phase 1R):**
- If event deserialization boilerplate exceeds ~100 lines across all event types,
  evaluate Pydantic for cleaner validation and schema evolution.
- Pydantic trades explicit code for declarative schema; decision to be made when
  we have concrete data on boilerplate burden.

---

## Datetime Dependency Injection (Phase 2)

**Decision:** Pass `created_at: datetime` as parameter, don't use Clock abstraction.

**Rationale:**
- Aggregate state should only hold what's needed to enforce invariants
- Infrastructure concern (Clock) has no place in domain state
- Caller responsibility: inject fixed datetime in tests, use `datetime.now()` in production
- Simpler than Clock pattern; no added abstraction

**Pattern:**
```python
# Production
campaign = Campaign.create_new(name)  # uses datetime.now()

# Tests (deterministic, no system time dependency)
campaign = Campaign.create_new(
    name,
    created_at=datetime(2045, 1, 1, 0, 0, 0)
)
```

**Trade-off:** Tests that call `create_new(name)` without `created_at` will have non-deterministic
timestamps. This is intentional: tests should inject known values. This pattern catches accidental
non-determinism.

---
