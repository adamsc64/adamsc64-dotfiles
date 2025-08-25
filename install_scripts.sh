#!/bin/bash
# Script to install/symlink custom scripts to ~/scripts directory
set -Eeu -o pipefail

# Python virtual environment
PYTHON_ENV_BASE="$HOME/.venvs"
PYTHON_ENV_PATH="$PYTHON_ENV_BASE/env3"
PYTHON_PACKAGES="beautifulsoup4 ipdb requests urllib3 pygame"

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

ensure_python_env() {
    echo "Ensuring Python environment at $PYTHON_ENV_PATH..."
    if [[ ! -d "$PYTHON_ENV_PATH" ]]; then
        echo "Creating Python virtual environment at $PYTHON_ENV_PATH..."
        mkdir -p "$PYTHON_ENV_BASE"
        python3 -m venv "$PYTHON_ENV_PATH"
        source "$PYTHON_ENV_PATH/bin/activate"
        pip install $PYTHON_PACKAGES
        deactivate
        echo "Virtual environment created at $PYTHON_ENV_PATH"
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
source ${PYTHON_ENV_PATH}/bin/activate
exec "${srcpath}" "\$@"
EOF
        chmod +x "$destpath"
    fi
}

main() {
    ensure_python_env
    add_executable_scripts py
    add_executable_scripts sh
    echo "Linking and wrapping scripts..."
    for script in "${scripts[@]}"; do
        link_script "$script"
        wrap_script "$script"
    done
}

main "$@"
