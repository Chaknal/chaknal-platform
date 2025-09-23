# 🚀 DuxSoup Integration Guide for Chaknal Platform

## Overview

This guide covers the integration of our new, production-ready DuxSoup wrapper with the Chaknal Platform. Our wrapper is designed specifically for our LinkedIn automation system and provides a clean, async-first interface to all DuxSoup APIs.

## 🏗️ Architecture

### Core Components

1. **`DuxSoupWrapper`** - Main wrapper class for individual DuxSoup users
2. **`DuxSoupManager`** - Multi-tenant manager for handling multiple accounts
3. **`DuxSoupUser`** - User configuration dataclass
4. **`DuxSoupCommand`** - Command configuration dataclass
5. **`DuxSoupResponse`** - Standardized API response format

### Key Features

- ✅ **Async-first design** with `aiohttp`
- ✅ **Built-in rate limiting** and retry logic
- ✅ **Comprehensive error handling** with custom exceptions
- ✅ **Multi-tenant support** for managing multiple DuxSoup accounts
- ✅ **Direct database integration** with our models
- ✅ **Campaign and sequence management**
- ✅ **Real-time status tracking**

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
pip install aiohttp
```

### 2. Environment Variables

Add to your `.env` file:

```env
# DuxSoup Configuration
DUXSOUP_BASE_URL=https://app.dux-soup.com/xapi/remote/control
DUXSOUP_DEFAULT_RATE_LIMIT=1.0
```

### 3. Import the Wrapper

```python
from app.services.duxwrap_new import (
    DuxSoupWrapper, 
    DuxSoupUser, 
    DuxSoupCommand, 
    DuxSoupManager
)
```

## 📱 Basic Usage

### Creating a DuxSoup User

```python
# Create user configuration
dux_user = DuxSoupUser(
    userid="your_dux_user_id",
    apikey="your_dux_api_key",
    label="Production User",
    daily_limits={
        "max_invites": 100,
        "max_messages": 50,
        "max_visits": 200
    },
    automation_settings={
        "auto_connect": True,
        "auto_message": True,
        "auto_endorse": False,
        "auto_follow": False
    },
    rate_limit_delay=1.0
)
```

### Using the Wrapper

```python
# Use async context manager for automatic session management
async with DuxSoupWrapper(dux_user) as wrapper:
    # Queue a profile visit
    response = await wrapper.visit_profile(
        "https://linkedin.com/in/targetuser",
        campaign_id="campaign_123"
    )
    
    if response.success:
        print(f"Visit queued: {response.message_id}")
    else:
        print(f"Error: {response.error}")
```

### Multi-tenant Management

```python
# Create manager
manager = DuxSoupManager()

# Add multiple users
await manager.add_user("user1", dux_user1)
await manager.add_user("user2", dux_user2)

# Get user wrapper
wrapper = manager.get_user("user1")

