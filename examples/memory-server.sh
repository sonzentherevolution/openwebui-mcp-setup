#!/bin/bash

# MCP Memory Server Quick Start
# This script sets up the MCP memory server through MCPO proxy

set -e

# Configuration
PORT=${PORT:-8001}
API_KEY=${API_KEY:-"demo-secret-key"}

echo "🚀 Starting MCP Memory Server via MCPO..."
echo "📍 Port: $PORT"
echo "🔐 API Key: $API_KEY"
echo "💾 This server provides persistent memory storage for your AI conversations"
echo ""

# Check if uvx is available
if ! command -v uvx &> /dev/null; then
    echo "❌ uvx is not installed. Installing via pip..."
    pip install uv
fi

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ npx is not installed. Please install Node.js first."
    exit 1
fi

# Start the MCPO proxy with memory server
echo "🔧 Starting MCPO proxy with MCP memory server..."
echo "📖 Interactive docs will be available at: http://localhost:$PORT/docs"
echo "🔗 Add this URL to Open Web UI: http://localhost:$PORT"
echo ""
echo "Memory server features:"
echo "  - Store and retrieve key-value pairs"
echo "  - Persistent storage across sessions"
echo "  - Search and list stored memories"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvx mcpo --port "$PORT" --api-key "$API_KEY" -- npx -y @modelcontextprotocol/server-memory