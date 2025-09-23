from fastapi import APIRouter, Query
from typing import Optional
import sqlite3

router = APIRouter(prefix="/api/contacts", tags=["contacts-campaign"])

@router.get("/campaign-data")
async def get_campaign_contacts(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    search: Optional[str] = Query(None),
    campaign: Optional[str] = Query(None),
    assigned_user: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    has_meeting: Optional[str] = Query(None)
):
    """Get contacts with campaign data and filtering"""
    
    try:
        # Connect directly to SQLite database
        conn = sqlite3.connect('chaknal.db')
        conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        cursor = conn.cursor()
        # Build SQL query with filters
        base_sql = """
        SELECT 
            c.contact_id, c.first_name, c.last_name, c.company, c.headline,
            c.linkedin_url, c.email, c.location, c.created_at, c.updated_at,
            cc.campaign_contact_id, cc.status, cc.assigned_to, cc.enrolled_at, cc.sequence_step,
            cn.name as campaign_name, cn.campaign_id
        FROM contacts c
        JOIN campaign_contacts cc ON c.contact_id = cc.contact_id
        JOIN campaigns_new cn ON cc.campaign_id = cn.campaign_id
        WHERE 1=1
        """
        
        params = []
        
        # Apply search filter
        if search:
            base_sql += """ AND (
                LOWER(c.first_name) LIKE ? 
                OR LOWER(c.last_name) LIKE ? 
                OR LOWER(c.company) LIKE ? 
                OR LOWER(c.headline) LIKE ? 
                OR LOWER(c.email) LIKE ?
            )"""
            search_param = f"%{search.lower()}%"
            params.extend([search_param, search_param, search_param, search_param, search_param])
        
        # Apply campaign filter
        if campaign:
            base_sql += " AND cn.name = ?"
            params.append(campaign)
        
        # Apply assigned user filter
        if assigned_user and assigned_user != 'all':
            base_sql += " AND cc.assigned_to = ?"
            params.append(assigned_user)
        
        # Apply status filter
        if status:
            if ',' in status:
                statuses = [s.strip() for s in status.split(',')]
                status_placeholders = ', '.join(['?' for _ in statuses])
                base_sql += f" AND cc.status IN ({status_placeholders})"
                params.extend(statuses)
            else:
                base_sql += " AND cc.status = ?"
                params.append(status)
        
        # Apply meeting filter
        if has_meeting == 'true':
            base_sql += " AND cc.status = ?"
            params.append('responded')
        
        # Apply sorting
        if sort_by in ['first_name', 'last_name', 'company', 'created_at']:
            base_sql += f" ORDER BY c.{sort_by}"
        elif sort_by in ['status', 'enrolled_at']:
            base_sql += f" ORDER BY cc.{sort_by}"
        else:
            base_sql += " ORDER BY c.created_at"
            
        if sort_order.lower() == 'desc':
            base_sql += " DESC"
        else:
            base_sql += " ASC"
        
        # Get total count - create a separate count query
        count_sql = """
        SELECT COUNT(*)
        FROM contacts c
        JOIN campaign_contacts cc ON c.contact_id = cc.contact_id
        JOIN campaigns_new cn ON cc.campaign_id = cn.campaign_id
        WHERE 1=1
        """
        
        # Add the same filters to count query
        if search:
            count_sql += """ AND (
                LOWER(c.first_name) LIKE ? 
                OR LOWER(c.last_name) LIKE ? 
                OR LOWER(c.company) LIKE ? 
                OR LOWER(c.headline) LIKE ? 
                OR LOWER(c.email) LIKE ?
            )"""
        
        if campaign:
            count_sql += " AND cn.name = ?"
        
        if assigned_user and assigned_user != 'all':
            count_sql += " AND cc.assigned_to = ?"
        
        if status:
            if ',' in status:
                statuses = [s.strip() for s in status.split(',')]
                status_placeholders = ', '.join(['?' for _ in statuses])
                count_sql += f" AND cc.status IN ({status_placeholders})"
            else:
                count_sql += " AND cc.status = ?"
        
        if has_meeting == 'true':
            count_sql += " AND cc.status = ?"
        
        # Get total count
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()[0]
        
        # Apply pagination
        base_sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute query
        cursor.execute(base_sql, params)
        rows = cursor.fetchall()
        
        # Close connection
        conn.close()
        
        # Format response
        contacts_data = []
        for row in rows:
            # Determine if contact has meeting
            has_meeting_bool = row['status'] == 'responded' and row['campaign_name'] == 'Professional Outreach'
            
            contact_data = {
                'contact_id': row['contact_id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'full_name': f"{row['first_name']} {row['last_name']}",
                'company': row['company'],
                'title': row['headline'],
                'headline': row['headline'],
                'linkedin_url': row['linkedin_url'],
                'email': row['email'],
                'location': row['location'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                
                # Campaign contact data
                'campaign_contact_id': row['campaign_contact_id'],
                'campaign': row['campaign_name'],
                'campaign_id': row['campaign_id'],
                'status': row['status'],
                'assigned_user': row['assigned_to'],
                'enrolled_at': row['enrolled_at'],
                'has_meeting': has_meeting_bool,
                'sequence_step': row['sequence_step']
            }
            contacts_data.append(contact_data)
        
        return {
            'success': True,
            'data': contacts_data,
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'count': len(contacts_data)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': [],
            'total': 0
        }
