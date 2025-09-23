import os
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/duxwrap')
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), 'database_schema.sql')

def run_migration():
    with open(SCHEMA_FILE, 'r') as f:
        schema_sql = f.read()
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()
        logger.info('Database schema migration completed successfully.')
    except Exception as e:
        logger.error(f'Error running migration: {e}')
        raise

if __name__ == '__main__':
    run_migration() 