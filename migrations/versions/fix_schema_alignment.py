"""Fix schema alignment with frontend requirements

Revision ID: fix_schema_alignment
Revises: febdbc88f63d
Create Date: 2025-01-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fix_schema_alignment'
down_revision: Union[str, None] = 'f772e0c9879c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create alembic_version table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS alembic_version (
            version_num VARCHAR(32) NOT NULL,
            CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
        );
    """)
    
    # Insert current version
    op.execute("INSERT INTO alembic_version (version_num) VALUES ('fix_schema_alignment') ON CONFLICT DO NOTHING;")
    
    # Fix contacts table - rename id to contact_id and add missing columns
    op.execute("ALTER TABLE contacts RENAME COLUMN id TO contact_id;")
    
    # Add missing columns to contacts table
    op.add_column('contacts', sa.Column('linkedin_id', sa.String(length=100), nullable=True))
    op.add_column('contacts', sa.Column('headline', sa.String(length=500), nullable=True))
    op.add_column('contacts', sa.Column('company_url', sa.String(length=500), nullable=True))
    op.add_column('contacts', sa.Column('industry', sa.String(length=255), nullable=True))
    op.add_column('contacts', sa.Column('connection_degree', sa.Integer(), nullable=True))
    op.add_column('contacts', sa.Column('profile_data', sa.JSON(), nullable=True))
    op.add_column('contacts', sa.Column('profile_id', sa.String(length=100), nullable=True))
    op.add_column('contacts', sa.Column('degree_level', sa.Integer(), nullable=True))
    op.add_column('contacts', sa.Column('connection_status', sa.String(length=50), nullable=True))
    op.add_column('contacts', sa.Column('connection_request_sent', sa.DateTime(timezone=True), nullable=True))
    op.add_column('contacts', sa.Column('connection_accepted', sa.DateTime(timezone=True), nullable=True))
    op.add_column('contacts', sa.Column('last_message_sent', sa.DateTime(timezone=True), nullable=True))
    op.add_column('contacts', sa.Column('message_count', sa.Integer(), nullable=True))
    op.add_column('contacts', sa.Column('can_send_email', sa.Boolean(), nullable=True))
    op.add_column('contacts', sa.Column('can_send_inmail', sa.Boolean(), nullable=True))
    op.add_column('contacts', sa.Column('can_send_connection', sa.Boolean(), nullable=True))
    
    # Data source tracking fields
    op.add_column('contacts', sa.Column('data_source', sa.String(length=50), nullable=True))
    op.add_column('contacts', sa.Column('source_id', sa.String(length=100), nullable=True))
    op.add_column('contacts', sa.Column('import_batch_id', sa.String(length=100), nullable=True))
    op.add_column('contacts', sa.Column('data_quality_score', sa.Integer(), nullable=True))
    
    # Standardized fields for better compatibility
    op.add_column('contacts', sa.Column('full_name', sa.String(length=255), nullable=True))
    op.add_column('contacts', sa.Column('job_title', sa.String(length=255), nullable=True))
    op.add_column('contacts', sa.Column('company_name', sa.String(length=255), nullable=True))
    op.add_column('contacts', sa.Column('company_size', sa.String(length=100), nullable=True))
    op.add_column('contacts', sa.Column('company_website', sa.String(length=500), nullable=True))
    op.add_column('contacts', sa.Column('connection_count', sa.Integer(), nullable=True))
    
    # Update existing data to populate new fields
    op.execute("""
        UPDATE contacts SET 
            full_name = COALESCE(first_name || ' ' || last_name, ''),
            job_title = COALESCE(title, ''),
            company_name = COALESCE(company, ''),
            company_website = COALESCE(company_url, '')
        WHERE full_name IS NULL OR job_title IS NULL OR company_name IS NULL;
    """)
    
    # Add unique constraints
    op.create_unique_constraint('uq_contacts_linkedin_id', 'contacts', ['linkedin_id'])
    op.create_unique_constraint('uq_contacts_linkedin_url', 'contacts', ['linkedin_url'])
    
    # Fix created_at and updated_at to be timezone aware
    op.execute("ALTER TABLE contacts ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;")
    op.execute("ALTER TABLE contacts ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;")
    
    # Add missing columns to campaigns_new table if they don't exist
    # Check if columns exist before adding them
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'campaigns_new' AND column_name = 'assigned_to') THEN
                ALTER TABLE campaigns_new ADD COLUMN assigned_to VARCHAR(36);
            END IF;
        END $$;
    """)
    
    # Add missing columns to campaign_contacts table
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'campaign_contacts' AND column_name = 'assigned_to') THEN
                ALTER TABLE campaign_contacts ADD COLUMN assigned_to VARCHAR(36);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'campaign_contacts' AND column_name = 'last_contact') THEN
                ALTER TABLE campaign_contacts ADD COLUMN last_contact TIMESTAMP WITH TIME ZONE;
            END IF;
        END $$;
    """)
    
    # Create meetings table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            meeting_id VARCHAR(36) PRIMARY KEY,
            contact_id VARCHAR(36) NOT NULL,
            campaign_id VARCHAR(36),
            meeting_date TIMESTAMP WITH TIME ZONE NOT NULL,
            meeting_type VARCHAR(50) DEFAULT 'call',
            status VARCHAR(50) DEFAULT 'scheduled',
            meeting_url TEXT,
            notes TEXT,
            created_by VARCHAR(36),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (contact_id) REFERENCES contacts(contact_id),
            FOREIGN KEY (campaign_id) REFERENCES campaigns_new(campaign_id)
        );
    """)
    
    # Create company_settings table for branding
    op.execute("""
        CREATE TABLE IF NOT EXISTS company_settings (
            id VARCHAR(36) PRIMARY KEY,
            company_id VARCHAR(36) NOT NULL,
            setting_key VARCHAR(100) NOT NULL,
            setting_value TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(company_id, setting_key)
        );
    """)
    
    # Create duxsoup_accounts table
    op.execute("""
        CREATE TABLE IF NOT EXISTS duxsoup_accounts (
            id VARCHAR(36) PRIMARY KEY,
            dux_soup_user_id VARCHAR(100) NOT NULL,
            dux_soup_auth_key VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            user_id VARCHAR(36),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (user_id) REFERENCES "user"(id)
        );
    """)
    
    # Create indexes for better performance
    op.create_index('idx_contacts_company_name', 'contacts', ['company_name'])
    op.create_index('idx_contacts_industry', 'contacts', ['industry'])
    op.create_index('idx_contacts_location', 'contacts', ['location'])
    op.create_index('idx_contacts_data_source', 'contacts', ['data_source'])
    op.create_index('idx_campaign_contacts_assigned_to', 'campaign_contacts', ['assigned_to'])
    op.create_index('idx_meetings_contact_id', 'meetings', ['contact_id'])
    op.create_index('idx_meetings_campaign_id', 'meetings', ['campaign_id'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('idx_meetings_campaign_id', table_name='meetings')
    op.drop_index('idx_meetings_contact_id', table_name='meetings')
    op.drop_index('idx_campaign_contacts_assigned_to', table_name='campaign_contacts')
    op.drop_index('idx_contacts_data_source', table_name='contacts')
    op.drop_index('idx_contacts_location', table_name='contacts')
    op.drop_index('idx_contacts_industry', table_name='contacts')
    op.drop_index('idx_contacts_company_name', table_name='contacts')
    
    # Drop new tables
    op.drop_table('duxsoup_accounts')
    op.drop_table('company_settings')
    op.drop_table('meetings')
    
    # Remove unique constraints
    op.drop_constraint('uq_contacts_linkedin_url', 'contacts', type_='unique')
    op.drop_constraint('uq_contacts_linkedin_id', 'contacts', type_='unique')
    
    # Remove added columns from contacts
    op.drop_column('contacts', 'connection_count')
    op.drop_column('contacts', 'company_website')
    op.drop_column('contacts', 'company_size')
    op.drop_column('contacts', 'company_name')
    op.drop_column('contacts', 'job_title')
    op.drop_column('contacts', 'full_name')
    op.drop_column('contacts', 'data_quality_score')
    op.drop_column('contacts', 'import_batch_id')
    op.drop_column('contacts', 'source_id')
    op.drop_column('contacts', 'data_source')
    op.drop_column('contacts', 'can_send_connection')
    op.drop_column('contacts', 'can_send_inmail')
    op.drop_column('contacts', 'can_send_email')
    op.drop_column('contacts', 'message_count')
    op.drop_column('contacts', 'last_message_sent')
    op.drop_column('contacts', 'connection_accepted')
    op.drop_column('contacts', 'connection_request_sent')
    op.drop_column('contacts', 'connection_status')
    op.drop_column('contacts', 'degree_level')
    op.drop_column('contacts', 'profile_id')
    op.drop_column('contacts', 'profile_data')
    op.drop_column('contacts', 'connection_degree')
    op.drop_column('contacts', 'industry')
    op.drop_column('contacts', 'company_url')
    op.drop_column('contacts', 'headline')
    op.drop_column('contacts', 'linkedin_id')
    
    # Rename contact_id back to id
    op.execute("ALTER TABLE contacts RENAME COLUMN contact_id TO id;")
    
    # Drop alembic_version table
    op.drop_table('alembic_version')
