#!/bin/bash

# Install dependencies first
pip install fastapi uvicorn sqlalchemy asyncpg alembic python-multipart python-dotenv pandas numpy pydantic httpx aiofiles jinja2 email-validator psycopg2-binary pytz

# Start the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000