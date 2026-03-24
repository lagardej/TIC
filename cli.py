#!/usr/bin/env python3
"""Development task CLI — dispatch to task scripts.

Usage:
    uv run cli.py <task> [-q] [-v] [task-specific args]
    uv run cli.py --help

Tasks:
    check-format    Check code formatting without modifying files
    check-types     Run pyright type checker
    check-doc       Check documentation formatting without modifying files
    lint            Run ruff linter without modifying files
    test            Run pytest with coverage
    format          Auto-format source files
    format-doc      Auto-format documentation files
    fix             Auto-fix lint violations and format code
    ci              Run check-format, check-doc, lint, check-types, test
    mutate          Run mutation tests (mutmut) — supports additional args
    install         Install git hooks

Options:
    -q, --quiet     Quiet mode (where supported)
    -v, --verbose   Verbose mode (where supported)

Mutate-specific options (see `uv run cli.py mutate --help`):
    pattern         Module pattern to filter (substring match)
    --runs N        Number of mutmut runs (default: 4)
    --min-runs M    Minimum runs to be stable
    --no-clear      Skip clearing mutmut cache
    --output FILE   Custom output file path
    --show-diffs    Print diffs to stdout
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Dispatch to task scripts."""
    parser = argparse.ArgumentParser(
        description="Development task CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
        add_help=False,  # Handle help manually for mutate compatibility
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="Task to run (see above for list)",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show this help message"
    )

    # Parse known args, capturing the rest
    args, remaining = parser.parse_known_args()

    # Handle help flag
    if args.help and not args.task:
        parser.print_help()
        sys.exit(0)

    # Map task names to script names
    task_map = {
        "check-format": "check_format",
        "check-types": "check_types",
        "check-doc": "check_doc",
        "lint": "lint",
        "test": "test",
        "format": "format",
        "format-doc": "format_doc",
        "fix": "fix",
        "ci": "ci",
        "mutate": "mutate",
        "install": "install",
    }

    if not args.task:
        parser.print_help()
        sys.exit(1)

    if args.task not in task_map:
        print(f"Error: unknown task '{args.task}'", file=sys.stderr)
        print(f"Valid tasks: {', '.join(task_map.keys())}", file=sys.stderr)
        sys.exit(1)

    script_name = task_map[args.task]
    script_path = Path("scripts") / f"{script_name}.py"

    # Build command line for the task script
    cmd = ["uv", "run", "python", str(script_path)]

    # Add global flags
    if args.quiet:
        cmd.append("-q")
    if args.verbose:
        cmd.append("-v")

    # Add remaining arguments (for mutate and other complex tasks)
    cmd.extend(remaining)

    # Execute the task script
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
