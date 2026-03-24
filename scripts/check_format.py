#!/usr/bin/env python3
"""Check code formatting without modifying files.

Usage:
    uv run scripts/check_format.py [-q] [-v]

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
    """Check code formatting without modifying files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    args = parser.parse_args()

    # Use timestamp from CI if available, otherwise generate one
    timestamp = os.environ.get("CI_TIMESTAMP", get_timestamp())

    log_path = make_log_path("check_format", timestamp)
    cmd = "uv run ruff format --check ."
    exit_code = run_cmd(cmd, log_file=log_path, quiet=args.quiet)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
