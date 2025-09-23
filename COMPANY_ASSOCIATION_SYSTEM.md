# 🏢 Company Association System

## 🎯 **How Users Are Associated with Companies**

The Chaknal Platform uses a **hybrid approach** that combines **automatic domain-based association** with **manual assignment capabilities**.

## 🔄 **Two Association Methods**

### **Method 1: Automatic Domain-Based Association (Recommended)**

#### **How It Works:**
1. **User registers/logs in** with email (e.g., `john.sales@techcorp.com`)
2. **System extracts domain** (`techcorp.com`)
3. **System finds existing company** by domain
4. **If company doesn't exist**, system creates it automatically
5. **User is automatically associated** with the company and a default organization

#### **Code Example:**
```python
# When user logs in:
user_email = "john.sales@techcorp.com"
domain = user_email.split("@")[1]  # "techcorp.com"

# System automatically finds/creates company
company = await CompanyService.get_or_create_company_by_domain(session, domain)

# User is automatically associated
user.company_id = company.id
user.organization_id = default_org.id
```

#### **Benefits:**
- ✅ **Zero configuration** - works automatically
- ✅ **Consistent** - all users from same domain get same company
- ✅ **Scalable** - supports thousands of companies
- ✅ **User-friendly** - no manual setup required

### **Method 2: Manual Assignment (Admin Control)**

#### **How It Works:**
1. **Admin manually assigns** users to specific companies
2. **Admin creates custom organizations** within companies
3. **Users are placed** in specific organizational structures

#### **Code Example:**
```python
# Admin manually assigns:
user.company_id = "manually_selected_company_id"
user.organization_id = "specific_org_id"

# Or admin creates custom organization:
org = await CompanyService.create_custom_organization(
    session, company_id, "Sales Team", "Handles B2B sales"
)
```

#### **Benefits:**
- ✅ **Full control** over company structure
- ✅ **Custom organizations** with specific purposes
- ✅ **Flexible hierarchy** - departments, teams, etc.
- ✅ **Audit trail** - track all assignments

## 🏗️ **Database Schema**

### **Current Structure:**
```sql
Company Table:
- id (UUID, Primary Key)
- name (String)
- domain (String, Unique)

Organization Table:
- id (UUID, Primary Key)
- name (String)
- company_id (UUID, Foreign Key to Company)

User Table:
- id (UUID, Primary Key)
- email (String, Unique)
- company_id (UUID, Foreign Key to Company)
- organization_id (UUID, Foreign Key to Organization)
```

### **Relationships:**
```
Company (1) ←→ (Many) Organization (1) ←→ (Many) User
     ↑                                              ↑
     └─────────────── Direct User Link ────────────┘
```

## 🚀 **How It Works in Practice**

### **Scenario 1: New Company, First User**
```
1. User registers: john.sales@startupcorp.com
2. System extracts domain: startupcorp.com
3. System creates company: "Startupcorp"
4. System creates organization: "Default Team"
5. User is associated with both
6. Result: User automatically belongs to Startupcorp > Default Team
```

### **Scenario 2: Existing Company, New User**
```
1. User registers: sarah.marketing@techcorp.com
2. System extracts domain: techcorp.com
3. System finds existing company: "TechCorp Solutions"
4. System finds existing organization: "Default Team"
5. User is associated with existing company/org
6. Result: User joins existing TechCorp Solutions > Default Team
```

### **Scenario 3: Admin Creates Custom Structure**
```
1. Admin creates company: "Enterprise Corp"
2. Admin creates organizations: "Sales Team", "Marketing Team", "Engineering Team"
3. Admin assigns users to specific teams
4. Result: Structured organizational hierarchy
```

## 🔧 **Implementation Details**

### **Company Service Methods:**
```python
class CompanyService:
    # Auto-create company from domain
    async def get_or_create_company_by_domain(session, domain, company_name=None)
    
    # Auto-create default organization
    async def get_or_create_default_organization(session, company_id, org_name="Default Team")
    
    # Auto-associate user with company
    async def associate_user_with_company(session, user_email, user_id, preferred_org_name=None)
    
    # Manual organization creation
    async def create_custom_organization(session, company_id, org_name, description=None)
    
    # Move users between organizations
    async def move_user_to_organization(session, user_id, new_org_id)
```

