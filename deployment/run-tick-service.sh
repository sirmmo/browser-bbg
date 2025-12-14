#!/bin/bash
# Simple script to run the tick service locally

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Default interval
INTERVAL=${1:-60}

echo "Starting tick service with ${INTERVAL}s interval..."
echo "Press Ctrl+C to stop"
echo ""

# Run the async tick service
python manage.py process_tick --async --interval "$INTERVAL"
