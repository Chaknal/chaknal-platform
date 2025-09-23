#!/usr/bin/env python3
"""
Script to check local SQLite database structure
"""
import sqlite3
import json

def check_local_database():
    """Check the structure of the local SQLite database"""
    try:
        # Connect to local SQLite database
        conn = sqlite3.connect('chaknal.db')
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        print('=== LOCAL DATABASE TABLES ===')
        for table in tables:
            table_name = table[0]
            print(f'\nTable: {table_name}')
            
            # Get table schema
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_str = ' PRIMARY KEY' if pk else ''
                not_null_str = ' NOT NULL' if not_null else ''
                default_str = f' DEFAULT {default_val}' if default_val else ''
                print(f'  {col_name} {col_type}{pk_str}{not_null_str}{default_str}')
            
            # Get row count
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'  Rows: {count}')
            
            # Show sample data for campaigns table
            if table_name == 'campaigns_new':
                cursor.execute(f'SELECT * FROM {table_name} LIMIT 3')
                sample_rows = cursor.fetchall()
                if sample_rows:
                    print(f'  Sample data:')
                    for row in sample_rows:
                        print(f'    {row}')

        conn.close()
        
    except Exception as e:
        print(f"Error checking local database: {e}")

if __name__ == "__main__":
    check_local_database()
