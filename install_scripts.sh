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
# Find and add all executable shell scripts
shell_scripts=("$THIS_DIR"/scripts/*.sh)
for file in "${shell_scripts[@]}"; do
    if [[ -f "$file" && -x "$file" ]]; then
        scripts+=("$(basename "$file")")
    fi
done
# Find and add all executable Python scripts
python_scripts=("$THIS_DIR"/scripts/*.py)
for file in "${python_scripts[@]}"; do
    if [[ -f "$file" && -x "$file" ]]; then
        scripts+=("$(basename "$file")")
    fi
done
# Loop through each script in the array
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
    else
        echo "${destpath} link already created"
    fi
done
