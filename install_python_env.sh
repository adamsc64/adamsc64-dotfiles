#!/bin/bash
# Sets up the shared Python virtual environment and installs required packages.
set -Eeu -o pipefail

PYTHON_ENV_BASE="$HOME/.venvs"
PYTHON_ENV_PATH="$PYTHON_ENV_BASE/env3"
PYTHON_PACKAGES="beautifulsoup4 ipdb requests urllib3 pygame yt-dlp selenium webdriver_manager pytesseract"

echo "Ensuring Python environment at $PYTHON_ENV_PATH..."
if [[ ! -d "$PYTHON_ENV_PATH" ]]; then
    echo "Creating Python virtual environment at $PYTHON_ENV_PATH..."
fi
mkdir -p "$PYTHON_ENV_BASE"
python3 -m venv "$PYTHON_ENV_PATH"
source "$PYTHON_ENV_PATH/bin/activate"
pip install $PYTHON_PACKAGES

# Pre-download chromedriver for wifi-login.py (needs to work offline)
echo "Pre-downloading chromedriver for offline use..."
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"

deactivate
echo "Python packages installed."
