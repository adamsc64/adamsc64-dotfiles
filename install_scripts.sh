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

link_script() {
    local script=$1
    local srcpath="${THIS_DIR}/scripts/${script}"
    local destpath="${SCRIPTS_BASE}/${script}"
    if [[ ! -f "$srcpath" ]]; then
        echo "Warning: Source file ${srcpath} does not exist, skipping"
        return
    fi
    if [[ ! -L "$destpath" ]]; then
        echo "Creating symlink from ${srcpath} to ${destpath}..."
        ln -s "$srcpath" "$destpath"
    fi
}

wrap_script() {
    local script=$1
    local srcpath="${THIS_DIR}/scripts/${script}"
    local wrapper_name="${script%.*}"  # Remove extension
    wrapper_name="${wrapper_name//_/-}"  # Replace underscores with dashes
    local destpath="${SCRIPTS_BASE}/${wrapper_name}"

    if [[ ! -f "$srcpath" ]]; then
        echo "Warning: Source file ${srcpath} does not exist, skipping"
        return
    fi

    if [[ ! -f "$destpath" ]]; then
        echo "Creating wrapper ${wrapper_name} for ${script}..."
        cat > "$destpath" << EOF
#!/bin/bash
source ~/.venvs/env3/bin/activate
exec "${srcpath}" "\$@"
EOF
        chmod +x "$destpath"
    fi
}

main() {
    add_executable_scripts py
    add_executable_scripts sh

    echo "Linking scripts..."

    for script in "${scripts[@]}"; do
        link_script "$script"
        wrap_script "$script"
    done
}

main "$@"
