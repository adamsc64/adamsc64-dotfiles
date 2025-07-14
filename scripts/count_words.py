#!/usr/bin/env python3
"""
Count space-like separators in a text stream.

By default a “separator” is either:
  • the literal space character ' '
  • the em-dash '—' (U+2014)

Feed a file through stdin:

    cat myfile.txt | python count_spaces.py
"""

import sys
import argparse

# Characters to treat as word separators
WORD_SEPARATORS = [" ", "\n", "–", "—"]


def count_separators(text: str) -> int:
    wanted = set(WORD_SEPARATORS)
    count = 0
    prev_is_sep = False
    for ch in text:
        if ch in wanted:
            if not prev_is_sep:
                count += 1
                prev_is_sep = True
        else:
            prev_is_sep = False
    return count

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Count spaces and dash-like word dividers."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Input file(s) to process. If none are given, reads from stdin."
    )
    args = parser.parse_args()

    if args.files:
        for fname in args.files:
            with open(fname, "r", encoding="utf-8") as f:
                text = f.read()
            print(f"{fname}: {count_separators(text)}")
    else:
        text = sys.stdin.read()
        print(count_separators(text))


if __name__ == "__main__":
    main()
