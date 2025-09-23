import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { BarChart3, Users, MessageSquare, Settings, Home, Zap, LogOut, UserPlus, Cog, Building2, Calendar } from 'lucide-react';
import axios from 'axios';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Dashboard from './components/Dashboard';
import Campaigns from './components/Campaigns';
import Contacts from './components/Contacts';
import Messages from './components/Messages';
import Analytics from './components/Analytics';
import SettingsPage from './components/Settings';
import UserManagement from './components/UserManagement';
import DuxSoupConfig from './components/DuxSoupConfig';
import ClientSwitcher from './components/ClientSwitcher';
import AgencyOverview from './components/AgencyOverview';
import DuxWrapTest from './components/DuxWrapTest';
import MeetingsDashboard from './components/MeetingsDashboard';
import CampaignPerformance from './components/CampaignPerformance';


function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

function AppContent() {
  const { user, loading, logout } = useAuth();
  const [currentClient, setCurrentClient] = useState(null);
  const [isAgency, setIsAgency] = useState(false); // Will be set based on user data
  const [companyLogo, setCompanyLogo] = useState(null);

  // Load company logo for white labeling
  useEffect(() => {
    const loadCompanyLogo = async () => {
      try {
        const companyId = currentClient?.id || 'mock-company-id';
        const response = await fetch(`https://chaknal-backend-container.azurewebsites.net/api/company-settings/branding/${companyId}`);
        const data = await response.json();
        
        if (data.success && data.data.logo_url) {
          setCompanyLogo(`https://chaknal-backend-container.azurewebsites.net${data.data.logo_url}`);
        } else {
          setCompanyLogo(null);
        }
      } catch (error) {
        console.error('Error loading company logo:', error);
        setCompanyLogo(null);
      }
    };

    loadCompanyLogo();
  }, [currentClient]);

  // Get current user from auth context or localStorage
  const currentUser = user || {
    email: localStorage.getItem('user_email') || "sercio@chaknal.com",
    company: { name: "Chaknal Company", domain: "chaknal.com" },
    organization: { name: "Chaknal Platform" },
    is_agency: localStorage.getItem('user_email') === 'sercio@chaknal.com' || localStorage.getItem('user_email') === 'sercio@ampedmktg.com' || localStorage.getItem('user_email') === 'user@chaknal.com',
    role: (localStorage.getItem('user_email') === 'sercio@chaknal.com' || localStorage.getItem('user_email') === 'sercio@ampedmktg.com' || localStorage.getItem('user_email') === 'user@chaknal.com') ? 'agency' : "user",
    user_id: (localStorage.getItem('user_email') === 'sercio@chaknal.com' || localStorage.getItem('user_email') === 'sercio@ampedmktg.com') ? '75a762b1-baf4-4494-836d-4725dcc1b816' : null
  };

  useEffect(() => {
    setIsAgency(currentUser.is_agency || currentUser.role === 'agency');
  }, [currentUser]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                {companyLogo ? (
                  <img 
                    src={companyLogo} 
                    alt="Company Logo" 
                    className="h-8 w-8 object-contain"
                  />
                ) : (
                  <Zap className="h-8 w-8 text-blue-600" />
                )}
                <span className="ml-2 text-xl font-bold text-gray-900">
                  {isAgency && currentClient ? currentClient.name : 'Chaknal Platform'}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                {currentUser.organization?.name || 'LinkedIn Automation Dashboard'}
              </span>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">{currentUser.email}</span>
                <button
                  onClick={logout}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200"
                >
                  <LogOut className="h-4 w-4 mr-1" />
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-white shadow-sm min-h-screen">
          <div className="p-4">
            <div className="mb-6">
              <div className="text-sm font-medium text-gray-500 mb-2">
                {isAgency ? 'Current Client' : 'Company'}
              </div>
              {isAgency ? (
                <ClientSwitcher 
                  onClientSwitch={setCurrentClient} 
                  currentClient={currentClient}
                />
              ) : (
                <div>
                  <div className="text-sm font-medium text-gray-900">
                    {currentUser.company?.name || 'N/A'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {currentUser.company?.domain || ''}
                  </div>
                </div>
              )}
            </div>
            <nav className="space-y-2">
              {isAgency && <NavLink to="/agency" icon={Building2} label="Agency Overview" />}
              <NavLink to="/" icon={BarChart3} label="Dashboard" />
              <NavLink to="/campaigns" icon={BarChart3} label="Campaigns" />
              <NavLink to="/contacts" icon={Users} label="Contacts" />
              <NavLink to="/messages" icon={MessageSquare} label="Messages" />
              <NavLink to="/meetings" icon={Calendar} label="Meetings" />
              <NavLink to="/users" icon={UserPlus} label="Add Users" />
              <NavLink to="/duxsoup-config" icon={Cog} label="DuxSoup Config" />
              <NavLink to="/duxwrap-test" icon={Zap} label="DuxWrap Test" />
              <NavLink to="/settings" icon={Settings} label="Settings" />
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-8">

          <Routes>
            <Route path="/" element={<Analytics currentClient={currentClient} isAgency={isAgency} onClientSwitch={setCurrentClient} />} />
            <Route path="/dashboard" element={<Dashboard currentClient={currentClient} isAgency={isAgency} />} />
            <Route path="/agency" element={<AgencyOverview onClientSelect={setCurrentClient} />} />
            <Route path="/campaigns" element={<Campaigns currentClient={currentClient} isAgency={isAgency} />} />
            <Route path="/contacts" element={<Contacts currentClient={currentClient} isAgency={isAgency} />} />
            <Route path="/messages" element={<Messages currentClient={currentClient} isAgency={isAgency} />} />
            <Route path="/meetings" element={<MeetingsDashboard currentClient={currentClient} isAgency={isAgency} />} />
            <Route path="/analytics" element={<Analytics currentClient={currentClient} isAgency={isAgency} onClientSwitch={setCurrentClient} />} />
            <Route path="/users" element={<UserManagement currentClient={currentClient} isAgency={isAgency} />} />
            <Route path="/duxsoup-config" element={<DuxSoupConfig currentClient={currentClient} isAgency={isAgency} />} />
            <Route path="/duxwrap-test" element={<DuxWrapTest />} />
            <Route path="/campaign-performance" element={<CampaignPerformance currentClient={currentClient} isAgency={isAgency} />} />
            <Route path="/settings" element={<SettingsPage currentClient={currentClient} isAgency={isAgency} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

function NavLink({ to, icon: Icon, label }) {
  return (
    <Link
      to={to}
      className="flex items-center px-4 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-50 hover:text-gray-900 group"
    >
      <Icon className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500" />
      {label}
    </Link>
  );
}

export default App;
