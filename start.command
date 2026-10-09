#!/bin/bash
# Move to the script's directory (Tic Tac Toe folder)
cd "$(dirname "$0")"

echo "=========================================================="
echo " Starting Tic-Tac-Toe AI (Minimax & Alpha-Beta Pruning)..."
echo "=========================================================="

# Activate the virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the app
python3 app.py
