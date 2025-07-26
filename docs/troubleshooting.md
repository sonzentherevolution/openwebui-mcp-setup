# Troubleshooting Guide

This guide covers common issues and their solutions when setting up MCP servers with Open Web UI using MCPO.

## Quick Diagnosis Checklist

Before diving into specific issues, run through this quick checklist:

```bash
# 1. Check if MCPO is running
curl -f http://localhost:8000/docs || echo "MCPO not responding"

# 2. Check if specific tools are available
curl -f http://localhost:8000/memory || echo "Memory tool not available"

# 3. Check API key authentication
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/docs || echo "Auth failed"

# 4. Check Open Web UI is running
curl -f http://localhost:3000 || echo "Open Web UI not responding"

# 5. Check container status (if using Docker)
docker-compose ps
```

## Connection Issues

### MCPO Not Starting

#### Symptoms
- Command hangs without output
- "Connection refused" errors
- Port already in use errors

#### Diagnosis
```bash
# Check port availability
netstat -tulpn | grep :8000
# OR on Windows
netstat -an | findstr :8000

# Check if process is running
ps aux | grep mcpo
# OR on Windows
tasklist | findstr mcpo

# Check system resources
free -h && df -h
```

#### Solutions

**Port conflict:**
```bash
# Use a different port
uvx mcpo --port 8001 --api-key "key" -- your-server

# Or kill the conflicting process
sudo kill $(lsof -ti:8000)
```

**Missing dependencies:**
```bash
# Install uv/uvx
pip install uv

# Install Node.js for npm/npx servers
# Download from https://nodejs.org/

# Check MCP server installation
uvx mcp-server-time --help
npx -y @modelcontextprotocol/server-memory --help
```

**Insufficient permissions:**
```bash
# On Linux/Mac, ensure user has permission to bind to port
# For ports < 1024, use sudo or run as root
sudo uvx mcpo --port 80 --api-key "key" -- your-server

# Or use unprivileged port
uvx mcpo --port 8000 --api-key "key" -- your-server
```

### Open Web UI Can't Connect to MCPO

#### Symptoms
- "Connection refused" in Open Web UI
- Tool servers show as offline
- Timeout errors when testing connections

#### Diagnosis
```bash
# Test connection from Open Web UI host
curl http://localhost:8000/docs

# If using Docker, test internal networking
docker-compose exec open-webui curl http://mcpo:8000/docs

# Check network configuration
docker network inspect $(docker-compose ps -q | xargs docker inspect --format='{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' | head -1)
```

#### Solutions

**Wrong URL configuration:**
```bash
# For same host setup
URL: http://localhost:8000

# For Docker internal networking
URL: http://mcpo:8000

# For external server
URL: http://server-ip:8000
```

**Firewall blocking connection:**
```bash
# Check firewall status
sudo ufw status
sudo iptables -L

# Allow MCPO port
sudo ufw allow 8000
# OR
sudo iptables -I INPUT -p tcp --dport 8000 -j ACCEPT
```

**Docker networking issues:**
```yaml
# Ensure services are on same network
networks:
  webui-network:
    driver: bridge

services:
  open-webui:
    networks:
      - webui-network
  mcpo:
    networks:
      - webui-network
```

## Authentication Issues

### Invalid API Key Errors

#### Symptoms
- "Unauthorized" or "403 Forbidden" errors
- "Invalid API key" messages
- Tool connections fail authentication

#### Diagnosis
```bash
# Test API key directly
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/docs

# Check MCPO configuration
echo $API_KEY
grep -i api.key config.json

# Check Open Web UI configuration
# (Manual check in UI settings)
```

#### Solutions

**API key mismatch:**
```bash
# Ensure same key in both MCPO and Open Web UI
export API_KEY="consistent-key-here"
uvx mcpo --api-key "$API_KEY" --port 8000 -- your-server

# In Open Web UI: Use same value in tool configuration
```

