#!/usr/bin/env python3
"""Check documentation formatting without modifying files.

Usage:
    uv run scripts/check_doc.py [-q] [-v]

Options:
    -q, --quiet     Suppress output (failures only)
    -v, --verbose   Show verbose output
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import get_timestamp, make_log_path


def main() -> None:
    """Check documentation formatting without modifying files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    args = parser.parse_args()

    # Use timestamp from CI if available, otherwise generate one
    timestamp = os.environ.get("CI_TIMESTAMP", get_timestamp())

    log_path = make_log_path("check_doc", timestamp)

    cmd = "uv run mdformat --check ."

    # Run mdformat once via the project's uv runner and capture output
    last_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # Log output
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        if last_result is not None:
            if last_result.stdout:
                f.write(last_result.stdout)
            if last_result.stderr:
                f.write(last_result.stderr)
            if (
                last_result.returncode == 0
                and not last_result.stdout
                and not last_result.stderr
            ):
                f.write("Documentation formatting is correct.\n")

    # Display output (or success message if quiet mode and no errors)
    if last_result.stdout and not args.quiet:
        print(last_result.stdout, end="")
    if last_result.stderr and not args.quiet:
        print(last_result.stderr, end="", file=sys.stderr)
    if (
        last_result.returncode == 0
        and not (last_result.stdout or last_result.stderr)
        and not args.quiet
    ):
        print("Documentation formatting is correct.")

    sys.exit(last_result.returncode)


if __name__ == "__main__":
    main()
