#!/bin/bash

# Chainlit Installation Script
# Fixes the Pydantic compatibility issue and installs dependencies

set -e  # Exit on any error

echo "Installing Chainlit with Pydantic compatibility fix..."
echo

# Check if we're in the right directory
if [ ! -f "backend/pyproject.toml" ]; then
    echo "Error: Please run this script from the root directory of the chainlit project"
    echo "Expected to find backend/pyproject.toml"
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install Poetry first:"
    echo "https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    echo "Error: pnpm is not installed. Please install pnpm first:"
    echo "https://pnpm.io/installation"
    exit 1
fi

echo "Prerequisites check passed"
echo

# Install JS dependencies
echo "Installing JavaScript dependencies..."
pnpm install
echo

# Build UI
echo "Building UI..."
pnpm run buildUi
echo

# Navigate to backend directory
cd backend

# Install Poetry shell plugin if not already installed
echo "Installing Poetry shell plugin..."
poetry self add poetry-plugin-shell 2>/dev/null || echo "Poetry shell plugin already installed or not needed"
echo

# Install Python dependencies with Poetry (this will use the fixed pyproject.toml with pydantic constraint)
echo "Installing Python dependencies..."
poetry install --only main
echo

# Test the installation
echo "Testing Chainlit installation..."
if poetry run chainlit --help > /dev/null 2>&1; then
    echo "Chainlit CLI is working"
else
    echo "Chainlit CLI test failed"
    exit 1
fi

echo
echo "Installation completed successfully"
echo
echo "To run the hello example:"
echo "  cd backend"
echo "  poetry shell"
echo "  chainlit run chainlit/hello.py"
echo
echo "Then open http://localhost:8000 in your browser"