#!/bin/bash

set -euxo pipefail  # Exit on error, undefined vars, pipe failures

echo "🔐 Installing SSH configuration from 1Password..."

# Check if op is installed
if ! command -v op &> /dev/null; then
    echo "❌ Error: 1Password CLI (op) is not installed"
    echo "Install it with: brew install 1password-cli"
    exit 1
fi

# Check if signed in to 1Password (op whoami returns success if signed in)
if ! op whoami &> /dev/null; then
    echo "🔑 Signing in to 1Password..."
    eval "$(op signin)" || { echo "❌ Failed to sign in"; exit 1; }
fi

# Create SSH keys directory
mkdir -p ~/.ssh/keys
chmod 700 ~/.ssh
chmod 700 ~/.ssh/keys

# Extract PEM files from 1Password
echo "📦 Extracting PEM files..."

# Extract yellowtiger.pem
echo "  - yellowtiger.pem"
op read "op://Personal/SSH-YellowTiger/main-key-2012-05-26.pem" \
    > ~/.ssh/keys/yellowtiger.pem
chmod 600 ~/.ssh/keys/yellowtiger.pem

# Extract newhavenlist.pem
echo "  - newhavenlist.pem"
op read "op://Personal/SSH-NewHavenList/thenewhavenlist_admin.pem" \
    > ~/.ssh/keys/newhavenlist.pem
chmod 600 ~/.ssh/keys/newhavenlist.pem

# Generate SSH config from template
echo "📝 Generating SSH config..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
op inject -i "$SCRIPT_DIR/config.template" -o ~/.ssh/config
chmod 600 ~/.ssh/config

echo "✅ SSH configuration installed successfully!"
echo ""
