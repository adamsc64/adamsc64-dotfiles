#!/bin/bash
set -Eeu -o pipefail
# Creates an index file, ``index.txt`` for a series useful directories.
# This is just a recursive list of files inside a directory.
paths=("$@")
for path in "${paths[@]}"
do
    TEMP_FILE="$(mktemp)"
    cd $path && find . > ${TEMP_FILE} 2> /dev/null
    awk '{ print length, $0 }' "${TEMP_FILE}" | sort -n | awk '{$1=""; print substr($0, 2)}' > "${TEMP_FILE}_sorted"
    mv "${TEMP_FILE}_sorted" "$path/index.txt"
    rm "${TEMP_FILE}"
done
