#!/usr/bin/env python3
"""Install git hooks.

Usage:
    uv run scripts/install.py [-q] [-v]

Options:
    -q, --quiet     Suppress output
    -v, --verbose   Show verbose output
"""

import argparse
import sys
from pathlib import Path


def main() -> None:
    """Install git hooks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    args = parser.parse_args()

    project_root = Path.cwd()
    hooks_dir = project_root / "scripts" / "hooks"
    git_hooks_dir = project_root / ".git" / "hooks"

    if not hooks_dir.exists():
        print(f"Error: {hooks_dir} not found", file=sys.stderr)
        sys.exit(1)

    git_hooks_dir.mkdir(parents=True, exist_ok=True)

    for hook_file in hooks_dir.iterdir():
        if hook_file.is_file():
            hook_name = hook_file.name
            git_hook_path = git_hooks_dir / hook_name

            # Make executable
            hook_file.chmod(0o755)

            # Create symlink
            if git_hook_path.is_symlink() or git_hook_path.exists():
                git_hook_path.unlink()
            git_hook_path.symlink_to(hook_file)

            if not args.quiet:
                print(f"Installed hook: {hook_name}")


if __name__ == "__main__":
    main()
