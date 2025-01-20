#!/bin/bash
set -Eeu -o pipefail

COMMON=(
    .bash_login
    .git-shortcuts
    .gitconfig
    .gitignore_global
    .psqlrc
)

# Check if the script is running in a GitHub Codespace environment.
if [ -n "${CODESPACES+x}" ] && [ "$CODESPACES" == true ]; then
    # For GitHub Codespaces, only include common dotfiles.
    DOTFILES=(
        "${COMMON[@]}"
    )
else
    # If not running in a GitHub Codespace environment, include additional dotfiles.
    DOTFILES=(
        .vimrc
        .zshenv
        .zshrc
        .zprofile
        "${COMMON[@]}"
    )
fi

for dotfile in "${DOTFILES[@]}"
do
    # Define the source and destination paths for the dotfile
    srcpath="$PWD/$dotfile"
    destpath=~/$dotfile
    # Check if the destination path is already a symlink
    if [[ -L "$destpath" ]]
    then
        echo "$destpath link already created"
        continue
    fi
    # Check if a file (non-symlink) already exists at the destination
    if [[ -e "$destpath" ]]
    then
        echo "$destpath already exists"
        continue
    fi
    # Create the symlink if neither a symlink nor a file exists
    echo "Creating symlink for $dotfile: $srcpath -> $destpath"
    ln -s $srcpath $destpath
done