### **Authentication Flow:**
```python
async def authenticate_user(session, email, password):
    # 1. Validate user credentials
    user = await find_user_by_email(session, email)
    
    # 2. Check if user has company/organization
    if not user.company_id or not user.organization_id:
        # 3. Auto-associate based on email domain
        await CompanyService.associate_user_with_company(session, email, user.id)
    
    # 4. Return user context with company/org info
    return build_user_context(user)
```

## 📊 **Real-World Examples**

### **Example 1: Tech Startup**
```
Email: john@myapp.com
Domain: myapp.com
Auto-created Company: "Myapp"
Auto-created Organization: "Default Team"
Result: john@myapp.com → Myapp > Default Team
```

### **Example 2: Large Corporation**
```
Email: sarah.sales@microsoft.com
Domain: microsoft.com
Existing Company: "Microsoft"
Existing Organization: "Sales Team"
Result: sarah.sales@microsoft.com → Microsoft > Sales Team
```

### **Example 3: Custom Structure**
```
Admin creates:
- Company: "Acme Corp"
- Organizations: "North Sales", "South Sales", "Marketing", "Engineering"

Users get assigned:
- john@acme.com → Acme Corp > North Sales
- sarah@acme.com → Acme Corp > Marketing
- mike@acme.com → Acme Corp > Engineering
```

## 🎯 **Best Practices**

### **When to Use Auto-Association:**
- ✅ **Small to medium companies** (1-100 users)
- ✅ **Quick setup** requirements
- ✅ **Standard organizational structure**
- ✅ **Self-service user onboarding**

### **When to Use Manual Assignment:**
- ✅ **Large enterprises** (100+ users)
- ✅ **Complex organizational hierarchy**
- ✅ **Compliance requirements**
- ✅ **Department-specific permissions**

### **Hybrid Approach (Recommended):**
1. **Start with auto-association** for quick setup
2. **Add custom organizations** as company grows
3. **Move users** to appropriate teams
4. **Maintain flexibility** for future changes

## 🔒 **Security & Data Isolation**

### **Automatic Isolation:**
```python
# All API endpoints automatically filter by company:
@app.get("/campaigns")
async def get_campaigns(current_user = Depends(get_current_user)):
    company_id = current_user["company"]["id"]
    # Only return campaigns for user's company
    campaigns = await get_campaigns_for_company(session, company_id)
    return campaigns
```

### **Permission-Based Access:**
```python
# Users can only access their company's data
# Superusers can manage company structure
# Organization admins can manage their teams
```

## 🚀 **Getting Started**

### **1. Test Auto-Association:**
```bash
# Register new user
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@newcompany.com", "password": "password123"}'
```

### **2. Check Company Info:**
```bash
# Get company details
curl "http://localhost:8000/users/company-info/test@newcompany.com"
```

### **3. Create Custom Organization:**
```bash
# Create custom team
curl -X POST "http://localhost:8000/users/create-organization" \
  -H "Content-Type: application/json" \
  -d '{"org_name": "Sales Team", "description": "B2B Sales Team"}'
```

## 🔄 **Migration & Updates**

### **Existing Users:**
- Users without company/org will be auto-associated on next login
- No data loss or manual intervention required
- System maintains backward compatibility

### **Adding New Features:**
- Company hierarchy (departments, teams, sub-teams)
- Cross-company collaboration
- Advanced permission systems
- Audit logging and compliance

## 📚 **Summary**

The Chaknal Platform uses a **smart, hybrid approach**:

1. **🎯 Automatic**: Users are automatically associated with companies based on email domains
2. **🔧 Flexible**: Admins can create custom organizational structures
3. **🔄 Seamless**: Existing users get auto-associated on login
4. **🔒 Secure**: Data isolation is enforced at the database level
5. **📈 Scalable**: Supports from 1 user to thousands of users

**The system is designed to "just work" while giving you full control when you need it.**
