@echo off
REM Multi MCP Server Setup (Windows)
REM This script sets up multiple MCP servers through MCPO proxy using a config file

setlocal

REM Configuration
if "%PORT%"=="" set PORT=8000
if "%API_KEY%"=="" set API_KEY=demo-secret-key
if "%CONFIG_FILE%"=="" set CONFIG_FILE=..\config\multi-server.json

echo 🚀 Starting Multiple MCP Servers via MCPO...
echo 📍 Port: %PORT%
echo 🔐 API Key: %API_KEY%
echo 📋 Config: %CONFIG_FILE%
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

REM Check if config file exists
if not exist "%CONFIG_FILE%" (
    echo ❌ Config file not found: %CONFIG_FILE%
    echo Creating a sample config file...
    
    mkdir ..\config 2>nul
    echo {> "%CONFIG_FILE%"
    echo   "mcpServers": {>> "%CONFIG_FILE%"
    echo     "memory": {>> "%CONFIG_FILE%"
    echo       "command": "npx",>> "%CONFIG_FILE%"
    echo       "args": ["-y", "@modelcontextprotocol/server-memory"]>> "%CONFIG_FILE%"
    echo     },>> "%CONFIG_FILE%"
    echo     "time": {>> "%CONFIG_FILE%"
    echo       "command": "uvx",>> "%CONFIG_FILE%"
    echo       "args": ["mcp-server-time", "--local-timezone=America/New_York"]>> "%CONFIG_FILE%"
    echo     }>> "%CONFIG_FILE%"
    echo   }>> "%CONFIG_FILE%"
    echo }>> "%CONFIG_FILE%"
    
    echo ✅ Created sample config file: %CONFIG_FILE%
)

REM Start the MCPO proxy with config file
echo 🔧 Starting MCPO proxy with multiple MCP servers...
echo 📖 Interactive docs will be available at: http://localhost:%PORT%/docs
echo.
echo 🔗 Add these URLs to Open Web UI:
echo   - Memory Server: http://localhost:%PORT%/memory
echo   - Time Server: http://localhost:%PORT%/time
echo.
echo Available servers:
echo   💾 Memory: Persistent storage for AI conversations
echo   🕒 Time: Current time and timezone utilities
echo.
echo Press Ctrl+C to stop all servers
echo.

uvx mcpo --port %PORT% --api-key "%API_KEY%" --config "%CONFIG_FILE%"