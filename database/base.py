from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to ensure they are registered with SQLAlchemy
# This is needed for Alembic to detect the models
import app.models.user
import app.models.company
import app.models.campaign
import app.models.contact
import app.models.campaign_contact
import app.models.message
import app.models.webhook_event
import app.models.duxsoup_user
import app.models.duxsoup_queue
import app.models.duxsoup_user_settings
import app.models.duxsoup_execution_log

# This ensures all models are available when creating tables
__all__ = ["Base"]
