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
    for i, line in enumerate(lines):
        if "<data:image" in line:
            continue  # Never include lines with images
        stripped = line.strip()
        # Check for the start of the footnotes, indicating the main
        # text of the article has ended.
        if stripped.startswith("[^1]:"):
            section_end = i
            break
        candidate_section_number = is_heading(stripped)
        if candidate_section_number is None:
            continue
        content = stripped[2:-2].strip()
        if not content:
            continue
        dot_index = content.find("\\.")  # google docs escapes it this way
        if dot_index == -1:
            continue
        # candidate_section_number = content[0:dot_index]
        if candidate_section_number != section_number:
            if section_start != -1:
                section_end = i
                break
            continue
        section_start = i
    if section_end == -1:
        section_end = len(lines)
    return lines[section_start:section_end] if section_start != -1 else []


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


def main(markdown_text, section_number):
    lines = markdown_text.splitlines(keepends=True)
    section = get_section(lines, section_number)
    footnotes = get_footnotes(section, lines)
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

    args = parser.parse_args()

    # Validate that exactly one mode is selected
    if args.outline and args.section:
        parser.error("Cannot specify both --outline and --section")
    if not args.outline and not args.section:
        parser.error("Must specify either --outline or --section")

    with open(args.input, "r", encoding="utf-8") as f:
        input_markdown = f.read()

    if args.outline:
        result = extract_outline(input_markdown)
    else:
        result = main(input_markdown, args.section)

    print(result)
