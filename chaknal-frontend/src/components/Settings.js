import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, User, Shield, Bell, Globe, Key, Image, Upload, X, Check } from 'lucide-react';
import axios from 'axios';

function Settings({ currentClient, isAgency }) {
  const [activeTab, setActiveTab] = useState(isAgency ? 'branding' : 'profile');
  const [logoFile, setLogoFile] = useState(null);
  const [logoPreview, setLogoPreview] = useState(null);
  const [currentLogo, setCurrentLogo] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [companyName, setCompanyName] = useState('');
  const [brandingLoading, setBrandingLoading] = useState(false);

  // Only show branding for agency mode
  const tabs = isAgency ? [
    { id: 'branding', name: 'Company Branding', icon: Image },
  ] : [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'integrations', name: 'Integrations', icon: Globe },
    { id: 'api', name: 'API Keys', icon: Key },
  ];

  // Get current company ID (mock for now)
  const getCurrentCompanyId = () => {
    if (isAgency && currentClient) {
      return currentClient.id;
    }
    return 'mock-company-id'; // Replace with actual company ID from auth context
  };

  // Load current branding
  useEffect(() => {
    loadCurrentBranding();
  }, [currentClient, isAgency]);

  const loadCurrentBranding = async () => {
    try {
      const companyId = getCurrentCompanyId();
      const response = await axios.get(`http://localhost:8000/api/company-settings/branding/${companyId}`);
      
      if (response.data.success) {
        const { company_name, logo_url } = response.data.data;
        setCompanyName(company_name || '');
        setCurrentLogo(logo_url ? `http://localhost:8000${logo_url}` : null);
      }
    } catch (error) {
      console.error('Error loading branding:', error);
      // Use mock data for demo
      setCompanyName(isAgency && currentClient ? currentClient.name : 'Marketing Masters');
      setCurrentLogo(null);
    }
  };

  // Handle logo file selection
  const handleLogoSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        alert('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
        return;
      }

      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
      }

      setLogoFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setLogoPreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // Upload logo
  const handleLogoUpload = async () => {
    if (!logoFile) return;

    try {
      setUploadLoading(true);
      const companyId = getCurrentCompanyId();
      
      const formData = new FormData();
      formData.append('file', logoFile);
      formData.append('company_id', companyId);

      const response = await axios.post(
        'http://localhost:8000/api/company-settings/upload-logo',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      if (response.data.success) {
        setCurrentLogo(`http://localhost:8000${response.data.logo_url}`);
        setLogoFile(null);
        setLogoPreview(null);
        alert('Logo uploaded successfully!');
      }
    } catch (error) {
      console.error('Error uploading logo:', error);
      alert('Failed to upload logo. Please try again.');
    } finally {
      setUploadLoading(false);
    }
  };

  // Remove logo
  const handleLogoRemove = async () => {
    try {
      const companyId = getCurrentCompanyId();
      const response = await axios.delete(`http://localhost:8000/api/company-settings/logo/${companyId}`);
      
      if (response.data.success) {
        setCurrentLogo(null);
        alert('Logo removed successfully!');
      }
    } catch (error) {
      console.error('Error removing logo:', error);
      alert('Failed to remove logo. Please try again.');
    }
  };

  // Cancel logo selection
  const handleCancelLogoSelection = () => {
    setLogoFile(null);
    setLogoPreview(null);
  };

  // Update company name
  const handleUpdateCompanyName = async () => {
    try {
      setBrandingLoading(true);
      const companyId = getCurrentCompanyId();
      
      const formData = new FormData();
      formData.append('company_name', companyName);

      const response = await axios.put(
        `http://localhost:8000/api/company-settings/branding/${companyId}`,
        formData
      );

      if (response.data.success) {
        alert('Company name updated successfully!');
      }
    } catch (error) {
      console.error('Error updating company name:', error);
      alert('Failed to update company name. Please try again.');
    } finally {
      setBrandingLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          {isAgency ? 'Client Branding Settings' : 'Settings'}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {isAgency 
            ? `Customize branding for ${currentClient ? currentClient.name : 'your clients'}` 
            : 'Manage your account settings and preferences'
          }
        </p>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="inline h-4 w-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'branding' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900">Company Branding</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Customize your company logo and branding for white labeling
                </p>
              </div>

              {/* Company Name */}
              <div className="bg-gray-50 rounded-lg p-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name
                </label>
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter company name"
                  />
                  <button
                    onClick={handleUpdateCompanyName}
                    disabled={brandingLoading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {brandingLoading ? 'Updating...' : 'Update'}
                  </button>
                </div>
              </div>

              {/* Current Logo */}
              <div className="bg-gray-50 rounded-lg p-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Logo
                </label>
                {currentLogo ? (
                  <div className="flex items-center space-x-4">
                    <img
                      src={currentLogo}
                      alt="Company Logo"
                      className="h-16 w-16 object-contain border border-gray-200 rounded-lg bg-white p-2"
                    />
                    <div className="flex-1">
                      <p className="text-sm text-gray-600">Logo is active</p>
                      <button
                        onClick={handleLogoRemove}
                        className="mt-2 px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200"
                      >
                        Remove Logo
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-16 w-16 bg-gray-200 border border-gray-300 rounded-lg">
                    <Image className="h-6 w-6 text-gray-400" />
                  </div>
                )}
              </div>

              {/* Logo Upload */}
              <div className="bg-gray-50 rounded-lg p-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload New Logo
                </label>
                
                {!logoPreview ? (
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                    <p className="text-sm text-gray-600 mb-2">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-gray-500 mb-4">
                      PNG, JPG, GIF, WebP up to 5MB
                    </p>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleLogoSelect}
                      className="hidden"
                      id="logo-upload"
                    />
                    <label
                      htmlFor="logo-upload"
                      className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 cursor-pointer"
                    >
                      Select File
                    </label>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-4">
                      <img
                        src={logoPreview}
                        alt="Logo Preview"
                        className="h-16 w-16 object-contain border border-gray-200 rounded-lg bg-white p-2"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {logoFile?.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {(logoFile?.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <button
                        onClick={handleCancelLogoSelection}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                    
                    <div className="flex space-x-3">
                      <button
                        onClick={handleLogoUpload}
                        disabled={uploadLoading}
                        className="flex-1 flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                      >
                        {uploadLoading ? (
                          'Uploading...'
                        ) : (
                          <>
                            <Check className="h-4 w-4 mr-2" />
                            Upload Logo
                          </>
                        )}
                      </button>
                      <button
                        onClick={handleCancelLogoSelection}
                        className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* White Labeling Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-900 mb-2">
                  White Labeling Benefits
                </h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Your logo appears in the dashboard header</li>
                  <li>• Clients see your branding throughout the platform</li>
                  <li>• Professional, customized experience</li>
                  <li>• Strengthens your brand identity</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">Profile Information</h3>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">First Name</label>
                  <input
                    type="text"
                    defaultValue="John"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Last Name</label>
                  <input
                    type="text"
                    defaultValue="Sales"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    type="email"
                    defaultValue="john.sales@techcorp.com"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Company</label>
                  <input
                    type="text"
                    defaultValue="TechCorp Solutions"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div className="flex justify-end">
                <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700">
                  Save Changes
                </button>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">Security Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Current Password</label>
                  <input
                    type="password"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">New Password</label>
                  <input
                    type="password"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Confirm New Password</label>
                  <input
                    type="password"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div className="flex justify-end">
                <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700">
                  Update Password
                </button>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">Notification Preferences</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Email Notifications</h4>
                    <p className="text-sm text-gray-500">Receive email updates about your campaigns</p>
                  </div>
                  <button className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-blue-600">
                    <span className="translate-x-5 inline-block h-5 w-5 transform rounded-full bg-white transition duration-200 ease-in-out"></span>
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Campaign Alerts</h4>
                    <p className="text-sm text-gray-500">Get notified when campaigns reach milestones</p>
                  </div>
                  <button className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-gray-200">
                    <span className="translate-x-0 inline-block h-5 w-5 transform rounded-full bg-white transition duration-200 ease-in-out"></span>
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Weekly Reports</h4>
                    <p className="text-sm text-gray-500">Receive weekly performance summaries</p>
                  </div>
                  <button className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 bg-blue-600">
                    <span className="translate-x-5 inline-block h-5 w-5 transform rounded-full bg-white transition duration-200 ease-in-out"></span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'integrations' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">LinkedIn Integration</h3>
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <Globe className="h-5 w-5 text-blue-400" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">LinkedIn Connected</h3>
                    <div className="mt-2 text-sm text-blue-700">
                      <p>Your LinkedIn account is connected and ready for automation.</p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex justify-end">
                <button className="px-4 py-2 text-sm font-medium text-red-600 bg-white border border-red-300 rounded-md hover:bg-red-50">
                  Disconnect LinkedIn
                </button>
              </div>
            </div>
          )}

          {activeTab === 'api' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">API Access</h3>
              <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">API Key</h4>
                    <p className="text-sm text-gray-500">Use this key to access the Chaknal Platform API</p>
                  </div>
                  <button className="px-3 py-1 text-sm font-medium text-blue-600 bg-white border border-blue-300 rounded-md hover:bg-blue-50">
                    Regenerate
                  </button>
                </div>
                <div className="mt-3">
                  <input
                    type="text"
                    readOnly
                    value="chk_1234567890abcdef"
                    className="block w-full bg-white border border-gray-300 rounded-md px-3 py-2 text-sm font-mono"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Settings;
