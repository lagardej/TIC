#!/usr/bin/env python3
"""Run pytest with coverage.

Usage:
    uv run scripts/test.py [-q] [-v]

Options:
    -q, --quiet     Quiet mode: minimal console output (log file unaffected)
    -v, --verbose   Verbose mode: full console output
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import get_timestamp, make_log_path, run_cmd


def main() -> None:
    """Run pytest with coverage."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    args = parser.parse_args()

    # Use timestamp from CI if available, otherwise generate one
    timestamp = os.environ.get("CI_TIMESTAMP", get_timestamp())

    # Always run pytest with default output (no -q/-v modifiers)
    # The quiet/verbose flags only affect console display, not the command
    log_path = make_log_path("test", timestamp)
    cmd = "uv run pytest"

    # Run pytest with tee to log file
    # The quiet flag only affects console output, not the log file
    exit_code = run_cmd(cmd, log_file=log_path, quiet=args.quiet)

    # Handle pytest special exit code 5 (no tests)
    if exit_code == 5:
        exit_code = 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
