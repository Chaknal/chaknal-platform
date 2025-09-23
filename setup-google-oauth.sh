#!/bin/bash

# Google OAuth Setup Script for Chaknall Platform
# This script helps you configure Google OAuth credentials

echo "🔐 Setting up Google OAuth for Chaknall Platform"
echo "=================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created"
else
    echo "📝 .env file already exists"
fi

echo ""
echo "🚀 Step 1: Create Google OAuth Credentials"
echo "==========================================="
echo "1. Go to: https://console.cloud.google.com/"
echo "2. Create a new project or select existing one"
echo "3. Enable Google+ API:"
echo "   - Go to 'APIs & Services' → 'Library'"
echo "   - Search for 'Google+ API' or 'Google Identity'"
echo "   - Click 'Enable'"
echo ""
echo "4. Create OAuth 2.0 Credentials:"
echo "   - Go to 'APIs & Services' → 'Credentials'"
echo "   - Click 'Create Credentials' → 'OAuth 2.0 Client IDs'"
echo "   - Application Type: Web application"
echo "   - Name: Chaknall Platform"
echo "   - Authorized redirect URIs:"
echo "     * Development: http://localhost:8000/auth/google/callback"
echo "     * Production: https://chacker-cdc9h6fahefudtgg.westus-01.azurewebsites.net/auth/google/callback"
echo ""

# Prompt for Google credentials
echo "🔑 Step 2: Enter Your Google OAuth Credentials"
echo "==============================================="

read -p "Enter your Google Client ID: " GOOGLE_CLIENT_ID
read -p "Enter your Google Client Secret: " GOOGLE_CLIENT_SECRET

# Update .env file
if [ -f ".env" ]; then
    # Update Google OAuth settings
    sed -i.bak "s/GOOGLE_CLIENT_ID=.*/GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID/" .env
    sed -i.bak "s/GOOGLE_CLIENT_SECRET=.*/GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET/" .env
    
    echo "✅ Google OAuth credentials updated in .env file"
else
    echo "❌ .env file not found. Please create it first."
    exit 1
fi

echo ""
echo "🧪 Step 3: Test Google OAuth"
echo "============================="
echo "1. Start your application:"
echo "   cd chaknal-platform"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Test Google OAuth:"
echo "   - Visit: http://localhost:8000/auth/google/login"
echo "   - Complete the OAuth flow"
echo "   - Should redirect to: http://localhost:3000/auth/callback?token=...&email=..."
echo ""

echo "🔧 Step 4: Production Configuration"
echo "==================================="
echo "For production deployment, set these in Azure Portal:"
echo "- Go to Azure Portal → chaknal-platform-2024 → Configuration → Application settings"
echo "- Add these settings:"
echo "  * GOOGLE_CLIENT_ID = $GOOGLE_CLIENT_ID"
echo "  * GOOGLE_CLIENT_SECRET = $GOOGLE_CLIENT_SECRET"
echo "  * GOOGLE_REDIRECT_URI = https://chacker-cdc9h6fahefudtgg.westus-01.azurewebsites.net/auth/google/callback"
echo ""

echo "✅ Google OAuth setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Test the OAuth flow locally"
echo "2. Configure production environment variables"
echo "3. Test in production"
echo "4. Add user registration functionality" 

---

### **Step-by-Step Instructions**

