@echo off
REM MCP Memory Server Quick Start (Windows)
REM This script sets up the MCP memory server through MCPO proxy

setlocal

REM Configuration
if "%PORT%"=="" set PORT=8001
if "%API_KEY%"=="" set API_KEY=demo-secret-key

echo 🚀 Starting MCP Memory Server via MCPO...
echo 📍 Port: %PORT%
echo 🔐 API Key: %API_KEY%
echo 💾 This server provides persistent memory storage for your AI conversations
echo.

REM Check if uvx is available
uvx --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ uvx is not installed. Installing via pip...
    pip install uv
    if %errorlevel% neq 0 (
        echo ❌ Failed to install uv. Please install it manually.
        exit /b 1
    )
)

REM Start the MCPO proxy with memory server
echo 🔧 Starting MCPO proxy with MCP memory server...
echo 📖 Interactive docs will be available at: http://localhost:%PORT%/docs
echo 🔗 Add this URL to Open Web UI: http://localhost:%PORT%
echo.
echo Memory server features:
echo   - Store and retrieve key-value pairs
echo   - Persistent storage across sessions
echo   - Search and list stored memories
echo.
echo Press Ctrl+C to stop the server
echo.

uvx mcpo --port %PORT% --api-key "%API_KEY%" -- npx -y @modelcontextprotocol/server-memory