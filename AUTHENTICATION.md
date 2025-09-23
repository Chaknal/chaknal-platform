# Authentication Guide - Chaknall Platform

## 🔐 Authentication Methods

Your application supports two authentication methods:

### 1. JWT Authentication (Username/Password)
- **Status**: ✅ Implemented and ready
- **Use Case**: Traditional login for admin users
- **Endpoints**: `/auth/login`, `/auth/me`, `/auth/protected`

### 2. Google OAuth 2.0
- **Status**: ✅ Implemented and ready
- **Use Case**: Social login for end users
- **Endpoints**: `/auth/google/login`, `/auth/google/callback`

### 3. Microsoft/Azure AD Authentication
- **Status**: ❌ Not implemented
- **Use Case**: Enterprise users, Azure AD integration
- **Priority**: Low (can be added later if needed)

---

## 🚀 Setting Up Authentication

### JWT Authentication Setup

**Already configured!** Default credentials:
- Username: `admin`
- Password: `admin123`

**For Production:**
1. Change the default password in `app/auth/jwt_handler.py`
2. Add user registration endpoint
3. Implement password reset functionality

### Google OAuth Setup

#### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Configure:
   - **Application type**: Web application
   - **Name**: Chaknall Platform
   - **Authorized redirect URIs**:
     - Development: `http://localhost:8000/auth/google/callback`
     - Production: `https://chaknal-platform-2024.azurewebsites.net/auth/google/callback`

#### Step 2: Set Environment Variables

**Development (.env file):**
```bash
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

**Production (Azure Portal):**
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://chaknal-platform-2024.azurewebsites.net/auth/google/callback
```

#### Step 3: Test Google OAuth

1. **Start your application:**
   ```bash
   cd chaknal-platform
   uvicorn app.main:app --reload
   ```

2. **Test the flow:**
   - Visit: `http://localhost:8000/auth/google/login`
   - Complete Google OAuth flow
   - Should redirect to: `http://localhost:3000/auth/callback?token=...&email=...`

---

## 🧪 Testing Authentication

### Test JWT Authentication

```bash
# 1. Login to get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Response:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "token_type": "bearer"
# }

# 2. Use token to access protected endpoint
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/auth/protected

# Response:
# {
#   "message": "This is a protected route",
#   "user": "admin",
#   "status": "authenticated"
# }

# 3. Get current user info
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/auth/me
```

### Test Google OAuth

```bash
# 1. Start OAuth flow (opens browser)
curl -L "http://localhost:8000/auth/google/login"

# 2. After completing OAuth, you'll get redirected to:
# http://localhost:3000/auth/callback?token=...&email=...

# 3. Verify token (optional)
curl -X POST "http://localhost:8000/auth/google/verify-token" \
  -H "Content-Type: application/json" \
  -d '{"id_token": "your-google-id-token"}'
```

### Test Authentication Status

```bash
# Check auth system status
curl http://localhost:8000/api/auth/status

# Response:
# {
#   "jwt_auth": "enabled",
#   "google_oauth": "enabled",
#   "environment": "development",
#   "endpoints": {
#     "jwt_login": "/auth/login",
#     "google_login": "/auth/google/login",
#     "google_callback": "/auth/google/callback"
#   }
# }
```

---

## 🔧 Authentication Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | JWT signing key | ✅ | Generated |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | ❌ | 1440 (24h) |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | ❌ | "" |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | ❌ | "" |
| `GOOGLE_REDIRECT_URI` | OAuth redirect URI | ❌ | "" |

### Security Settings

**JWT Configuration:**
- Algorithm: HS256
- Token expiration: 24 hours (configurable)
- Secure secret key required

**Google OAuth Scopes:**
- `openid` - OpenID Connect
- `https://www.googleapis.com/auth/userinfo.email` - Email access
- `https://www.googleapis.com/auth/userinfo.profile` - Profile access

---

## 🛡️ Security Best Practices

### JWT Security
- ✅ Use strong secret key (32+ characters)
- ✅ Set reasonable token expiration
- ✅ Validate tokens on every request
- ✅ Store tokens securely on client

### OAuth Security
- ✅ Use HTTPS in production
- ✅ Validate redirect URIs
- ✅ Verify ID tokens
- ✅ Handle errors gracefully

### General Security
- ✅ Rate limiting enabled
- ✅ CORS properly configured
- ✅ Error messages don't leak sensitive info
- ✅ Log authentication events

---

## 🚨 Troubleshooting

### Common JWT Issues

**"Could not validate credentials"**
- Check SECRET_KEY is set
- Verify token hasn't expired
- Ensure token format is correct

**"Incorrect username or password"**
- Verify credentials in `jwt_handler.py`
- Check password hashing
- Test with known good credentials

### Common OAuth Issues

**"Google OAuth not configured"**
- Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
- Verify redirect URI matches Google Console
- Check environment variables

