# 🏢 Organization Authentication System

## Overview

The Chaknal Platform uses a **multi-tenant architecture** where users belong to organizations, and organizations belong to companies. This system ensures data isolation and proper access control.

## 🏗️ **Database Structure**

```
Company (1) ←→ (Many) Organization (1) ←→ (Many) User
```

### **Company Table**
- `id`: Unique identifier
- `name`: Company name (e.g., "TechCorp Solutions")
- `domain`: Company domain (e.g., "techcorp.com")

### **Organization Table**
- `id`: Unique identifier
- `name`: Organization name (e.g., "Sales Team", "Marketing Team")
- `company_id`: Foreign key to Company

### **User Table**
- `id`: Unique identifier
- `email`: User's email address
- `organization_id`: Foreign key to Organization
- `company_id`: Foreign key to Company
- `is_superuser`: Admin privileges flag

## 🔐 **Authentication Flow**

### **1. User Login**
```python
# User provides email/password
POST /auth/login
{
  "email": "john.sales@techcorp.com",
  "password": "password123"
}
```

### **2. System Validation**
```python
# Backend validates:
1. Email exists in database
2. Password hash matches
3. User is active
4. User belongs to organization
5. Organization belongs to company
```

### **3. JWT Token Creation**
```python
# Token contains:
{
  "sub": "user_uuid",
  "email": "john.sales@techcorp.com",
  "org_id": "org_uuid",
  "company_id": "company_uuid",
  "permissions": ["campaign:read", "contact:write"],
  "exp": "expiration_timestamp"
}
```

### **4. User Context Returned**
```python
# Login response includes:
{
  "access_token": "jwt_token_here",
  "user_context": {
    "user_id": "user_uuid",
    "email": "john.sales@techcorp.com",
    "organization": {
      "id": "org_uuid",
      "name": "TechCorp Sales Team"
    },
    "company": {
      "id": "company_uuid",
      "name": "TechCorp Solutions",
      "domain": "techcorp.com"
    },
    "permissions": ["campaign:read", "contact:write"]
  }
}
```

## 🎯 **How Organization Context is Used**

### **Frontend Storage**
```javascript
// After login, frontend stores:
localStorage.setItem('access_token', token);
localStorage.setItem('user_context', JSON.stringify(userContext));

// Every API request includes:
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

### **API Request Context**
```javascript
// Every API request automatically includes:
- User ID
- Organization ID
- Company ID
- User permissions
```

### **Data Filtering**
```python
# Backend automatically filters data by organization:
@app.get("/campaigns")
async def get_campaigns(
    current_user: Dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Only return campaigns for user's organization
    org_id = current_user["organization"]["id"]
    campaigns = await get_campaigns_for_organization(session, org_id)
    return campaigns
```

## 🔒 **Permission System**

### **Permission Levels**
```python
# Superuser permissions:
- user:write, user:delete
- campaign:read, campaign:write, campaign:delete
- contact:read, contact:write, contact:delete
- organization:read, organization:write, organization:delete
- company:read, company:write, company:delete

# Regular user permissions:
- campaign:read, campaign:write
- contact:read, contact:write
- message:read, message:write
- organization:read
- company:read
```

### **Permission Checking**
```python
# In API endpoints:
@app.post("/campaigns")
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: Dict = Depends(require_permission("campaign:write")),
    session: AsyncSession = Depends(get_session)
):
    # User must have campaign:write permission
    # current_user contains full context
    pass
```

## 🚀 **Usage Examples**

### **1. Login and Get Organization Info**
```javascript
import { useAuth } from './contexts/AuthContext';

function Dashboard() {
  const { user, getUserOrganization, getUserCompany } = useAuth();
  
  const org = getUserOrganization();
  const company = getUserCompany();
  
  return (
    <div>
      <h1>Welcome to {org.name}</h1>
      <p>Company: {company.name}</p>
    </div>
  );
}
```

### **2. Check User Permissions**
```javascript
function CampaignList() {
  const { hasPermission, isSuperuser } = useAuth();
  
  return (
    <div>
      {hasPermission('campaign:write') && (
        <button>Create Campaign</button>
      )}
      
      {isSuperuser() && (
        <button>Delete All Campaigns</button>
      )}
    </div>
  );
}
```

### **3. Organization-Specific Data**
```javascript
function ContactList() {
  const { user } = useAuth();
  const [contacts, setContacts] = useState([]);
  
  useEffect(() => {
    // API automatically filters by user's organization
    axios.get('/contacts').then(response => {
      setContacts(response.data);
    });
  }, []);
  
  return (
    <div>
      <h2>Contacts for {user.organization.name}</h2>
      {/* Contact list */}
    </div>
  );
}
```

## 🔧 **Backend Dependencies**

### **Required Dependencies**
```python
# In requirements.txt:
PyJWT==2.8.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

### **Environment Variables**
```bash
# In .env:
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🧪 **Testing the System**

### **Test Users Available**
```bash
# Test Company Inc.
Email: test@testcompany.com
Password: password123
Organization: Sales Team

# TechCorp Solutions
Email: john.sales@techcorp.com
Password: password123
Organization: TechCorp Sales Team

# SalesForce Pro
Email: mike.bd@salesforcepro.com
Password: password123
Organization: SalesForce Business Development
```

### **Testing Organization Isolation**
1. Login as user from Company A
2. Create campaigns/contacts
3. Login as user from Company B
4. Verify you can't see Company A's data
5. Verify you can only see Company B's data

## 🚨 **Security Considerations**

### **Data Isolation**
- Users can only access data from their organization
- API endpoints automatically filter by organization
- JWT tokens contain organization context
- Database queries include organization filters

### **Permission Validation**
- Frontend shows/hides features based on permissions
- Backend validates permissions on every request
- Superuser status is checked server-side
- Organization membership is verified

### **Token Security**
- JWT tokens expire automatically
- Tokens contain minimal necessary information
- Refresh mechanism for long sessions
- Secure token storage in localStorage

## 📚 **API Endpoints**

### **Authentication**
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user context
- `POST /auth/logout` - User logout
- `GET /auth/organization` - Get user's organization
- `GET /auth/permissions` - Get user's permissions

### **Protected Endpoints**
- All endpoints require valid JWT token
- Organization context is automatically included
- Data is filtered by user's organization
- Permissions are checked for write operations

## 🔄 **Future Enhancements**

### **Planned Features**
- Role-based access control (RBAC)
- Organization hierarchy (departments, teams)
- Cross-organization collaboration
- Audit logging for all operations
- Multi-factor authentication (MFA)

### **Scalability**
- Support for thousands of organizations
- Efficient database indexing
- Caching for organization context
- Rate limiting per organization
