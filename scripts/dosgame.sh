#!/bin/sh

set -eu

dosroot="$HOME/Library/CloudStorage/Dropbox/Chris/games/DOS"
game="${1:-}"
program="${2:-}"

if [ -z "$game" ]; then
    echo "Usage: dosgame <game-dir> [program]" >&2
    echo "Example: dosgame simant SIMANT.EXE" >&2
    exit 1
fi

if [ ! -d "$dosroot/$game" ]; then
    echo "Game directory not found: $dosroot/$game" >&2
    exit 1
fi

if [ -z "$program" ]; then
    program="$(find "$dosroot/$game" -maxdepth 1 -type f \( -iname '*.bat' -o -iname '*.exe' -o -iname '*.com' \) \
        | sed "s#^$dosroot/$game/##" \
        | grep -vi '^install\.' \
        | grep -vi '^setup\.' \
        | grep -vi '^info\.' \
        | head -n 1)"
fi

if [ -z "$program" ]; then
    echo "No launch program found in: $dosroot/$game" >&2
    exit 1
fi

dosgame_path="$(printf '%s' "$game" | tr '/' '\\')"

exec dosbox-x -fastlaunch \
    -c "mount c \"$dosroot\"" \
    -c "c:" \
    -c "cd $dosgame_path" \
    -c "$program"
