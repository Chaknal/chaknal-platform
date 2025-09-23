# Mock Data Management Checklist

## 🎯 Purpose
This document tracks all components and endpoints that use mock data for local development, and provides a roadmap for production readiness.

## 🚨 PRODUCTION READINESS CHECKLIST

### Frontend Components Using Mock Data

#### ✅ **UserManagement.js** - `/frontend/src/components/UserManagement.js`
- **Mock Data Location:** Lines 75-145 in `fetchUsers()` catch block
- **What's Mocked:** User list with 5 sample users (Sercio, Shayne, John, Sarah, Mike)
- **Trigger:** API call to `/api/users` fails (authentication required)
- **Production Fix Needed:** ✅ Implement proper JWT authentication
- **Mock Data Details:**
  ```javascript
  // 5 users with roles: user, admin, manager
  // Companies: Marketing Masters, Attimis Solutions, TechCorp, SalesForce Pro
  // Includes: email, name, phone, company info, created dates
  ```

#### ✅ **ClientSwitcher.js** - `/frontend/src/components/ClientSwitcher.js`
- **Mock Data Location:** Lines 18-55 in `fetchClients()`
- **What's Mocked:** Agency client list (TechCorp, Marketing Masters, SalesForce Pro)
- **Trigger:** Always uses mock data (no API call)
- **Production Fix Needed:** ✅ Create `/api/agency/clients` endpoint
- **Mock Data Details:**
  ```javascript
  // 3 clients with stats (campaigns, contacts, messages)
  // Each has: id, name, domain, access_level, stats
  ```

#### ✅ **Dashboard.js** - `/frontend/src/components/Dashboard.js`
- **Mock Data Location:** Lines 30-47 in `fetchClientDashboardData()` + Lines 95-122 fallback
- **What's Mocked:** Dashboard statistics and recent activity
- **Trigger:** Client-specific data OR API failures
- **Production Fix Needed:** ✅ Real campaign/contact/message APIs
- **Mock Data Details:**
  ```javascript
  // Campaign stats, contact counts, message counts, recent activity
  // Client-specific variations based on currentClient
  ```

#### ✅ **Messages.js** - `/frontend/src/components/Messages.js`
- **Mock Data Location:** Multiple locations
  - Lines 66-103: `generateClientUsers()`
  - Lines 105-150: `generateUserConnections()`
  - Lines 227-294: `generateMockMessages()`
- **What's Mocked:** Users, connections, conversation history
- **Trigger:** Always uses mock data for user lists and connections
- **Production Fix Needed:** ✅ Real user/contact APIs and message storage
- **Mock Data Details:**
  ```javascript
  // Users: Sercio Campos + generated users per client
  // Connections: LinkedIn profiles with conversation status
  // Messages: Realistic conversation threads
  ```

#### ✅ **Campaigns.js / CampaignsNew.js** - Campaign Management
- **Mock Data Location:** Various components have campaign fallbacks
- **What's Mocked:** Campaign lists, performance metrics
- **Trigger:** API failures or client-specific data
- **Production Fix Needed:** ✅ Complete campaign API integration
- **Mock Data Details:**
  ```javascript
  // Campaign performance data, contact assignments, sequence steps
  ```

#### ✅ **Contacts.js** - `/frontend/src/components/Contacts.js`
- **Mock Data Location:** Lines 50-200+ in various generate functions
- **What's Mocked:** Contact lists, campaign assignments, status data
- **Trigger:** Client-specific data OR API failures
- **Production Fix Needed:** ✅ Real contact management API
- **Mock Data Details:**
  ```javascript
  // Contacts with LinkedIn URLs, campaign assignments, response status
  // Filtering and pagination support
  ```

#### ✅ **Analytics.js** - `/frontend/src/components/Analytics.js`
- **Mock Data Location:** Multiple mock data generators
- **What's Mocked:** Performance metrics, user activity, campaign stats
- **Trigger:** Always uses mock data for most metrics
- **Production Fix Needed:** ✅ Real analytics data pipeline
- **Mock Data Details:**
  ```javascript
  // Campaign performance, user activity tables, meeting stats
  ```

### Backend APIs Using Mock/Hardcoded Data

#### ✅ **DuxSoup Configuration** - Various files
- **Mock Data Location:** 
  - `frontend/src/components/DuxSoupConfig.js` - Lines 85-96 (fallback users)
  - `app/api/duxsoup_auth_test.py` - Hardcoded TEST_USER_ID, TEST_API_KEY
