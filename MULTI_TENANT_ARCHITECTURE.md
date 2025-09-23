# 🏗️ Chaknal Platform - Multi-Tenant Architecture

## 📋 **Overview**

The Chaknal Platform is built with a **comprehensive multi-tenant architecture** that supports:
- **Multiple Companies** with complete data isolation
- **Organizations** for enterprise-level grouping
- **Role-based Access Control** (User, Manager, Admin)
- **Automatic Tenant Isolation** for all data operations
- **Scalable User Management** across different business units

## 🏢 **Architecture Layers**

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   User Dashboard│  │ Admin Dashboard │  │ Company Mgmt│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ User Management│  │ Company Mgmt    │  │ Prospect Mgmt│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Contact Dashboard│  │ Campaign Mgmt   │  │ Automation  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  MIDDLEWARE LAYER                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Tenant Middleware│  │ Rate Limiting  │  │ Auth Middleware│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   DATA LAYER                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   User Models   │  │ Company Models  │  │ Contact Models│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Campaign Models │  │ Tenant Mixins   │  │ Base Models │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🏢 **Company & Organization Structure**

### **Company Level (Tenant)**
```
Company A (tenant-1)
├── Users
│   ├── John Doe (john@company-a.com) - Admin
│   ├── Jane Smith (jane@company-a.com) - Manager
│   └── Bob Wilson (bob@company-a.com) - User
├── Contacts
├── Campaigns
└── Data (fully isolated)

Company B (tenant-2)
├── Users
│   ├── Alice Johnson (alice@company-b.com) - Admin
│   └── Charlie Brown (charlie@company-b.com) - User
├── Contacts
├── Campaigns
└── Data (fully isolated)
```

### **Organization Level (Enterprise)**
```
Enterprise Corp (org-1)
├── Company A (subsidiary)
│   ├── Users: 25
│   ├── Contacts: 1,000
│   └── Campaigns: 15
├── Company B (subsidiary)
│   ├── Users: 15
│   ├── Contacts: 500
│   └── Campaigns: 8
└── Company C (subsidiary)
    ├── Users: 40
    ├── Contacts: 2,000
    └── Campaigns: 25
```

## 👥 **User Roles & Permissions**

### **User (Basic)**
- ✅ Access own company data
- ✅ Manage own profile
- ✅ Create/edit campaigns
- ✅ Manage contacts
- ❌ Access other companies
- ❌ Manage users
- ❌ Create organizations

### **Manager**
- ✅ All User permissions
- ✅ Manage users in company
- ✅ View company analytics
- ✅ Manage company settings
- ❌ Access other companies
- ❌ Create organizations

### **Admin**
- ✅ All Manager permissions
- ✅ Access organization data
- ✅ Create/manage companies
- ✅ Create/manage organizations
- ✅ Cross-company access (within org)
- ✅ System-wide analytics

## 🔒 **Data Isolation & Security**

### **Automatic Tenant Isolation**
```python
# Every model automatically includes tenant context
class Contact(Base, TenantAwareMixin):
    __tablename__ = "contacts"
    
    # Automatically added by TenantAwareMixin:
    # - company_id: Links to company
    # - organization_id: Links to organization
    
    # User can only see contacts from their company
    # Admin can see contacts from their organization
```

### **Access Control Flow**
```
1. User makes request → JWT token extracted
2. Tenant middleware → Sets tenant context
3. Database query → Automatically filtered by company_id
4. Response → Only company data returned
5. Security → Cross-tenant access prevented
```

### **Data Boundaries**
- **Company Level**: Complete isolation between companies
- **Organization Level**: Shared access for admins within org
- **User Level**: Individual user data within company
- **Campaign Level**: Company-scoped campaigns
- **Contact Level**: Company-scoped prospect database

## 🚀 **Key Features**

### **1. Multi-Tenant User Management**
```python
# Users are automatically associated with companies
POST /api/users/register
{
    "email": "john@company-a.com",
    "company_name": "Company A",
    "role": "admin"
}

# Result: User created in Company A tenant
```

### **2. Company & Organization Management**
```python
# Create company
POST /api/companies
{
    "name": "Tech Corp",
    "domain": "techcorp.com",
    "organization_id": "org-123"
}

# Create organization
POST /api/companies/organizations
{
    "name": "Enterprise Group",
    "description": "Multi-company organization"
}
```

### **3. Automatic Data Isolation**
```python
# All queries automatically filtered by tenant
GET /api/prospects/search
# Returns only prospects from user's company

GET /api/campaigns
# Returns only campaigns from user's company
```

### **4. Role-Based Access Control**
```python
# Admin can see organization data
GET /api/companies?organization_id=org-123
# Returns all companies in organization

# Manager can only see company data
GET /api/companies
# Returns only user's company
```

## 🗄️ **Database Schema**

### **Core Tables**
```sql
-- Users with tenant context
CREATE TABLE user (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    company_id UUID REFERENCES company(id),
    organization_id UUID REFERENCES organization(id),
    role VARCHAR NOT NULL DEFAULT 'user'
);

-- Companies (tenants)
CREATE TABLE company (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    domain VARCHAR UNIQUE NOT NULL,
    organization_id UUID REFERENCES organization(id)
);

-- Organizations (enterprise grouping)
CREATE TABLE organization (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT
);

-- Tenant-aware contacts
CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES company(id),
    organization_id UUID REFERENCES organization(id),
    -- ... other fields
);
```

