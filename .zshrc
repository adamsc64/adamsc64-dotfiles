# .zshrc
#
# The .zshrc file is sourced whenever an interactive shell is started,
# which includes most terminal sessions (but not when running scripts
# or non-interactive processes). It is not sourced by default for
# non-interactive shells like cron jobs or when running scripts
# directly.
#
# Load order:
# 1. .zshenv
#     Always sourced for every shell (login, interactive, and non-interactive).
#     It often contains exported variables that should be available to other
#     programs. For example, $PATH, $EDITOR, and $PAGER.
#     Avoid interactive commands here.
#
# 2. .zprofile
#     Sourced for login shells (not interactive shells).
#     It's similar to .zlogin, but sourced before .zshrc.
#     Typically used for login-specific environment settings.
#     A login shell is typically the first shell session you start when
#     logging into a system or when connecting to a remote server.
#     An interactive shell is any shell where you can directly interact
#     with the command line. All login shells are also interactive, but
#     not all interactive shells are login shells. Opening a new
#     terminal window or starting a new session within an
#     already-logged-in environment starts an interactive shell.
#
# 3. .zshrc
#     Sourced for interactive shells only.
#     Contains interactive shell configuration, such as aliases, functions,
#     shell options, prompt settings, and plugin managers.
#
# 4. .zlogin
#     Sourced only for login shells (just like .zprofile), but after .zshrc if the
#     shell is interactive and a login shell. Typically used for commands that
#     should be run when logging in, like starting services or running a welcome message.
#
# 5. .zlogout
#     Sourced when logging out from a login shell.

function set-prompt() {
    setopt prompt_subst  # allows for command substitution within $PS1
    setopt interactivecomments  # Ignores comments (i.e. '# ...') on commandline

    # Set the prompt
    autoload -U colors && colors
    PS1=""
    PS1="${PS1}%F{33}%D{%H:%M:%S} "
    PS1="${PS1}%F{magenta}★ "
    PS1="${PS1}%F{8}%m "
    PS1="${PS1}%F{24}%~ "
    PS1="${PS1}%F{12}\$(git branch 2>/dev/null | grep '^*' | colrm 1 2 | sed 's/^/\[/' | sed 's/$/\] /')"
    PS1="${PS1}%F{8}%# %f"
}

function set-colors() {
    # Colorize ls
    export LSCOLORS="GxFxCxDxBxegedabagaced"
    alias ls="ls -G"
    # Colorize grep
    export GREP_OPTIONS='--color=auto'
    # Enable all colors
    export CLICOLOR=1
}

function configure-terminal-history() {
    # maximum number of lines contained in the history file
    export HISTFILESIZE=100000
    # maximum number of commands for the current shell session's history
    export HISTSIZE=100000
    # the file in which command history is saved
    [ -z "$HISTFILE" ] && export HISTFILE="$HOME/.zsh_history"
    # number of commands to save in the history file when the shell exits
    export SAVEHIST=$HISTSIZE
    # Append every command to the history file immediately
    setopt INC_APPEND_HISTORY
    # Share history across all sessions
    setopt SHARE_HISTORY
    # Enable timestamp for history
    # %F: This placeholder represents the date in the format YYYY-MM-DD.
    # %T: This placeholder represents the time in the format HH:MM:SS.
    export HISTTIMEFORMAT="[%F %T] "
    setopt EXTENDED_HISTORY
    setopt HIST_FIND_NO_DUPS
}

function set-git-helpers() {
    # Git Helpers
    # -----------
    # ghl: give me a canonical link to a github entity
    ghl() {
        # Get all results from GitHub API via CLI
        RESULTS=$(gh pr list -A adamsc64 --json url,title,number -sall)
        # If no argument is provided, return all results
        [ -z "$1" ] && { echo "${RESULTS}" | jq; return 0; }
        # If an argument is provided, return the matched PR
        echo "$RESULTS" | jq ".[] | select(.number == $1)"
    }
    # gd: git diff from merge base
    alias gd='git diff $(git merge-base HEAD origin/$(gm)) HEAD'
    # gl: list of commits since merge base
    alias gl='git log $(git merge-base HEAD origin/$(gm))..HEAD'
    # gr: git rebase since merge base
    alias gr='git rebase -i $(git merge-base HEAD origin/$(gm))'
    # gm: get name of master or main branch
    alias gm='git symbolic-ref refs/remotes/origin/HEAD | sed "s@^refs/remotes/origin/@@g"'
    # gpr: list pull requests in the current repo
    alias gpr='gh pr list -A $USERNAME --json url,title,number'
}

# Special function in Zsh that runs before each prompt is displayed
function precmd() {
    function set-title() {
        # Send an escape sequence to set the terminal window title to the
        # provided argument ($1)
        echo -ne "\e]1;$1\a"
    }

    # Check if running in iTerm2 by checking ITERM_SESSION_ID
    if [ $ITERM_SESSION_ID ]; then
        # Set the terminal title to "username@hostname current_directory"
        set-title "${PWD##*/}"
    fi
}

set-prompt
set-colors
configure-terminal-history
set-git-helpers

# Force the 'backspace' key to properly erase characters in the
# terminal.
#
# Explanation:
# - Different terminal emulators and systems may send different
#   control codes for the 'backspace' key.
# - The most common control codes for 'backspace' are '^?' (ASCII DEL,
#   value 127) and '^H' (ASCII BS, value 8).
# - Some systems or configurations may incorrectly interpret the
#   'backspace' key, causing it to insert a character like `^?` or
#   not function as expected.
# - By using the 'stty erase' command with '^?', we ensure that the
#   terminal interprets 'backspace' correctly as a command to delete
#   the character before the cursor, rather than doing nothing or
#   producing unintended characters.
#
# This configuration is particularly useful if you're encountering
# problems where the 'backspace' key does not behave as expected in a
# terminal, such as after SSHing into a remote machine or in some
# custom terminal setups.
stty erase '^?'

# By default, BuildKit shows its progress using an interactive
# display with fancy status indicators (like progress bars).
# Setting BUILDKIT_PROGRESS to 'plain' forces the progress output
# to be simpler and more readable in non-interactive environments
# (like CI/CD pipelines), where the interactive display may not
# render properly or may clutter the logs.
export BUILDKIT_PROGRESS=plain

# if the script `github-copilot-cli` is in path
if command -v github-copilot-cli &> /dev/null
then
    # alias the script `github-copilot-cli` to `copilot`
    eval "$(github-copilot-cli alias -- "$0")"
fi

# rbenv configuration
export PATH="$HOME/.rbenv/bin:$PATH"
if command -v rbenv 1>/dev/null 2>&1; then
  eval "$(rbenv init - zsh)"
fi

# Source local configuration if it exists
[ -f "$HOME/.zshrc.local" ] && source "$HOME/.zshrc.local"