- **What's Mocked:** DuxSoup user credentials and settings
- **Trigger:** API failures or missing database entries
- **Production Fix Needed:** ✅ Complete DuxSoup user management
- **Mock Data Details:**
  ```javascript
  // Sercio Campos and Shayne Stubbs DuxSoup credentials
  // Fallback DuxSoup settings and configurations
  ```

### Authentication System

#### ✅ **App.js** - Main Authentication
- **Mock Data Location:** Lines 59-66
- **What's Mocked:** Current user context (agency user)
- **Trigger:** Always uses mock user
- **Production Fix Needed:** ✅ Complete JWT authentication system
- **Mock Data Details:**
  ```javascript
  // Agency user with company and organization info
  // is_agency: true, role: "agency"
  ```

## 🔧 PRODUCTION MIGRATION PLAN

### Phase 1: Authentication Foundation
- [ ] Implement JWT authentication system
- [ ] Create user registration/login flows
- [ ] Set up role-based access control
- [ ] Remove mock user from App.js

### Phase 2: User Management
- [ ] Complete `/api/users` endpoint with proper auth
- [ ] Remove mock data from UserManagement.js
- [ ] Implement real user CRUD operations
- [ ] Add proper user roles and permissions

### Phase 3: Agency System
- [ ] Create `/api/agency/clients` endpoint
- [ ] Remove mock data from ClientSwitcher.js
- [ ] Implement real agency-client relationships
- [ ] Add client switching with real data

### Phase 4: Core Features
- [ ] Replace Dashboard.js mock data with real APIs
- [ ] Complete Contacts.js with real contact management
- [ ] Implement real campaign management
- [ ] Replace Messages.js with real conversation data

### Phase 5: DuxSoup Integration
- [ ] Complete DuxSoup user management
- [ ] Remove hardcoded credentials
- [ ] Implement real DuxSoup API integration
- [ ] Add proper error handling

### Phase 6: Analytics
- [ ] Implement real analytics data pipeline
- [ ] Remove mock performance metrics
- [ ] Add real-time data updates
- [ ] Complete reporting system

## 🚨 MOCK DATA DETECTION

### Environment Variable Approach
```javascript
// Add to .env files
REACT_APP_USE_MOCK_DATA=true  // Local development
REACT_APP_USE_MOCK_DATA=false // Production

// Usage in components:
const useMockData = process.env.REACT_APP_USE_MOCK_DATA === 'true';
```

### Logging System
```javascript
// Add to each component using mock data
if (useMockData) {
  console.warn('🎭 MOCK DATA ACTIVE:', {
    component: 'UserManagement',
    dataType: 'user_list',
    count: mockUsers.length,
    production_ready: false
  });
}
```

## 📋 TESTING CHECKLIST

### Before Production Deployment
- [ ] Set `REACT_APP_USE_MOCK_DATA=false`
- [ ] Verify all API endpoints return real data
- [ ] Test authentication flows
- [ ] Verify no console.warn mock data messages
- [ ] Test all CRUD operations with real database
- [ ] Verify DuxSoup integration with real credentials
- [ ] Test agency client switching with real data
- [ ] Validate all analytics show real metrics

### Mock Data Audit Commands
```bash
# Search for mock data in codebase
grep -r "mock" frontend/src/components/
grep -r "Mock" frontend/src/components/
grep -r "demo" frontend/src/components/
grep -r "fallback" frontend/src/components/

# Search for hardcoded credentials
grep -r "TEST_USER_ID" app/
grep -r "TEST_API_KEY" app/
grep -r "demo123" app/
```

## 🎯 MOCK DATA REMOVAL PRIORITY

### High Priority (Core Functionality)
1. **Authentication System** - App.js mock user
2. **User Management** - UserManagement.js user list
3. **Agency System** - ClientSwitcher.js client list

### Medium Priority (Business Logic)
4. **Dashboard Metrics** - Dashboard.js statistics
5. **Contact Management** - Contacts.js contact lists
6. **Campaign System** - Campaign mock data

### Lower Priority (Nice to Have)
7. **Analytics Data** - Analytics.js performance metrics
8. **Message History** - Messages.js conversation data
9. **DuxSoup Settings** - DuxSoup configuration fallbacks

---

**⚠️ IMPORTANT:** This checklist must be reviewed and updated whenever new mock data is added to the codebase. All mock data should be documented here with clear production migration paths.
