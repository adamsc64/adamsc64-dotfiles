#!/bin/bash
set -Eeux -o pipefail
SCRIPTS_BASE=~/scripts
mkdir -p $SCRIPTS_BASE
scripts=(f update_indexes.sh)
for script in "${scripts[@]}"
do
    srcpath="$PWD/scripts/$script"
    destpath=$SCRIPTS_BASE/$script
    if [[ ! -L "$destpath" ]]
    then
        ln -s $srcpath $destpath
    fi
done


