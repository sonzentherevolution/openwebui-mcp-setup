# Configuration Files

This directory contains MCPO configuration templates for different use cases.

## Available Configurations

### 1. Single Server (`single-server.json`)
**Use case**: Simple setup with one MCP server

```bash
mcpo --config config/single-server.json --port 8000
```

**Access**: `http://localhost:8000`

**Includes**:
- Time server with New York timezone

### 2. Multi Server (`multi-server.json`)
**Use case**: Multiple MCP servers in one proxy instance

```bash
mcpo --config config/multi-server.json --port 8000 --api-key "your-secret"
```

**Access**:
- Memory: `http://localhost:8000/memory`
- Time: `http://localhost:8000/time`
- Filesystem: `http://localhost:8000/filesystem`

**Includes**:
- Memory server for persistent storage
- Time server with timezone support
- Filesystem server with restricted access

### 3. Production (`production.json`)
**Use case**: Production deployment with security and external services

```bash
mcpo --config config/production.json --port 8000 --api-key "secure-production-key" --env-path .env
```

**Features**:
- Environment variable support
- External service integration via SSE and HTTP
- Security-hardened configurations
- Production-ready settings

**Includes**:
- All standard MCP servers with production settings
- External SSE-based MCP server
- External HTTP-based MCP server
- Git repository server

### 4. Annotated (`annotated.json`)
**Use case**: Learning and customization reference

**Features**:
- Detailed comments explaining each option
- Examples of all transport types
- Security configuration examples
- Environment variable usage

**Note**: Remove comment lines (starting with `_`) before using.

## Configuration Structure

### Basic Server Definition
```json
{
  "mcpServers": {
    "server_name": {
      "command": "executable",
      "args": ["arg1", "arg2"],
      "env": {
        "VAR_NAME": "value"
      }
    }
  }
}
```

### Transport Types

#### 1. Stdio (Default)
```json
{
  "server_name": {
    "command": "uvx",
    "args": ["mcp-server-time"]
  }
}
```

#### 2. Server-Sent Events (SSE)
```json
{
  "server_name": {
    "type": "sse",
    "url": "http://remote-server:8001/sse",
    "headers": {
      "Authorization": "Bearer token"
    }
  }
}
```

#### 3. Streamable HTTP
```json
{
  "server_name": {
    "type": "streamable_http",
    "url": "http://remote-server:8002/mcp",
    "headers": {
      "X-API-Key": "key"
    }
  }
}
```

## Environment Variables

### Using Environment Variables in Config
Reference environment variables using `${VAR_NAME}` syntax:

```json
{
  "external_service": {
    "type": "sse",
    "url": "http://service:8001/sse",
    "headers": {
      "Authorization": "Bearer ${SERVICE_TOKEN}"
    }
  }
}
```

### Loading Environment Files
```bash
mcpo --config config.json --env-path .env
```

### Example .env File
```bash
SERVICE_TOKEN=abc123xyz
API_KEY=secure-secret-key
TIMEZONE=America/New_York
```

## Common MCP Servers

### Memory Server
```json
{
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  }
}
```

### Time Server
```json
{
  "time": {
    "command": "uvx",
    "args": ["mcp-server-time", "--local-timezone=America/New_York"]
  }
}
```

### Filesystem Server
```json
{
  "filesystem": {
    "command": "npx",
    "args": [
      "-y", 
      "@modelcontextprotocol/server-filesystem",
      "--allowed-directories",
      "./safe-directory"
    ]
  }
}
```

### Git Server
```json
{
  "git": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-git"]
  }
}
```

## Security Best Practices

### 1. Use Environment Variables
Never hardcode secrets in configuration files:
```json
{
  "headers": {
    "Authorization": "Bearer ${SECRET_TOKEN}"
  }
}
```

### 2. Restrict Filesystem Access
Always limit directory access:
```json
{
  "args": [
    "--allowed-directories",
    "/app/data",
    "/app/uploads"
  ]
}
```

### 3. Use API Keys
Always configure API keys for production:
```bash
mcpo --config config.json --api-key "${API_KEY}"
```

### 4. HTTPS in Production
Use HTTPS URLs for external services:
```json
{
  "url": "https://secure-service.com/mcp"
}
```

## Troubleshooting

### Configuration Validation
Use the validation script to check your config:
```bash
python scripts/validate-config.py config/your-config.json
```

### Common Issues

**"Server failed to start"**
- Check command paths are correct
- Verify all dependencies are installed
- Review server logs for specific errors

**"Environment variable not found"**
- Ensure .env file exists and is readable
- Check variable names match exactly
- Use --env-path flag if .env is not in current directory

**"Permission denied"**
- Check file/directory permissions
- Ensure allowed directories exist
- Verify user has access to specified paths

### Debug Mode
Add debug logging to see detailed startup information:
```bash
mcpo --config config.json --log-level debug
```

## Customization

### Adding New Servers
1. Install the MCP server package
2. Add configuration entry following examples above
3. Test with single server first
4. Add to multi-server configuration

### Modifying Existing Servers
1. Copy an existing configuration file
2. Modify server arguments or environment variables
3. Test the configuration
4. Deploy to production

### Creating Custom Transport
For advanced use cases, you can:
1. Implement custom MCP server with HTTP transport
2. Use SSE or streamable_http type in configuration
3. Add authentication headers as needed
4. Test connectivity before production deployment

## Open Web UI Integration

### Adding Configured Servers
Each server in your configuration becomes available at its own path:

1. **Single server setup**: Use base URL
   - `http://localhost:8000`

2. **Multi-server setup**: Use server-specific paths
   - Memory: `http://localhost:8000/memory`
   - Time: `http://localhost:8000/time`
   - Git: `http://localhost:8000/git`

### Configuration Steps
1. Start MCPO with your configuration
2. Open Open Web UI settings
3. Go to External Tools section
4. Add each server individually with its specific URL
5. Test the connection for each tool

### API Key Configuration
If you set an API key for MCPO, configure it in Open Web UI:
1. Enter the tool URL
2. Add the API key in the authentication field
3. Test and save the configuration