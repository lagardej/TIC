# TIC — Terra Invicta Companion
### *TIC Isn't Competent*

A personal companion tool for [Terra Invicta](https://store.steampowered.com/app/1176470/Terra_Invicta/), filling the gaps in the game's UI with data visualisation and historical trend tracking.

## Purpose

Terra Invicta surfaces a lot of data but offers limited tools for analysing it over time. TIC complements the in-game UI by providing:

- Visualisation of game state data
- Historical trend tracking across saves
- Custom views for information the base UI doesn't expose clearly

## Project Goals

Beyond the tool itself, TIC is a **learning project for AI-assisted development**:

- Architecture and feature decisions are driven by the developer
- Implementation, refactoring, and documentation are handled collaboratively with an AI coding agent
- The workflow itself is part of what's being explored

---

## Architecture

TIC follows **DDD, CQRS, and Event Sourcing** principles, organised by bounded context.

### Bounded Contexts

- **campaign** — imports Terra Invicta save files and maintains the Campaign aggregate
- **game_state** — projects current world state from the event store
- **history** — projects trends and changes over time
- **reporting** — serves queries to the UI and CLI

### Project Structure

```
tic/
├── cli.py                # root CLI entry point — aggregates bounded context sub-apps
├── <context>/            # e.g. campaign, game_state, history, reporting
│   ├── domain/           # aggregates, value objects, ABCs for repository and services
│   │   └── events/       # one file per event
│   ├── application/      # one file per use case — contains command dataclass and handler
│   │   └── <abc>.py      # ABC for any service the application layer depends on
│   ├── infrastructure/   # concrete implementations — named after technology and role
│   └── interface/
│       └── cli/          # one file per CLI command
└── shared/               # event store, message bus — same internal structure as contexts
    ├── domain/
    └── infrastructure/
```

**Bounded context communication:** contexts never import from each other directly. All cross-context communication goes through domain events on the message bus in `shared/`. A context publishes events; other contexts subscribe. `shared/` is the sole exception — all contexts may import from it directly.

**Layer dependency rule:**
```
interface → application → domain
infrastructure → any layer (never the reverse)
```
If a class in any layer needs a service backed by a third-party dependency, it declares an ABC in its own layer. The concrete implementation lives in `infrastructure/` and is injected via constructor.

**File granularity:** one file per concept — event, command, CLI command, ABC, implementation. `__init__.py` files aggregate and re-export; they contain no logic. Infrastructure implementations are named after their technology: `sqlite_campaign_repository.py`, not `campaign_repository.py`.

### Storage

Each campaign is stored as an isolated SQLite database. A lightweight app-level database tracks the campaign registry.

```
~/.tic/
├── tic.db                # campaign registry and app settings
└── campaigns/
    ├── <uuid>.db         # campaign 1 event store + projections
    └── <uuid>.db         # campaign 2 event store + projections
```

---

## Save File Ingestion

Save files are read from the Terra Invicta saves directory. Both plain `.json` and `.gz` compressed saves are supported. The primary use case is auto-import from `Autosave.gz` and `Autosave2.gz`.

**Source of truth is always the save file content**, never the filename.

### Campaign Identity

- One faction per TIC instance (set on first import, never changes)
- Multiple campaigns per faction are supported — each gets its own database
- On import: if a campaign exists for the save's faction → append snapshot; otherwise → create campaign and append
- No user prompts, no ambiguity — the process is fully automatic
- Deduplication is by in-game date (`currentDateTime`): importing the same save twice is a no-op

### Save File Format

- Encoding: UTF-8 with BOM (`utf-8-sig`)
- Structure: `{ currentID, gamestates: { "<type>": [ { Key, Value } ] } }`
- Type names use the `PavonisInteractive.TerraInvicta.` namespace prefix
- Campaign metadata sourced from `TIMetadataState` and `TITimeState`

---

## Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+ |
| Storage | SQLite (stdlib) |
| Web server | FastAPI |
| Frontend | HTMX + Jinja2 |
| Charts | Apache ECharts (locally cached) |
| CLI | Typer |
| File watching | Watchdog |

Runs fully locally. No internet connection required after initial setup.
Compatible with Windows and Linux.

---

## Demo Mode

A live demo is hosted on [Render](https://render.com) and auto-deployed on every push to `main`.

### How It Works

The demo runs TIC in a read-only mode seeded with sample save data shipped in the repository under `samples/`. On startup, the app detects demo mode, seeds a pre-built campaign from those samples, and serves the UI — no save files or local setup required.

Demo mode is activated via an environment variable:

```
TIC_DEMO=1
```

### Constraints

- No file watching — the watcher is disabled, imports are seeded at startup only
- No writes — the campaign database is ephemeral, rebuilt fresh on each startup
- No personal data — sample saves in `samples/` contain only game state, no player-identifying information

### Deployment

The repository includes a `render.yaml` for one-click deploy. Render auto-deploys on every push to `main`.

---

## Status

Early development — scaffolding in progress.
