# 🚀 **Agency Multi-Client System - Testing Guide**

## ✅ **System Status: READY FOR TESTING**

### **🌐 Running Services:**
- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Database**: SQLite (chaknal.db)

---

## 🧪 **How to Test the Agency System**

### **1. Frontend Testing**
1. **Open Browser**: Go to http://localhost:3000
2. **Agency Mode**: The app is currently set to agency mode (demo)
3. **Navigation**: You'll see:
   - **Agency Overview** in the sidebar
   - **Client Switcher** at the top of the main content
   - **Same Dashboard** for all client management

### **2. Agency Features to Test**

#### **Agency Overview Dashboard**
- **URL**: http://localhost:3000/agency
- **Features**:
  - View all managed clients
  - See aggregate statistics
  - Recent activity log
  - Client management buttons

#### **Client Switching**
- **Location**: Top of main content area
- **Features**:
  - Dropdown with all clients
  - Client statistics display
  - Seamless switching between accounts
  - Same interface for all clients

#### **Read-Only User Creation**
- **API Endpoint**: `POST /api/agency/create-read-only-user`
- **Purpose**: Create customer access accounts
- **Features**:
  - Read-only access to client data
  - No client switching capability
  - Same dashboard interface

### **3. API Testing**

#### **Agency Endpoints** (All require authentication):
```
GET    /api/agency/clients                    # Get managed clients
POST   /api/agency/clients/add               # Add client to agency
DELETE /api/agency/clients/{id}              # Remove client
POST   /api/agency/switch-client/{id}        # Switch client context
GET    /api/agency/overview                  # Get agency overview
POST   /api/agency/create-read-only-user     # Create read-only user
GET    /api/agency/available-companies       # Get available companies
```

#### **Test with API Documentation**:
1. Go to http://localhost:8000/docs
2. Find "Agency Management" section
3. Test endpoints (requires authentication)

### **4. Database Verification**
- **Tables Created**:
  - `agency_client` - Agency-client relationships
  - `agency_invitation` - Client invitations
  - `agency_activity_log` - Activity tracking
  - Updated `user` table with agency fields
  - Updated `company` table with timestamps

---

## 🎯 **Testing Scenarios**

### **Scenario 1: Agency User Experience**
1. **Login** as agency user
2. **View Overview** - See all managed clients
3. **Select Client** - Use client switcher
4. **Manage Data** - Full access to client's DuxSoup, campaigns, contacts
5. **Switch Client** - Move to different client account
6. **Create Read-Only** - Generate customer access

### **Scenario 2: Read-Only User Experience**
1. **Login** as read-only user
2. **View Dashboard** - Same interface as regular users
3. **Browse Data** - Can see all analytics, campaigns, contacts
4. **No Editing** - Cannot modify any settings or data
5. **No Switching** - Cannot access other client accounts

### **Scenario 3: Regular User Experience**
1. **Login** as regular user
2. **Standard Dashboard** - Normal client experience
3. **Full Access** - Can manage their own data
4. **No Agency Features** - No client switcher or agency tools

---

## 🔧 **Development Notes**

### **Current Demo Configuration**:
- **Agency User**: `agency@chaknal.com`
- **Mock Data**: Uses demo companies and users
- **Authentication**: Bypassed for demo purposes

### **Production Setup**:
- Enable proper authentication
- Create real agency and client accounts
- Configure proper user roles and permissions

---

## 🚨 **Troubleshooting**

### **If Backend Not Running**:
```bash
cd /Users/lacomp/Desktop/chaknal-platform
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **If Frontend Not Running**:
```bash
cd /Users/lacomp/Desktop/chaknal-platform/frontend
npm start
```

### **If Database Issues**:
- Check `chaknal.db` exists
- Verify all agency tables are created
- Run database verification script

---

## 🎉 **Ready to Test!**

The complete agency multi-client system is now running and ready for testing. You can:

1. **Test the UI** at http://localhost:3000
2. **Test the API** at http://localhost:8000/docs
3. **Create agency accounts** and manage multiple clients
4. **Generate read-only access** for customers
5. **Switch between client accounts** seamlessly

**Everything is working and ready for your testing!** 🚀
