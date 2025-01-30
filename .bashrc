# .bashrc
# This file is sourced by interactive shells.
# It should contain commands to set the command prompt and
# other interactive functions, such as alias creation.

# Fancy colorized terminal settings #
#####################################
# What I'm doing here is defining the environment variable that the bash shell
# uses to render its prompt. The terminal uses the first part to override its
# default window title.
#
# For informating about colors:
# https://wiki.archlinux.org/index.php/Color_Bash_Prompt
#
function set_custom_prompt {
    #Prompt and prompt colors
    # 30m - Black
    # 31m - Red
    # 32m - Green
    # 33m - Yellow
    # 34m - Blue
    # 35m - Purple
    # 36m - Cyan
    # 37m - White
    # 0 - Normal
    # 1 - Bold
    local BLACK="\[\033[0;30m\]"
    local BLACKBOLD="\[\033[1;30m\]"
    local RED="\[\033[0;31m\]"
    local REDBOLD="\[\033[1;31m\]"
    local GREEN="\[\033[0;32m\]"
    local GREENBOLD="\[\033[1;32m\]"
    local YELLOW="\[\033[0;33m\]"
    local YELLOWBOLD="\[\033[1;33m\]"
    local BLUE="\[\033[0;34m\]"
    local BLUEBOLD="\[\033[1;34m\]"
    local PURPLE="\[\033[0;35m\]"
    local PURPLEBOLD="\[\033[1;35m\]"
    local CYAN="\[\033[0;36m\]"
    local CYANBOLD="\[\033[1;36m\]"
    local WHITE="\[\033[0;37m\]"
    local WHITEBOLD="\[\033[1;37m\]"

    # Sets the terminal title to username, hostname, and $CWD.
    export PS1="\[\e]2;\u@\H \w\a\]"
    # Current time:
    export PS1+="$BLACKBOLD\t "
    # Current hostname:
    export PS1+="$PURPLE\h"
    # @ symbol
    export PS1+="$BLACKBOLD@"
    # The current working directory
    export PS1+="$GREEN\w "
    # The classic $
    export PS1+="$GREENBOLD\$ "
    # Reset back to normal color.
    export PS1+="\[\e[0m\]"
}
# If on GitHub Codespaces, don't set the custom prompt.
if [[ ! -v CODESPACES ]]; then
    set_custom_prompt
fi

# Also, default ls to colorized display.
# See http://geoff.greer.fm/lscolors/
export CLICOLOR=1
export LSCOLORS=FxFxCxDxBxegedabagacad
# Set grep to color by default
alias grep="grep --color=auto"

# Store history permanently and with time
export HISTFILESIZE=1000000
export HISTSIZE=1000000
export HISTCONTROL=ignoreboth
# Append to PROMPT_COMMAND while preserving existing commands
export PROMPT_COMMAND="history -a"
# Codespaces persisted share directory
CODESPACES_PERSISTED_SHARE="/workspaces/.codespaces/.persistedshare"
# If the persisted share directory exists, use history file there.
if [[ -d $CODESPACES_PERSISTED_SHARE ]]; then
    export HISTFILE="$CODESPACES_PERSISTED_SHARE/.bash_history"
fi

# Set $PATH variable. #
#######################
# Note that these definitions are in reverse order.
# Always have my own executables come first.
export PATH="${HOME}/go/bin:${PATH}"
export PATH="${HOME}/scripts:${PATH}"
export PATH="${HOME}/bin:${PATH}"

export PYTHONDONTWRITEBYTECODE=1

source ~/.git-shortcuts
