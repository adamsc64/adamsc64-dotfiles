#!/bin/bash
set -Eeu -o pipefail
dotfiles=(
    .vimrc
    .bash_login
    .psqlrc
    .gitconfig
    .gitignore_global
    .zshenv
    .zshrc
)
for dotfile in "${dotfiles[@]}"
do
    srcpath="$PWD/$dotfile"
    destpath=~/$dotfile
    if [[ ! -L "$destpath" ]]
    then
        ln -s $srcpath $destpath
    else
        echo "$destpath link already created"
    fi
done
