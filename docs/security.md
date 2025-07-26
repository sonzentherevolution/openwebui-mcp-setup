# Security Guide

This guide covers security best practices for deploying MCP servers with Open Web UI using MCPO in production environments.

## Security Architecture Overview

```
Internet → Reverse Proxy → Open Web UI → MCPO → MCP Servers
   ↓            ↓            ↓         ↓         ↓
SSL/TLS    Rate Limiting   Auth    API Keys   Sandboxing
Firewall   Headers       Tokens   Network   File Access
WAF        Logging       Session  Isolation  Permissions
```

## Authentication and Authorization

### API Key Management

#### Generating Secure API Keys

```bash
# Generate cryptographically secure API keys
openssl rand -base64 32

# Generate multiple environment-specific keys
echo "Development: $(openssl rand -base64 32)"
echo "Staging: $(openssl rand -base64 32)"
echo "Production: $(openssl rand -base64 32)"

# Using UUID format
python3 -c "import uuid; print(str(uuid.uuid4()))"

# Using custom format with date
echo "mcpo-$(date +%Y%m%d)-$(openssl rand -hex 16)"
```

#### Key Storage Best Practices

**Environment Variables (Recommended)**:
```bash
# .env file with restricted permissions
echo "API_KEY=$(openssl rand -base64 32)" > .env
chmod 600 .env
chown $USER:$USER .env

# Never commit to version control
echo '.env*' >> .gitignore
```

**External Secret Management**:
```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name "mcpo/api-key" \
  --secret-string "$(openssl rand -base64 32)"

# Retrieve in application
API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id mcpo/api-key --query SecretString --output text)

# Kubernetes Secrets
kubectl create secret generic mcpo-secrets \
  --from-literal=api-key="$(openssl rand -base64 32)"

# Docker Secrets
echo "$(openssl rand -base64 32)" | docker secret create mcpo_api_key -
```

**HashiCorp Vault**:
```bash
# Store secret
vault kv put secret/mcpo api_key="$(openssl rand -base64 32)"

# Retrieve secret
API_KEY=$(vault kv get -field=api_key secret/mcpo)
```

#### Key Rotation Strategy

```bash
#!/bin/bash
# rotate-api-keys.sh

set -e

# Generate new key
NEW_KEY=$(openssl rand -base64 32)
BACKUP_KEY="$API_KEY"

echo "Rotating API keys..."

# Step 1: Update MCPO with new key
export API_KEY="$NEW_KEY"
docker-compose restart mcpo

# Step 2: Test new key works
if curl -H "Authorization: Bearer $NEW_KEY" http://localhost:8000/docs > /dev/null; then
    echo "✓ New API key is working"
else
    echo "✗ New API key failed, rolling back"
    export API_KEY="$BACKUP_KEY"
    docker-compose restart mcpo
    exit 1
fi

# Step 3: Update Open Web UI (manual step)
echo "Please update Open Web UI with new API key: $NEW_KEY"

# Step 4: Update stored secrets
echo "API_KEY=$NEW_KEY" > .env.new
mv .env.new .env

echo "API key rotation completed successfully"
```

### JWT Token Security

For advanced authentication scenarios:

```yaml
# docker-compose.yml
services:
  mcpo:
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - JWT_EXPIRY=3600  # 1 hour
      - JWT_ALGORITHM=HS256
```

```bash
# Generate JWT secret
JWT_SECRET=$(openssl rand -base64 32)

# Token with expiration
python3 -c "
import jwt
import datetime
payload = {
    'sub': 'open-webui',
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}
token = jwt.encode(payload, '$JWT_SECRET', algorithm='HS256')
print(token)
"
```

## Network Security

### Firewall Configuration

#### iptables Rules

