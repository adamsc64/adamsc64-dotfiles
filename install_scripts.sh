#!/bin/bash
set -Eeu -o pipefail
SCRIPTS_BASE=~/scripts
mkdir -p $SCRIPTS_BASE
scripts=(f update_indexes.sh cdd trim random random_numbers.py)
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