**Special characters in API key:**
```bash
# Avoid special characters or escape them properly
API_KEY="simple-alphanumeric-key-123"

# Or use base64 encoded keys
API_KEY=$(echo "my-secret" | base64)
```

**Environment variable not loaded:**
```bash
# Check if variable is set
echo "API key is: '$API_KEY'"

# Export explicitly
export API_KEY="your-key"

# Or use .env file
echo "API_KEY=your-key" > .env
uvx mcpo --env-path .env --port 8000 -- your-server
```

### Authentication Headers

#### Wrong header format:**
```bash
# Correct format
Authorization: Bearer your-api-key

# Not these formats
Authorization: your-api-key
X-API-Key: your-api-key
```

## MCP Server Issues

### Server Won't Start

#### Symptoms
- MCPO starts but tools don't work
- "Server failed to initialize" errors
- Missing tool endpoints

#### Diagnosis
```bash
# Check MCPO logs
uvx mcpo --log-level debug --port 8000 --api-key "key" -- your-server

# Test MCP server directly
uvx mcp-server-time --help
npx -y @modelcontextprotocol/server-memory --help

# Check dependencies
npm list -g | grep modelcontextprotocol
pip list | grep mcp
```

#### Solutions

**Missing MCP server:**
```bash
# Install common MCP servers
npx -y @modelcontextprotocol/server-memory
npx -y @modelcontextprotocol/server-filesystem
uvx mcp-server-time

# Verify installation
which mcp-server-time
npm list -g @modelcontextprotocol/server-memory
```

**Incorrect command arguments:**
```bash
# Check server help for correct arguments
uvx mcp-server-time --help

# Common correct formats
uvx mcp-server-time --local-timezone=America/New_York
npx -y @modelcontextprotocol/server-memory
npx -y @modelcontextprotocol/server-filesystem --allowed-directories ./sandbox
```

**Permission errors:**
```bash
# Check directory permissions
ls -la ./sandbox
chmod 755 ./sandbox

# For filesystem server, ensure directories exist
mkdir -p ./sandbox ./uploads
```

### Configuration File Issues

#### Symptoms
- "Configuration file not found" errors
- MCPO won't start with config file
- Individual servers in config don't work

#### Diagnosis
```bash
# Check file exists and is readable
ls -la config/multi-server.json
cat config/multi-server.json

# Validate JSON syntax
python -m json.tool config/multi-server.json

# Check file permissions
stat config/multi-server.json
```

#### Solutions

**JSON syntax errors:**
```bash
# Use JSON validator
python -m json.tool config/multi-server.json > /dev/null

# Common issues to fix:
# - Trailing commas
# - Missing quotes around strings
# - Unescaped quotes in strings

# Example of fixing common errors:
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

**Path issues:**
```bash
# Use absolute paths in config
{
  "command": "/usr/local/bin/uvx",
  "args": ["mcp-server-time"]
}

# Or ensure PATH includes required directories
export PATH=$PATH:/usr/local/bin
```

## Docker-Specific Issues

### Container Won't Start

#### Symptoms
- Docker container exits immediately
- "Container failed to start" errors
- Services stuck in "starting" state

#### Diagnosis
```bash
# Check container logs
docker-compose logs mcpo

# Check container status
docker-compose ps

# Inspect container configuration
docker inspect mcpo-container-name

# Check resource usage
docker stats
```

#### Solutions

**Resource limits:**
```yaml
# Increase memory/CPU limits
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
```

**Volume mount issues:**
```bash
# Check volume permissions
ls -la ./config/
chmod -R 755 ./config/

# Use absolute paths
volumes:
  - /absolute/path/to/config:/app/config:ro
```

**Network conflicts:**
```bash
# Use custom network
networks:
  custom-network:
    driver: bridge

# Or remove conflicting networks
docker network prune
```

### Volume and Mount Issues

#### Symptoms
- Configuration files not found in container
- Data not persisting between restarts
- Permission denied errors

#### Diagnosis
```bash
# Check volume mounts
docker inspect container-name | grep -A 10 "Mounts"

