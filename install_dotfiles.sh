#!/bin/bash
set -Eeux -o pipefail
dotfiles=(
    .vimrc
    .bash_login
    .psqlrc
    .gitconfig
    .gitignore_global
)
for dotfile in "${dotfiles[@]}"
do
    srcpath="$PWD/$dotfile"
    destpath=~/$dotfile
    if [[ ! -L "$destpath" ]]
    then
        ln -s $srcpath $destpath
    fi
done
