#!/bin/bash

# MCP Time Server Quick Start
# This script sets up the MCP time server through MCPO proxy

set -e

# Configuration
PORT=${PORT:-8000}
API_KEY=${API_KEY:-"demo-secret-key"}
TIMEZONE=${TIMEZONE:-"America/New_York"}

echo "🚀 Starting MCP Time Server via MCPO..."
echo "📍 Port: $PORT"
echo "🔐 API Key: $API_KEY"
echo "🌍 Timezone: $TIMEZONE"
echo ""

# Check if uvx is available
if ! command -v uvx &> /dev/null; then
    echo "❌ uvx is not installed. Installing via pip..."
    pip install uv
fi

# Start the MCPO proxy with time server
echo "🔧 Starting MCPO proxy with MCP time server..."
uvx mcpo --port "$PORT" --api-key "$API_KEY" -- uvx mcp-server-time --local-timezone="$TIMEZONE"

# Note: The above command will block and run the server
# Press Ctrl+C to stop the server