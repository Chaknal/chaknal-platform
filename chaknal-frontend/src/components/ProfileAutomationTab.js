import React, { useState } from 'react';
import { Users, Play, Pause, RotateCcw, Eye, MessageCircle, UserPlus, AlertCircle, CheckCircle } from 'lucide-react';

export const ProfileAutomationTab = ({ config, updateSetting, validationErrors = {} }) => {
  const [profileUrl, setProfileUrl] = useState('');
  const [connectionMessage, setConnectionMessage] = useState('');
  const [automationStatus, setAutomationStatus] = useState('idle');
  const [queueStatus, setQueueStatus] = useState(null);
  const [lastAction, setLastAction] = useState(null);

  const handleVisitProfile = async () => {
    if (!profileUrl.trim()) {
      alert('Please enter a LinkedIn profile URL');
      return;
    }

    try {
      setAutomationStatus('running');
      const response = await fetch('/api/duxsoup-auth-test/visit-profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ profile_url: profileUrl })
      });

      const result = await response.json();
      
      if (result.success) {
        setLastAction({
          type: 'visit',
          profile: profileUrl,
          status: 'success',
          message: result.message,
          timestamp: new Date().toLocaleTimeString()
        });
        setProfileUrl(''); // Clear the input
      } else {
        setLastAction({
          type: 'visit',
          profile: profileUrl,
          status: 'error',
          message: result.error,
          timestamp: new Date().toLocaleTimeString()
        });
      }
    } catch (error) {
      setLastAction({
        type: 'visit',
        profile: profileUrl,
        status: 'error',
        message: error.message,
        timestamp: new Date().toLocaleTimeString()
      });
    } finally {
      setAutomationStatus('idle');
    }
  };

  const handleSendConnection = async () => {
    if (!profileUrl.trim()) {
      alert('Please enter a LinkedIn profile URL');
      return;
    }

    try {
      setAutomationStatus('running');
      const response = await fetch('/api/duxsoup-auth-test/send-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          profile_url: profileUrl,
          message: connectionMessage 
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setLastAction({
          type: 'connect',
          profile: profileUrl,
          status: 'success',
          message: result.message,
          timestamp: new Date().toLocaleTimeString()
        });
        setProfileUrl(''); // Clear the input
        setConnectionMessage(''); // Clear message
      } else {
        setLastAction({
          type: 'connect',
          profile: profileUrl,
          status: 'error',
          message: result.error,
          timestamp: new Date().toLocaleTimeString()
        });
      }
    } catch (error) {
      setLastAction({
        type: 'connect',
        profile: profileUrl,
        status: 'error',
        message: error.message,
        timestamp: new Date().toLocaleTimeString()
      });
    } finally {
      setAutomationStatus('idle');
    }
  };

  const handleGetQueueStatus = async () => {
    try {
      const response = await fetch('/api/duxsoup-auth-test/queue-status');
      const result = await response.json();
      
      if (result.success) {
        setQueueStatus(result.data);
      } else {
        alert(`Failed to get queue status: ${result.error}`);
      }
    } catch (error) {
      alert(`Error getting queue status: ${error.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h4 className="text-lg font-medium text-gray-900 mb-2">Profile Automation</h4>
        <p className="text-sm text-gray-600">
          Manually trigger DuxSoup actions and monitor automation status
        </p>
      </div>

      {/* Queue Status */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h5 className="text-sm font-medium text-gray-900">Queue Status</h5>
          <button
            onClick={handleGetQueueStatus}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Refresh
          </button>
        </div>
        
        {queueStatus ? (
          <div className="text-sm text-gray-700">
            <p>Queue size: <span className="font-medium">{queueStatus.result || 0}</span> items</p>
          </div>
        ) : (
          <p className="text-sm text-gray-500">Click refresh to check queue status</p>
        )}
      </div>

      {/* Manual Profile Actions */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h5 className="text-sm font-medium text-gray-900 mb-3">Manual Profile Actions</h5>
        
        <div className="space-y-4">
          {/* Profile URL Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              LinkedIn Profile URL
            </label>
            <input
              type="url"
              value={profileUrl}
              onChange={(e) => setProfileUrl(e.target.value)}
              placeholder="https://linkedin.com/in/profile-name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Connection Message (for connection requests) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Connection Message (Optional)
            </label>
            <textarea
              value={connectionMessage}
              onChange={(e) => setConnectionMessage(e.target.value)}
              placeholder="Hi [First Name], I'd like to connect..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <button
              onClick={handleVisitProfile}
              disabled={automationStatus === 'running' || !profileUrl.trim()}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Eye className="h-4 w-4 mr-2" />
              {automationStatus === 'running' ? 'Queuing...' : 'Visit Profile'}
            </button>

            <button
              onClick={handleSendConnection}
              disabled={automationStatus === 'running' || !profileUrl.trim()}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <UserPlus className="h-4 w-4 mr-2" />
              {automationStatus === 'running' ? 'Queuing...' : 'Send Connection'}
            </button>
          </div>
        </div>
      </div>

      {/* Last Action Result */}
      {lastAction && (
        <div className={`rounded-lg p-4 ${
          lastAction.status === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-center">
            {lastAction.status === 'success' ? (
              <CheckCircle className="h-5 w-5 text-green-400" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-400" />
            )}
            <div className="ml-3">
              <h6 className={`text-sm font-medium ${
                lastAction.status === 'success' ? 'text-green-800' : 'text-red-800'
              }`}>
                {lastAction.type === 'visit' ? 'Profile Visit' : 'Connection Request'} 
                {lastAction.status === 'success' ? ' Queued' : ' Failed'}
              </h6>
              <div className={`mt-1 text-sm ${
                lastAction.status === 'success' ? 'text-green-700' : 'text-red-700'
              }`}>
                <p><strong>Profile:</strong> {lastAction.profile}</p>
                <p><strong>Result:</strong> {lastAction.message}</p>
                <p><strong>Time:</strong> {lastAction.timestamp}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Automation Settings */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h5 className="text-sm font-medium text-gray-900 mb-3">Automation Settings</h5>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config?.settings?.autoconnect || false}
                onChange={(e) => updateSetting('autoconnect', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">Auto-connect enabled</span>
            </label>
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config?.settings?.autoconnectmessageflag || false}
                onChange={(e) => updateSetting('autoconnectmessageflag', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">Send message with connection</span>
            </label>
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config?.settings?.previsitdialog || false}
                onChange={(e) => updateSetting('previsitdialog', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">Show pre-visit dialog</span>
            </label>
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config?.settings?.runautomationsonmanualvisits || false}
                onChange={(e) => updateSetting('runautomationsonmanualvisits', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">Run automations on manual visits</span>
            </label>
          </div>
        </div>

        {/* Connection Message Template */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Default Connection Message
          </label>
          <textarea
            value={config?.settings?.autoconnectmessagetext || ''}
            onChange={(e) => updateSetting('autoconnectmessagetext', e.target.value)}
            placeholder="Hi [First Name], I'd like to connect..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="mt-1 text-xs text-gray-500">
            Use _FN_ for first name, _LN_ for last name, _CN_ for company name
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h5 className="text-sm font-medium text-blue-900 mb-3">Quick Actions</h5>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <button
            onClick={() => setProfileUrl('https://linkedin.com/in/sergio-campos-97b9b7362/')}
            className="flex items-center justify-center px-3 py-2 bg-white border border-blue-300 text-blue-700 rounded-md hover:bg-blue-50"
          >
            <Users className="h-4 w-4 mr-2" />
            Test with Sergio
          </button>
          
          <button
            onClick={handleGetQueueStatus}
            className="flex items-center justify-center px-3 py-2 bg-white border border-blue-300 text-blue-700 rounded-md hover:bg-blue-50"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Refresh Queue
          </button>
          
          <button
            onClick={() => {
              setProfileUrl('');
              setConnectionMessage('');
              setLastAction(null);
            }}
            className="flex items-center justify-center px-3 py-2 bg-white border border-blue-300 text-blue-700 rounded-md hover:bg-blue-50"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Clear Form
          </button>
        </div>
      </div>
    </div>
  );
};
