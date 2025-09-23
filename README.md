# Chaknal Platform - LinkedIn Automation & CRM

A comprehensive LinkedIn automation and CRM platform built with FastAPI (Python) backend and React frontend, designed for agencies to manage multiple client campaigns.

## 🚀 Features

### Core Functionality
- **Multi-tenant Agency Management** - Manage multiple client accounts
- **LinkedIn Automation** - DuxSoup integration for profile visits, connections, and messaging
- **Campaign Management** - Create and manage outreach sequences
- **Contact Management** - Track prospects, responses, and meeting bookings
- **Real-time Analytics** - Performance metrics and reporting
- **Message Management** - Conversation tracking and management
- **Meeting Scheduling** - Track and manage meeting bookings

### Technical Features
- **Authentication System** - JWT-based user authentication
- **Database Integration** - SQLite (development) / PostgreSQL (production)
- **Mock Data Logging** - Development system to track mock vs real data
- **Responsive UI** - Modern React interface with Tailwind CSS
- **API Documentation** - FastAPI automatic documentation

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **API Layer**: FastAPI with automatic OpenAPI documentation
- **Database**: SQLAlchemy ORM with async support
- **Authentication**: JWT tokens with role-based access
- **External APIs**: DuxSoup integration for LinkedIn automation
- **File Storage**: Local storage (dev) / Azure Blob Storage (prod)

### Frontend (React + JavaScript)
- **UI Framework**: React with modern hooks
- **Styling**: Tailwind CSS for responsive design
- **State Management**: React hooks and context
- **Routing**: React Router for SPA navigation
- **API Client**: Axios for HTTP requests

### Database Schema
- **Users & Companies**: Multi-tenant user management
- **Campaigns**: Outreach sequence management
- **Contacts**: Prospect and lead tracking
- **Messages**: Conversation history storage
- **Meetings**: Meeting booking and tracking
- **DuxSoup Integration**: Account and settings management

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- SQLite (included with Python)

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Environment Variables
Copy `env.template` to `.env.development` and configure:
```bash
REACT_APP_USE_MOCK_DATA=true
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## 📊 Mock Data System

The platform includes a comprehensive mock data logging system for development:

- **Mock Data Logger**: Tracks when components use mock vs real data
- **Environment Controls**: Toggle mock data via environment variables
- **Production Readiness**: Audit trail for production deployment
- **Documentation**: Complete inventory in `MOCK_DATA_CHECKLIST.md`

## 🚀 Production Deployment

### Azure Deployment
The platform is designed for Azure deployment with:
- **App Services**: Separate services for frontend and backend
- **PostgreSQL**: Azure Database for PostgreSQL
- **Blob Storage**: File uploads and static assets
- **Key Vault**: Secure credential management

### Environment Configuration
```bash
REACT_APP_USE_MOCK_DATA=false
REACT_APP_API_BASE_URL=https://your-backend.azurewebsites.net
DATABASE_URL=postgresql://user:pass@host:port/dbname
JWT_SECRET_KEY=your-secret-key
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-based Access**: User, admin, and agency roles
- **CORS Configuration**: Proper cross-origin request handling
- **Rate Limiting**: API rate limiting middleware
- **Input Validation**: Pydantic model validation
- **SQL Injection Protection**: SQLAlchemy ORM protection

## 📈 Monitoring & Analytics

- **Campaign Performance**: Track outreach success rates
- **User Activity**: Monitor team member activity
- **Meeting Analytics**: Track meeting booking rates
- **System Health**: API performance monitoring
- **Error Tracking**: Comprehensive error logging

## 🤝 API Integration

### DuxSoup Integration
- **Profile Automation**: Automated profile visits and connections
- **Message Sending**: Automated LinkedIn messaging
- **Settings Management**: Remote configuration management
- **Webhook Support**: Real-time event processing
- **Queue Management**: Automation queue control

### Webhook Events
- Profile visits
- Connection requests
- Message sending
- Automation status updates
- Remote control commands

## 📚 Documentation

- **API Documentation**: Available at `/docs` when running backend
- **Mock Data Checklist**: See `MOCK_DATA_CHECKLIST.md`
- **Deployment Guide**: Production deployment instructions
- **Architecture Overview**: System design documentation

## 🧪 Testing

### Backend Testing
```bash
pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📝 License

Private - All rights reserved

## 👥 Support

For support and questions, contact the development team.

---

**Built with ❤️ for LinkedIn automation and CRM management**