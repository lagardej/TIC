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
    cmd = "uv run mdformat --check README.md AGENTS.md CONTRIBUTING.md docs/ src/"

    # Run the command
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )

    # Log output
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        if result.stdout:
            f.write(result.stdout)
        if result.stderr:
            f.write(result.stderr)
        if result.returncode == 0 and not result.stdout and not result.stderr:
            f.write("Documentation formatting is correct.\n")

    # Display output (or success message if quiet mode and no errors)
    if (result.stdout or result.stderr) and not args.quiet:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
    elif result.returncode == 0 and not args.quiet:
        print("Documentation formatting is correct.")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
