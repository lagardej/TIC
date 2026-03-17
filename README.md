# TIC — Terra Invicta Companion

### *TIC Isn't Competent*

A personal companion tool for [Terra Invicta](https://store.steampowered.com/app/1176470/Terra_Invicta/), filling the
gaps in the game's UI with data visualisation and historical trend tracking.
---

## Purpose

Terra Invicta surfaces a lot of data but offers limited tools for analysing it over time. TIC complements the in-game UI
by providing:

- Visualisation of game state data
- Historical trend tracking across saves
- Custom views for information the base UI doesn't expose clearly

---

## Project Goals

Beyond the tool itself, TIC is a **learning project for AI-assisted development:**

- The developer makes overall architecture, design, and feature decisions.
- The AI agent generates implementations, refactors, and documentation.

---

## Framework Dependency

TIC consumes `abcdef` as an extracted framework package from its own repository.

- Source: <https://github.com/lagardej/abcdef-py>
- Dependency is resolved from git; no local clone is required.
- To update to the latest `abcdef` commit, run `uv lock --upgrade-package abcdef` in this repo.

---

## Development

Common tasks are available as Make targets. Run `make` or `make help` for the full list.

```
make check-format  check formatting without modifying files
make check-types   run pyright type checker
make lint          run ruff linter without modifying files
make test          run pytest with coverage

make fix           auto-fix lint violations then format
make format        auto-format source files

make ci            run check-format, lint, check-types, test
make mutate        run mutation tests (mutmut)

make install       install git hooks
```

### Verbosity

`test` and `ci` support a `V` variable controlling output detail:

| `V` | Level   | Behaviour                                 |
|-----|---------|-------------------------------------------|
| `0` | quiet   | dots and failures only                    |
| `1` | default | file-level progress (default if omitted)  |
| `2` | verbose | per-test names, full tracebacks           |

```
make test V=0
make ci V=2
```

`check-format`, `check-types`, `lint`, `fix`, `format`, and `mutate` are unaffected — they already only print what is
relevant.

### Logs

`test`, `ci`, and `mutate` tee output to timestamped log files under `logs/`:

```
logs/test-20260314-074744.log
logs/ci-20260314-074814.log
logs/mutate-20260314-075001.log
```

`logs/test.log`, `logs/ci.log`, and `logs/mutate.log` are symlinks that always point to the latest run.
