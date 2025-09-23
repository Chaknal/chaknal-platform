# 🎨 Chaknal Platform Frontend

A modern React-based frontend for the Chaknal Platform LinkedIn automation dashboard.

## 🚀 Features

- **📊 Dashboard**: Overview of campaigns, contacts, and performance metrics
- **📈 Campaigns**: Create and manage LinkedIn automation campaigns
- **👥 Contacts**: Manage LinkedIn connections and prospects
- **💬 Messages**: View and send LinkedIn messages
- **📊 Analytics**: Campaign performance and engagement metrics
- **⚙️ Settings**: User preferences and account management
- **🔐 Authentication**: JWT-based authentication with organization context

## 🛠️ Tech Stack

- **React 18** - Modern React with hooks
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client for API calls
- **Context API** - State management

## 📦 Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm start
   ```

4. **Open browser**:
   Navigate to `http://localhost:3000`

## 🔧 Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Project Structure

```
src/
├── components/          # React components
│   ├── Dashboard.js    # Main dashboard
│   ├── Campaigns.js    # Campaign management
│   ├── Contacts.js     # Contact management
│   ├── Messages.js     # Message handling
│   ├── Analytics.js    # Performance metrics
│   ├── Settings.js     # User settings
│   └── Login.js        # Authentication
├── contexts/            # React contexts
│   └── AuthContext.js  # Authentication state
├── App.js              # Main app component
└── index.js            # App entry point
```

## 🔐 Authentication

The frontend uses JWT-based authentication with automatic organization context:

1. **Login**: Users authenticate with email/password
2. **Auto-association**: System automatically associates users with companies based on email domain
3. **Organization Context**: All data is filtered by user's organization
4. **Protected Routes**: All routes require authentication

### Demo Accounts

- **TechCorp Solutions**: `john.sales@techcorp.com` / `password123`
- **Test Company**: `test@testcompany.com` / `password123`

## 🎨 UI Components

### Dashboard
- Statistics cards
- Campaign status overview
- Recent activity timeline
- Quick action buttons

### Campaigns
- Campaign list with status indicators
- Performance metrics
- Create/edit campaign forms
- Campaign management actions

### Contacts
- Contact list with search and filters
- Connection status indicators
- LinkedIn profile integration
- Contact management tools

### Analytics
- Performance metrics
- Chart placeholders (ready for Recharts integration)
- Campaign breakdown
- Engagement statistics

### Settings
- Profile management
- Security settings
- Notification preferences
- LinkedIn integration status
- API key management

## 🔌 API Integration

The frontend is configured to connect to the backend API at `http://localhost:8000`:

- **Proxy**: Configured in `package.json`
- **Authentication**: JWT tokens in Authorization headers
- **Error Handling**: Comprehensive error states and user feedback
- **Loading States**: Loading spinners and skeleton screens

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

### Environment Variables

Create `.env` file for production:

```bash
REACT_APP_API_URL=https://your-api-domain.com
REACT_APP_ENVIRONMENT=production
```

## 🔧 Customization

### Styling
- **Tailwind CSS**: Utility classes for rapid styling
- **Component Library**: Reusable UI components
- **Responsive Design**: Mobile-first approach
- **Dark Mode**: Ready for future implementation

### Adding New Features
1. Create component in `src/components/`
2. Add route in `App.js`
3. Update navigation in sidebar
4. Implement API integration
5. Add to authentication context if needed

## 📱 Responsive Design

The frontend is fully responsive with:
- **Mobile-first** approach
- **Breakpoint system** using Tailwind CSS
- **Flexible layouts** that adapt to screen sizes
- **Touch-friendly** interface elements

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Protected Routes**: All routes require authentication
- **Organization Isolation**: Data filtered by user's organization
- **Input Validation**: Form validation and sanitization
- **HTTPS Ready**: Secure communication protocols

## 🧪 Testing

### Manual Testing
1. **Authentication Flow**: Login, logout, token refresh
2. **Navigation**: All routes and sidebar navigation
3. **Responsive Design**: Test on different screen sizes
4. **Error Handling**: Test error states and edge cases

### Automated Testing
```bash
npm test
```

## 🚀 Future Enhancements

- **Real-time Updates**: WebSocket integration for live data
- **Advanced Charts**: Recharts integration for analytics
- **Dark Mode**: Theme switching capability
- **Mobile App**: React Native version
- **PWA**: Progressive Web App features
- **Internationalization**: Multi-language support

## 📚 Documentation

- **Component API**: Each component has inline documentation
- **Authentication Flow**: See `AuthContext.js` for auth logic
- **Styling Guide**: Tailwind CSS utility classes
- **API Reference**: Backend endpoint documentation

## 🤝 Contributing

1. Follow React best practices
2. Use functional components with hooks
3. Implement proper error handling
4. Add loading states for async operations
5. Maintain responsive design
6. Test on multiple devices

## 📄 License

This project is part of the Chaknal Platform and follows the same licensing terms.
