#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

echo "Setting up SNMP simulator..."

# Activate virtual environment if it exists, create it if it doesn't
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo "Activating existing virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
else
    echo "Creating new virtual environment..."
    python3 -m venv "$PROJECT_ROOT/venv"
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Install required packages
echo "Installing required packages..."
pip install -U pip setuptools wheel
pip install -r "$PROJECT_ROOT/requirements.txt"
pip install --upgrade pysnmp
pip install --upgrade snmpsim

# Verify installation
echo "Verifying installation..."
which snmpsim-command-responder

# Make scripts executable
chmod +x "$SCRIPT_DIR/start_agents.sh"

echo "Setup complete! You can now run './scripts/start_agents.sh' to start the SNMP agent."