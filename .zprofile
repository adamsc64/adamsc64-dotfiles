# .zprofile: Sourced only for login shells. A login shell is typically
# when you log into your system via SSH or start a terminal that
# requires login (e.g., the first shell session after logging into your
# desktop environment or virtual terminal). It is not sourced for all
# interactive shells.

BREW="/opt/homebrew/bin/brew"
[ -f "$BREW" ] && eval "$($BREW shellenv)"
