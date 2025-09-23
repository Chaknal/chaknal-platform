# Database Migration Guide - Chaknal Platform

## 🚨 Critical Issue
Campaign creation is failing because only **6 out of 18 tables** exist in Azure PostgreSQL. The most critical missing table is `campaign_contacts` which contains **449 rows** of campaign-contact relationships.

## Current Status
- ✅ **Backend**: Deployed to Azure App Service
- ✅ **Frontend**: Deployed to Azure Static Web Apps  
- ✅ **Authentication**: Google OAuth working
- ❌ **Database**: Missing 12 critical tables

## Tables Status

### ✅ Already Created in Azure PostgreSQL (6 tables):
- `organization` (7 rows)
- `company` (21 rows) 
- `campaigns_new` (13 rows)
- `user` (23 rows)
- `contacts` (449 rows)
- `webhook_events` (0 rows)

### ❌ Missing Critical Tables (12 tables):
- **`campaign_contacts`** - 449 rows 🚨 **CRITICAL FOR CAMPAIGNS**
- `duxsoup_user` - 6 rows (DuxSoup configurations)
- `duxsoup_user_settings` - 0 rows (DuxSoup detailed settings)
- `messages` - 7 rows (Message history)
- `duxsoup_execution_log` - 2 rows (Command logs)
- `agency_client` - 3 rows (Agency relationships)
- `agency_activity_log` - 0 rows (Activity tracking)
- `agency_invitation` - 0 rows (Invitations)
- `meetings` - 1 row (Meeting data)
- `duxsoup_queue` - 0 rows (Command queue)
- `tenant_campaigns` - 0 rows (Multi-tenant)
- `tenant_contacts` - 0 rows (Multi-tenant)
- `alembic_version` - 1 row (Migration tracking)

## Migration Scripts

### 1. Quick Status Check
```bash
# Check current database status
python3 database_status_check.py
```

### 2. Critical Fix (Immediate)
```bash
# Fix the most critical issue - campaign_contacts table
export POSTGRES_PASSWORD="your_azure_postgres_password"
python3 critical_campaign_contacts_migration.py
```

### 3. Complete Migration
```bash
# Migrate all 18 tables and data
export POSTGRES_PASSWORD="your_azure_postgres_password" 
python3 complete_database_migration.py
```

## Database Connection Details
- **Server**: `chaknal-db-server.postgres.database.azure.com`
- **Database**: `chaknal_platform`
- **User**: `chaknaladmin`
- **Port**: `5432`
- **SSL**: Required

## Step-by-Step Instructions

### Step 1: Set Environment Variable
```bash
export POSTGRES_PASSWORD="your_azure_postgres_password"
```

### Step 2: Check Current Status
```bash
cd /Users/lacomp/Desktop/chaknal-platform
python3 database_status_check.py
```

### Step 3: Run Critical Migration First
```bash
# This fixes campaign creation immediately
python3 critical_campaign_contacts_migration.py
```

### Step 4: Test Campaign Creation
1. Go to https://app.chaknal.com
2. Try creating a new campaign
3. Verify it can link to contacts

### Step 5: Complete Full Migration
```bash
# Migrate all remaining tables
python3 complete_database_migration.py
```

### Step 6: Verify Everything Works
1. Test campaign creation ✅
2. Test DuxSoup integration ✅  
3. Test contact management ✅
4. Test agency features ✅

## What Each Script Does

### `database_status_check.py`
- Compares SQLite vs PostgreSQL tables
- Shows row counts for each table
- Identifies missing tables and data
- Provides migration recommendations

### `critical_campaign_contacts_migration.py`  
- **URGENT**: Creates `campaign_contacts` table
- Migrates 449 critical campaign-contact relationships
- Fixes campaign creation immediately
- Quick 2-minute fix for the main issue

### `complete_database_migration.py`
- Creates all 18 tables in PostgreSQL
- Migrates all data from SQLite
- Handles foreign key relationships
- Comprehensive 10-minute full migration

## Troubleshooting

### Connection Issues
```bash
# Test PostgreSQL connection
psql -h chaknal-db-server.postgres.database.azure.com -U chaknaladmin -d chaknal_platform
```

### Permission Issues
```bash
# Make scripts executable
chmod +x *.py
```

### Missing Dependencies
```bash
# Install required packages
pip install psycopg2-binary tabulate
```

## Post-Migration Verification

### Check Table Counts
```sql
-- Run in PostgreSQL
SELECT 
    schemaname,
    tablename,
    n_tup_ins as "rows"
FROM pg_stat_user_tables
ORDER BY n_tup_ins DESC;
```

### Test Critical Relationships
```sql
-- Verify campaign-contact links
SELECT 
    c.name as campaign_name,
    COUNT(cc.contact_id) as contact_count
FROM campaigns_new c
LEFT JOIN campaign_contacts cc ON c.campaign_id = cc.campaign_id  
GROUP BY c.campaign_id, c.name
ORDER BY contact_count DESC;
```

## URLs
- **Frontend**: https://app.chaknal.com
- **Backend**: https://chaknal-backend-1758294239.azurewebsites.net
- **Health Check**: https://chaknal-backend-1758294239.azurewebsites.net/health

## Priority Order
1. 🚨 **CRITICAL**: Run `critical_campaign_contacts_migration.py` first
2. 🧪 **TEST**: Verify campaign creation works
3. 📋 **COMPLETE**: Run `complete_database_migration.py`
4. ✅ **VERIFY**: Test all functionality

The campaign creation issue will be fixed immediately after running the critical migration script!
