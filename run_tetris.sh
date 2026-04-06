#!/bin/bash
cd "$(dirname "$0")"

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install pygame if not explicitly present
pip install --upgrade pip > /dev/null 2>&1
pip install pygame > /dev/null 2>&1

# Run the game
python3 tetris.py
