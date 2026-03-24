#!/usr/bin/env python3
"""Run CI pipeline: check-format, check-doc, lint, check-types, test.

Usage:
    uv run scripts/ci.py [-q] [-v]

Options:
    -q, --quiet     Quiet mode: minimal output
    -v, --verbose   Verbose mode: full output
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import get_timestamp, make_log_path


def run_task(task_name: str, args: list[str], env: dict) -> int:
    """Run a task script and return exit code."""
    cmd = [
        "uv",
        "run",
        "python",
        f"scripts/{task_name}.py",
        *args,
    ]
    result = subprocess.run(
        cmd,
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        env=env,
    )

    # Print to console
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    return result.returncode


def main() -> None:
    """Run CI pipeline."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    args = parser.parse_args()

    # Capture timestamp at start of CI run
    timestamp = get_timestamp()

    # Build args list for task scripts
    task_args = []
    if args.quiet:
        task_args.append("-q")
    if args.verbose:
        task_args.append("-v")

    # Create log file for the CI run
    log_path = make_log_path("ci", timestamp)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Tasks to run in order
    tasks = [
        "check_format",
        "check_doc",
        "lint",
        "check_types",
        "test",
    ]

    if not args.quiet:
        print(f"Running CI pipeline: {', '.join(tasks)}", file=sys.stderr)
        print(f"Logging to {log_path}", file=sys.stderr)

    # Pass timestamp to child tasks via environment variable
    env = os.environ.copy()
    env["CI_TIMESTAMP"] = timestamp

    # Run all tasks, capturing exit code
    exit_code = 0
    for task in tasks:
        code = run_task(task, task_args, env)
        if code != 0:
            exit_code = code
            print(f"Task {task} failed with exit code {code}", file=sys.stderr)
            break

    # After all tasks, aggregate their logs into ci.log
    logs_dir = log_path.parent
    with log_path.open("w", encoding="utf-8") as ci_log:
        for task in tasks:
            task_log = logs_dir / f"{task}.log"
            ci_log.write(f"\n--- {task} ---\n")
            if task_log.exists():
                ci_log.write(task_log.read_text(encoding="utf-8"))
            else:
                ci_log.write(f"(no log file for {task})\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
