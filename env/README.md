# Environment Configuration

This directory contains environment configuration files for different deployment scenarios.

## Available Environment Files

### 1. `.env.example`
**Use case**: Template file with all available options

Contains comprehensive documentation of all environment variables with default values and examples.

**Usage**:
```bash
# Copy and customize
cp env/.env.example .env
# Edit .env with your values
```

### 2. `.env.development`
**Use case**: Local development setup

Pre-configured with developer-friendly defaults including verbose logging, relaxed security, and local service URLs.

**Features**:
- Debug logging enabled
- Relaxed rate limiting
- Local service URLs
- Hot reloading enabled
- Mock external services

**Usage**:
```bash
# Copy for development
cp env/.env.development .env

# Or use directly
mcpo --env-path env/.env.development --config config/multi-server.json
```

### 3. `.env.production`
**Use case**: Production deployment

Security-hardened configuration with production-ready defaults and placeholder values for sensitive information.

**Features**:
- Secure defaults
- Production logging
- Strict rate limiting
- Monitoring enabled
- Resource limits configured

**Usage**:
```bash
# Copy and secure
cp env/.env.production .env
# Replace all REPLACE_WITH_* values
# Review and adjust all settings
```

## Environment Variable Categories

### Basic Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | MCPO authentication key | `demo-secret-key` |
| `MCPO_PORT` | Proxy server port | `8000` |
| `MCPO_HOST` | Host binding | `0.0.0.0` |
| `LOG_LEVEL` | Logging verbosity | `info` |

### MCP Server Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `TIMEZONE` | Time server timezone | `America/New_York` |
| `MEMORY_STORAGE_PATH` | Memory server data path | `./data/memory` |
| `FILESYSTEM_ALLOWED_DIRS` | Allowed filesystem directories | `./sandbox` |
| `MAX_FILE_SIZE` | Maximum file size (bytes) | `52428800` |

### External Services
| Variable | Description | Default |
|----------|-------------|---------|
| `EXTERNAL_SSE_URL` | SSE service endpoint | - |
| `EXTERNAL_SSE_TOKEN` | SSE authentication token | - |
| `EXTERNAL_HTTP_URL` | HTTP service endpoint | - |
| `EXTERNAL_HTTP_KEY` | HTTP service API key | - |

### Database Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `openwebui` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | - |
| `REDIS_PASSWORD` | Redis authentication | - |

### Security Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET` | JWT signing key | - |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `RATE_LIMIT_REQUESTS` | Requests per window | `100` |
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | `60` |

## Usage Patterns

### Command Line Usage
```bash
# Use specific environment file
mcpo --env-path env/.env.development --config config.json

# Multiple environment files (later files override earlier ones)
mcpo --env-path env/.env.example --env-path env/.env.local --config config.json
```

### Docker Compose Usage
```yaml
services:
  mcpo:
    image: ghcr.io/open-webui/mcpo:main
    env_file:
      - env/.env.production
    # Or inline environment
    environment:
      - API_KEY=${API_KEY}
      - MCPO_PORT=${MCPO_PORT}
```

### Shell Export
```bash
# Export for shell usage
export $(cat env/.env.development | xargs)

# Then use normally
mcpo --config config.json
```

## Environment File Precedence

Environment variables are loaded in this order (later sources override earlier ones):

1. **System environment variables**
2. **--env-path file** (in order specified)
3. **Command line arguments** (highest priority)

Example:
```bash
# System has API_KEY=system-key
# .env file has API_KEY=file-key
# Command line has --api-key cli-key

# Result: API_KEY=cli-key (command line wins)
mcpo --env-path .env --api-key cli-key
```

## Security Best Practices

### Secret Management

#### Development
```bash
# Use simple keys for development
API_KEY=dev-key-123
JWT_SECRET=dev-jwt-secret
```

#### Production
```bash
# Generate secure keys
API_KEY=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
WEBUI_SECRET_KEY=$(openssl rand -base64 32)
```

