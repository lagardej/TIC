# TIC — Roadmap

Delivery is organised by feature slice. Each slice is a working vertical
cut through the full stack: domain → application → infrastructure → CLI →
web UI. Nothing is considered done until it is tested, wired end-to-end,
and reachable from both the CLI and the web UI.

The roadmap covers F0 in full. Later slices will be detailed when F0 is complete.

---

## F0 — Campaign Metadata

**Objective:** import a save file and display campaign metadata in the CLI
and web UI. Every architectural layer is exercised. No relational joins
required — the three source types (`TITimeState`, `TIGlobalValuesState`,
`TIGlobalResearchState`) have no ID references to other entities.

This slice is the foundation. All subsequent slices reuse what is built here.

---

### Domain decisions

**Campaign identity:** `name` (e.g. `"ResistCouncil"`) is the natural
campaign identity — one campaign per faction. The UUID is an internal
surrogate key for storage. `name` maps to a human-readable display
name via `TIGlobalValuesState.scenarioCustomizations.customFactionText`.

**`TIMetadataState` is not used.** All fields it carries are available with
better types from other sources:
- `playerFactionName` (display) → derived from `customFactionText[name].customDisplayName`
- `difficulty` (string label) → derived at display time from `TIGlobalValuesState.difficulty` (int)
- `selectedFactionsForScenario` → `scenarioCustomizations.selectedFactionsForScenario`

---

### Phase 0 — Project Hygiene

Complete the project setup before writing any domain code.

- [ ] `pyproject.toml`: add `ruff` and `mypy` to dev dependencies; add
      `[tool.ruff]` and `[tool.mypy]` config sections (strict mode)
- [ ] `pyproject.toml`: add `fail_under = 80` to `[tool.coverage.report]`
- [ ] `.github/workflows/ci.yml`: lint (`ruff`), type-check (`mypy`),
      test (`pytest`) on every push
- [ ] `.gitignore`: verify `*.json` exclusion does not block `samples/` —
      add `!samples/**` if needed
- [ ] Confirm `tic/` is empty and ready for scaffolding

---

### Phase 1 — Shared Infrastructure

Builds the event store and message bus that all bounded contexts depend on.
Lives in `shared/`.

**Domain:**
- [ ] `shared/domain/event_store.py` — `EventStore` ABC:
      `append(campaign_id, event)`, `load(campaign_id) -> list`
- [ ] `shared/domain/message_bus.py` — `MessageBus` ABC:
      `publish(event)`, `subscribe(event_type, handler)`

**Infrastructure:**
- [ ] `shared/infrastructure/sqlite_event_store.py` — `SqliteEventStore`:
      full implementation, append-only, serialises events as JSON rows,
      stores event type name for deserialisation
- [ ] `shared/infrastructure/in_memory_message_bus.py` — `InMemoryMessageBus`:
      synchronous, used in tests and local mode
- [ ] `shared/infrastructure/sqlite_schema.py` — schema creation helpers,
      called on first connection

**Tests (`tests/shared/`):**
- [ ] `test_sqlite_event_store.py` — append, load, ordering, isolation
      between campaign IDs
- [ ] `test_in_memory_message_bus.py` — publish, subscribe, multiple handlers

---

### Phase 2 — Campaign Bounded Context: Domain

Defines what a campaign is and what happened to it.

**Domain (`campaign/domain/`):**
- [ ] `campaign.py` — `Campaign` aggregate: `id` (UUID), `name`
      (str — e.g. `"ResistCouncil"`), `created_at` (datetime); raises
      `SaveAlreadyImported` if deduplication check fails
- [ ] `campaign_repository.py` — `CampaignRepository` ABC:
      `get(campaign_id: UUID) -> Campaign | None`,
      `get_by_name(name: str) -> Campaign | None`,
      `save(campaign: Campaign)`
- [ ] `events/save_imported.py` — `SaveImported` dataclass:
      `campaign_id` (UUID), `name` (str), `faction_display_name` (str),
      `game_date` (datetime), `difficulty` (int), `scenario` (str),
      `selected_factions` (list[str]), `research_speed_multiplier` (float),
      `alien_progression_speed` (float), `cp_maintenance_bonus` (int),
      `imported_at` (datetime)

**Tests (`tests/campaign/domain/`):**
- [ ] `test_campaign.py` — aggregate creation, deduplication guard
- [ ] `test_save_imported.py` — event construction, field types

---

### Phase 3 — Campaign Bounded Context: Application

Orchestrates the import use case. Reads the save file, produces events,
persists them.

**Application (`campaign/application/`):**
- [ ] `save_file_reader.py` — `SaveFileReader` ABC:
      `read(path: Path) -> SaveFileData`
- [ ] `import_save.py` — `ImportSaveCommand` dataclass (`file_path: Path`);
      `ImportSaveHandler`: resolves or creates campaign by `name`,
      deduplicates by `game_date`, appends `SaveImported` event, publishes
      to message bus
- [ ] `save_file_data.py` — `SaveFileData` value object: typed fields
      extracted from three source types. Canonical sources and types:

      **`TITimeState`**
      - `currentDateTime` — nested object `{ year, month, day, hour, minute,
        second, millisecond }`; infrastructure constructs a `datetime` from
        these fields
      - `scenarioMetaTemplateName` (str)
      - `daysInCampaign` (int)

      **`TIGlobalValuesState`**
      - `difficulty` (int)
      - `controlPointMaintenanceFreebies` (int)
      - `campaignStartVersion` (str)
      - `latestSaveVersion` (str)
      - `scenarioCustomizations.selectedFactionsForScenario` (list[str])
      - `scenarioCustomizations.researchSpeedMultiplier` (float)
      - `scenarioCustomizations.alienProgressionSpeed` (float)
      - `scenarioCustomizations.customFactionText` (dict[str, str]) —
        extracted as a map of `name → display_name`, sourced from
        `customFactionText[name].customDisplayName` for each entry

      **`TIGlobalResearchState`**
      - `finishedTechsNames` (list[str])
      - `campaignStartYear` (int)
      - `useHarshTree` (bool)
      - `endGameTechsCompletedByCategory` (dict[str, int])
      - (`techProgress` faction ID refs are not extracted in this slice)