# Cleanup when done
await manager.cleanup()
```

## 🔌 API Methods

### LinkedIn Activity API

| Method | Description | Parameters |
|--------|-------------|------------|
| `visit_profile()` | Queue profile visit | `profile_url`, `campaign_id`, `force` |
| `connect_profile()` | Queue connection request | `profile_url`, `message_text`, `campaign_id`, `force` |
| `send_message()` | Queue direct message | `profile_url`, `message_text`, `campaign_id`, `force` |
| `send_inmail()` | Queue InMail message | `profile_url`, `subject`, `message_text`, `campaign_id`, `force` |
| `follow_profile()` | Queue profile follow | `profile_url`, `campaign_id`, `force` |
| `endorse_profile()` | Queue profile endorsement | `profile_url`, `skills`, `campaign_id`, `force` |
| `tag_profile()` | Queue profile tagging | `profile_url`, `tags`, `campaign_id`, `force` |
| `save_to_pdf()` | Queue profile PDF save | `profile_url`, `campaign_id`, `force` |
| `save_as_lead()` | Queue profile save as lead | `profile_url`, `campaign_id`, `force` |

### Queue Management API

| Method | Description | Parameters |
|--------|-------------|------------|
| `get_queue_size()` | Get queue size | `campaign_id`, `profile_id`, `command` |
| `get_queue_items()` | Get queue items | `campaign_id`, `profile_id`, `command` |
| `clear_queue()` | Clear all queued messages | None |

### User Settings API

| Method | Description | Parameters |
|--------|-------------|------------|
| `get_settings()` | Get all user settings | None |
| `update_settings()` | Update user settings | `settings` |
| `update_daily_limits()` | Update daily activity limits | `max_invites`, `max_messages`, `max_visits` |
| `update_automation_settings()` | Update automation settings | `auto_connect`, `auto_message`, `auto_endorse`, `auto_follow` |

### Extension Control API

| Method | Description | Parameters |
|--------|-------------|------------|
| `reload_extension()` | Force extension reload | None |
| `check_message_bridge()` | Check message bridge | `box_name`, `days_back` |
| `reset_data()` | Clear captured profile data | None |

### User Profile API

| Method | Description | Parameters |
|--------|-------------|------------|
| `get_profile()` | Get user profile information | None |

## 🎯 Campaign Integration

### Creating Campaign Commands

```python
# Create a sequence of commands for a campaign
commands = [
    DuxSoupCommand(
        command="visit",
        params={"profile": "https://linkedin.com/in/user1"},
        campaign_id="campaign_123",
        priority=5
    ),
    DuxSoupCommand(
        command="connect",
        params={
            "profile": "https://linkedin.com/in/user1",
            "messagetext": "Hi! I'd like to connect."
        },
        campaign_id="campaign_123",
        priority=4
    ),
    DuxSoupCommand(
        command="message",
        params={
            "profile": "https://linkedin.com/in/user1",
            "messagetext": "Thanks for connecting! How are you?"
        },
        campaign_id="campaign_123",
        priority=3
    )
]

# Queue all commands
async with DuxSoupWrapper(dux_user) as wrapper:
    responses = await wrapper.batch_queue_actions(commands)
    
    for i, response in enumerate(responses):
        if response.success:
            print(f"Command {i+1} queued: {response.message_id}")
        else:
            print(f"Command {i+1} failed: {response.error}")
```

### Campaign Status Tracking

```python
# Get comprehensive queue health
health = await wrapper.get_queue_health()

print(f"Queue size: {health['size']}")
print(f"Recent items: {health['items']}")
print(f"User profile: {health['profile']}")
print(f"Errors: {health['errors']}")
```

## 🚨 Error Handling

### Custom Exceptions

```python
from app.services.duxwrap_new import (
    DuxSoupAPIError,
    DuxSoupRateLimitError,
    DuxSoupAuthenticationError
)

try:
    response = await wrapper.visit_profile("https://linkedin.com/in/user")
except DuxSoupRateLimitError:
    print("Rate limit exceeded, waiting...")
    await asyncio.sleep(60)
except DuxSoupAuthenticationError:
    print("Authentication failed, check credentials")
except DuxSoupAPIError as e:
    print(f"API error: {e}")
```

### Response Validation

```python
response = await wrapper.connect_profile("https://linkedin.com/in/user")

if response.success:
    # Success case
    message_id = response.message_id
    data = response.data
    print(f"Connection queued: {message_id}")
else:
    # Error case
    error = response.error
    print(f"Failed to queue connection: {error}")
```

## 📊 Monitoring & Statistics

### Wrapper Statistics

```python
stats = wrapper.get_stats()

print(f"Version: {stats['version']}")
print(f"User ID: {stats['user_id']}")
print(f"Request count: {stats['request_count']}")
print(f"Error count: {stats['error_count']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Rate limit delay: {stats['rate_limit_delay']}s")
```

### Manager Statistics

```python
all_stats = manager.get_all_stats()

for user_id, user_stats in all_stats.items():
    print(f"User {user_id}:")
    print(f"  Success rate: {user_stats['success_rate']:.1f}%")
    print(f"  Request count: {user_stats['request_count']}")
```

## 🔄 Integration with Existing Services

### Update LinkedIn Automation Service

```python
# In app/services/linkedin_automation.py
from app.services.duxwrap_new import DuxSoupWrapper, DuxSoupUser

async def get_dux_wrapper(dux_user_id: str) -> DuxSoupWrapper:
    """Get DuxSoup wrapper for a user"""
    # Get DuxSoup user from database
    dux_user = await get_dux_user_from_db(dux_user_id)
    
    # Create wrapper
    wrapper = DuxSoupWrapper(dux_user)
    await wrapper.__aenter__()
    
    return wrapper

