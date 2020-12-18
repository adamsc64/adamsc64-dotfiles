#!/bin/bash
set -Eeux -o pipefail
SCRIPTS_BASE=~/scripts
mkdir -p $SCRIPTS_BASE
scripts=(f)
for script in "${scripts[@]}"
do
    srcpath="$PWD/$script"
    destpath=$SCRIPTS_BASE/$script
    if [[ ! -L "$destpath" ]]
    then
        ln -s $srcpath $destpath
    fi
done


