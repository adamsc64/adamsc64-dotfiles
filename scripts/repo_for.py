#!/usr/bin/env python3
"""Print the Git repository root for the symlink target of a command.

This entry point expects a single argument: the name of a command to locate
on PATH.

Usage:
    repo_for.py <command>
"""
import sys
import os
import shutil
import subprocess


def main():
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {os.path.basename(sys.argv[0])} <command>\n")
        sys.exit(2)

    cmd = sys.argv[1]

    # Find the command like `which`
    cmd_path = shutil.which(cmd)
    if not cmd_path:
        # Command not found in PATH
        sys.exit(1)

    # Resolve the path (follows symlinks if present)
    target_path = os.path.realpath(cmd_path)
    target_dir = os.path.dirname(target_path)

    # Ask git for the repo root from the target directory
    try:
        result = subprocess.run(
            ["git", "-C", target_dir, "rev-parse", "--show-toplevel"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except subprocess.CalledProcessError:
        # Not inside a git repo or git failed; end silently
        sys.exit(0)

    repo_root = result.stdout.strip()
    if repo_root:
        print(repo_root)

if __name__ == "__main__":
    main()