#!/bin/bash
# Usage: last-download.sh [grep_pattern]
if [[ -n "$1" ]]; then
	realpath "$(ls -1t "$HOME/Downloads"/* | grep -- "$1" | head -n1)"
else
	realpath "$(ls -1t "$HOME/Downloads"/* | head -n1)"
fi
