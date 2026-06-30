#!/usr/bin/env python3

from pathlib import Path
import sys


def find_matches(coding_dir: Path, query: str) -> list[str]:
    matches: list[tuple[int, str]] = []
    for path in coding_dir.rglob(".venv"):
        if not path.is_dir():
            continue
        path_str = str(path)
        if query in path_str.lower():
            depth = path_str.count("/")
            matches.append((depth, path_str))

    matches.sort(key=lambda item: (item[0], item[1]))
    return [item[1] for item in matches]


def parse_args(argv: list[str]) -> tuple[bool, str] | None:
    single_only = False
    args = argv[:]

    if args and args[0] == "-1":
        single_only = True
        args = args[1:]

    if len(args) > 1:
        return None

    query = args[0].lower() if args else ""
    return single_only, query


def main() -> int:
    parsed = parse_args(sys.argv[1:])
    if parsed is None:
        print("Usage: venv-match [-1] [project-name-fragment]", file=sys.stderr)
        return 1

    single_only, query = parsed

    coding_dir = Path.home() / "coding"

    matches = find_matches(coding_dir, query)
    if not matches:
        return 1

    if single_only:
        print(matches[0])
        return 0

    print("\n".join(matches))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())