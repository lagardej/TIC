#!/usr/bin/env python3
"""Common utilities for task scripts.

Provides:
- run_cmd() — execute shell commands
- make_log_path() — generate log file path in timestamped directory
- parse_verbosity() — convert -q/-v to verbosity levels
- get_timestamp() — get current timestamp
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_verbosity(quiet: bool = False, verbose: bool = False) -> int:
    """Convert boolean flags to verbosity level.

    Args:
        quiet: If True, verbosity is 0
        verbose: If True, verbosity is 2

    Returns:
        Verbosity level: 0 (quiet), 1 (default), or 2 (verbose)
    """
    if quiet:
        return 0
    if verbose:
        return 2
    return 1


def get_timestamp() -> str:
    """Get current timestamp as YYYYMMDD-HHMMSS string."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def make_log_path(
    task_name: str, timestamp: str, logs_dir: Path = Path("logs")
) -> Path:
    """Generate a log file path in a timestamped directory.

    Logs are grouped by timestamp: logs/YYYYMMDD-HHMMSS/task.log

    Args:
        task_name: Name of the task (e.g., 'test', 'ci', 'mutate')
        timestamp: Timestamp string (e.g., from get_timestamp())
        logs_dir: Parent logs directory (default: 'logs')

    Returns:
        Path object for the log file
    """
    task_log_dir = logs_dir / timestamp
    task_log_dir.mkdir(parents=True, exist_ok=True)
    return task_log_dir / f"{task_name}.log"


def run_cmd(
    cmd: str,
    description: str = "",
    log_file: Path | None = None,
    quiet: bool = False,
) -> int:
    """Execute a shell command and optionally log output.

    The -q/--quiet flag only suppresses console output, not log files.
    Log files always contain the full output.

    Args:
        cmd: Shell command to run
        description: Human-readable description (printed before running)
        log_file: Optional Path to append output to (always gets full output)
        quiet: If True, suppress console stdout/stderr (log file unaffected)

    Returns:
        Exit code from the command
    """
    if description and not quiet:
        print(description, file=sys.stderr)

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
    )

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as f:
            if description:
                f.write(f"{description}\n")
            f.write(result.stdout)
            if result.stderr:
                f.write(result.stderr)

    # Only suppress console output if quiet mode
    if not quiet:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)

    return result.returncode
