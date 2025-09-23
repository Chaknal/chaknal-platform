import React, { useState, useEffect } from 'react';
import { 
  Save, 
  Download, 
  Upload, 
  Settings, 
  Clock, 
  Filter, 
  Zap, 
  Bell, 
  Globe, 
  Users,
  Calendar,
  AlertCircle,
  CheckCircle,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { 
  RateLimitsTab, 
  FilteringTab, 
  AutomationTab, 
  NotificationsTab, 
  AdvancedTab 
} from './DuxSoupConfigTabs';
import { logMockData } from '../utils/mockDataLogger';
import { ProfileAutomationTab } from './ProfileAutomationTab';
import { SchedulePlannerTab } from './SchedulePlannerTab';

const DuxSoupConfig = () => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [pushing, setPushing] = useState(false);
  const [pulling, setPulling] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('profileAutomation');
  const [selectedUserId, setSelectedUserId] = useState('');
  const [validationErrors, setValidationErrors] = useState({});
  const [hasChanges, setHasChanges] = useState(false);

  const [duxsoupUsers, setDuxsoupUsers] = useState([]);

  useEffect(() => {
    loadDuxSoupUsers();
  }, []);

  useEffect(() => {
    if (selectedUserId) {
      loadConfig(selectedUserId);
    }
  }, [selectedUserId]);

  const loadDuxSoupUsers = async () => {
    try {
      const response = await fetch('/api/duxsoup-accounts/');
      if (response.ok) {
        const data = await response.json();
        console.log('✅ DuxSoup accounts API response:', data);
        
        // Add Sercio manually since he might not be in database yet
        const realUsers = data.accounts || [];
        const sercioExists = realUsers.some(user => user.email === 'scampos@wallarm.com');
        
        if (!sercioExists) {
          realUsers.unshift({
            id: '690354bb-fa6a-4f77-a9e7-4214a263a75a',
            email: 'scampos@wallarm.com',
            first_name: 'Sercio',
            last_name: 'Campos',
            dux_soup_user_id: '117833704731893145427'
          });
        }
        
        setDuxsoupUsers(realUsers);
        console.log('✅ Total DuxSoup users loaded:', realUsers.length);
        
        // Log each user for debugging
        realUsers.forEach(user => {
          console.log(`  - ${user.first_name} ${user.last_name} (${user.email}) - ID: ${user.id}`);
        });
      } else {
        console.error('Failed to load DuxSoup users, status:', response.status);
        
        // Log mock data usage
        logMockData('DuxSoupConfig', 'fallback_users', {
          reason: 'API_STATUS_ERROR',
          status: response.status,
          fallback: true
        });
        
        // Fallback to include key users
        setDuxsoupUsers([
          { id: '690354bb-fa6a-4f77-a9e7-4214a263a75a', email: 'scampos@wallarm.com', first_name: 'Sercio', last_name: 'Campos' },
          { id: '42369828-16a2-4edf-b4b3-5988572f93ad', email: 'shayne@attimis.co', first_name: 'Shayne', last_name: 'Stubbs' }
        ]);
      }
    } catch (error) {
      console.error('Error loading DuxSoup users:', error);
      
      // Log mock data usage
      logMockData('DuxSoupConfig', 'error_fallback_users', {
        reason: 'API_ERROR',
        error: error.message,
        fallback: true
      });
      
      // Fallback to include key users
      setDuxsoupUsers([
        { id: '690354bb-fa6a-4f77-a9e7-4214a263a75a', email: 'scampos@wallarm.com', first_name: 'Sercio', last_name: 'Campos' },
        { id: '42369828-16a2-4edf-b4b3-5988572f93ad', email: 'shayne@attimis.co', first_name: 'Shayne', last_name: 'Stubbs' }
      ]);
    }
  };

  const loadConfig = async (userId) => {
    setLoading(true);
    setError(null);
    try {
      // Use the new properly authenticated endpoint
      const response = await fetch(`/api/duxsoup-auth-test/config/${userId}`);
      if (!response.ok) throw new Error('Failed to load configuration');
      const data = await response.json();
      setConfig(data);
      console.log('✅ DuxSoup config loaded successfully:', Object.keys(data.settings || {}));
    } catch (err) {
      console.error('❌ DuxSoup config load failed:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async () => {
    if (!selectedUserId || !config) return;
    
    // Check for validation errors
    if (Object.keys(validationErrors).length > 0) {
      setError('Please fix validation errors before saving');
      return;
    }
    
    setSaving(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await fetch(`/api/duxsoup-config/${selectedUserId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config.settings)
      });
      
      if (!response.ok) throw new Error('Failed to save configuration');
      
      const data = await response.json();
      setConfig(data);
      setHasChanges(false);
      setSuccess('Configuration saved successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const pushToDuxSoup = async () => {
    if (!selectedUserId || !config) return;
    
    setPushing(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await fetch(`/api/duxsoup-auth-test/push/${selectedUserId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          settings: config.settings
        })
      });
      
      if (!response.ok) throw new Error('Failed to push to DuxSoup');
      
      const data = await response.json();
      setSuccess('Configuration pushed to DuxSoup successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setPushing(false);
    }
  };

  const pullFromDuxSoup = async () => {
    if (!selectedUserId) return;
    
    setPulling(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await fetch(`/api/duxsoup-auth-test/pull/${selectedUserId}`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to pull from DuxSoup');
      
      const data = await response.json();
      setConfig(data);
      setSuccess('Configuration pulled from DuxSoup successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setPulling(false);
    }
  };

  const validateSetting = (key, value) => {
    const errors = { ...validationErrors };
    
    // Rate limit validations
    if (key === 'throttle_time' && (value < 1 || value > 60)) {
      errors[key] = 'Throttle time must be between 1 and 60 seconds';
    } else if (key === 'scan_throttle_time' && (value < 1000 || value > 10000)) {
      errors[key] = 'Scan throttle time must be between 1000 and 10000 milliseconds';
    } else if (key === 'max_visits' && (value < 0 || value > 1000)) {
      errors[key] = 'Max visits must be between 0 and 1000';
    } else if (key === 'max_invites' && (value < 0 || value > 100)) {
      errors[key] = 'Max invites must be between 0 and 100';
    } else if (key === 'max_messages' && (value < 0 || value > 500)) {
      errors[key] = 'Max messages must be between 0 and 500';
    } else if (key === 'max_enrolls' && (value < 0 || value > 1000)) {
      errors[key] = 'Max enrolls must be between 0 and 1000';
    } else if (key === 'linkedin_limits_nooze' && (value < 1 || value > 30)) {
      errors[key] = 'LinkedIn limits pause must be between 1 and 30 days';
    } else if (key === 'exclude_low_connection_count_value' && (value < 0 || value > 10000)) {
      errors[key] = 'Connection count threshold must be between 0 and 10000';
    } else if (key === 'auto_endorse_target' && (value < 1 || value > 10)) {
      errors[key] = 'Auto-endorse target must be between 1 and 10';
    } else if (key === 'skip_days' && (value < 0 || value > 30)) {
      errors[key] = 'Skip days must be between 0 and 30';
    } else if (key === 'page_init_delay' && (value < 1000 || value > 30000)) {
      errors[key] = 'Page init delay must be between 1000 and 30000 milliseconds';
    } else if (key === 'wait_minutes' && (value < 1 || value > 60)) {
      errors[key] = 'Wait minutes must be between 1 and 60';
    } else if (key === 'wait_visits' && (value < 1 || value > 100)) {
      errors[key] = 'Wait visits must be between 1 and 100';
    } else if (key === 'max_page_load_time' && (value < 5000 || value > 60000)) {
      errors[key] = 'Max page load time must be between 5000 and 60000 milliseconds';
    } else if (key === 'message_bridge_interval' && (value < 60 || value > 3600)) {
      errors[key] = 'Message bridge interval must be between 60 and 3600 seconds';
    } else {
      // Clear error if validation passes
      delete errors[key];
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const updateSetting = (key, value) => {
    if (!config) return;
    
    // Validate the setting
    const isValid = validateSetting(key, value);
    
    setConfig({
      ...config,
      settings: {
        ...config.settings,
        [key]: value
      }
    });
    
    setHasChanges(true);
  };

  const tabs = [
    { id: 'profileAutomation', label: 'Profile Automation', icon: Users },
    { id: 'schedulePlanner', label: 'Schedule Planner', icon: Calendar },
    { id: 'rateLimits', label: 'Rate Limits', icon: Clock },
    { id: 'filtering', label: 'Filtering', icon: Filter },
    { id: 'automation', label: 'Automation', icon: Zap },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'advanced', label: 'Advanced', icon: Settings }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading configuration...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">DuxSoup Configuration</h1>
            <p className="text-gray-600 mt-2">Manage DuxSoup settings and automation parameters</p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select DuxSoup User</option>
              {duxsoupUsers.map(user => (
                <option key={user.id} value={user.id}>
                  {user.first_name} {user.last_name} ({user.email})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <CheckCircle className="h-5 w-5 text-green-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">Success</h3>
              <div className="mt-2 text-sm text-green-700">{success}</div>
            </div>
          </div>
        </div>
      )}

      {!selectedUserId ? (
        <div className="text-center py-12">
          <Settings className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No User Selected</h3>
          <p className="mt-1 text-sm text-gray-500">Please select a DuxSoup user to manage their configuration.</p>
        </div>
      ) : !config ? (
        <div className="text-center py-12">
          <Loader2 className="mx-auto h-12 w-12 text-gray-400 animate-spin" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Loading Configuration</h3>
          <p className="mt-1 text-sm text-gray-500">Please wait while we load the configuration...</p>
        </div>
      ) : (
        <>
          {/* User Info */}
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {config.first_name} {config.last_name}
                </h2>
                <p className="text-gray-600">{config.email}</p>
                <p className="text-sm text-gray-500">
                  Last updated: {new Date(config.last_updated).toLocaleString()}
                </p>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={pullFromDuxSoup}
                  disabled={pulling}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  {pulling ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Download className="h-4 w-4 mr-2" />
                  )}
                  Pull from DuxSoup
                </button>
                <button
                  onClick={pushToDuxSoup}
                  disabled={pushing}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  {pushing ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Upload className="h-4 w-4 mr-2" />
                  )}
                  Push to DuxSoup
                </button>
                <button
                  onClick={saveConfig}
                  disabled={saving || Object.keys(validationErrors).length > 0}
                  className={`inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white disabled:opacity-50 ${
                    hasChanges 
                      ? 'bg-green-600 hover:bg-green-700' 
                      : 'bg-gray-400 cursor-not-allowed'
                  }`}
                >
                  {saving ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Save className="h-4 w-4 mr-2" />
                  )}
                  {hasChanges ? 'Save Changes' : 'No Changes'}
                </button>
              </div>
            </div>
          </div>

          {/* Configuration Tabs */}
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 px-6">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                        activeTab === tab.id
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <Icon className="h-5 w-5 mr-2" />
                      {tab.label}
                    </button>
                  );
                })}
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'profileAutomation' && <ProfileAutomationTab config={config} updateSetting={updateSetting} validationErrors={validationErrors} />}
              {activeTab === 'schedulePlanner' && <SchedulePlannerTab config={config} updateSetting={updateSetting} validationErrors={validationErrors} />}
              {activeTab === 'rateLimits' && <RateLimitsTab config={config} updateSetting={updateSetting} validationErrors={validationErrors} />}
              {activeTab === 'filtering' && <FilteringTab config={config} updateSetting={updateSetting} validationErrors={validationErrors} />}
              {activeTab === 'automation' && <AutomationTab config={config} updateSetting={updateSetting} validationErrors={validationErrors} />}
              {activeTab === 'notifications' && <NotificationsTab config={config} updateSetting={updateSetting} validationErrors={validationErrors} />}
              {activeTab === 'advanced' && <AdvancedTab config={config} updateSetting={updateSetting} validationErrors={validationErrors} />}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DuxSoupConfig;
