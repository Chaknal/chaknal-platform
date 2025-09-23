# 🚀 DuxSoup Sequence Integration Guide

## Overview

This guide explains how the Chaknal Platform now integrates with DuxSoup to automatically execute LinkedIn automation sequences when contacts are assigned to team members.

## 🔄 How It Works

### 1. **Contact Assignment Flow**
```
User assigns contacts → Launch sequence → DuxSoup API calls → Status updates via webhooks
```

### 2. **Sequence Execution Process**

#### **Step 1: Assignment & Launch**
- User assigns contacts to team members in the UI
- User clicks "Launch Sequence" for a specific team member
- System finds all pending contacts assigned to that user

#### **Step 2: DuxSoup API Integration**
- System retrieves DuxSoup user credentials from database
- Creates DuxSoup API wrapper with proper authentication
- Executes LinkedIn actions for each assigned contact

#### **Step 3: LinkedIn Actions**
- **Visit Profile** (if enabled in campaign)
- **Send Connection Request** with personalized message
- **Schedule Follow-up Messages** based on campaign settings
- **Update Contact Status** in real-time

#### **Step 4: Status Tracking**
- DuxSoup sends webhooks when actions complete
- System updates contact status automatically
- UI reflects real-time status changes

## 🛠️ Technical Implementation

### **New Components Added:**

#### **1. DuxSequenceLauncher Service** (`app/services/dux_sequence_launcher.py`)
- Handles all DuxSoup API interactions
- Manages sequence execution for assigned contacts
- Processes webhook status updates
- Implements rate limiting and error handling

#### **2. Enhanced API Endpoints** (`app/api/contact_assignment.py`)
- **`POST /api/campaigns/{campaign_id}/launch-sequence`** - Launches sequences with DuxSoup
- **`POST /api/webhooks/dux-status-update`** - Handles DuxSoup webhook updates

#### **3. DuxSoup Integration Features:**
- **Real API Calls**: Actually sends LinkedIn actions through DuxSoup
- **Personalized Messages**: Uses contact data to customize messages
- **Follow-up Scheduling**: Automatically schedules follow-up actions
- **Status Tracking**: Real-time status updates via webhooks
- **Error Handling**: Comprehensive error handling and logging

## 📋 Configuration Requirements

### **1. DuxSoup User Setup**
You need to configure DuxSoup user credentials in your database:

```sql
INSERT INTO duxsoup_user (
    dux_soup_user_id,
    dux_soup_auth_key,
    email,
    first_name,
    last_name
) VALUES (
    'your_dux_user_id',
    'your_dux_api_key',
    'user@example.com',
    'John',
    'Doe'
);
```

### **2. Campaign Configuration**
Link campaigns to DuxSoup users:

```sql
UPDATE campaigns_new 
SET dux_user_id = 'your_dux_user_id'
WHERE campaign_id = 'your_campaign_id';
```

### **3. Webhook Configuration**
Configure DuxSoup to send webhooks to your platform:

**Webhook URL**: `https://your-domain.com/api/webhooks/dux-status-update`

**Webhook Payload Format**:
```json
{
    "campaign_id": "campaign-uuid",
    "contact_id": "contact-uuid",
    "status": "accepted|replied|declined|blacklisted",
    "profile_url": "https://linkedin.com/in/profile"
}
```

## 🎯 Sequence Types Supported

### **1. Connection Sequence**
```
Visit Profile → Send Connection Request → Schedule Follow-up Message
```

### **2. Direct Message Sequence**
```
Send Initial Message → Schedule Follow-up Messages
```

### **3. Custom Sequences**
Based on campaign configuration:
- **Initial Action**: `visit`, `connect`, `message`
- **Follow-up Actions**: Array of actions to execute
- **Delay Days**: Time between actions
- **Random Delay**: Add randomization to avoid detection

## 📊 Status Tracking

### **Contact Status Flow:**
```
pending → active → accepted → responded → completed
```

### **Status Meanings:**
- **`pending`**: Contact assigned, waiting for sequence launch
- **`active`**: Sequence launched, actions sent to DuxSoup
- **`accepted`**: Connection request accepted
- **`responded`**: Contact replied to message
- **`not_accepted`**: Connection request declined
- **`blacklisted`**: Contact blocked or reported
- **`completed`**: Sequence finished successfully

## 🔧 API Usage Examples

### **Launch Sequence for User**
```bash
curl -X POST "http://localhost:8001/api/campaigns/{campaign_id}/launch-sequence" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-uuid"}'
```

### **Webhook Status Update**
```bash
curl -X POST "http://localhost:8001/api/webhooks/dux-status-update" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "campaign-uuid",
    "contact_id": "contact-uuid", 
    "status": "accepted",
    "profile_url": "https://linkedin.com/in/profile"
  }'
```

## 🚨 Error Handling

### **Common Issues & Solutions:**

#### **1. DuxSoup User Not Configured**
```
Error: "DuxSoup user not configured"
Solution: Add DuxSoup credentials to duxsoup_user table
```

#### **2. Invalid LinkedIn URL**
```
Error: "No LinkedIn URL available"
Solution: Ensure contacts have valid linkedin_url field
```

#### **3. API Rate Limiting**
```
Error: "Rate limit exceeded"
Solution: System automatically handles rate limiting with delays
```

#### **4. Webhook Failures**
```
Error: "Failed to update status"
Solution: Check webhook URL configuration in DuxSoup
```

## 📈 Monitoring & Analytics

### **Real-time Status Updates:**
- Contact status changes are reflected immediately in the UI
- Assignment breakdown shows current status for each user
- Detailed filtering by status and user

### **Performance Metrics:**
- Success rate of connection requests
- Response rate to messages
- Time to completion for sequences
- User performance comparison

## 🔒 Security Considerations

### **API Key Management:**
- DuxSoup API keys stored securely in database
- Keys are not exposed in API responses
- Proper authentication for webhook endpoints

### **Rate Limiting:**
- Built-in delays between API calls
- Respects DuxSoup's rate limits
- Prevents account suspension

### **Data Privacy:**
- Contact data is handled securely
- LinkedIn URLs are validated
- Personal information is protected

## 🎉 Benefits

### **For Users:**
- **Automated Outreach**: No manual LinkedIn actions needed
- **Real-time Tracking**: See status updates as they happen
- **Team Management**: Assign contacts to team members
- **Performance Analytics**: Track success rates and responses

### **For Administrators:**
- **Centralized Control**: Manage all LinkedIn automation from one platform
- **Scalable Operations**: Handle hundreds of contacts efficiently
- **Compliance**: Built-in rate limiting and error handling
- **Integration**: Seamless integration with existing campaign management

## 🚀 Next Steps

1. **Configure DuxSoup Credentials**: Add your DuxSoup user credentials to the database
2. **Set Up Webhooks**: Configure DuxSoup to send status updates to your platform
3. **Test Integration**: Launch sequences with a small group of contacts
4. **Monitor Performance**: Track success rates and optimize sequences
5. **Scale Up**: Gradually increase the number of contacts and team members

## 📞 Support

If you encounter any issues with the DuxSoup integration:

1. Check the application logs for detailed error messages
2. Verify DuxSoup credentials are correctly configured
3. Ensure webhook URL is accessible from DuxSoup
4. Test with a small number of contacts first
5. Monitor rate limits and API quotas

---

**🎯 The DuxSoup integration is now fully implemented and ready for production use!**
