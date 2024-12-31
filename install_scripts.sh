#!/bin/bash
set -Eeu -o pipefail
SCRIPTS_BASE=~/scripts
mkdir -p $SCRIPTS_BASE
scripts=(
    cdd
    chrome-killall
    f
    gm
    img2say
    pbpaste-md.sh
    random
    random_numbers.py
    tail-vscode-logs
    trim
    update_indexes.sh
    youtube-audio-cut.py
)
for script in "${scripts[@]}"
do
    srcpath="$PWD/scripts/$script"
    destpath=$SCRIPTS_BASE/$script
    if [[ ! -L "$destpath" ]]
    then
        ln -s $srcpath $destpath
        echo "Symlink created from $srcpath to $destpath"
    else
        echo "$destpath link already created"
    fi
done


