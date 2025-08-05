#!/bin/bash
# Script to install/symlink custom scripts to ~/scripts directory
set -Eeu -o pipefail
# Get the directory where this script is located
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Define the destination directory for scripts
SCRIPTS_BASE="$HOME/scripts"
# Create the scripts directory if it doesn't exist
mkdir -p "$SCRIPTS_BASE"
# Array of specific scripts to install
scripts=(
    cdd
    chrome-killall
    f
    gm
    img2say
    pulls
    random
    tail-vscode-logs
    trim
    # executable .py and .sh scripts will be added dynamically
)
add_executable_scripts() {
    local ext=$1
    echo "Finding and adding executable '.${ext}' scripts..."
    local pattern="$THIS_DIR/scripts/*.$ext"
    for file in $pattern; do
        [[ -f "$file" && -x "$file" ]] || continue
        local name
        name=$(basename "$file")
        scripts+=("$name")
    done
}

add_executable_scripts sh
add_executable_scripts py

echo "Linking scripts..."
for script in "${scripts[@]}"
do
    # Define source and destination paths
    srcpath="${THIS_DIR}/scripts/${script}"
    destpath="${SCRIPTS_BASE}/${script}"
    # Check if source file exists
    if [[ ! -f "$srcpath" ]]
    then
        echo "Warning: Source file ${srcpath} does not exist, skipping"
        continue
    fi
    # Create symlink if it doesn't already exist
    if [[ ! -L "$destpath" ]]
    then
        ln -s "$srcpath" "$destpath"
        echo "Symlink created from ${srcpath} to ${destpath}"
    fi
done