async def execute_campaign_step(campaign_id: str, step_type: str, profile_url: str):
    """Execute a campaign step using the new wrapper"""
    wrapper = await get_dux_wrapper(campaign_id)
    
    try:
        if step_type == "visit":
            response = await wrapper.visit_profile(profile_url, campaign_id)
        elif step_type == "connect":
            response = await wrapper.connect_profile(profile_url, campaign_id=campaign_id)
        elif step_type == "message":
            response = await wrapper.send_message(profile_url, "Hello!", campaign_id)
        
        # Handle response
        if response.success:
            # Update database with success
            await update_campaign_step_status(campaign_id, "completed", response.message_id)
        else:
            # Handle error
            await update_campaign_step_status(campaign_id, "failed", error=response.error)
            
    finally:
        await wrapper.__aexit__(None, None, None)
```

## 🧪 Testing

### Run Standalone Tests

```bash
python3 test_duxwrap_simple.py
```

### Test with Real API

```python
# Create real user configuration
real_user = DuxSoupUser(
    userid="your_real_user_id",
    apikey="your_real_api_key"
)

# Test real API calls
async with DuxSoupWrapper(real_user) as wrapper:
    # Test profile visit
    response = await wrapper.visit_profile("https://linkedin.com/in/testuser")
    print(f"Real API response: {response}")
```

## 🚀 Production Deployment

### Docker Configuration

```dockerfile
# Add to your Dockerfile
RUN pip install aiohttp
```

### Environment Configuration

```yaml
# docker-compose.yml
environment:
  - DUXSOUP_BASE_URL=https://app.dux-soup.com/xapi/remote/control
  - DUXSOUP_DEFAULT_RATE_LIMIT=1.0
```

### Health Checks

```python
# Add to your health check endpoint
async def check_dux_wrapper_health():
    """Check DuxSoup wrapper health"""
    try:
        # Test with a mock user
        test_user = DuxSoupUser(userid="test", apikey="test")
        async with DuxSoupWrapper(test_user) as wrapper:
            # Test signature creation
            signature = wrapper._create_signature("test")
            return {"status": "healthy", "signature_test": "passed"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## 📝 Best Practices

### 1. Always Use Async Context Manager

```python
# ✅ Good
async with DuxSoupWrapper(dux_user) as wrapper:
    response = await wrapper.visit_profile(url)

# ❌ Bad
wrapper = DuxSoupWrapper(dux_user)
response = await wrapper.visit_profile(url)
# Forgot to close session!
```

### 2. Handle Rate Limits Gracefully

```python
# Use exponential backoff for rate limits
try:
    response = await wrapper.visit_profile(url)
except DuxSoupRateLimitError:
    await asyncio.sleep(60)  # Wait 1 minute
    response = await wrapper.visit_profile(url)  # Retry
```

### 3. Validate Responses

```python
response = await wrapper.connect_profile(url, message)

if not response.success:
    logger.error(f"Failed to queue connection: {response.error}")
    # Handle error appropriately
    return None

# Use response data
message_id = response.message_id
```

### 4. Monitor Performance

```python
# Log wrapper statistics periodically
stats = wrapper.get_stats()
logger.info(f"DuxSoup wrapper stats: {stats}")

if stats['success_rate'] < 90:
    logger.warning(f"Low success rate: {stats['success_rate']}%")
```

## 🔗 Related Files

- `app/services/duxwrap_new.py` - Main wrapper implementation
- `app/services/linkedin_automation.py` - Integration service
- `app/api/automation.py` - API endpoints
- `test_duxwrap_simple.py` - Standalone tests
- `DUXSOUP_INTEGRATION.md` - This guide

## 📞 Support

For issues or questions about the DuxSoup wrapper:

1. Check the test output for basic functionality
2. Review error logs for specific issues
3. Verify DuxSoup credentials and API access
4. Check rate limiting and daily limits
5. Review network connectivity and firewall settings

---

**🎯 Next Steps:**
1. ✅ Test the wrapper functionality
2. 🔄 Integrate with existing automation service
3. 🧪 Test with real DuxSoup API
4. 🚀 Deploy to production
5. 📊 Monitor performance and success rates
