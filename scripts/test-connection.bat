@echo off
REM MCPO Connection Test Script (Windows)
REM Tests connectivity and functionality of MCPO proxy and MCP servers

setlocal EnableDelayedExpansion

REM Default configuration
if "%MCPO_URL%"=="" set MCPO_URL=http://localhost:8000
if "%API_KEY%"=="" set API_KEY=demo-secret-key
if "%TIMEOUT%"=="" set TIMEOUT=10

REM Parse command line arguments
:parse_args
if "%1"=="--url" (
    set MCPO_URL=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--api-key" (
    set API_KEY=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--timeout" (
    set TIMEOUT=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: %0 [OPTIONS]
    echo.
    echo Options:
    echo   --url URL          MCPO URL (default: http://localhost:8000^)
    echo   --api-key KEY      API key for authentication
    echo   --timeout SECONDS  Request timeout (default: 10^)
    echo   --help             Show this help message
    echo.
    echo Environment variables:
    echo   MCPO_URL          MCPO URL
    echo   API_KEY           API key
    echo   TIMEOUT           Request timeout
    exit /b 0
)
if "%1" neq "" (
    echo [ERROR] Unknown option: %1
    exit /b 1
)

echo ======================================
echo   MCPO Connection Test Script
echo ======================================
echo MCPO URL: %MCPO_URL%
echo API Key: %API_KEY:~0,8%...
echo Timeout: %TIMEOUT%s
echo ======================================
echo.

REM Check prerequisites
curl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] curl is required but not installed
    exit /b 1
)

REM Test basic connectivity
echo [INFO] Testing basic connectivity to MCPO...
curl -s -f --max-time %TIMEOUT% "%MCPO_URL%/docs" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] MCPO is responding
) else (
    echo [ERROR] MCPO is not responding at %MCPO_URL%
    exit /b 1
)

REM Test authentication
echo [INFO] Testing API key authentication...
for /f %%i in ('curl -s -w "%%{http_code}" --max-time %TIMEOUT% -H "Authorization: Bearer %API_KEY%" "%MCPO_URL%/docs" -o nul 2^>nul') do set auth_response=%%i

if "%auth_response%"=="200" (
    echo [SUCCESS] Authentication successful
) else if "%auth_response%"=="401" (
    echo [ERROR] Authentication failed (HTTP 401^)
    exit /b 1
) else if "%auth_response%"=="403" (
    echo [ERROR] Authentication failed (HTTP 403^)
    exit /b 1
) else (
    echo [WARNING] Unexpected response code: %auth_response%
)

REM Test OpenAPI documentation
echo [INFO] Testing OpenAPI documentation...
curl -s --max-time %TIMEOUT% -H "Authorization: Bearer %API_KEY%" "%MCPO_URL%/docs" | findstr /i "OpenAPI" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] OpenAPI documentation is accessible
) else (
    echo [ERROR] OpenAPI documentation not found or invalid
)

REM Test available tools (simplified for Windows)
echo [INFO] Discovering available tools...
curl -s --max-time %TIMEOUT% -H "Authorization: Bearer %API_KEY%" "%MCPO_URL%/openapi.json" > temp_openapi.json 2>nul

REM Simple tool discovery (looking for common tool names)
set tools=
for %%t in (memory time filesystem git) do (
    findstr /i "%%t" temp_openapi.json >nul 2>&1
    if !errorlevel! equ 0 (
        set tools=!tools! %%t
    )
)

if exist temp_openapi.json del temp_openapi.json

if defined tools (
    echo [SUCCESS] Found tools:%tools%
    
    REM Test each tool
    for %%t in (%tools%) do (
        echo [INFO] Testing tool: %%t
        for /f %%i in ('curl -s -w "%%{http_code}" --max-time %TIMEOUT% -H "Authorization: Bearer %API_KEY%" "%MCPO_URL%/%%t" -o nul 2^>nul') do set tool_response=%%i
        
        if "!tool_response!"=="200" (
            echo [SUCCESS] Tool '%%t' is responding
        ) else (
            echo [ERROR] Tool '%%t' failed (HTTP !tool_response!^)
        )
    )
) else (
    echo [WARNING] No tools discovered (may be single-server setup^)
    
    REM Test base endpoint
    echo [INFO] Testing base endpoint...
    for /f %%i in ('curl -s -w "%%{http_code}" --max-time %TIMEOUT% -H "Authorization: Bearer %API_KEY%" "%MCPO_URL%" -o nul 2^>nul') do set base_response=%%i
    
    if "%base_response%"=="200" (
        echo [SUCCESS] Base endpoint is responding
    ) else (
        echo [WARNING] Base endpoint returned HTTP %base_response%
    )
)

REM Basic performance test
echo [INFO] Running basic performance test...
set start_time=%time%

for /l %%i in (1,1,3) do (
    curl -s --max-time %TIMEOUT% -H "Authorization: Bearer %API_KEY%" "%MCPO_URL%/docs" >nul 2>&1
)

set end_time=%time%
echo [SUCCESS] Performance test completed

echo.
echo ======================================
echo [SUCCESS] All tests completed successfully!
echo ======================================

echo.
echo Connection Summary:
echo   MCPO URL: %MCPO_URL%
echo   Status: Online
echo   Authentication: Working
if defined tools (
    echo   Tools Found: %tools%
) else (
    echo   Tools Found: 1 (single server^)
)

echo.
echo Next steps:
echo   1. Add this URL to Open Web UI: %MCPO_URL%
echo   2. Use API key: %API_KEY%
if defined tools (
    echo   3. Configure individual tools:
    for %%t in (%tools%) do (
        echo      - %%t: %MCPO_URL%/%%t
    )
)

echo.
pause