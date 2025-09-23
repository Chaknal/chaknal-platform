# 🚀 Chaknal Platform Production Deployment Guide

This guide provides comprehensive instructions for deploying the Chaknal Platform with DuxSoup integration to production.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [DuxSoup Configuration](#duxsoup-configuration)
5. [Deployment Options](#deployment-options)
6. [Monitoring & Logging](#monitoring--logging)
7. [Security Configuration](#security-configuration)
8. [Performance Optimization](#performance-optimization)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 12+
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ minimum, 16GB+ recommended
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection for DuxSoup API

### Software Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: Latest version
- **Python**: 3.9+ (for local development)

### DuxSoup Requirements
- **Account**: Active DuxSoup Turbo or Cloud subscription
- **API Access**: Enabled in DuxSoup dashboard
- **Credentials**: User ID and API key ready

## 🌍 Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/chaknal-platform.git
cd chaknal-platform
```

### 2. Configure Environment Variables
```bash
# Copy production environment template
cp env.production .env

# Edit with your production values
nano .env
```

**Critical Variables to Update:**
```bash
# Database
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=chaknal_prod

# JWT Security
JWT_SECRET_KEY=your_very_long_random_secret_key_here
SECRET_KEY=another_very_long_random_secret_key_here

# DuxSoup API
DUXSOUP_API_BASE_URL=https://app.dux-soup.com/xapi/remote/control

# Domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 3. Create Required Directories
```bash
mkdir -p logs uploads ssl monitoring/grafana monitoring/prometheus nginx
```

## 🗄️ Database Setup

### Option 1: Docker PostgreSQL (Recommended for Development)
```bash
# Start PostgreSQL container
docker run -d \
  --name chaknal-postgres \
  --network chaknal-network \
  -e POSTGRES_DB=chaknal_prod \
  -e POSTGRES_USER=chaknal_user \
  -e POSTGRES_PASSWORD=your_password \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15-alpine
```

### Option 2: External PostgreSQL Server
1. Install PostgreSQL on your server
2. Create database and user
3. Update `.env` with external connection details

### Run Database Migrations
```bash
# Using Docker
docker run --rm \
  --network chaknal-network \
  --env-file .env \
  chaknal-platform:latest \
  python -m alembic upgrade head

# Or locally
python -m alembic upgrade head
```

## 🔑 DuxSoup Configuration

### 1. Verify API Credentials
```bash
# Test your DuxSoup credentials
python3 test_real_duxwrap_standalone.py
```

### 2. Configure DuxSoup Users in Database
```sql
INSERT INTO duxsoup_users (
    dux_soup_user_id,
    dux_soup_auth_key,
    first_name,
    last_name,
    daily_invite_limit,
    daily_message_limit,
    daily_visit_limit,
    auto_connect,
    auto_message
) VALUES (
    '117833704731893145427',
    'e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR',
    'Your',
    'Name',
    100,
    50,
    200,
    true,
    true
);
```

### 3. Test Integration
```bash
# Test the full automation service
python3 -c "
import asyncio
from app.services.linkedin_automation_v2 import linkedin_automation_service_v2
from database.database import get_db

async def test():
    async for db in get_db():
        result = await linkedin_automation_service_v2.get_queue_status('117833704731893145427', db)
        print('Queue Status:', result)
        break

asyncio.run(test())
"
```

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended)
```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f app
```

### Option 2: Manual Docker Deployment
```bash
# Build image
docker build -t chaknal-platform:latest .

# Run container
docker run -d \
  --name chaknal-platform-prod \
  --network chaknal-network \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/uploads:/app/uploads \
  chaknal-platform:latest
```

### Option 3: Production Script
```bash
# Make script executable
chmod +x deploy-production.sh

# Run deployment
./deploy-production.sh
```

## 📊 Monitoring & Logging

### 1. Application Logs
```bash
# View application logs
docker logs -f chaknal-platform-prod

# View log files
tail -f logs/chaknal-platform.log
tail -f logs/chaknal-platform-error.log
```

### 2. Prometheus Metrics
- **URL**: http://yourdomain.com:9090
- **Targets**: Application metrics, database metrics, system metrics

### 3. Grafana Dashboards
- **URL**: http://yourdomain.com:3000
- **Default**: admin/admin
- **Dashboards**: Pre-configured for Chaknal Platform

### 4. ELK Stack
- **Elasticsearch**: http://yourdomain.com:9200
- **Kibana**: http://yourdomain.com:5601

## 🔒 Security Configuration

### 1. SSL/TLS Setup
```bash
# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Or use Let's Encrypt for production
certbot certonly --standalone -d yourdomain.com
```

### 2. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # App (if exposed)
sudo ufw enable
```

### 3. Environment Security
```bash
# Set secure file permissions
chmod 600 .env
chmod 600 ssl/*.pem
chmod 755 logs uploads
```

## ⚡ Performance Optimization

### 1. Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_campaign_contacts_campaign_id ON campaign_contacts(campaign_id);
CREATE INDEX idx_messages_campaign_id ON messages(campaign_id);
CREATE INDEX idx_campaign_contacts_status ON campaign_contacts(status);
```

### 2. Application Tuning
```bash
# Update .env with performance settings
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000
DB_POOL_SIZE=20
CACHE_TTL=3600
```

### 3. Rate Limiting
```bash
# Configure rate limits in .env
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
AUTOMATION_DELAY_BETWEEN_ACTIONS=1.0
```

## 💾 Backup & Recovery

### 1. Database Backup
```bash
# Create backup script
cat > backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec chaknal-postgres-prod pg_dump -U chaknal_user chaknal_prod > "$BACKUP_DIR/db_backup_$DATE.sql"
gzip "$BACKUP_DIR/db_backup_$DATE.sql"
echo "Backup created: db_backup_$DATE.sql.gz"
EOF

chmod +x backup-db.sh
```

### 2. Application Backup
```bash
# Backup application data
tar -czf "backups/app_backup_$(date +%Y%m%d_%H%M%S).tar.gz" \
  logs/ uploads/ .env
```

### 3. Automated Backups
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/chaknal-platform/backup-db.sh
```

## 🚨 Troubleshooting

### Common Issues

#### 1. DuxSoup Authentication Failed
```bash
# Check credentials
python3 test_real_duxwrap_standalone.py

# Verify API key is active in DuxSoup dashboard
# Check if user has API access enabled
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status
docker exec chaknal-postgres-prod pg_isready -U chaknal_user

# Verify connection string in .env
# Check network connectivity
```

#### 3. Application Won't Start
```bash
# Check container logs
docker logs chaknal-platform-prod

# Verify environment variables
docker exec chaknal-platform-prod env | grep POSTGRES

# Check port availability
netstat -tlnp | grep :8000
```

#### 4. Performance Issues
```bash
# Monitor resource usage
docker stats chaknal-platform-prod

# Check database performance
docker exec chaknal-postgres-prod psql -U chaknal_user -d chaknal_prod -c "SELECT * FROM pg_stat_activity;"

# Review application logs for slow queries
grep "slow" logs/chaknal-platform.log
```

### Health Check Endpoints
```bash
# Application health
curl http://yourdomain.com:8000/health

# Automation health
curl http://yourdomain.com:8000/api/automation/v2/health-check

# Database health
curl http://yourdomain.com:8000/api/db/schema
```

## 📈 Scaling & Maintenance

### 1. Horizontal Scaling
```bash
# Scale application containers
docker-compose -f docker-compose.prod.yml up -d --scale app=3

# Use load balancer (nginx) to distribute traffic
```

### 2. Database Scaling
```bash
# Consider read replicas for heavy read workloads
# Implement connection pooling
# Monitor query performance
```

### 3. Regular Maintenance
```bash
# Weekly: Review logs and metrics
# Monthly: Update dependencies and security patches
# Quarterly: Performance review and optimization
```

## 🎯 Next Steps

1. **Test Your Deployment**: Verify all endpoints work correctly
2. **Configure Monitoring**: Set up alerts for critical metrics
3. **Create Your First Campaign**: Test the LinkedIn automation
4. **Set Up CI/CD**: Automate future deployments
5. **Document Procedures**: Create runbooks for your team

## 📞 Support

- **Documentation**: Check the main README.md
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join our community channels

---

**🎉 Congratulations!** Your Chaknal Platform is now production-ready with full DuxSoup integration for LinkedIn automation.
