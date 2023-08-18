#!/bin/bash
set -Eeu -o pipefail

COMMON=(
    .bash_login
    .git-shortcuts
    .gitconfig
    .gitignore_global
    .psqlrc
)

if [ -n "${CODESPACES+x}" ] && [ "$CODESPACES" == true ]; then
    DOTFILES=(
        "${COMMON[@]}"
    )
else
    DOTFILES=(
        .vimrc
        .zshenv
        .zshrc
        "${COMMON[@]}"
    )
fi

for dotfile in "${DOTFILES[@]}"
do
    srcpath="$PWD/$dotfile"
    destpath=~/$dotfile
    if [[ -L "$destpath" ]]
    then
        echo "$destpath link already created"
        continue
    fi
    if [[ -e "$destpath" ]]
    then
        echo "$destpath already exists"
        continue
    fi
    echo "Creating symlink for $dotfile: $srcpath -> $destpath"
    ln -s $srcpath $destpath
done