**"Invalid Google token"**
- Token may be expired
- Client ID mismatch
- Token format issue

**Redirect URI Mismatch**
- Ensure redirect URI in Google Console matches your app
- Check for trailing slashes
- Verify protocol (http vs https)

### Debug Steps

1. **Check environment variables:**
   ```bash
   curl http://localhost:8000/api/auth/status
   ```

2. **Test individual endpoints:**
   ```bash
   # Test JWT login
   curl -X POST "http://localhost:8000/auth/login" \
     -d "username=admin&password=admin123"
   
   # Test Google OAuth (opens browser)
   curl -L "http://localhost:8000/auth/google/login"
   ```

3. **Check logs:**
   ```bash
   # View application logs
   tail -f logs/app.log
   ```

---

## 🔄 Adding Microsoft Authentication

If you need Microsoft/Azure AD authentication later:

### Steps:
1. Register app in Azure AD
2. Get client ID and secret
3. Implement Microsoft OAuth handler
4. Add endpoints: `/auth/microsoft/login`, `/auth/microsoft/callback`
5. Update settings and documentation

### Dependencies needed:
```bash
pip install msal
```

### Example endpoints:
- `GET /auth/microsoft/login` - Start Microsoft OAuth
- `GET /auth/microsoft/callback` - Handle OAuth callback
- `POST /auth/microsoft/verify-token` - Verify Microsoft token

---

## 📋 Authentication Checklist

### JWT Authentication
- [ ] SECRET_KEY set and secure
- [ ] Token expiration configured
- [ ] Login endpoint working
- [ ] Protected endpoints working
- [ ] User info endpoint working

### Google OAuth
- [ ] Google OAuth credentials created
- [ ] Environment variables set
- [ ] Redirect URI configured
- [ ] Login flow working
- [ ] Callback handling working
- [ ] Token verification working

### Security
- [ ] HTTPS enabled (production)
- [ ] CORS configured
- [ ] Rate limiting enabled
- [ ] Error handling implemented
- [ ] Logging configured

### Testing
- [ ] JWT login tested
- [ ] Google OAuth tested
- [ ] Protected endpoints tested
- [ ] Error cases tested
- [ ] Token expiration tested

---

## 🎯 Next Steps

### Immediate (This Week)
1. ✅ Set up Google OAuth credentials
2. ✅ Test authentication flows
3. ✅ Configure production environment variables

### Short Term (Next 2 Weeks)
1. Add user registration endpoint
2. Implement password reset
3. Add email verification
4. Create user management dashboard

### Medium Term (Next Month)
1. Add role-based access control
2. Implement user profiles
3. Add session management
4. Consider Microsoft authentication if needed

---

## 📞 Support

For authentication issues:
1. Check environment variables
2. Test endpoints manually
3. Review application logs
4. Verify OAuth configuration
5. Test with known good credentials

**Emergency Reset:**
```bash
# Reset to default admin user
# Edit app/auth/jwt_handler.py and update fake_users_db
```

## 🔑 **What is SECRET_KEY?**
- It is a long, random string.
- Used to sign JWT tokens (so only your server can create/verify them).
- Should be unique and kept private (never share it publicly).
- If you change it, all existing tokens become invalid.

## 🛠️ **How to Generate a Secure SECRET_KEY**

You can generate a secure key using Python. Here's how:

### **Option 1: Use Python (Recommended)**
Open your terminal and run:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
This will output a long string, for example:
```
Qw8k2v1Jp3lK4mN5oP6qR7sT8uV9wX0yZ1aB2cD3eF4gH5iJ
```

### **Option 2: Use an Online Generator**
You can also use a trusted password generator (make sure it's at least 32 characters and uses letters, numbers, and symbols).

---

## 🔒 **How to Add SECRET_KEY in Azure Portal**

1. Copy the generated key.
2. In Azure Portal, go to your Web App → Configuration → Application settings.
3. Click **New application setting**.
4. Set:
   - **Name:** `SECRET_KEY`
   - **Value:** (paste your generated key)
5. Click **OK** and then **Save** at the top.

---

## ✅ **After Adding SECRET_KEY**
- Wait for your app to restart (1-2 minutes).
- Your authentication and sessions will now be secure.
- You can now safely use JWT and OAuth in production.

---

**Would you like me to generate a sample key for you right now, or do you want to run the command yourself?**  
Let me know if you want a sample key to copy! 

## 📋 **Endpoints to Test**

Try visiting these URLs in your browser or with a tool like `curl` or Postman:

1. **Health Check**
   - [https://chaknal-platform-2024-code.azurewebsites.net/health](https://chaknal-platform-2024-code.azurewebsites.net/health)
   - Should return:  
     ```json
     {"status": "healthy", "service": "chaknall-platform", ...}
     ``` 