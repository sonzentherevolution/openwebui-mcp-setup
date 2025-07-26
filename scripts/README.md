# Testing and Validation Scripts

This directory contains scripts for testing, validating, and monitoring your MCPO setup.

## Available Scripts

### 1. Connection Test Scripts

#### `test-connection.sh` (Linux/Mac) and `test-connection.bat` (Windows)
**Purpose**: Test basic connectivity and functionality of MCPO proxy

**Usage**:
```bash
# Linux/Mac
./test-connection.sh --url http://localhost:8000 --api-key "your-key"

# Windows  
test-connection.bat --url http://localhost:8000 --api-key "your-key"
```

**Features**:
- Tests basic MCPO connectivity
- Validates API key authentication
- Discovers available tools
- Tests individual tool endpoints
- Basic performance testing
- Provides setup instructions for Open Web UI

**Options**:
- `--url URL`: MCPO URL (default: http://localhost:8000)
- `--api-key KEY`: API key for authentication
- `--timeout SECONDS`: Request timeout (default: 10)
- `--help`: Show help message

**Environment Variables**:
- `MCPO_URL`: MCPO URL
- `API_KEY`: API key
- `TIMEOUT`: Request timeout

### 2. Configuration Validator

#### `validate-config.py`
**Purpose**: Validate MCPO configuration files for syntax and common issues

**Installation**:
```bash
# Ensure Python 3.6+ is installed
python3 --version

# No additional dependencies required for basic validation
```

**Usage**:
```bash
# Validate single configuration file
python3 validate-config.py config/multi-server.json

# Validate with environment file
python3 validate-config.py config/production.json --env env/.env.production

# Validate all configurations
python3 validate-config.py --check-all

# Verbose output
python3 validate-config.py config/multi-server.json --verbose
```

**Features**:
- JSON syntax validation
- Configuration structure validation
- Server configuration validation
- Command and argument validation
- Environment variable checking
- Security best practice warnings
- Common MCP server validation

**Exit Codes**:
- `0`: All configurations valid
- `1`: Configuration errors found

### 3. Health Check System

#### `health-check.py`
**Purpose**: Comprehensive health monitoring for MCPO and related services

**Installation**:
```bash
# Install optional dependencies for full functionality
pip install requests psutil psycopg2-binary redis

# Or install just requests for basic functionality
pip install requests
```

**Usage**:
```bash
# Basic health check
python3 health-check.py

# Custom configuration
python3 health-check.py --config health-config.json

# JSON output
python3 health-check.py --format json

# Continuous monitoring
python3 health-check.py --continuous 30

# Exit with error code on failures
python3 health-check.py --exit-code

# Prometheus metrics format
python3 health-check.py --format prometheus
```

**Features**:
- MCPO connectivity testing
- Authentication validation
- Individual tool health checks
- Performance monitoring
- System resource monitoring
- Docker container health
- Database connectivity (PostgreSQL, Redis)
- Network connectivity to external services
- Multiple output formats (human, JSON, Prometheus)
- Continuous monitoring mode

**Configuration File Example**:
```json
{
  "mcpo_url": "http://localhost:8000",
  "api_key": "your-api-key",
  "timeout": 10,
  "performance_threshold": 2.0,
  "cpu_threshold": 80,
  "memory_threshold": 80,
  "disk_threshold": 90,
  "tools": ["memory", "time", "filesystem"],
  "docker_containers": ["mcpo", "open-webui"],
  "database": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "openwebui",
    "user": "postgres",
    "password": "your-password"
  },
  "external_services": [
    {
      "name": "external_api",
      "url": "https://api.example.com"
    }
  ],
  "enabled_checks": [
    "mcpo_connectivity",
    "mcpo_authentication",
    "mcpo_tools",
    "system_resources"
  ]
}
```

## Usage Patterns

### Development Workflow

```bash
# 1. Validate configuration before starting
python3 scripts/validate-config.py config/multi-server.json

# 2. Start MCPO (in another terminal)
uvx mcpo --config config/multi-server.json --port 8000 --api-key "dev-key"

# 3. Test connectivity
./scripts/test-connection.sh --api-key "dev-key"

# 4. Run health check
python3 scripts/health-check.py
```

### Production Monitoring

```bash
# Create health check configuration
cat > health-config.json << EOF
{
  "mcpo_url": "http://localhost:8000",
  "api_key": "${API_KEY}",
  "performance_threshold": 1.0,
  "enabled_checks": [
    "mcpo_connectivity",
    "mcpo_authentication", 
    "mcpo_tools",
    "mcpo_performance",
    "system_resources",
    "docker_health"
  ]
}
EOF

# Run continuous monitoring
python3 scripts/health-check.py --config health-config.json --continuous 60 --exit-code

# Or one-time check with Prometheus output
python3 scripts/health-check.py --config health-config.json --format prometheus > /var/lib/prometheus/mcpo_metrics.prom
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test MCPO Configuration

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Validate configurations
        run: |
          python3 scripts/validate-config.py --check-all
      
      - name: Start MCPO
        run: |
          pip install mcpo
          mcpo --config config/multi-server.json --port 8000 --api-key "test-key" &
          sleep 10
      
      - name: Test connectivity
        run: |
          export API_KEY="test-key"
          ./scripts/test-connection.sh
      
      - name: Health check
        run: |
          pip install requests
          python3 scripts/health-check.py --exit-code
```

### Docker Integration

```bash
# Test Docker setup
docker-compose up -d
sleep 30

# Test connectivity to containerized MCPO
./scripts/test-connection.sh --url http://localhost:8000 --api-key "${API_KEY}"

# Monitor Docker health
python3 scripts/health-check.py --config docker-health-config.json --continuous 30
```

## Automation Examples

### Cron Job for Regular Health Checks

```bash
# Add to crontab (crontab -e)
# Run health check every 5 minutes and log results
*/5 * * * * cd /path/to/openweb-mcp && python3 scripts/health-check.py --format json >> /var/log/mcpo-health.log 2>&1

# Daily configuration validation
0 6 * * * cd /path/to/openweb-mcp && python3 scripts/validate-config.py --check-all > /var/log/mcpo-config-check.log 2>&1
```

### Systemd Service for Continuous Monitoring

```ini
# /etc/systemd/system/mcpo-health-monitor.service
[Unit]
Description=MCPO Health Monitor
After=network.target

[Service]
Type=simple
User=mcpo
WorkingDirectory=/opt/openweb-mcp
ExecStart=/usr/bin/python3 scripts/health-check.py --config health-config.json --continuous 60
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start the service
sudo systemctl enable mcpo-health-monitor
sudo systemctl start mcpo-health-monitor

# Check status
sudo systemctl status mcpo-health-monitor
```

### Prometheus Integration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mcpo-health'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: /metrics
    scrape_interval: 30s
```

```bash
# Script to generate Prometheus metrics
#!/bin/bash
# generate-metrics.sh

cd /opt/openweb-mcp
python3 scripts/health-check.py --format prometheus > /var/lib/prometheus/textfile_collector/mcpo_health.prom.tmp
mv /var/lib/prometheus/textfile_collector/mcpo_health.prom.tmp /var/lib/prometheus/textfile_collector/mcpo_health.prom
```

### Alerting Integration

```bash
#!/bin/bash
# alert-on-failure.sh

cd /opt/openweb-mcp

# Run health check and capture exit code
python3 scripts/health-check.py --exit-code --format json > /tmp/health-result.json
exit_code=$?

if [ $exit_code -ne 0 ]; then
    # Send alert (choose your method)
    
    # Slack webhook
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"🚨 MCPO Health Check Failed"}' \
        "${SLACK_WEBHOOK_URL}"
    
    # Email alert
    mail -s "MCPO Health Check Failed" admin@example.com < /tmp/health-result.json
    
    # Discord webhook
    curl -H "Content-Type: application/json" \
        -d '{"content": "🚨 MCPO Health Check Failed"}' \
        "${DISCORD_WEBHOOK_URL}"