```bash
#!/bin/bash
# firewall-setup.sh

# Flush existing rules
iptables -F

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (change port as needed)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS (reverse proxy)
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Block direct access to MCPO (only allow from reverse proxy)
iptables -A INPUT -p tcp --dport 8000 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP

# Block direct access to databases
iptables -A INPUT -p tcp --dport 5432 -s 127.0.0.1 -j ACCEPT  # PostgreSQL
iptables -A INPUT -p tcp --dport 6379 -s 127.0.0.1 -j ACCEPT  # Redis
iptables -A INPUT -p tcp --dport 5432 -j DROP
iptables -A INPUT -p tcp --dport 6379 -j DROP

# Save rules
iptables-save > /etc/iptables/rules.v4
```

#### UFW (Ubuntu Firewall)

```bash
# Enable UFW
sudo ufw enable

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow reverse proxy
sudo ufw allow 80
sudo ufw allow 443

# Deny direct access to services
sudo ufw deny 8000  # MCPO
sudo ufw deny 5432  # PostgreSQL
sudo ufw deny 6379  # Redis

# Allow specific IPs to management ports (if needed)
sudo ufw allow from 10.0.0.0/8 to any port 8000
```

### Network Segmentation

#### Docker Networks

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Public-facing services
  nginx:
    networks:
      - public
      - internal
  
  open-webui:
    networks:
      - internal
      - backend
  
  # Internal services
  mcpo:
    networks:
      - backend
      - database
  
  # Database services
  postgres:
    networks:
      - database
  
  redis:
    networks:
      - database

networks:
  public:
    driver: bridge
  internal:
    driver: bridge
    internal: true  # No external access
  backend:
    driver: bridge
    internal: true
  database:
    driver: bridge
    internal: true
```

#### VPN Access

```bash
# WireGuard configuration for admin access
[Interface]
PrivateKey = <admin-private-key>
Address = 10.0.0.2/24

[Peer]
PublicKey = <server-public-key>
Endpoint = server.example.com:51820
AllowedIPs = 10.0.0.0/24

# Allow VPN access to management ports
sudo ufw allow in on wg0 to any port 8000
```

## HTTPS and TLS

### SSL Certificate Management

#### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d mcpo.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet

# Copy certificates for Docker
sudo cp /etc/letsencrypt/live/mcpo.yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/mcpo.yourdomain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*.pem
```

#### Self-Signed Certificates (Development)

```bash
#!/bin/bash
# generate-ssl.sh

mkdir -p ssl

# Generate CA private key
openssl genrsa -out ssl/ca-key.pem 4096

# Generate CA certificate
openssl req -new -x509 -days 365 -key ssl/ca-key.pem -sha256 -out ssl/ca.pem -subj "/C=US/ST=CA/L=San Francisco/O=MyOrg/CN=MyCA"

# Generate server private key
openssl genrsa -out ssl/key.pem 4096

# Generate certificate signing request
openssl req -subj "/CN=localhost" -sha256 -new -key ssl/key.pem -out ssl/server.csr

# Generate server certificate
echo "subjectAltName = DNS:localhost,IP:127.0.0.1,IP:0.0.0.0" > ssl/extfile.cnf
openssl x509 -req -days 365 -in ssl/server.csr -CA ssl/ca.pem -CAkey ssl/ca-key.pem -out ssl/cert.pem -extfile ssl/extfile.cnf -CAcreateserial

# Clean up
rm ssl/server.csr ssl/extfile.cnf

# Set permissions
chmod 400 ssl/key.pem ssl/ca-key.pem
chmod 444 ssl/cert.pem ssl/ca.pem

echo "SSL certificates generated in ssl/ directory"
```

### Nginx SSL Configuration

