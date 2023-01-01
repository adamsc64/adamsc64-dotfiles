# My .zshrc
#
# Load order:
# .zshenv
#     always sourced, it often contains exported variables that should be
#     available to other programs. For example, $PATH, $EDITOR, and $PAGER
# .zprofile
#     is basically the same as .zlogin except it's sourced before .zshrc
# .zshrc
#     interactive shell configuration
# .zlogin
#     sourced on the start of a login shell but after .zshrc if the shell is
#     also interactive


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