fi
```

## Troubleshooting Scripts

### Common Issues

#### Script Permissions
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Fix Python script permissions
chmod +x scripts/*.py
```

#### Missing Dependencies
```bash
# Install all optional dependencies
pip install requests psutil psycopg2-binary redis

# Or minimal installation
pip install requests
```

#### Connection Issues
```bash
# Test with verbose curl
curl -v -H "Authorization: Bearer your-key" http://localhost:8000/docs

# Check if port is open
netstat -tulpn | grep :8000

# Test from inside Docker network
docker-compose exec open-webui curl http://mcpo:8000/docs
```

### Debug Mode

All scripts support various debug options:

```bash
# Connection test with debug
export DEBUG=1
./scripts/test-connection.sh

# Configuration validation with verbose output
python3 scripts/validate-config.py config.json --verbose

# Health check with detailed output
python3 scripts/health-check.py --format json | jq '.'
```

## Custom Script Development

### Creating New Test Scripts

Use existing scripts as templates:

```bash
# Copy and modify existing script
cp scripts/test-connection.sh scripts/custom-test.sh

# Follow the same structure:
# 1. Configuration and defaults
# 2. Helper functions
# 3. Test functions
# 4. Main execution
# 5. Command line argument parsing
```

### Script Standards

- **Exit codes**: 0 for success, 1 for failure
- **Output format**: Clear success/failure indicators
- **Error handling**: Graceful failure with informative messages
- **Configuration**: Support environment variables and command line options
- **Documentation**: Include help text and examples

## Integration with Other Tools

### Nagios/Icinga Integration

```bash
#!/bin/bash
# /usr/local/nagios/libexec/check_mcpo

cd /opt/openweb-mcp
python3 scripts/health-check.py --exit-code --format json > /tmp/mcpo_health.json

if [ $? -eq 0 ]; then
    echo "OK - MCPO is healthy"
    exit 0
else
    echo "CRITICAL - MCPO health check failed"
    exit 2
fi
```

### Grafana Dashboard

Create dashboards using the Prometheus metrics generated by the health check script. Example queries:

```promql
# Overall health status
mcpo_health_overall

# Individual check status
mcpo_health_check{check="mcpo_connectivity"}

# Response times
mcpo_health_check_duration{check="mcpo_performance"}
```

These scripts provide comprehensive testing and monitoring capabilities for your MCPO setup, helping ensure reliable operation in both development and production environments.