```nginx
# nginx-ssl.conf
server {
    listen 443 ssl http2;
    server_name mcpo.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /ssl/cert.pem;
    ssl_certificate_key /ssl/key.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    
    # Proxy to MCPO
    location / {
        proxy_pass http://mcpo:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Security
        proxy_hide_header X-Powered-By;
        proxy_hide_header Server;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name mcpo.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Input Validation and Sanitization

### MCP Server Security

#### Filesystem Server Restrictions

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y", 
        "@modelcontextprotocol/server-filesystem",
        "--allowed-directories", "/app/safe-data,/app/uploads",
        "--denied-patterns", "*.exe,*.bat,*.cmd,*.sh",
        "--max-file-size", "10485760",
        "--max-files", "100"
      ],
      "env": {
        "NODE_ENV": "production",
        "SAFE_MODE": "true"
      }
    }
  }
}
```

#### Memory Server Data Validation

```bash
# Environment variables for memory server security
export MEMORY_MAX_KEY_LENGTH=256
export MEMORY_MAX_VALUE_LENGTH=10240
export MEMORY_MAX_ENTRIES=1000
export MEMORY_SANITIZE_HTML=true
```

#### Custom Validation Middleware

```python
# validation_middleware.py
import re
import html

def sanitize_input(data):
    """Sanitize user input to prevent injection attacks"""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        data = re.sub(r'[<>"\']', '', data)
        # HTML encode
        data = html.escape(data)
        # Limit length
        data = data[:1000]
    return data

def validate_file_path(path):
    """Validate file paths to prevent directory traversal"""
    # Normalize path
    path = os.path.normpath(path)
    
    # Check for directory traversal
    if '..' in path or path.startswith('/'):
        raise ValueError("Invalid path")
    
    # Check allowed extensions
    allowed_extensions = {'.txt', '.json', '.csv', '.md'}
    if not any(path.endswith(ext) for ext in allowed_extensions):
        raise ValueError("File type not allowed")
    
    return path
```

### Rate Limiting

#### Nginx Rate Limiting

```nginx
# Rate limiting configuration
http {
    # Define rate limit zones
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=1r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;
    
    server {
        # General rate limiting
        limit_req zone=general burst=20 nodelay;
        
        # Strict rate limiting for auth endpoints
        location /auth {
            limit_req zone=auth burst=5 nodelay;
            proxy_pass http://mcpo:8000;
        }
        
        # API rate limiting
        location /api {
            limit_req zone=api burst=50 nodelay;
            proxy_pass http://mcpo:8000;
        }
    }
}
```

#### Application-Level Rate Limiting

```python
# rate_limiter.py
from functools import wraps
from time import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, max_requests=100, window=3600):
        self.max_requests = max_requests
        self.window = window
        self.clients = defaultdict(deque)
    
    def is_allowed(self, client_ip):
        now = time()
        
        # Clean old requests
        while (self.clients[client_ip] and 
               self.clients[client_ip][0] < now - self.window):
            self.clients[client_ip].popleft()
        
        # Check if limit exceeded
        if len(self.clients[client_ip]) >= self.max_requests:
            return False
        
        # Add current request
        self.clients[client_ip].append(now)
        return True

# Usage in MCPO
rate_limiter = RateLimiter(max_requests=100, window=3600)

def rate_limit_middleware(client_ip):
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

## Container Security

### Docker Security Best Practices

#### Secure Dockerfile

```dockerfile
# Use specific version, not latest
FROM python:3.11.5-slim

# Create non-root user
RUN groupadd -r mcpo && useradd -r -g mcpo mcpo

# Set working directory
WORKDIR /app

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY --chown=mcpo:mcpo . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Remove unnecessary packages
RUN apt-get remove -y --purge curl && apt-get autoremove -y

# Set security options
USER mcpo
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

CMD ["mcpo", "--host", "0.0.0.0", "--port", "8000"]
```

#### Secure Docker Compose

```yaml
version: '3.8'

services:
  mcpo:
    image: ghcr.io/open-webui/mcpo:main
    
    # Security options
    security_opt:
      - no-new-privileges:true
    read_only: true
    user: "1000:1000"
    
    # Capabilities
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only if binding to port < 1024
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    
    # Tmpfs for writable directories
    tmpfs:
      - /tmp:noexec,nosuid,size=128m
      - /var/tmp:noexec,nosuid,size=64m
    
    # Environment
    environment:
      - NODE_ENV=production
    
    # Restart policy
    restart: unless-stopped
    
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Container Scanning

