#!/usr/bin/env python3
"""Auto-fix lint violations and format code.

Usage:
    uv run scripts/fix.py [-q] [-v]

Options:
    -q, --quiet     Suppress output (failures only)
    -v, --verbose   Show verbose output
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import get_timestamp, make_log_path, run_cmd


def main() -> None:
    """Auto-fix lint violations and format code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    args = parser.parse_args()

    # Use timestamp from CI if available, otherwise generate one
    timestamp = os.environ.get("CI_TIMESTAMP", get_timestamp())

    log_path = make_log_path("fix", timestamp)
    commands = [
        "uv run ruff check --fix .",
        "uv run ruff format .",
        "uv run mdformat README.md AGENTS.md CONTRIBUTING.md docs/ src/",
    ]

    for cmd in commands:
        exit_code = run_cmd(cmd, log_file=log_path, quiet=args.quiet)
        if exit_code != 0:
            sys.exit(exit_code)


if __name__ == "__main__":
    main()
