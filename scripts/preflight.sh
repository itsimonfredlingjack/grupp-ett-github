#!/bin/bash
# Preflight checks for Jules Health Check

echo "Running preflight checks..."

# Ensure we are in the root of the repo (basic check)
if [ ! -f "pyproject.toml" ]; then
    echo "Warning: pyproject.toml not found in current directory."
fi

# Ensure python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found."
    exit 1
fi

echo "Preflight check passed."
exit 0
