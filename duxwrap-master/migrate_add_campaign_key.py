import os
import psycopg2
import uuid

DB_URL = os.getenv('DATABASE_URL')

if not DB_URL:
    raise Exception('DATABASE_URL environment variable not set')

def migrate():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    try:
        print('Adding campaign_key column to campaigns...')
        cur.execute('''
            ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS campaign_key UUID;
        ''')
        print('Populating campaign_key in campaigns...')
        cur.execute('''
            UPDATE campaigns SET campaign_key = gen_random_uuid() WHERE campaign_key IS NULL;
        ''')
        print('Adding campaign_key column to campaign_contacts...')
        cur.execute('''
            ALTER TABLE campaign_contacts ADD COLUMN IF NOT EXISTS campaign_key UUID;
        ''')
        print('Copying campaign_key to campaign_contacts...')
        cur.execute('''
            UPDATE campaign_contacts cc
            SET campaign_key = c.campaign_key
            FROM campaigns c
            WHERE cc.campaign_id::text = c.campaign_id::text;
        ''')
        print('Setting campaign_key as NOT NULL...')
        cur.execute('''
            ALTER TABLE campaigns ALTER COLUMN campaign_key SET NOT NULL;
            ALTER TABLE campaign_contacts ALTER COLUMN campaign_key SET NOT NULL;
        ''')
        print('Adding indexes...')
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_campaigns_campaign_key ON campaigns(campaign_key);
            CREATE INDEX IF NOT EXISTS idx_campaign_contacts_campaign_key ON campaign_contacts(campaign_key);
        ''')
        conn.commit()
        print('✅ Migration completed successfully!')
    except Exception as e:
        conn.rollback()
        print(f'❌ Migration failed: {e}')
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    migrate() 