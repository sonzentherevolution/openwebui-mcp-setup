# Open Web UI Integration Guide

This guide provides step-by-step instructions for integrating MCP servers with Open Web UI using MCPO.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Setup](#quick-setup)
3. [Single Server Integration](#single-server-integration)
4. [Multi-Server Integration](#multi-server-integration)
5. [Docker Integration](#docker-integration)
6. [Advanced Configuration](#advanced-configuration)
7. [Troubleshooting](#troubleshooting)
8. [Security Considerations](#security-considerations)

## Prerequisites

Before starting, ensure you have:

- **Open Web UI** installed and running
- **MCPO** installed (via uvx, pip, or Docker)
- **MCP servers** you want to integrate
- **Network access** between Open Web UI and MCPO

### Checking Prerequisites

```bash
# Verify Open Web UI is running
curl http://localhost:3000

# Verify MCPO installation
uvx mcpo --help
# OR
pip show mcpo
# OR  
docker pull ghcr.io/open-webui/mcpo:main

# Test MCP server (example with time server)
uvx mcp-server-time --help
```

## Quick Setup

### Step 1: Start MCPO with a Test Server

```bash
# Start time server via MCPO
uvx mcpo --port 8000 --api-key "test-key" -- uvx mcp-server-time --local-timezone=America/New_York
```

### Step 2: Configure Open Web UI

1. **Open Open Web UI** in your browser: `http://localhost:3000`
2. **Click Settings** (gear icon) in the bottom left
3. **Navigate to External Tools** or **Tool Servers**
4. **Click "Add Tool Server"**
5. **Enter Details**:
   - **Name**: `Time Server`
   - **URL**: `http://localhost:8000`
   - **API Key**: `test-key`
6. **Click Test** to verify connection
7. **Click Save** to add the tool

### Step 3: Test Integration

1. **Start a new chat** in Open Web UI
2. **Type a message** like "What time is it?"
3. **Look for tool usage** in the response - you should see the AI using the time server

## Single Server Integration

### Configuration Options

#### Option A: Command Line
```bash
# Basic setup
uvx mcpo --port 8000 --api-key "your-secure-key" -- uvx mcp-server-memory

# With environment variables
export API_KEY="your-secure-key"
export PORT=8000
uvx mcpo --port $PORT --api-key "$API_KEY" -- npx -y @modelcontextprotocol/server-memory
```

#### Option B: Configuration File
Create `config/single-server.json`:
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

Start MCPO:
```bash
uvx mcpo --port 8000 --api-key "your-key" --config config/single-server.json
```

### Open Web UI Configuration

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `Memory Server` | Descriptive name for the tool |
| **URL** | `http://localhost:8000` | MCPO proxy URL |
| **API Key** | `your-secure-key` | Must match MCPO API key |
| **Headers** | (optional) | Additional HTTP headers if needed |

## Multi-Server Integration

For multiple MCP servers, each gets its own route path.

### Step 1: Create Configuration

Create `config/multi-server.json`:
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "time": {
      "command": "uvx", 
      "args": ["mcp-server-time", "--local-timezone=America/New_York"]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y", 
        "@modelcontextprotocol/server-filesystem",
        "--allowed-directories",
        "./sandbox"
      ]
    }
  }
}
```

### Step 2: Start MCPO

```bash
uvx mcpo --port 8000 --api-key "multi-server-key" --config config/multi-server.json
```

### Step 3: Add Each Tool to Open Web UI

**Memory Server**:
- Name: `Memory`
- URL: `http://localhost:8000/memory`
- API Key: `multi-server-key`

**Time Server**:
- Name: `Time`
- URL: `http://localhost:8000/time`
- API Key: `multi-server-key`

**Filesystem Server**:
- Name: `Filesystem`
- URL: `http://localhost:8000/filesystem`
- API Key: `multi-server-key`

### Important Notes for Multi-Server

⚠️ **Each server needs a separate configuration in Open Web UI**
⚠️ **Use the full path including the server name**
⚠️ **All servers share the same API key**

## Docker Integration

### Basic Docker Setup

#### Step 1: Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - open-webui-data:/app/backend/data
    environment:
      - ENABLE_DIRECT_CONNECTIONS=true
    networks:
      - webui-network

  mcpo:
    image: ghcr.io/open-webui/mcpo:main
    ports:
      - "8000:8000"
    volumes:
      - ./config/multi-server.json:/app/config.json:ro
    command: >
      mcpo --host 0.0.0.0 --port 8000 
      --api-key "${API_KEY:-secure-key}"
      --config /app/config.json
    networks:
      - webui-network

volumes:
  open-webui-data:

networks:
  webui-network:
```

#### Step 2: Start Services
```bash
# Set API key
export API_KEY="docker-secure-key"

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

#### Step 3: Configure Tools in Open Web UI

Since both services are in the same Docker network:

**For Memory Server**:
- Name: `Memory`
- URL: `http://mcpo:8000/memory` (internal Docker networking)
- API Key: `docker-secure-key`

**Alternative (external access)**:
- URL: `http://localhost:8000/memory` (if accessing from outside Docker)

### Advanced Docker Setup

For production with security features:

```yaml
version: '3.8'

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - open-webui-data:/app/backend/data
    environment:
      - ENABLE_DIRECT_CONNECTIONS=true
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
    depends_on:
      - mcpo
    networks:
      - webui-network

  mcpo:
    image: ghcr.io/open-webui/mcpo:main
    expose:
      - "8000"
    volumes:
      - ./config/production.json:/app/config.json:ro
      - ./env/.env.production:/app/.env:ro
      - mcpo-data:/app/data
    command: >
      mcpo --host 0.0.0.0 --port 8000
      --config /app/config.json
      --env-path /app/.env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - webui-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/ssl:ro
    depends_on:
      - mcpo
    networks:
      - webui-network

volumes:
  open-webui-data:
  mcpo-data:

networks:
  webui-network:
    driver: bridge
```

## Advanced Configuration

### External Service Integration

For MCP servers running on external systems:

#### SSE Transport
```json
{
  "mcpServers": {
    "external_sse": {
      "type": "sse",
      "url": "http://external-server:8001/sse",
      "headers": {
        "Authorization": "Bearer ${SSE_TOKEN}"
      }
    }
  }
}
```

#### HTTP Transport
```json
{
  "mcpServers": {
    "external_http": {
      "type": "streamable_http", 
      "url": "http://api-server:8002/mcp",
      "headers": {
        "X-API-Key": "${HTTP_API_KEY}"
      }
    }
  }
}
```

### Custom Headers and Authentication

#### MCPO Configuration
```bash
# Start with custom headers
uvx mcpo --port 8000 --api-key "key" --header "X-Custom: value" -- your-server
```

#### Open Web UI Configuration
In Open Web UI tool settings, add custom headers:
```
Authorization: Bearer your-token
X-Client-ID: open-webui
```

### Load Balancing Multiple MCPO Instances

#### Setup
```yaml
# docker-compose.yml
services:
  mcpo-1:
    image: ghcr.io/open-webui/mcpo:main
    ports:
      - "8001:8000"
    # ... configuration

  mcpo-2:
    image: ghcr.io/open-webui/mcpo:main
    ports:
      - "8002:8000"
    # ... configuration

  nginx:
    image: nginx:alpine
    ports:
      - "8000:80"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf:ro
```

#### Nginx Load Balancer Config
```nginx
upstream mcpo_backend {
    server mcpo-1:8000;
    server mcpo-2:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://mcpo_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused
**Symptoms**: Open Web UI shows "Connection refused" error

**Diagnosis**:
```bash
# Check if MCPO is running
curl http://localhost:8000/docs

# Check port availability
netstat -tulpn | grep :8000

# Check container networking (if using Docker)
docker network inspect webui-network
```

**Solutions**:
- Ensure MCPO is running on the correct port
- Check firewall settings
- Verify network connectivity between services
- Use internal Docker networking (`http://mcpo:8000` instead of `localhost`)

#### 2. Tool Not Found (404)
**Symptoms**: Open Web UI shows "Tool not found" or 404 error

**Diagnosis**:
```bash
# List available tools
curl http://localhost:8000/docs

# Check specific tool endpoint
curl http://localhost:8000/memory
```

**Solutions**:
- Verify the tool path is correct (e.g., `/memory` not `/memory/`)
- Check MCPO configuration file for correct server names
- Ensure MCP server started successfully in MCPO logs

#### 3. Authentication Errors
**Symptoms**: "Unauthorized" or "Invalid API key" errors

**Diagnosis**:
```bash
# Test with API key
curl -H "Authorization: Bearer your-key" http://localhost:8000/docs

# Check MCPO logs for auth errors
docker-compose logs mcpo
```

**Solutions**:
- Verify API key matches between MCPO and Open Web UI
- Check for typos in API key configuration
- Ensure API key is set correctly in environment variables

#### 4. MCP Server Startup Failures
**Symptoms**: MCPO starts but individual tools don't work

**Diagnosis**:
```bash
# Check MCPO logs
docker-compose logs mcpo

# Test MCP server directly
uvx mcp-server-memory --help

# Check dependencies
npm list -g | grep @modelcontextprotocol
```

**Solutions**:
- Install missing MCP server dependencies
- Check MCP server command and arguments
- Verify file permissions for local MCP servers

### Debug Mode

Enable detailed logging:

#### MCPO Debug Mode
```bash
uvx mcpo --log-level debug --port 8000 --api-key "key" -- your-server
```

#### Open Web UI Debug Info
1. Open browser developer tools (F12)
2. Check Network tab for API requests
3. Look for failed requests and error messages
4. Check Console tab for JavaScript errors

### Health Checks

#### Manual Health Check
```bash
# Test MCPO health
curl http://localhost:8000/docs

# Test specific tool
curl -H "Authorization: Bearer your-key" http://localhost:8000/memory

# Check tool functionality
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer your-key" \
     -d '{"method": "list_tools", "params": {}}' \
     http://localhost:8000/memory
```

#### Automated Health Monitoring
```bash
#!/bin/bash
# health-check.sh

MCPO_URL="http://localhost:8000"
API_KEY="your-key"

# Check MCPO availability
if ! curl -s -f "$MCPO_URL/docs" > /dev/null; then
    echo "ERROR: MCPO is not responding"
    exit 1
fi

# Check tools
for tool in memory time filesystem; do
    if ! curl -s -f -H "Authorization: Bearer $API_KEY" "$MCPO_URL/$tool" > /dev/null; then
        echo "WARNING: Tool $tool is not responding"
    else
        echo "OK: Tool $tool is healthy"
    fi
done

echo "Health check completed"
```

## Security Considerations

### API Key Management

#### Generate Secure Keys
```bash
# Generate a secure API key
openssl rand -base64 32

# Generate multiple keys for different environments
echo "Development: $(openssl rand -base64 32)"
echo "Staging: $(openssl rand -base64 32)"
echo "Production: $(openssl rand -base64 32)"
```

#### Key Rotation
```bash
# 1. Generate new key
NEW_KEY=$(openssl rand -base64 32)

# 2. Update MCPO configuration
export API_KEY="$NEW_KEY"

# 3. Restart MCPO
docker-compose restart mcpo

# 4. Update Open Web UI with new key
# (Manual step in UI)

# 5. Verify functionality
curl -H "Authorization: Bearer $NEW_KEY" http://localhost:8000/docs
```

### Network Security

#### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 3000  # Open Web UI
sudo ufw allow 8000  # MCPO (if external access needed)
sudo ufw deny 11434  # Block direct Ollama access

# For production, block MCPO external access
sudo ufw deny 8000
```

#### Reverse Proxy Security
```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    listen 443 ssl;
    
    # Rate limiting
    limit_req zone=api burst=20 nodelay;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    location / {
        proxy_pass http://mcpo:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### MCP Server Security

#### Filesystem Server Restrictions
```json
{
  "filesystem": {
    "command": "npx",
    "args": [
      "-y", 
      "@modelcontextprotocol/server-filesystem",
      "--allowed-directories",
      "/app/safe-data",
      "/app/uploads",
      "--max-file-size",
      "10485760"
    ]
  }
}
```

#### Environment Variable Security
```bash
# Use environment files instead of command line
uvx mcpo --env-path .env --config config.json

# Secure file permissions
chmod 600 .env
chown $USER:$USER .env

# Never commit secrets to version control
echo '.env*' >> .gitignore
```

### Monitoring and Alerting

#### Log Monitoring
```bash
# Monitor MCPO logs for suspicious activity
tail -f /var/log/mcpo/access.log | grep -E '(401|403|404|429|500)'

# Alert on repeated failures
tail -f /var/log/mcpo/access.log | \
  awk '$9 >= 400 {print $0; system("echo Alert: HTTP error " $9 " | mail admin@example.com")}'
```

#### Metrics Collection
```yaml
# Add monitoring to docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

This comprehensive integration guide should help you successfully integrate MCP servers with Open Web UI using MCPO. Remember to test each step thoroughly and monitor your setup for any issues.