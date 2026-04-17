"""
Given a Google Docs markdown export, extract a specific section and its
footnotes, OR print an outline of all headings. This script is designed
to work with markdown files that have been exported from Google Docs,
where sections are marked with bold headers like "**1. Introduction**".

Example usage:
# Extract a specific section:
$ python3 extract_markdown_section.py \
    -i "$(last-download.sh)" -s6 \
    | pbcopy

# Print outline of all headings:
$ python3 extract_markdown_section.py \
    -i "$(last-download.sh)" -o
"""

import argparse
import re
import sys
import os
from count_words import count_separators


def is_bold(text):
    return text.startswith("**") and text.endswith("**")


def is_heading(text):
    match = re.match(r"^#+\s+(\d+)\\.", text)
    if match:
        return match.group(1)
    return None


def is_subheading(text):
    match = re.match(r"^#+\s+(\d+.\d+)", text)
    if match:
        return match.group(1)
    return None


def is_thesis_statement(text):
    if "Thesis " in text:
        return text
    return None


def get_section(lines, section_number):
    section_start = -1
    section_end = -1
    filtered_lines = [line for line in lines if "<data:image" not in line]
    is_subsection = "." in section_number

    for i, line in enumerate(filtered_lines):
        stripped = line.strip()
        # Check for the start of the footnotes, indicating the main
        # text of the article has ended.
        if stripped.startswith("[^1]:"):
            if section_start != -1:
                section_end = i
                break
            else:
                # Footnotes reached before target section found
                return []

        candidate = is_subheading(stripped) if is_subsection else is_heading(stripped)

        if candidate is None:
            # A top-level heading always ends an in-progress subsection
            if is_subsection and section_start != -1 and is_heading(stripped) is not None:
                section_end = i
                break
            continue

        if candidate == section_number:
            section_start = i
        elif section_start != -1:
            # We found a new heading after our target section started
            section_end = i
            break

    if section_start == -1:
        return []
    if section_end == -1:
        section_end = len(filtered_lines)

    return filtered_lines[section_start:section_end]


def get_footnotes(section, lines):
    footnotes = dict()
    to_return = []
    for i, line in enumerate(lines):
        if not line.strip().startswith("[^"):
            continue
        match = re.match(r"\[\^(\d+)\]:\s*(.+)", line)
        if not match:
            continue
        note_number, note_text = match.group(1), match.group(0)
        footnotes[int(note_number)] = note_text.strip()
    for i, line in enumerate(section):
        if "[^" not in line:
            continue
        matches = re.findall(r"\[\^(\d+)\]", line)
        for match in matches:
            if int(match) in footnotes:
                to_return.append(footnotes[int(match)])
    return to_return


def extract_outline(markdown_text):
    """Extract and return all heading lines from the markdown text."""
    lines = markdown_text.splitlines(keepends=True)
    outline_lines = []
    for line in lines:
        stripped = line.strip()
        if is_heading(stripped):
            outline_lines.append(line)
            continue
        if is_subheading(stripped):
            outline_lines.append("    " + line)
            continue
        if is_thesis_statement(stripped):
            outline_lines.append("    " + line)
    return "".join(outline_lines)


def word_count_from_chapter_one(markdown_text):
    lines = markdown_text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if is_heading(line.strip()) == "1":
            body = "".join(lines[i:])
            return count_separators(body)
    return 0


def extract_section(markdown_text, section_number):
    lines = markdown_text.splitlines(keepends=True)
    section = get_section(lines, section_number)
    footnotes = get_footnotes(section, lines)
    if not section:
        return ""
    return "".join(section) + "\n\n" + "\n\n".join(footnotes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract a markdown section and its footnotes, or print an outline."
    )
    parser.add_argument("-i", "--input", required=True, help="Input markdown file")
    parser.add_argument("-s", "--section", help="Section number to extract (e.g., '2')")
    parser.add_argument(
        "-o", "--outline", action="store_true", help="Print outline of all headings"
    )
    parser.add_argument(
        "-c", "--count", action="store_true",
        help="Count words starting from chapter 1"
    )

    args = parser.parse_args()

    # Validate that exactly one mode is selected
    modes = [args.outline, bool(args.section), args.count]
    if sum(modes) > 1:
        parser.error("Cannot specify more than one of --outline, --section, --count")
    if sum(modes) == 0:
        parser.error("Must specify one of --outline, --section, or --count")

    with open(args.input, "r", encoding="utf-8") as f:
        input_markdown = f.read()

    if args.outline:
        result = extract_outline(input_markdown)
    elif args.count:
        result = str(word_count_from_chapter_one(input_markdown))
    else:
        result = extract_section(input_markdown, args.section)

    print(result)
