#!/bin/bash
set -Eeu -o pipefail

if [ -n "${CODESPACES+x}" ] && [ "$CODESPACES" == true ]; then
    exit 0
fi

dotfiles=(
    .vimrc
    .bash_login
    .psqlrc
    .git-shortcuts
    .gitconfig
    .gitignore_global
    .zshenv
    .zshrc
)
for dotfile in "${dotfiles[@]}"
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
    ln -s $srcpath $destpath
done
