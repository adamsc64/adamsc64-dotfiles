#!/bin/bash
set -Eeu -o pipefail
# Creates an index file, ``index.txt`` for a series useful directories.
# This is just a recursive list of files inside a directory.
paths=("$@")
for path in "${paths[@]}"
do
    cd $path && find . > index.txt 2> /dev/null
done
