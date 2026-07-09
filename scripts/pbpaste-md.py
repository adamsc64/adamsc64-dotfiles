#!/usr/bin/env python3
"""Convert clipboard contents to Markdown, preferring rich HTML content."""

import re
import subprocess
import sys

import html2text
from bs4 import BeautifulSoup

HTML_PREFIX = "«data HTML"


def get_clipboard_html() -> str | None:
    result = subprocess.run(
        [
            "osascript",
            "-e",
            "try",
            "-e",
            "the clipboard as «class HTML»",
            "-e",
            "end try",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    encoded = result.stdout.strip()
    if result.returncode != 0 or not encoded:
        return None
    return decode_clipboard_html(encoded)


def decode_clipboard_html(encoded: str) -> str:
    stripped = encoded.strip()
    if not stripped.startswith(HTML_PREFIX) or not stripped.endswith("»"):
        raise ValueError(
            "Clipboard HTML payload is not in the expected AppleScript format"
        )
    hex_payload = re.sub(r"\s+", "", stripped[len(HTML_PREFIX) : -1])
    return bytes.fromhex(hex_payload).decode("utf-8")


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(True):
        tag.attrs.pop("style", None)
    if soup.head is not None:
        soup.head.decompose()

    body = soup.body
    if body is None:
        return soup.decode_contents()

    element_children = [
        child for child in body.contents if getattr(child, "name", None)
    ]
    if len(element_children) == 1 and element_children[0].name == "b":
        return element_children[0].decode_contents()

    if element_children and element_children[0].name == "b":
        remainder = "".join(str(node) for node in element_children[1:]).strip()
        if remainder:
            return remainder
    return body.decode_contents()


def html_to_markdown(html: str) -> str:
    converter = html2text.HTML2Text()
    converter.body_width = 0
    return converter.handle(html)


def get_plain_clipboard() -> str:
    result = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True)
    return result.stdout


def clipboard_to_markdown() -> str:
    try:
        html = get_clipboard_html()
    except (OSError, ValueError):
        html = None

    if html is None:
        return get_plain_clipboard()

    return html_to_markdown(clean_html(html))


def main() -> int:
    sys.stdout.write(clipboard_to_markdown())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