#### Trivy Security Scanning

```bash
# Install Trivy
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update && sudo apt-get install trivy

# Scan container image
trivy image ghcr.io/open-webui/mcpo:main

# Scan for critical vulnerabilities only
trivy image --severity CRITICAL,HIGH ghcr.io/open-webui/mcpo:main

# Scan filesystem
trivy fs .

# Generate report
trivy image --format json --output results.json ghcr.io/open-webui/mcpo:main
```

#### Automated Security Scanning

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'ghcr.io/open-webui/mcpo:main'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

## Monitoring and Logging

### Security Event Logging

#### Structured Logging Configuration

```yaml
# docker-compose.yml
services:
  mcpo:
    environment:
      - LOG_LEVEL=info
      - LOG_FORMAT=json
      - SECURITY_LOG_FILE=/app/logs/security.log
    volumes:
      - ./logs:/app/logs
```

#### Log Forwarding to SIEM

```yaml
# Fluent Bit configuration
services:
  fluent-bit:
    image: fluent/fluent-bit:latest
    volumes:
      - ./logs:/var/log
      - ./fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf
    depends_on:
      - mcpo
```

```ini
# fluent-bit.conf
[INPUT]
    Name tail
    Path /var/log/*.log
    Parser json
    Tag mcpo.*

[FILTER]
    Name grep
    Match mcpo.*
    Regex message (ERROR|WARN|auth|security)

[OUTPUT]
    Name forward
    Match mcpo.*
    Host siem-server.example.com
    Port 24224
```

### Intrusion Detection

#### Fail2Ban Configuration

```ini
# /etc/fail2ban/jail.d/mcpo.conf
[mcpo]
enabled = true
port = 8000
filter = mcpo
logpath = /var/log/mcpo/access.log
maxretry = 5
bantime = 3600
findtime = 600
action = iptables-allports[name=mcpo, protocol=tcp]
```

```ini
# /etc/fail2ban/filter.d/mcpo.conf
[Definition]
failregex = ^<HOST> .* "GET .* HTTP/.*" (401|403|429) .*$
            ^<HOST> .* "POST .* HTTP/.*" (401|403|429) .*$
ignoreregex =
```

#### OSSEC Integration

```xml
<!-- /var/ossec/etc/ossec.conf -->
<ossec_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/mcpo/security.log</location>
  </localfile>
  
  <rules>
    <include>mcpo_rules.xml</include>
  </rules>
</ossec_config>
```

### Audit Logging

#### API Access Logging

```python
# audit_logger.py
import json
import time
from datetime import datetime

class SecurityAuditLogger:
    def __init__(self, log_file='/app/logs/audit.log'):
        self.log_file = log_file
    
    def log_event(self, event_type, user_id, resource, action, result, details=None):
        audit_event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'result': result,
            'details': details or {},
            'session_id': getattr(request, 'session_id', None),
            'client_ip': getattr(request, 'client_ip', None),
            'user_agent': getattr(request, 'user_agent', None)
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(audit_event) + '\n')

# Usage
audit_logger = SecurityAuditLogger()

def log_api_access(user_id, endpoint, method, status_code):
    result = 'success' if status_code < 400 else 'failure'
    audit_logger.log_event(
        event_type='api_access',
        user_id=user_id,
        resource=endpoint,
        action=method,
        result=result,
        details={'status_code': status_code}
    )
```

## Backup and Recovery Security

### Encrypted Backups

