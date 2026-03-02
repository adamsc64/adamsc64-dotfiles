#!/usr/bin/env python3
"""Kill memory-heavy Chrome Renderer processes."""

import argparse
import subprocess
import sys
from typing import List, NamedTuple, Optional


class ProcessInfo(NamedTuple):
    """Information about a Chrome Renderer process."""

    pid: int
    rss_kb: int
    mem_percent: float

    @property
    def rss_mb(self) -> float:
        """Get RSS in megabytes."""
        return self.rss_kb / 1024


class ChromeProcessManager:
    """Manages Chrome Renderer process operations."""

    RENDERER_PROCESS_NAME = "Google Chrome Helper (Renderer)"
    EXTENSION_PROCESS_FLAG = "extension-process"

    def __init__(self, min_rss_mb: int, max_kill: int):
        """Initialize the process manager.

        Args:
            min_rss_mb: Minimum RSS in MB to filter processes
            max_kill: Maximum number of processes to return
        """
        self.min_rss_mb = min_rss_mb
        self.min_rss_kb = min_rss_mb * 1024
        self.max_kill = max_kill

    def _run_ps_command(self) -> Optional[str]:
        """Run the ps command to get process information.

        Returns:
            Command output as string, or None on error
        """
        try:
            result = subprocess.run(
                ["ps", "x", "-m", "-o", "pid=,rss=,%mem=,command"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running ps: {e}", file=sys.stderr)
            return None

    def _is_renderer_process(self, line: str) -> bool:
        """Check if a process line is a Chrome Renderer process.

        Args:
            line: Process line from ps output

        Returns:
            True if it's a renderer process (not extension)
        """
        if self.RENDERER_PROCESS_NAME not in line:
            return False
        if self.EXTENSION_PROCESS_FLAG in line:
            return False
        return True

    def _parse_process_line(self, line: str) -> Optional[Tuple[int, int, float]]:
        """Parse a process line into structured data.

        Args:
            line: Process line from ps output

        Returns:
            Tuple of (pid, rss_kb, mem_percent) or None if parsing fails
        """
        parts = line.split()
        if len(parts) < 3:
            return None

        try:
            pid = int(parts[0])
            rss_kb = int(parts[1])
            mem_percent = float(parts[2])

            if rss_kb > self.min_rss_kb:
                return (pid, rss_kb, mem_percent)
        except (ValueError, IndexError):
            pass

        return None

    def get_processes(self) -> List[Tuple[int, int, float]]:
        """Get Chrome Renderer processes sorted by memory usage.

        Returns:
            List of tuples (pid, rss_kb, mem_percent) sorted by RSS descending
        """
        output = self._run_ps_command()
        if not output:
            return []

        processes = []
        for line in output.split("\n"):
            if not self._is_renderer_process(line):
                continue
            if '79115' in line:
                import ipdb; ipdb.set_trace()
            process_data = self._parse_process_line(line)
            if process_data:
                processes.append(process_data)

        # Sort by RSS (descending) and limit
        processes.sort(key=lambda x: x[1], reverse=True)
        return processes[: self.max_kill]

    @staticmethod
    def kill_processes(pids: List[int]) -> None:
        """Kill processes by PID using SIGTERM.

        Args:
            pids: List of process IDs to kill
        """
        for pid in pids:
            try:
                subprocess.run(["kill", "-TERM", str(pid)], check=False)
            except Exception as e:
                print(f"Error killing PID {pid}: {e}", file=sys.stderr)


def setup_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Kill memory-heavy Chrome Renderer processes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              # Dry-run, show what would be killed
  %(prog)s --kill       # Actually kill processes
  %(prog)s 200 5        # Target processes using > 200MB, max 5 processes
  %(prog)s --kill 100   # Kill processes using > 100MB
        """,
    )

    parser.add_argument(
        "--kill", action="store_true", help="Actually kill processes (default: dry-run)"
    )

    parser.add_argument(
        "min_rss_mb",
        type=int,
        nargs="?",
        default=150,
        help="Minimum memory in MB (default: 150)",
    )

    parser.add_argument(
        "max_kill",
        type=int,
        nargs="?",
        default=10,
        help="Maximum processes to kill (default: 10)",
    )

    return parser


def display_configuration(min_rss_mb: int, max_kill: int, dry_run: bool) -> None:
    """Display the current configuration settings."""
    print(f"Targeting Chrome Renderer processes using > {min_rss_mb}MB RAM")
    print(f"Will kill maximum of {max_kill} processes")

    if dry_run:
        print("*** DRY RUN MODE - use --kill to actually kill processes ***")
    print()


def display_processes(processes: List[Tuple[int, int, float]]) -> None:
    """Display process information in a formatted table."""
    print("Found processes to kill:")
    print("PID       RSS(MB)  %MEM")
    print("------------------------")

    for pid, rss_kb, mem_percent in processes:
        rss_mb = rss_kb / 1024
        print(f"{pid:<9} {rss_mb:<8.1f} {mem_percent}%")

    print()


def execute_action(pids: List[int], do_kill: bool) -> None:
    """Execute the kill action or show dry-run message."""
    if do_kill:
        print(f"Killing {len(pids)} process(es)...")
        ChromeProcessManager.kill_processes(pids)
        print(f"Done. Killed {len(pids)} Chrome Renderer process(es)")
    else:
        print(f"Would kill {len(pids)} process(es) (PIDs: {' '.join(map(str, pids))})")
        print("Run with --kill to actually kill them")


def main():
    parser = setup_argument_parser()
    args = parser.parse_args()

    display_configuration(args.min_rss_mb, args.max_kill, not args.kill)

    manager = ChromeProcessManager(args.min_rss_mb, args.max_kill)
    processes = manager.get_processes()

    if not processes:
        print(f"No Chrome Renderer processes found using more than {args.min_rss_mb}MB")
        return 0

    display_processes(processes)

    pids = [p[0] for p in processes]
    execute_action(pids, args.kill)

    return 0


if __name__ == "__main__":
    sys.exit(main())