#### Using Secret Management Services
```bash
# AWS Secrets Manager
API_KEY=$(aws secretsmanager get-secret-value --secret-id mcpo/api-key --query SecretString --output text)

# Kubernetes Secrets
# Mount as volume and read from file
API_KEY=$(cat /var/secrets/api-key)

# HashiCorp Vault
API_KEY=$(vault kv get -field=api_key secret/mcpo)
```

### File Permissions
```bash
# Secure environment files
chmod 600 .env*
chown $USER:$USER .env*

# Never commit sensitive files
echo '.env' >> .gitignore
echo '.env.local' >> .gitignore
echo '.env.production' >> .gitignore
```

## Environment Validation

### Required Variables Check
```bash
# Script to validate required variables
#!/bin/bash
required_vars=("API_KEY" "WEBUI_SECRET_KEY" "POSTGRES_PASSWORD")

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo "Error: $var is not set"
        exit 1
    fi
done

echo "All required variables are set"
```

### Using the Validation Script
```bash
# Make script executable
chmod +x scripts/validate-env.sh

# Run validation
source .env && ./scripts/validate-env.sh
```

## Dynamic Configuration

### Runtime Environment Detection
```bash
# Auto-select environment file based on NODE_ENV
if [[ "$NODE_ENV" == "production" ]]; then
    ENV_FILE="env/.env.production"
elif [[ "$NODE_ENV" == "development" ]]; then
    ENV_FILE="env/.env.development"
else
    ENV_FILE=".env"
fi

mcpo --env-path "$ENV_FILE" --config config.json
```

### Feature Flags
```bash
# Enable features based on environment
ENABLE_DEBUG_ENDPOINTS=${NODE_ENV:-development}
ENABLE_METRICS=${METRICS_ENABLED:-true}
ENABLE_AUTH=${SECURITY_ENABLED:-true}
```

## Troubleshooting

### Environment Loading Issues

**Variables not loaded**
```bash
# Check file exists and is readable
ls -la env/.env.development
cat env/.env.development

# Check for syntax errors
grep -n '=' env/.env.development | grep -v '^[[:space:]]*#'
```

**Permission denied**
```bash
# Fix file permissions
chmod 644 env/.env.development

# Check owner
ls -la env/.env.development
```

**Variable substitution not working**
```bash
# Check for missing variables
grep '\${' env/.env.development

# Set missing variables
export MISSING_VAR=value
```

### Docker Environment Issues

**Environment file not found**
```yaml
# Use absolute path or relative to docker-compose.yml
env_file:
  - ./env/.env.production
```

**Variables not interpolated**
```bash
# Export variables before running docker-compose
export API_KEY=your-key
docker-compose up -d

# Or use .env file in same directory as docker-compose.yml
```

### Common Validation Errors

**Invalid characters in values**
```bash
# Quote values with special characters
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
```

**Multiline values**
```bash
# Use quotes for multiline values
PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----"
```

## Creating Custom Environment Files

### Template Structure
```bash
# Header with description
# CUSTOM ENVIRONMENT - Description here

# Group related variables
# ============================================================================
# SECTION NAME
# ============================================================================

# Document each variable
# Variable description and usage notes
VARIABLE_NAME=default_value

# End with usage instructions
# Usage: mcpo --env-path path/to/this/file --config config.json
```

### Best Practices
1. **Group related variables** with clear section headers
2. **Document each variable** with comments
3. **Provide examples** for complex values
4. **Use descriptive names** that indicate purpose
5. **Set safe defaults** for development
6. **Mark required variables** that need user input
7. **Include usage instructions** at the top or bottom

### Testing Custom Environments
```bash
# Validate syntax
bash -n env/.env.custom

# Test loading
mcpo --env-path env/.env.custom --help

# Dry run configuration
mcpo --env-path env/.env.custom --config config.json --help
```