#!/usr/bin/env python3
"""Run mutation tests with mutmut N times and compute stable survivors.

Usage:
    uv run scripts/mutate.py [options] [pattern]

Arguments:
    pattern     Module pattern to filter (substring match). Omit to show all.

Options:
    --runs N        Number of mutmut runs to perform (default: 4).
    --min-runs M    Minimum runs a mutant must survive to be reported.
                    Defaults to N (full intersection). Use e.g. --min-runs 3
                    to accept mutants surviving in 3 of 4 runs.
    --no-clear      Skip clearing the mutmut cache before the first run.
    --output FILE   Write the survivor diffs to FILE
                    (default: logs/TIMESTAMP/stable_survivors.log).
    --show-diffs    Print diffs to stdout as well as writing to file.
    -q, --quiet     Suppress some output.

Examples:
    # 4 runs, full intersection, all modules
    uv run scripts/mutate.py

    # 4 runs, full intersection, validation_boundary only
    uv run scripts/mutate.py validation_boundary

    # 5 runs, accept survivors in at least 4
    uv run scripts/mutate.py --runs 5 --min-runs 4

    # Skip cache clear (already cleared)
    uv run scripts/mutate.py --no-clear extraction
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import get_timestamp

MUTANTS_DIR = Path("mutants")
STATS_FILE = MUTANTS_DIR / "mutmut-stats.json"


def run_mutmut_once(results_log: Path) -> None:
    """Run mutmut and write only the clean `mutmut results` output to results_log.

    The noisy spinner output from `mutmut run` is discarded (sent to /dev/null).
    Only the clean results list is written to results_log for later parsing.
    """
    results_log.parent.mkdir(parents=True, exist_ok=True)
    print("  → mutmut run …", flush=True)
    subprocess.run(
        ["uv", "run", "mutmut", "run"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"  → collecting results → {results_log}", flush=True)
    result = subprocess.run(
        ["uv", "run", "mutmut", "results"],
        capture_output=True,
        text=True,
    )
    results_log.write_text(result.stdout, encoding="utf-8")


def clear_cache() -> None:
    """Delete the mutmut stats database to force a clean run."""
    if STATS_FILE.exists():
        STATS_FILE.unlink()
        print(f"  → cleared {STATS_FILE}", flush=True)
    else:
        print(f"  → {STATS_FILE} not found, nothing to clear", flush=True)


def survivors_from_results(results_log: Path, pattern: str) -> set[str]:
    """Parse a `mutmut results` log and return surviving mutant IDs matching pattern.

    Each line in a results log looks like:
        abcdef.some.module.xǁClassǁmethod__mutmut_N: survived
    """
    survivors: set[str] = set()
    try:
        text = results_log.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"  Warning: cannot read {results_log}: {e}", file=sys.stderr)
        return survivors
    for line in text.splitlines():
        line = line.strip()
        if ": survived" not in line:
            continue
        mutant_id = line.split(":")[0].strip()
        if not pattern or pattern in mutant_id:
            survivors.add(mutant_id)
    return survivors


def show_mutant(mutant_id: str) -> str:
    """Return the diff output for a single mutant."""
    result = subprocess.run(
        ["uv", "run", "mutmut", "show", mutant_id],
        capture_output=True,
        text=True,
    )
    return result.stdout or result.stderr


def compute_stable_survivors(
    results_logs: list[Path],
    pattern: str,
    min_runs: int,
) -> tuple[list[str], dict[str, int]]:
    """Return mutant IDs surviving in at least min_runs logs, sorted by frequency."""
    counts: Counter[str] = Counter()
    for lp in results_logs:
        for mid in survivors_from_results(lp, pattern):
            counts[mid] += 1
    stable = sorted(
        (mid for mid, c in counts.items() if c >= min_runs),
        key=lambda mid: (-counts[mid], mid),
    )
    return stable, dict(counts)


def run_mutmut_rounds(n_runs: int, timestamp: str, quiet: bool) -> list[Path]:
    """Run mutmut N times and return list of result log paths."""
    if not quiet:
        print(f"\n[2/3] Running mutmut {n_runs} times …")
    results_logs: list[Path] = []
    logs_dir = Path("logs") / timestamp
    for i in range(1, n_runs + 1):
        if not quiet:
            print(f"\n  Run {i}/{n_runs}:")
        lp = logs_dir / f"mutate-results-run{i}.log"
        run_mutmut_once(lp)
        results_logs.append(lp)
    return results_logs


def build_output(
    survivors: list[str],
    counts: dict[str, int],
    n_runs: int,
    min_runs: int,
    pattern: str,
    timestamp: str,
    results_logs: list[Path],
) -> str:
    """Build the output text containing survivor info and diffs."""
    pattern_label = repr(pattern) if pattern else "(all modules)"
    mode_desc = (
        f"in all {n_runs} runs"
        if min_runs == n_runs
        else f"in at least {min_runs}/{n_runs} runs"
    )

    lines: list[str] = []
    lines.append(
        f"Stable survivors matching {pattern_label} {mode_desc}: {len(survivors)}\n"
    )
    lines.append(f"Runs: {n_runs}  Min-runs: {min_runs}  Timestamp: {timestamp}\n")
    lines.append(f"Results logs: {', '.join(str(lp) for lp in results_logs)}\n")
    lines.append("=" * 72 + "\n\n")

    if not survivors:
        lines.append("No stable survivors found.\n")
    else:
        for mid in survivors:
            c = counts.get(mid, 0)
            lines.append(f"=== {mid} (survived {c}/{n_runs} runs) ===\n")
            lines.append(show_mutant(mid))
            lines.append("\n")

    return "".join(lines)


def main() -> None:
    """Parse arguments, run mutmut N times, and report stable survivors."""
    parser = argparse.ArgumentParser(
        description="Run mutmut N times and report stable survivors.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "pattern",
        nargs="?",
        default="",
        help="Module pattern to filter (substring match). Omit for all modules.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=4,
        metavar="N",
        help="Number of mutmut runs (default: 4).",
    )
    parser.add_argument(
        "--min-runs",
        type=int,
        default=None,
        metavar="M",
        help="Minimum runs to be considered stable (default: same as --runs).",
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Skip clearing the mutmut cache before the first run.",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Output file for diffs (default: logs/TIMESTAMP/stable_survivors.log).",
    )
    parser.add_argument(
        "--show-diffs",
        action="store_true",
        help="Also print diffs to stdout.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress some output.",
    )
    args = parser.parse_args()

    # Capture timestamp at start
    timestamp = get_timestamp()

    pattern: str = args.pattern
    n_runs: int = args.runs
    min_runs: int = args.min_runs if args.min_runs is not None else n_runs
    logs_dir = Path("logs") / timestamp
    output_path = (
        Path(args.output) if args.output else logs_dir / "stable_survivors.log"
    )

    # --- Clear cache ---
    if not args.quiet:
        print("\n[1/3] Clearing mutmut cache …")
    if not args.no_clear:
        clear_cache()
    else:
        if not args.quiet:
            print("  → skipping cache clear (--no-clear)")

    # --- Run mutmut N times ---
    results_logs = run_mutmut_rounds(n_runs, timestamp, args.quiet)

    # --- Compute stable survivors ---
    if not args.quiet:
        print(f"\n[3/3] Computing stable survivors (min {min_runs}/{n_runs} runs) …")
    survivors, counts = compute_stable_survivors(results_logs, pattern, min_runs)

    if not args.quiet:
        print()
        for i, lp in enumerate(results_logs, 1):
            n = len(survivors_from_results(lp, pattern))
            label = repr(pattern) if pattern else "(all)"
            print(f"  Run {i}: {n} survivors matching {label}")

        mode_desc = (
            f"in all {n_runs} runs"
            if min_runs == n_runs
            else f"in at least {min_runs}/{n_runs} runs"
        )
        print(f"\n  Stable survivors {mode_desc}: {len(survivors)}")

    # --- Build and write output ---
    output = build_output(
        survivors, counts, n_runs, min_runs, pattern, timestamp, results_logs
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")

    if not args.quiet:
        print(f"\n  Written to {output_path}")

    if args.show_diffs:
        print("\n" + output)


if __name__ == "__main__":
    main()
