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
# .zlogout
#     Sourced when logging out from a login shell.


autoload -U colors && colors

function set-title() {
    echo -ne "\e]1;$1\a"
}

function precmd(){
    if [ $ITERM_SESSION_ID ]; then
        set-title "$USER@$HOST ${PWD##*/}"
    fi
}

function set_custom_prompt {
    local RED="%{$fg[red]%}"
    local YELLOW="%{$fg[yellow]%}"
    local GREEN="%{$fg[green]%}"
    local GREENBOLD="%{$bold_color$fg[green]%}"
    local BLUE="%{$fg[blue]%}"
    local BLUEBOLD="%{$bold_color$fg[blue]%}"
    local BLACKBOLD="%{$bold_color$fg[black]%}"
    local RESETCOLOR="%{$reset_color%}"

    PS1=""
    # Current date and time
    PS1+="$BLACKBOLD%D %t "
    # Current hostname
    PS1+="$BLUEBOLD%m"
    # @ symbol
    PS1+="$BLACKBOLD@"
    # The current working directory
    PS1+="$GREEN%~ "
    # The % prompt
    PS1+="$GREENBOLD%% "
    # Reset back to normal color.
    PS1+="$RESETCOLOR"
    export PS1
}
set_custom_prompt  # invokes function


# Colorize ls and grep
alias ls="ls -G"
export LSCOLORS="FxFxCxDxBxegedabagacad"
export GREP_OPTIONS='--color=auto'

export HISTFILESIZE=1000000000
export HISTSIZE=1000000000
[ -z "$HISTFILE" ] && export HISTFILE="$HOME/.zsh_history"
export SAVEHIST=$HISTSIZE
setopt INC_APPEND_HISTORY
export HISTTIMEFORMAT="[%F %T] "
setopt EXTENDED_HISTORY
setopt HIST_FIND_NO_DUPS

stty erase '^?'

[ -f ".zshrc.local" ] && source ".zshrc.local"
export PATH="/usr/local/sbin:$PATH"
# if the script `github-copilot-cli` is in path
if command -v github-copilot-cli &> /dev/null
then
    # alias the script `github-copilot-cli` to `copilot`
    eval "$(github-copilot-cli alias -- "$0")"
fi