**Tests (`tests/campaign/application/`):**
- [ ] `test_import_save_handler.py` — successful import, deduplication
      (same game_date → no-op), new campaign creation, existing campaign
      append; use fakes for `SaveFileReader`, `CampaignRepository`,
      `EventStore`, `MessageBus`

---

### Phase 4 — Campaign Bounded Context: Infrastructure

Concrete implementations for storage and file parsing.

**Infrastructure (`campaign/infrastructure/`):**
- [ ] `sqlite_campaign_repository.py` — `SqliteCampaignRepository`:
      stores campaigns in `~/.tic/tic.db`, creates schema on first use
- [ ] `ti_save_file_reader.py` — `TISaveFileReader`: reads `.json` and
      `.gz` files (UTF-8 BOM), extracts `SaveFileData` from the three
      source types, parses defensively (missing keys are silently ignored);
      constructs `datetime` from `TITimeState.currentDateTime` nested fields;
      flattens `customFactionText` to `dict[str, str]` (`name →
      display_name`)

**Tests (`tests/campaign/infrastructure/`):**
- [ ] `test_sqlite_campaign_repository.py` — save, get by id, get by
      name, not found
- [ ] `test_ti_save_file_reader.py` — reads plain JSON, reads gz,
      handles missing fields, handles unknown fields; use a real minimal
      save fixture (not the full 30MB file)

---

### Phase 5 — game_state Bounded Context: Projection

Derives queryable campaign metadata from the event store. Subscribes to
`SaveImported` events via the message bus.

**Domain (`game_state/domain/`):**
- [ ] `campaign_metadata.py` — `CampaignMetadata` value object: all
      display fields derived from `SaveImported`; `faction_display_name`
      sourced from the event (not recomputed from `customFactionText`)
- [ ] `campaign_metadata_repository.py` — `CampaignMetadataRepository`
      ABC: `get(campaign_id: UUID) -> CampaignMetadata | None`

**Application (`game_state/application/`):**
- [ ] `project_campaign_metadata.py` — `ProjectCampaignMetadataHandler`:
      subscribes to `SaveImported`, writes/updates projection;
      `RebuildCampaignMetadataCommand` + handler: replays all events
      and rebuilds from scratch

**Infrastructure (`game_state/infrastructure/`):**
- [ ] `sqlite_campaign_metadata_repository.py` —
      `SqliteCampaignMetadataRepository`: reads/writes projection table
      in `~/.tic/campaigns/<uuid>.db`; creates the file and schema on
      first use

**Tests (`tests/game_state/`):**
- [ ] `test_project_campaign_metadata.py` — handler updates projection
      on `SaveImported`; rebuild replays correctly; use fakes for storage

---

### Phase 6 — reporting Bounded Context: Queries

Serves campaign metadata to the CLI and web UI. Read-only; no writes.

**Application (`reporting/application/`):**
- [ ] `get_campaign_metadata.py` — `GetCampaignMetadataQuery` dataclass
      (`campaign_id: UUID`); `GetCampaignMetadataHandler`: reads from
      `CampaignMetadataRepository`, returns `CampaignMetadata | None`

**Tests (`tests/reporting/`):**
- [ ] `test_get_campaign_metadata.py` — found, not found; use fake repository

---

### Phase 7 — CLI Interface

Wires the use cases to Typer commands.

**Interface (`campaign/interface/cli/`, `reporting/interface/cli/`):**
- [ ] `campaign/interface/cli/import_save.py` — `import_save` command:
      accepts file path, constructs and dispatches `ImportSaveCommand`,
      prints confirmation or deduplication notice
- [ ] `reporting/interface/cli/campaign_metadata.py` — `metadata` command:
      dispatches `GetCampaignMetadataQuery`, renders result as a table
- [ ] `tic/cli.py` — root entry point wired with both sub-apps

**Manual verification:**
- `tic import <save_file>` — imports correctly, prints game date and faction
- `tic import <save_file>` again — prints deduplication notice, no error
- `tic campaign metadata` — displays game date, faction, difficulty, settings

---

### Phase 8 — Web UI

Wires the query to a FastAPI + HTMX + Jinja2 page.

**Interface (`reporting/interface/web/`):**
- [ ] `app.py` — FastAPI app, registered in root or via sub-app
- [ ] `routes/campaign_metadata.py` — `GET /campaign/metadata`: dispatches
      query, passes result to template
- [ ] `templates/campaign_metadata.html` — HTMX-compatible Jinja2 template:
      game date, faction display name, difficulty label, scenario, selected
      factions, key settings

**Manual verification:**
- Start server, navigate to `/campaign/metadata` — page renders correctly
- Import a new save, refresh — page reflects updated data

---

### Definition of Done for F0

- All tests pass (`pytest`)
- Coverage ≥ 80% on `tic/`
- `ruff` and `mypy --strict` report no errors
- CI pipeline green on push
- `tic import <file>` works end-to-end on the real save file
- `tic campaign metadata` renders correct output
- Web UI page renders correct output
- Projection is fully rebuildable from the event store