# Test file access inside container
docker-compose exec mcpo ls -la /app/config/
docker-compose exec mcpo cat /app/config/multi-server.json

# Check host file permissions
ls -la config/multi-server.json
```

#### Solutions

**Fix file permissions:**
```bash
# Make files readable by container
chmod 644 config/*.json
chmod 755 config/

# For volumes requiring write access
chmod 666 data/
```

**Use bind mounts correctly:**
```yaml
# Correct syntax
volumes:
  - ./config/multi-server.json:/app/config.json:ro
  - ./data:/app/data:rw

# Not this
volumes:
  - config/multi-server.json:/app/config.json  # Missing ./
```

## Open Web UI Integration Issues

### Tools Not Appearing

#### Symptoms
- Added tools don't show up in Open Web UI
- "No tools available" messages
- Tools added but not functional

#### Diagnosis
```bash
# Check tool server configuration in Open Web UI
# 1. Go to Settings > External Tools
# 2. Verify each tool configuration
# 3. Test connection for each tool

# Check MCPO endpoints
curl http://localhost:8000/docs
curl http://localhost:8000/memory
curl http://localhost:8000/time
```

#### Solutions

**Incorrect URL paths:**
```bash
# For single server setup
URL: http://localhost:8000

# For multi-server setup - each tool needs separate config
Memory: http://localhost:8000/memory
Time: http://localhost:8000/time
Filesystem: http://localhost:8000/filesystem
```

**Missing API key:**
```bash
# Ensure API key is configured in Open Web UI
# Settings > External Tools > [Tool Name] > API Key: your-api-key
```

### Tool Responses Not Working

#### Symptoms
- Tools connect but don't provide responses
- Empty or error responses from tools
- Tools timeout during use

#### Diagnosis
```bash
# Test tool functionality directly
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer your-key" \
     -d '{"method": "list_tools", "params": {}}' \
     http://localhost:8000/memory

# Check MCPO logs during tool usage
docker-compose logs -f mcpo

# Check Open Web UI logs
docker-compose logs -f open-webui
```

#### Solutions

**Tool not properly initialized:**
```bash
# Restart MCPO with debug logging
uvx mcpo --log-level debug --port 8000 --api-key "key" -- your-server

# Check for initialization errors in logs
```

**Timeout issues:**
```bash
# Increase timeout in Open Web UI if available
# Or restart both services
docker-compose restart mcpo open-webui
```

## Performance Issues

### Slow Response Times

#### Symptoms
- Tools take long time to respond
- Open Web UI shows loading indicators for extended periods
- Timeout errors

#### Diagnosis
```bash
# Check system resources
top
htop
docker stats

# Test response times
time curl http://localhost:8000/docs
time curl -H "Authorization: Bearer key" http://localhost:8000/memory

# Check network latency
ping localhost
```

#### Solutions

**Resource constraints:**
```yaml
# Increase container limits
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2.0'
```

**Too many concurrent requests:**
```bash
# Reduce concurrent connections or add rate limiting
# Configure in nginx or application settings
```

### High Memory Usage

#### Symptoms
- Containers using excessive memory
- System becomes unresponsive
- Out of memory errors

#### Diagnosis
```bash
# Check memory usage
docker stats
free -h

# Check for memory leaks
docker-compose logs mcpo | grep -i memory
```

#### Solutions

**Set memory limits:**
```yaml
services:
  mcpo:
    deploy:
      resources:
        limits:
          memory: 512M
    mem_limit: 512M
```

**Restart services periodically:**
```bash
# Add restart policy
restart: unless-stopped

# Or set up cron job to restart
0 2 * * * docker-compose restart mcpo
```

## Advanced Debugging

### Enable Debug Logging

#### MCPO Debug Mode
```bash
# Maximum verbosity
uvx mcpo --log-level trace --port 8000 --api-key "key" -- your-server

# With file logging
uvx mcpo --log-level debug --log-file mcpo.log --port 8000 --api-key "key" -- your-server
```

#### Container Debug Mode
```yaml
# Add debug environment
environment:
  - DEBUG=true
  - LOG_LEVEL=debug

# Or override command
command: >
  mcpo --log-level debug --host 0.0.0.0 --port 8000
  --api-key "${API_KEY}" --config /app/config.json
```

### Network Debugging

#### Check Network Connectivity
```bash
# From Open Web UI container to MCPO
docker-compose exec open-webui ping mcpo
docker-compose exec open-webui curl http://mcpo:8000/docs

# Check port binding
docker port mcpo-container 8000

# Check network configuration
docker network ls
docker network inspect webui-network
```

#### Network Troubleshooting
```bash
# Test with netcat
nc -zv localhost 8000

# Check routing
traceroute localhost
# OR on Windows
tracert localhost

# Test DNS resolution
nslookup mcpo
dig mcpo
```

### Health Check Scripts

#### Comprehensive Health Check
```bash
#!/bin/bash
# health-check.sh

set -e

echo "=== MCPO Health Check ==="

# Check MCPO availability
echo "Checking MCPO availability..."
if curl -s -f http://localhost:8000/docs > /dev/null; then
    echo "✓ MCPO is responding"
else
    echo "✗ MCPO is not responding"
    exit 1
fi

# Check authentication
echo "Checking authentication..."
if curl -s -f -H "Authorization: Bearer $API_KEY" http://localhost:8000/docs > /dev/null; then
    echo "✓ Authentication working"
else
    echo "✗ Authentication failed"
    exit 1
fi

# Check individual tools
echo "Checking individual tools..."
for tool in memory time filesystem; do
    if curl -s -f -H "Authorization: Bearer $API_KEY" http://localhost:8000/$tool > /dev/null; then
        echo "✓ Tool $tool is healthy"
    else
        echo "⚠ Tool $tool is not responding"
    fi
done

# Check Open Web UI connectivity
echo "Checking Open Web UI..."
if curl -s -f http://localhost:3000 > /dev/null; then
    echo "✓ Open Web UI is responding"
else
    echo "⚠ Open Web UI is not responding"
fi

echo "=== Health Check Complete ==="
```

#### Usage
```bash
# Make executable
chmod +x health-check.sh

# Set API key and run
export API_KEY="your-key"
./health-check.sh

# Run periodically
watch -n 30 ./health-check.sh
```

## Getting Help

### Log Collection

When seeking help, collect these logs:

```bash
# MCPO logs
uvx mcpo --log-level debug --port 8000 --api-key "key" -- your-server 2>&1 | tee mcpo.log

# Docker logs
docker-compose logs --timestamps mcpo > mcpo-docker.log
docker-compose logs --timestamps open-webui > openwebui.log

# System information
uname -a > system-info.txt
docker version >> system-info.txt
docker-compose version >> system-info.txt
```

### Issue Template

When reporting issues, include:

1. **Environment Information**:
   - Operating system and version
   - Docker/Docker Compose versions
   - MCPO version
   - Open Web UI version

2. **Configuration**:
   - MCPO configuration file (sanitized)
   - Docker Compose file (sanitized)
   - Environment variables (without secrets)

3. **Steps to Reproduce**:
   - Exact commands used
   - Expected behavior
   - Actual behavior

4. **Logs**:
   - MCPO logs (with debug level)
   - Container logs
   - Browser console errors

5. **Debugging Attempts**:
   - What you've already tried
   - Results of troubleshooting steps

### Community Resources

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check official Open Web UI and MCPO docs
- **Community Forums**: Search for similar issues
- **Discord/Slack**: Real-time community support

Remember to sanitize any sensitive information (API keys, passwords, internal URLs) before sharing logs or configuration files.