### **Tenant Isolation Indexes**
```sql
-- Ensure fast tenant filtering
CREATE INDEX idx_contacts_company_id ON contacts(company_id);
CREATE INDEX idx_contacts_organization_id ON contacts(organization_id);
CREATE INDEX idx_campaigns_company_id ON campaigns(company_id);
CREATE INDEX idx_users_company_id ON users(company_id);
```

## 🔧 **Implementation Details**

### **Tenant Context Middleware**
```python
class TenantMiddleware:
    async def __call__(self, scope, receive, send):
        # Extract user from JWT token
        user = await self._get_authenticated_user(request)
        
        # Set tenant context
        tenant_context = TenantContext(
            company_id=user.company_id,
            organization_id=user.organization_id,
            user_id=user.id
        )
        
        # All subsequent operations use this context
        set_current_tenant_context(tenant_context)
```

### **Tenant-Aware Models**
```python
class TenantAwareMixin:
    @declared_attr
    def company_id(cls):
        return Column(String(36), ForeignKey("company.id"), nullable=False)
    
    @declared_attr
    def organization_id(cls):
        return Column(String(36), ForeignKey("organization.id"), nullable=True)

# Usage
class Contact(Base, TenantAwareMixin):
    __tablename__ = "contacts"
    # Automatically gets company_id and organization_id
```

### **Automatic Query Filtering**
```python
def tenant_filter_query(query, model_class):
    context = get_current_tenant_context()
    
    # Apply company-level filtering
    if hasattr(model_class, 'company_id'):
        query = query.filter(model_class.company_id == context.company_id)
    
    # Apply organization-level filtering for admins
    if context.organization_id and hasattr(model_class, 'organization_id'):
        query = query.filter(model_class.organization_id == context.organization_id)
    
    return query
```

## 📊 **Scaling & Performance**

### **Horizontal Scaling**
- **Database Sharding**: By company_id for large deployments
- **Microservices**: Separate services per tenant type
- **Caching**: Redis with tenant-aware keys
- **Load Balancing**: Route by company domain

### **Performance Optimizations**
- **Tenant-Aware Indexes**: Fast filtering by company_id
- **Connection Pooling**: Separate pools per tenant
- **Query Optimization**: Automatic tenant filtering
- **Caching Strategy**: Tenant-scoped cache invalidation

## 🔐 **Security Features**

### **Data Isolation**
- ✅ **Automatic**: All queries filtered by tenant
- ✅ **Middleware**: Tenant context enforced at request level
- ✅ **Database**: Foreign key constraints prevent cross-tenant access
- ✅ **API**: Role-based access control

### **Authentication & Authorization**
- ✅ **JWT Tokens**: Include tenant information
- ✅ **Role Validation**: Check permissions at endpoint level
- ✅ **Company Validation**: Ensure user belongs to company
- ✅ **Organization Validation**: Admin-only cross-company access

## 🚀 **Deployment Scenarios**

### **Single Company**
```
Company A
├── Users: 10-50
├── Data: Company-scoped only
└── Access: Company employees only
```

### **Multi-Company Organization**
```
Enterprise Corp
├── Company A (Marketing Agency)
├── Company B (Sales Team)
├── Company C (Support Team)
└── Shared: Analytics, reporting, admin tools
```

### **Multi-Organization Platform**
```
Chaknal Platform
├── Organization 1 (Tech Corp)
├── Organization 2 (Marketing Group)
├── Organization 3 (Sales Network)
└── Complete isolation between organizations
```

## 📈 **Benefits**

### **For Companies**
- ✅ **Data Security**: Complete isolation from other companies
- ✅ **Customization**: Company-specific settings and branding
- ✅ **Scalability**: Grow from 1 to 1000+ users
- ✅ **Compliance**: GDPR, SOC2, HIPAA ready

### **For Organizations**
- ✅ **Centralized Management**: Admin all subsidiaries
- ✅ **Shared Resources**: Templates, best practices
- ✅ **Cross-Company Analytics**: Organization-wide insights
- ✅ **Unified Billing**: Single invoice for all companies

### **For Platform**
- ✅ **Multi-Tenant**: Serve multiple customers efficiently
- ✅ **Resource Sharing**: Optimize infrastructure costs
- ✅ **Scalability**: Add new tenants without code changes
- ✅ **Revenue Growth**: Multiple revenue streams

## 🔮 **Future Enhancements**

### **Advanced Multi-Tenancy**
- **Database Sharding**: Automatic sharding by company size
- **Custom Domains**: company-name.chaknal.com
- **White-Label**: Custom branding per company
- **API Rate Limiting**: Per-tenant rate limits

### **Enterprise Features**
- **Single Sign-On**: SAML, OAuth integration
- **Audit Logging**: Complete activity tracking
- **Data Export**: GDPR compliance tools
- **Advanced Analytics**: Cross-company insights

---

## 📞 **Support & Documentation**

- **API Documentation**: `/docs` endpoint
- **Architecture Guide**: This document
- **Implementation Examples**: See code comments
- **Best Practices**: Follow tenant isolation patterns

---

**🏗️ Built with ❤️ for scalable, secure, multi-tenant applications**
