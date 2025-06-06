#!/bin/sh
# Test script for cross-environment Python detection

# Function to detect Python command
find_python() {
    # Try to detect if we're on Windows
    if [ -n "$WINDIR" ] || [ "$OSTYPE" = "msys" ] || [ "$OSTYPE" = "cygwin" ]; then
        # Windows environment - try various Python commands
        if command -v py >/dev/null 2>&1; then
            echo "py"
        elif command -v python >/dev/null 2>&1; then
            echo "python"
        elif command -v python3 >/dev/null 2>&1; then
            echo "python3"
        else
            echo ""
        fi
    else
        # Unix/Linux/WSL environment
        if command -v python3 >/dev/null 2>&1; then
            echo "python3"
        elif command -v python >/dev/null 2>&1; then
            echo "python"
        else
            echo ""
        fi
    fi
}

# Test the function
echo "Testing Python detection..."
echo "Environment: $OSTYPE"
echo "WINDIR: $WINDIR"

PYTHON_CMD=$(find_python)
if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python not found"
else
    echo "✅ Found Python: $PYTHON_CMD"
    $PYTHON_CMD --version
fi