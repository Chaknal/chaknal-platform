# Chaknall Platform Deployment Guide

## 🚀 Production Deployment Checklist

### 1. Security & Environment Setup

#### Environment Variables
Set these in Azure Portal → Configuration → Application settings:

**Required for Production:**
```
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=<generate-a-secure-random-key>
DATABASE_URL=<your-postgresql-connection-string>
ALLOWED_ORIGINS=["https://chacker-cdc9h6fahefudtgg.westus-01.azurewebsites.net"]
```

**Optional:**
```
GOOGLE_CLIENT_ID=<your-google-oauth-client-id>
GOOGLE_CLIENT_SECRET=<your-google-oauth-client-secret>
GOOGLE_REDIRECT_URI=https://chacker-cdc9h6fahefudtgg.westus-01.azurewebsites.net/auth/google/callback
ACCESS_TOKEN_EXPIRE_MINUTES=1440
RATE_LIMIT_PER_MINUTE=60
PROJECT_NAME=Chaknall Platform
```

#### Generate Secure Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Database Setup

#### Option A: Azure Database for PostgreSQL
1. Create PostgreSQL server in Azure Portal
2. Create database
3. Get connection string:
   ```
   postgresql+asyncpg://username:password@server.postgres.database.azure.com:5432/database
   ```

#### Option B: Azure SQL Database
1. Create SQL Database in Azure Portal
2. Update requirements.txt to include `pyodbc`
3. Use connection string:
   ```
   mssql+pyodbc://username:password@server.database.windows.net:1433/database?driver=ODBC+Driver+17+for+SQL+Server
   ```

### 3. Authentication & Authorization

#### JWT Authentication
- ✅ Already implemented
- Test endpoints:
  - `POST /auth/login` (username: admin, password: admin123)
  - `GET /auth/me` (requires Bearer token)
  - `GET /auth/protected` (requires Bearer token)

#### Google OAuth
1. Create Google OAuth 2.0 credentials
2. Set redirect URI: `https://chacker-cdc9h6fahefudtgg.westus-01.azurewebsites.net/auth/google/callback`
3. Add credentials to Azure app settings

### 4. CORS Configuration

**Development:**
```python
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

**Production:**
```python
ALLOWED_ORIGINS=["https://chacker-cdc9h6fahefudtgg.westus-01.azurewebsites.net"]
```

### 5. HTTPS & Security

#### Azure Configuration
1. Enable HTTPS only in Azure Portal
2. Configure custom domain with SSL certificate
3. Set up Application Gateway for additional security

#### Security Headers
Add to your frontend or configure in Azure:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 6. Monitoring & Observability

#### Azure Application Insights
1. Create Application Insights resource
2. Add instrumentation key to app settings
3. Monitor:
   - Request rates
   - Response times
   - Error rates
   - Custom events

#### Health Checks
- Endpoint: `GET /health`
- Monitor: `GET /api/auth/status`

### 7. Rate Limiting

Current configuration:
- 60 requests per minute per IP
- Configurable via `RATE_LIMIT_PER_MINUTE`

### 8. Deployment Steps

#### Manual Deployment
```bash
# 1. Set environment variables
export AZURE_WEBAPP_NAME="chacker"
export AZURE_RESOURCE_GROUP="chaknal-platform-rg"
export ENVIRONMENT="production"
export SECRET_KEY="your-secure-secret-key"
export DATABASE_URL="your-database-connection-string"

# 2. Run deployment script
cd chaknal-platform
chmod +x deploy-azure.sh
./deploy-azure.sh
```

#### GitHub Actions Deployment
1. Push to `chaknal-platform-2024` branch
2. Actions will:
   - Run tests and linting
   - Security scan
   - Deploy to Azure
   - Configure app settings
   - Enable HTTPS
   - Health check

### 9. Testing Your Deployment

#### Health Check
```bash
curl https://chacker-cdc9h6fahefudtgg.westus-01.azurewebsites.net/health
```

#### Authentication Test
```bash
# Login
curl -X POST "https://chacker-cdc9h6fahefudtgg.westus-01.azurewebsites.net/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Use token to access protected endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://chacker-cdc9h6fahefudtgg.westus-01.azurewebsites.net/auth/protected
```

#### Rate Limiting Test
```bash
# Test rate limiting (should get 429 after 60 requests)
for i in {1..65}; do
  curl https://chacker-cdc9h6fahefudtgg.westus-01.azurewebsites.net/health
done
```

### 10. Troubleshooting

#### Common Issues

**Database Connection Errors:**
- Check DATABASE_URL format
- Verify firewall rules
- Test connection string locally

**Authentication Issues:**
- Verify SECRET_KEY is set
- Check token expiration
- Validate CORS settings

**Deployment Failures:**
- Check Azure credentials
- Verify resource group exists
- Review deployment logs

#### Logs
- Azure Portal → App Service → Log stream
- Application Insights → Logs
- GitHub Actions → Run logs

### 11. Next Steps

#### Immediate (Week 1)
1. ✅ Set up environment variables
2. ✅ Configure database
3. ✅ Test authentication
4. ✅ Enable HTTPS

#### Short Term (Week 2-3)
1. Set up Application Insights
2. Configure custom domain
3. Add user registration
4. Implement role-based access

#### Medium Term (Month 1-2)
1. Add automated tests
2. Set up staging environment
3. Implement CI/CD improvements
4. Add API documentation

#### Long Term (Month 2+)
1. Add advanced monitoring
2. Implement backup strategies
3. Add performance optimization
4. Scale infrastructure

### 12. Security Checklist

- [ ] HTTPS only enabled
- [ ] Secure secret key generated
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Environment variables secured
- [ ] Database connection encrypted
- [ ] Authentication tested
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Health checks working

### 13. Performance Optimization

#### Database
- Use connection pooling
- Implement caching (Redis)
- Optimize queries
- Regular maintenance

#### Application
- Enable compression
- Use CDN for static files
- Implement caching headers
- Monitor performance metrics

### 14. Backup & Recovery

#### Database Backups
- Enable automated backups
- Test restore procedures
- Document recovery process

#### Application Backups
- Version control (Git)
- Configuration backups
- Environment snapshots

---

## 🆘 Support

For deployment issues:
1. Check Azure Portal logs
2. Review GitHub Actions logs
3. Test endpoints manually
4. Verify environment variables
5. Contact support with specific error messages

**Emergency Rollback:**
```bash
# Revert to previous deployment
az webapp deployment list --resource-group chaknal-platform-rg --name chaknal-platform-2024
az webapp deployment rollback --resource-group chaknal-platform-rg --name chaknal-platform-2024 --target <deployment-id>
``` 