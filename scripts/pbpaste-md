#!/bin/bash
# This script converts rich content from the clipboard to Markdown
# format. It first attempts to extract HTML from the clipboard, cleans
# it by removing styles and unnecessary tags, and then uses html2text
# to convert it to Markdown.
#
# Dependencies: install a python virtualenv, and then `pip install bs4 html2text lxml`
if encoded=$(osascript -e 'try' -e 'the clipboard as «class HTML»' -e 'end try' \
2>/dev/null); then
    echo "$encoded" | \
    perl -ne 'print chr foreach unpack("C*",pack("H*",substr($_,11,-3)))' | \
    python -c "import sys; \
               from bs4 import BeautifulSoup; \
               html = sys.stdin.read(); \
               soup = BeautifulSoup(html, 'lxml'); \
               [tag.attrs.pop('style', None) for tag in \
                soup.find_all(True)]; \
               [soup.head.decompose() if soup.head else None]; \
               contents = (soup.body.b.decode_contents() \
                if soup.body.contents[0].name == 'b' \
                else soup.body.decode_contents()); \
               print(contents); \
               " | \
    python -m html2text -b 0
else
    pbpaste
fi