```bash
#!/bin/bash
# secure-backup.sh

set -e

BACKUP_DIR="/secure/backups"
ENCRYPTION_KEY="$BACKUP_ENCRYPTION_KEY"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
pg_dump -h postgres -U postgres openwebui | \
    gpg --cipher-algo AES256 --compress-algo 1 --s2k-mode 3 \
        --s2k-digest-algo SHA512 --s2k-count 65536 --force-mdc \
        --quiet --no-greeting --batch --yes \
        --passphrase "$ENCRYPTION_KEY" \
        --symmetric --output "$BACKUP_DIR/db_$DATE.sql.gpg"

# Backup configuration files
tar -czf - config/ env/ docker/ | \
    gpg --cipher-algo AES256 --compress-algo 1 --s2k-mode 3 \
        --s2k-digest-algo SHA512 --s2k-count 65536 --force-mdc \
        --quiet --no-greeting --batch --yes \
        --passphrase "$ENCRYPTION_KEY" \
        --symmetric --output "$BACKUP_DIR/config_$DATE.tar.gz.gpg"

# Remove old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.gpg" -mtime +30 -delete

echo "Secure backup completed: $DATE"
```

### Backup Verification

```bash
#!/bin/bash
# verify-backup.sh

BACKUP_FILE="$1"
ENCRYPTION_KEY="$BACKUP_ENCRYPTION_KEY"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Verify GPG integrity
if gpg --quiet --batch --yes --passphrase "$ENCRYPTION_KEY" \
       --decrypt "$BACKUP_FILE" > /dev/null 2>&1; then
    echo "✓ Backup integrity verified: $BACKUP_FILE"
else
    echo "✗ Backup integrity check failed: $BACKUP_FILE"
    exit 1
fi
```

## Compliance and Privacy

### Data Protection

#### GDPR Compliance

```python
# gdpr_compliance.py
class GDPRCompliance:
    def __init__(self):
        self.personal_data_fields = {
            'user_id', 'email', 'ip_address', 'session_id'
        }
    
    def anonymize_logs(self, log_entry):
        """Anonymize personal data in logs"""
        import hashlib
        
        for field in self.personal_data_fields:
            if field in log_entry:
                # Replace with hash
                original = log_entry[field]
                anonymized = hashlib.sha256(original.encode()).hexdigest()[:16]
                log_entry[field] = f"anon_{anonymized}"
        
        return log_entry
    
    def data_retention_cleanup(self, retention_days=365):
        """Clean up old data per retention policy"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Clean logs
        # Clean session data
        # Clean temporary files
        pass
```

#### Data Encryption at Rest

```yaml
# docker-compose.yml with encrypted volumes
services:
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=scram-sha-256
    volumes:
      - encrypted-db:/var/lib/postgresql/data

volumes:
  encrypted-db:
    driver: local
    driver_opts:
      type: "tmpfs"
      device: "tmpfs"
      o: "size=1g,uid=999,gid=999,mode=0700"
```

### Compliance Monitoring

```bash
#!/bin/bash
# compliance-check.sh

echo "=== Security Compliance Check ==="

# Check SSL configuration
echo "Checking SSL configuration..."
if openssl s_client -connect localhost:443 -brief 2>/dev/null | grep -q "Verification: OK"; then
    echo "✓ SSL certificate valid"
else
    echo "✗ SSL certificate issues"
fi

# Check for security headers
echo "Checking security headers..."
headers=$(curl -I -s https://localhost:443)
if echo "$headers" | grep -q "Strict-Transport-Security"; then
    echo "✓ HSTS header present"
else
    echo "✗ Missing HSTS header"
fi

# Check file permissions
echo "Checking file permissions..."
if [ "$(stat -c %a .env)" = "600" ]; then
    echo "✓ Environment file permissions correct"
else
    echo "✗ Environment file permissions too permissive"
fi

# Check for default passwords
echo "Checking for default passwords..."
if grep -q "changeme\|password123\|admin" .env 2>/dev/null; then
    echo "✗ Default passwords detected"
else
    echo "✓ No default passwords found"
fi

echo "=== Compliance Check Complete ==="
```

This security guide provides comprehensive protection for your MCPO deployment. Regularly review and update security measures as threats evolve and new vulnerabilities are discovered.