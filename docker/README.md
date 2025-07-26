# Docker Configurations

This directory contains Docker Compose configurations for different deployment scenarios.

## Available Configurations

### 1. Basic Setup (`docker-compose.yml`)
**Use case**: Simple development setup with separate MCPO instances

```bash
docker-compose up -d
```

**Services**:
- `mcpo` - Time server on port 8000
- `mcpo-memory` - Memory server on port 8001

**Access**:
- Time server: `http://localhost:8000`
- Memory server: `http://localhost:8001`
- OpenAPI docs: `http://localhost:8000/docs`, `http://localhost:8001/docs`

### 2. Production Setup (`docker-compose.prod.yml`)
**Use case**: Production deployment with security features

```bash
# Set required environment variables
export API_KEY="your-secure-api-key"
export REDIS_PASSWORD="secure-redis-password"

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

**Services**:
- `mcpo` - Multi-server configuration with volume mounts
- `redis` - Session storage
- `nginx` - HTTPS reverse proxy

**Features**:
- Configuration file based setup
- Volume mounts for persistence
- Health checks
- Resource limits
- HTTPS termination
- Rate limiting

### 3. Full Stack (`docker-compose.full.yml`)
**Use case**: Complete Open Web UI + MCPO + Ollama setup

```bash
# Set environment variables
export WEBUI_SECRET_KEY="your-webui-secret"
export MCPO_API_KEY="your-mcpo-key"
export POSTGRES_PASSWORD="secure-db-password"
export REDIS_PASSWORD="secure-redis-password"

# Start all services
docker-compose -f docker-compose.full.yml up -d
```

**Services**:
- `open-webui` - Web interface on port 3000
- `ollama` - LLM inference on port 11434
- `mcpo` - MCP proxy on port 8000
- `postgres` - Database storage
- `redis` - Caching and sessions

**Access**:
- Open Web UI: `http://localhost:3000`
- MCPO Tools: `http://localhost:8000`
- Ollama API: `http://localhost:11434`

## Environment Variables

### Required Variables

Create a `.env` file in the docker directory:

```bash
# Basic configuration
API_KEY=your-secure-mcpo-api-key
WEBUI_SECRET_KEY=your-webui-secret-key
MCPO_API_KEY=your-mcpo-api-key

# Database passwords
POSTGRES_PASSWORD=secure-database-password
REDIS_PASSWORD=secure-redis-password

# Optional settings
TIMEZONE=America/New_York
MCPO_PORT=8000
```

### Optional Variables

```bash
# Database configuration
POSTGRES_DB=openwebui
POSTGRES_USER=postgres

# Docker image tags
OPEN_WEBUI_TAG=main
OLLAMA_TAG=latest
MCPO_TAG=main

# Resource limits
MCPO_MEMORY_LIMIT=512M
MCPO_CPU_LIMIT=0.5
```

## SSL/HTTPS Setup

### Self-Signed Certificates (Development)
```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

### Let's Encrypt (Production)
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
```

## GPU Support

### NVIDIA GPU Setup
1. Install NVIDIA Docker runtime:
```bash
# Ubuntu/Debian
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

2. Uncomment GPU sections in docker-compose files:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

## Usage Instructions

### Starting Services

#### Development
```bash
# Basic setup
docker-compose up -d

# View logs
docker-compose logs -f mcpo

# Stop services
docker-compose down
```

#### Production
```bash
# Create required directories
mkdir -p ssl logs

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Check health
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs mcpo
```

#### Full Stack
```bash
# Pull required models (optional)
docker-compose -f docker-compose.full.yml exec ollama ollama pull llama2

# Start full stack
docker-compose -f docker-compose.full.yml up -d

# Check all services
docker-compose -f docker-compose.full.yml ps
```

### Configuring Open Web UI

1. **Access Open Web UI**: http://localhost:3000
2. **Go to Settings** → External Tools
3. **Add MCP Tools**:
   - Memory: `http://mcpo:8000/memory` (internal) or `http://localhost:8000/memory` (external)
   - Time: `http://mcpo:8000/time`
   - Filesystem: `http://mcpo:8000/filesystem`
4. **Set API Key**: Use the value from `MCPO_API_KEY`
5. **Test Connection**: Verify each tool works

### Updating Services

```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose up -d --force-recreate

# Clean up old images
docker image prune -f
```

## Monitoring and Logs

### Health Checks
```bash
# Check service health
docker-compose ps

# Detailed health status
docker inspect mcpo-proxy --format='{{.State.Health.Status}}'
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mcpo

# Last N lines
docker-compose logs --tail=100 mcpo

# Follow logs with timestamps
docker-compose logs -f -t
```

### Resource Monitoring
```bash
# Resource usage
docker stats

# Disk usage
docker system df

# Network information
docker network ls
docker network inspect open-webui-network
```

## Backup and Restore

### Creating Backups
```bash
# Stop services
docker-compose down

# Backup volumes
docker run --rm -v mcpo-data:/data -v $(pwd):/backup ubuntu tar czf /backup/mcpo-backup.tar.gz -C /data .
docker run --rm -v open-webui-data:/data -v $(pwd):/backup ubuntu tar czf /backup/webui-backup.tar.gz -C /data .

# Backup database
docker-compose exec postgres pg_dump -U postgres openwebui > backup/database.sql
```

### Restoring Backups
```bash
# Stop services
docker-compose down

# Restore volumes
docker run --rm -v mcpo-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/mcpo-backup.tar.gz -C /data
docker run --rm -v open-webui-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/webui-backup.tar.gz -C /data

# Restore database
docker-compose up -d postgres
docker-compose exec -T postgres psql -U postgres openwebui < backup/database.sql

# Start all services
docker-compose up -d
```

## Troubleshooting

### Common Issues

**Port conflicts**
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8000

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Changed from 8000:8000
```

**Permission errors**
```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./config
sudo chmod -R 755 ./config
```

**SSL certificate issues**
```bash
# Verify certificate
openssl x509 -in ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect localhost:443
```

**Memory/CPU limits**
```bash
# Check container resources
docker stats mcpo-proxy

# Adjust limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
```

### Debug Mode

Enable debug logging:
```yaml
# In docker-compose.yml
command: >
  mcpo --host 0.0.0.0 --port 8000 --log-level debug
  --api-key "${API_KEY}" --config /app/config.json
```

### Network Issues

Check container networking:
```bash
# List networks
docker network ls

# Inspect network
docker network inspect open-webui-network

# Test connectivity
docker-compose exec open-webui ping mcpo
docker-compose exec mcpo curl http://localhost:8000/docs
```

## Security Considerations

### Production Checklist
- [ ] Change all default passwords
- [ ] Use strong API keys
- [ ] Enable HTTPS with valid certificates
- [ ] Configure rate limiting
- [ ] Set up proper firewall rules
- [ ] Enable container security scanning
- [ ] Use non-root users in containers
- [ ] Regularly update images
- [ ] Monitor logs for security issues
- [ ] Backup data regularly

### Network Security
```bash
# Restrict external access
iptables -A INPUT -p tcp --dport 8000 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP
```

### Container Security
```yaml
# Add security options
security_opt:
  - no-new-privileges:true
read_only: true
user: "1000:1000"
```