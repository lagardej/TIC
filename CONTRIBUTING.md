# Contributing to ABCDEF

## Prerequisites

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) for dependency management and running tools

All commands below use `uv run`. No global installs are required.

______________________________________________________________________

## Using the cross-platform development CLI

This project provides a small cross-platform CLI at `cli.py` that dispatches to the task scripts in `scripts/`. The CLI is the canonical way to run development tasks on any platform. Run it via `uv` so commands execute inside the project's environment:

```bash
uv run cli.py <task>         # run a task (default verbosity)
uv run cli.py -q <task>      # quiet mode (where supported)
uv run cli.py -v <task>      # verbose mode (where supported)
```

The CLI is cross-platform and forwards any extra arguments to the underlying task script. For example, to pass pytest flags or coverage options:

```bash
uv run cli.py test -- --cov=abcdef --cov-report=term-missing
```

You can still invoke tools directly (for advanced use), e.g. `uv run ruff` or `uv run pytest`, but `uv run cli.py <task>` is the preferred, consistent interface.

______________________________________________________________________

## Tasks (commands)

The following tasks are available via `uv run cli.py <task>` and are the recommended way to run development checks locally. Each description is one line describing what the task does.

- check-format — Check code formatting without modifying files (uses ruff/formatters in check mode).
- check-types — Run the type checker (pyright) to validate static types.
- check-doc — Check documentation formatting without modifying files.
- lint — Run the linter (ruff) without modifying files.
- test — Run pytest with coverage enabled (reports are shown after tests finish).
- format — Auto-format Python source files.
- format-doc — Auto-format documentation files.
- fix — Auto-fix lint violations and format source files.
- ci — Run the full CI sequence: check-format, check-doc, lint, check-types, and test.
- mutate — Run mutation tests (mutmut). Supports additional mutate-specific arguments (see `uv run cli.py mutate --help`).
- install — Install project git hooks (writes to .git/hooks or config as implemented by the script).

Examples:

```bash
# Run the test suite (normal verbosity)
uv run cli.py test

# Run the linter only (quiet)
uv run cli.py -q lint

# Auto-format the repository
uv run cli.py format
```

______________________________________________________________________

## Running tests and coverage

Run the test suite using the CLI (preferred):

```bash
uv run cli.py test               # normal output
uv run cli.py -q test            # quiet — failures only (where supported)
uv run cli.py -v test            # verbose — per-test names, full tracebacks
```

To show coverage with missing lines:

```bash
uv run cli.py test -- --cov=abcdef --cov-report=term-missing
```

Branch coverage is enabled. The project targets high coverage but accepts that `pass`/`...` bodies in `@abstractmethod` definitions are structurally unreachable and will appear as misses.

______________________________________________________________________

## Linting, formatting and type checking

Use the CLI tasks (preferred):

```bash
uv run cli.py lint            # lint (ruff) without changing files
uv run cli.py check-format    # check formatting without changing files
uv run cli.py format          # auto-format source files
uv run cli.py fix             # auto-fix lint violations and format
uv run cli.py check-types     # run pyright type checker
uv run cli.py format-doc      # auto-format documentation files
uv run cli.py check-doc       # check documentation formatting
```

Direct invocations of tools are still supported for advanced use (not required):

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

______________________________________________________________________

## Full CI check

Run the full verification sequence locally with:

```bash
uv run cli.py ci
```

This runs the same steps as CI: format check, doc check, lint, type check, and tests.

______________________________________________________________________

## Logs

Long-running or aggregated tasks (for example `test`, `ci`, and `mutate`) write output to timestamped log files under the `logs/` directory. Logs are grouped by run timestamp in the format `logs/YYYYMMDD-HHMMSS/<task>.log`. Each command run creates its own log file inside the timestamped run directory.

Log files always contain the full output of the command. The `-q`/`--quiet` flags only affect console output, not log contents.
