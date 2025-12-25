#!/bin/bash

# Desktop App Setup Script
# This script installs Node.js and dependencies for the Budget App desktop client

set -e

echo "=== Budget App Desktop Setup ==="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✓ Homebrew found"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    brew install node
    echo "✓ Node.js installed"
else
    echo "✓ Node.js already installed ($(node --version))"
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please reinstall Node.js."
    exit 1
fi

echo "✓ npm found ($(npm --version))"
echo ""

# Navigate to desktop directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To run the desktop app:"
echo "  cd desktop"
echo "  npm start"
echo ""
echo "To build distributable packages:"
echo "  npm run build:mac    # macOS"
echo "  npm run build:win    # Windows"
echo "  npm run build:linux  # Linux"
echo ""