#### 1. **Open your Terminal**
- On Mac: Press `Cmd + Space`, type **Terminal**, and press Enter.
- Or use the integrated terminal in VS Code (`` Ctrl+` ``).

#### 2. **Run your Docker container with environment variables**
Replace the values with your actual secrets and database URL:
```sh
docker run -e SECRET_KEY=your_secret -e DATABASE_URL=your_db_url -p 8000:80 sercio/chaknal-platform:latest
```
- This command tells Docker to:
  - Set the `SECRET_KEY` and `DATABASE_URL` environment variables inside the container.
  - Map port 80 in the container to port 8000 on your computer.
  - Run the image `sercio/chaknal-platform:latest`.

#### 3. **Watch for Output**
- If the app starts, you’ll see logs in your terminal.
- If it crashes, you’ll see error messages—**copy and paste those here**.

#### 4. **If the Container Exits Immediately**
- List all containers (including stopped ones):
  ```sh
  docker ps -a
  ```
- Find the container ID for the one that just exited.
- View its logs:
  ```sh
  docker logs <container_id>
  ```
  (Replace `<container_id>` with the actual ID.)

#### 5. **Test in Browser**
- If the container is running, open your browser and go to:  
  [http://localhost:8000/health](http://localhost:8000/health)

---

**If you get any errors or see output you don’t understand, copy it here and I’ll help you troubleshoot!** 

Here’s the exact Docker command you should copy and paste into your terminal, using your provided environment variables:

```sh
docker run \
  -e SECRET_KEY=A5GIneIlYYCHM4bqpqhY9yZZU3icQVxr5oStOLjd7Ws \
  -e DATABASE_URL=tziban.postgres.database.azure.com \
  -e DEBUG=false \
  -e DOCKER_REGISTRY_SERVER_URL=https://index.docker.io/v1 \
  -e ENVIRONMENT=production \
  -e WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
  -p 8000:80 \
  sercio/chaknal-platform:latest
```

**Instructions:**
1. Copy the entire command above.
2. Paste it into your terminal.
3. Press Enter.

**What happens next:**
- The container will start (or fail) and you’ll see logs in your terminal.
- If you see any errors, copy and paste them here so I can help you troubleshoot!

**Tip:**  
If your `DATABASE_URL` needs to be a full connection string (not just the host), you may need to update it to something like:
```
postgresql+asyncpg://username:password@tziban.postgres.database.azure.com:5432/dbname
```
Let me know if you need help with the full connection string! 

---

## **Critical Error in Your Logs**

```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from given URL string
```

**Root Cause:**  
Your `DATABASE_URL` is set to just `tziban.postgres.database.azure.com`, which is **not a valid SQLAlchemy connection string**.  
It needs to be a **full connection string** including the database dialect, username, password, host, port, and database name.

---

## **How to Fix**

### 1. **Update Your DATABASE_URL**

For PostgreSQL with async support, the format should be:

```
<code_block_to_apply_changes_from>
```

**Example:**
```
postgresql+asyncpg://myuser:mypassword@tziban.postgres.database.azure.com:5432/mydatabase
```

- Replace `myuser`, `mypassword`, and `mydatabase` with your actual PostgreSQL credentials and database name.

---

### 2. **Run the Docker Command Again**

Update your Docker command to use the full connection string, for example:

```sh
docker run \
  -e SECRET_KEY=A5GIneIlYYCHM4bqpqhY9yZZU3icQVxr5oStOLjd7Ws \
  -e DATABASE_URL=postgresql+asyncpg://myuser:mypassword@tziban.postgres.database.azure.com:5432/mydatabase \
  -e DEBUG=false \
  -e DOCKER_REGISTRY_SERVER_URL=https://index.docker.io/v1 \
  -e ENVIRONMENT=production \
  -e WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
  -p 8000:80 \
  sercio/chaknal-platform:latest
```

---

### 3. **What to Expect**

- If the credentials are correct and the database is accessible, your app should start up and you’ll see logs indicating it’s running.
- If there’s another error, copy and paste the new logs here.

---

**Let me know if you need help finding your PostgreSQL connection string or credentials!**  
Once you update the `DATABASE_URL`, your app should start both locally and on Azure. 

---

## **Critical Error in Your Logs**

```
AttributeError: 'Settings' object has no attribute 'SECRET'
```

---

## **What This Means**

- Your code is trying to access `settings.SECRET`, but your settings/configuration only has `SECRET_KEY`.
- This is a **typo** in your code and will cause your app to crash on startup, both locally and on Azure.

---

## **How to Fix**

1. **Find all places in your code where you use `settings.SECRET`.**
2. **Change them to use `settings.SECRET_KEY` instead.**

**Example:**
```python
# WRONG
reset_password_token_secret = settings.SECRET

# CORRECT
reset_password_token_secret = settings.SECRET_KEY
```

---

### **What to Do Next**

1. **Search your codebase for `settings.SECRET` and replace it with `settings.SECRET_KEY`.**
   - Most likely in `app/api/auth.py` or similar files.
2. **Rebuild your Docker image:**
   ```sh
   docker build -t sercio/chaknal-platform:latest .
   ```
3. **Push the new image to Docker Hub:**
   ```sh
   docker push sercio/chaknal-platform:latest
   ```
4. **Run your Docker container again with the correct environment variables.**

---

**Once you fix this typo and rebuild, your app should start! If you need help finding the exact line, let me know.** 

---

## **How to Find the Correct Directory**

1. **Check your current directory:**
   ```sh
   pwd
   ```
   This will show you where you are in your filesystem.

2. **List the contents to see your folders:**
   ```sh
   ls
   ```
   Look for the `chaknal-platform` directory.

3. **Navigate to the correct directory:**
   If you are in your project root and see `chaknal-platform` listed, run:
   ```sh
   cd chaknal-platform
   ```

4. **Verify the Dockerfile is present:** 