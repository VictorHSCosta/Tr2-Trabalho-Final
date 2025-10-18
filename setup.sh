#!/usr/bin/env bash
# Bootstrap the Flask development environment.
set -euo pipefail

PYTHON_BIN=${PYTHON_BIN:-python3}

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Python executable '$PYTHON_BIN' not found." >&2
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON_BIN" -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing project and dev dependencies..."
pip install -r requirements-dev.txt

echo "Done! Activate the environment with 'source .venv/bin/activate'."
echo "Run the app with 'flask --app app run --debug'."
