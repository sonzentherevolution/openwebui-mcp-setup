# Quick Start Examples

This directory contains ready-to-use scripts for setting up common MCP servers with MCPO proxy.

## Available Examples

### 1. Time Server
**Files**: `time-server.bat` (Windows), `time-server.sh` (Linux/Mac)

Provides current time, date, and timezone utilities.

**Usage:**
```bash
# Windows
time-server.bat

# Linux/Mac
./time-server.sh
```

**Features:**
- Current date and time
- Timezone conversions
- Time calculations
- Date formatting

**Open Web UI URL**: `http://localhost:8000`

### 2. Memory Server
**Files**: `memory-server.bat` (Windows), `memory-server.sh` (Linux/Mac)

Provides persistent memory storage for AI conversations.

**Usage:**
```bash
# Windows
memory-server.bat

# Linux/Mac
./memory-server.sh
```

**Features:**
- Store key-value pairs
- Retrieve stored memories
- Search memories
- Persistent storage across sessions

**Open Web UI URL**: `http://localhost:8001`

### 3. Multi-Server Setup
**Files**: `multi-server.bat` (Windows)

Runs multiple MCP servers simultaneously using a configuration file.

**Usage:**
```bash
# Windows
multi-server.bat
```

**Features:**
- Multiple servers in one process
- Configuration file based setup
- Automatic config generation
- Individual tool paths

**Open Web UI URLs:**
- Memory: `http://localhost:8000/memory`
- Time: `http://localhost:8000/time`

## Environment Variables

All scripts support these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000/8001 | Port for MCPO proxy |
| `API_KEY` | "demo-secret-key" | API key for authentication |
| `TIMEZONE` | "America/New_York" | Timezone for time server |
| `CONFIG_FILE` | "../config/multi-server.json" | Config file path |

**Example:**
```bash
# Windows
set PORT=9000
set API_KEY=my-secret-key
time-server.bat

# Linux/Mac
PORT=9000 API_KEY=my-secret-key ./time-server.sh
```

## Prerequisites

### Required Software
- **Python 3.8+**: For uvx and MCPO
- **Node.js**: For memory server (npm/npx)
- **uv**: Python package installer (installed automatically)

### Automatic Installation
All scripts will automatically install missing dependencies:
- `uv` package manager
- `mcpo` proxy server
- Required MCP servers

## Getting Started

1. **Choose an example** based on your needs
2. **Run the script** from this directory
3. **Wait for startup** - first run may take longer due to downloads
4. **Check the OpenAPI docs** at the provided URL
5. **Add to Open Web UI** using the URLs shown in output

## Troubleshooting

### Common Issues

**"uvx command not found"**
- The script will automatically install `uv`
- If it fails, manually install: `pip install uv`

**"npx command not found"**
- Install Node.js from https://nodejs.org/
- Restart your terminal after installation

**"Port already in use"**
- Change the port: `set PORT=9000` (Windows) or `PORT=9000` (Linux/Mac)
- Or stop the conflicting service

**"Connection refused in Open Web UI"**
- Ensure the script is still running
- Check the port matches what you configured in Open Web UI
- Verify the URL includes the correct path for multi-server setups

### Debug Mode

Add debug logging to any script:
```bash
# Add to the uvx mcpo command
--log-level debug
```

### Testing Connection

Use curl to test the API:
```bash
# Test basic connection
curl http://localhost:8000/docs

# Test with API key
curl -H "Authorization: Bearer demo-secret-key" http://localhost:8000/docs
```

## Customization

### Modifying Scripts
- Edit environment variables at the top of each script
- Add additional command-line arguments to the `uvx mcpo` command
- Modify MCP server arguments as needed

### Creating New Examples
1. Copy an existing script as a template
2. Update the MCP server command
3. Adjust port numbers to avoid conflicts
4. Update documentation strings
5. Test thoroughly before submitting

## Security Notes

- Change default API keys in production
- Use environment variables for sensitive values
- Consider HTTPS for production deployments
- Monitor logs for security issues

## Next Steps

After running an example:

1. **Explore the OpenAPI docs** at `/docs` endpoint
2. **Test the tools** directly via the API
3. **Configure Open Web UI** with the provided URLs
4. **Create custom configurations** using the config files in `../config/`
5. **Deploy to production** using Docker configurations in `../docker/`