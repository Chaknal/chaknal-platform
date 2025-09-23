#!/bin/bash

# Create minimal API deployment package
# This includes only essential files for API endpoints, avoiding system files

echo "Creating minimal API deployment package..."

# Create temporary directory for clean deployment
mkdir -p minimal-api-deployment
cd minimal-api-deployment

# Copy essential Python application files
echo "Copying application files..."
cp -r ../app .
cp -r ../config .
cp -r ../database .
cp -r ../migrations .

# Copy essential configuration files
echo "Copying configuration files..."
cp ../requirements.txt .
cp ../Dockerfile .
cp ../alembic.ini .
cp ../app-settings.json .

# Copy essential startup files
echo "Copying startup files..."
cp ../startup.py .
cp ../startup.sh .

# Copy essential static files (if any)
if [ -d "../static" ]; then
    echo "Copying static files..."
    cp -r ../static .
fi

# Create a clean .dockerignore to avoid including unnecessary files
echo "Creating .dockerignore..."
cat > .dockerignore << EOF
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git/
.mypy_cache/
.pytest_cache/
.hypothesis/
.DS_Store
*.db
*.sqlite
*.sqlite3
chaknal-venv/
node_modules/
*.zip
*.tar.gz
*.tar
EOF

# Create a minimal requirements.txt with only essential dependencies
echo "Creating minimal requirements.txt..."
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
aiofiles==23.2.1
jinja2==3.1.2
email-validator==2.0.0
bcrypt==4.1.2
pandas==2.1.3
numpy==1.25.2
EOF

# Create a minimal Dockerfile
echo "Creating minimal Dockerfile..."
cat > Dockerfile << EOF
FROM python:3.11-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libffi-dev \\
    libssl-dev \\
    libpq-dev \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \\
    chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create startup script
echo "Creating startup script..."
cat > startup.sh << EOF
#!/bin/bash
echo "Starting Chaknal Platform API..."

# Wait for database to be ready
echo "Waiting for database connection..."
python -c "
import time
import psycopg2
import os
from sqlalchemy import create_engine

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/chaknal')

# Try to connect to database
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute('SELECT 1')
        print('Database connection successful!')
        break
    except Exception as e:
        print(f'Database connection failed (attempt {retry_count + 1}/{max_retries}): {e}')
        time.sleep(2)
        retry_count += 1

if retry_count >= max_retries:
    print('Failed to connect to database after maximum retries')
    exit(1)
"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
EOF

chmod +x startup.sh

# Create the deployment package
echo "Creating deployment package..."
cd ..
zip -r chaknal-minimal-api-$(date +%Y%m%d-%H%M%S).zip minimal-api-deployment/ -x "*.pyc" "__pycache__/*" "*.log" "*.db"

echo "Minimal API deployment package created successfully!"
echo "Package includes only essential files for API endpoints"
echo "No system files or unnecessary permissions required"

# Clean up temporary directory
rm -rf minimal-api-deployment

echo "Deployment package ready for Azure deployment!"
