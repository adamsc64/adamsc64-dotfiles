#!/bin/bash
set -Eeuo pipefail

# Post-macOS-upgrade automation helper.
#
# This script intentionally uses safe defaults:
# - It does not force OS updates unless requested.
# - It does not run your dotfiles installers unless requested.
# - It prints reminders for steps macOS privacy controls often block from automation.

DRY_RUN=0
RUN_OS_UPDATES=0
RUN_DOTFILES=0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
    cat <<'EOF'
Usage: macos_post_upgrade.sh [options]

Options:
  --dry-run           Print commands without executing them
  --with-os-updates   Run softwareupdate --install --all
  --with-dotfiles     Run this repo's install scripts
  -h, --help          Show this help message

Examples:
  macos_post_upgrade.sh
  macos_post_upgrade.sh --with-os-updates
  macos_post_upgrade.sh --with-dotfiles --dry-run
EOF
}

log() {
    printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

run_cmd() {
    local cmd="$*"
    if [[ "$DRY_RUN" -eq 1 ]]; then
        printf '[dry-run] %s\n' "$cmd"
    else
        eval "$cmd"
    fi
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                DRY_RUN=1
                ;;
            --with-os-updates)
                RUN_OS_UPDATES=1
                ;;
            --with-dotfiles)
                RUN_DOTFILES=1
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                usage
                exit 1
                ;;
        esac
        shift
    done
}

ensure_macos() {
    if [[ "$(uname -s)" != "Darwin" ]]; then
        echo "This script is for macOS only." >&2
        exit 1
    fi
}

install_or_check_clt() {
    log "Checking Apple Command Line Tools"
    if xcode-select -p >/dev/null 2>&1; then
        echo "Command Line Tools appear installed."
    else
        # xcode-select --install opens a GUI flow and may need user interaction.
        run_cmd "xcode-select --install"
    fi
}

accept_xcode_license_if_needed() {
    log "Attempting to accept Xcode license (if required)"
    # This can fail harmlessly when full Xcode is not installed.
    if ! run_cmd "sudo xcodebuild -license accept"; then
        echo "Skipping: license acceptance not required or not available."
    fi
}

run_homebrew_updates() {
    log "Running Homebrew updates"
    if ! command -v brew >/dev/null 2>&1; then
        echo "Homebrew not found. Install from https://brew.sh first."
        return
    fi

    run_cmd "brew update"
    run_cmd "brew upgrade"
    run_cmd "brew upgrade --cask"
    run_cmd "brew cleanup"

    # doctor is informative and can exit non-zero; do not fail entire script.
    if ! run_cmd "brew doctor"; then
        echo "brew doctor reported issues. Review output above."
    fi
}

run_optional_software_update() {
    if [[ "$RUN_OS_UPDATES" -ne 1 ]]; then
        return
    fi

    log "Installing pending macOS software updates"
    run_cmd "sudo softwareupdate --install --all"
}

run_optional_dotfiles_installers() {
    if [[ "$RUN_DOTFILES" -ne 1 ]]; then
        return
    fi

    log "Running dotfiles install scripts from this repo"
    if [[ -x "${REPO_ROOT}/install.sh" ]]; then
        run_cmd "\"${REPO_ROOT}/install.sh\""
    else
        # Fallback for repos where install.sh is not executable.
        run_cmd "bash \"${REPO_ROOT}/install.sh\""
    fi
}

main() {
    parse_args "$@"
    ensure_macos

    install_or_check_clt
    accept_xcode_license_if_needed
    run_homebrew_updates
    run_optional_software_update
    run_optional_dotfiles_installers

    log "Post-upgrade automation flow completed"
}

main "$@"