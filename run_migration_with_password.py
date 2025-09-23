#!/usr/bin/env python3
"""
Simple Migration Runner
======================

Run this script with the PostgreSQL password as an argument:
python3 run_migration_with_password.py YOUR_PASSWORD_HERE
"""

import sys
import os

if len(sys.argv) != 2:
    print("Usage: python3 run_migration_with_password.py <postgres_password>")
    print("")
    print("Example: python3 run_migration_with_password.py mypassword123")
    sys.exit(1)

# Set the password in environment
os.environ['POSTGRES_PASSWORD'] = sys.argv[1]

# Import and run the migration
from critical_campaign_contacts_migration import migrate_campaign_contacts

print("🚀 Starting Critical Migration with provided password...")
success = migrate_campaign_contacts()

if success:
    print("\n✅ SUCCESS: Critical migration completed!")
    print("🧪 Test campaign creation at: https://app.chaknal.com")
else:
    print("\n❌ FAILED: Migration failed - check output above")
