# .zshenv
#
# Sourced every time a Zsh session starts, regardless of whether it is
# a login, interactive, or non-interactive shell. This means it's read
# for all kinds of Zsh sessions. It is the first file sourced by Zsh
# during startup, even before .zshrc.

function set-paths() {
    # Set Homebrew path based on system architecture
    if [[ "$(uname -m)" == "x86_64" ]]; then
        # For Intel Macs
        export PATH="/usr/local/sbin:$PATH"
    else
        # For Apple Silicon Macs (M1/M2)
        export PATH="/opt/homebrew/sbin:$PATH"
    fi
    # Add user scripts and Go binaries to PATH
    export PATH="${HOME}/go/bin:${PATH}"
    export PATH="${HOME}/scripts:${PATH}"
    # Prepend ~/bin to prioritize it in PATH
    export PATH="${HOME}/bin:${PATH}"  # Prepend first
}

set-paths

[ -f "$HOME/.zshenv.local" ] && source "$HOME/.zshenv.local"
