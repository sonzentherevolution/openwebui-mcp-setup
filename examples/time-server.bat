@echo off
REM MCP Time Server Quick Start (Windows)
REM This script sets up the MCP time server through MCPO proxy

setlocal

REM Configuration
if "%PORT%"=="" set PORT=8000
if "%API_KEY%"=="" set API_KEY=demo-secret-key
if "%TIMEZONE%"=="" set TIMEZONE=America/New_York

echo 🚀 Starting MCP Time Server via MCPO...
echo 📍 Port: %PORT%
echo 🔐 API Key: %API_KEY%
echo 🌍 Timezone: %TIMEZONE%
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

REM Start the MCPO proxy with time server
echo 🔧 Starting MCPO proxy with MCP time server...
echo 📖 Interactive docs will be available at: http://localhost:%PORT%/docs
echo 🔗 Add this URL to Open Web UI: http://localhost:%PORT%
echo.
echo Press Ctrl+C to stop the server
echo.

uvx mcpo --port %PORT% --api-key "%API_KEY%" -- uvx mcp-server-time --local-timezone="%TIMEZONE%"