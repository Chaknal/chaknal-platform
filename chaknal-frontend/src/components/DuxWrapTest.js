import React, { useState, useEffect } from 'react';
import { Play, User, MessageSquare, UserPlus, Trash2, RefreshCw } from 'lucide-react';
import axios from 'axios';

function DuxWrapTest() {
  const [profile, setProfile] = useState(null);
  const [queueStatus, setQueueStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [profileUrl, setProfileUrl] = useState('https://linkedin.com/in/test-profile');
  const [message, setMessage] = useState('Hi! Thanks for connecting.');
  const [connectionMessage, setConnectionMessage] = useState('I\'d like to connect with you!');
  const [lastAction, setLastAction] = useState(null);

  useEffect(() => {
    loadProfile();
    loadQueueStatus();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/duxwrap-test/profile');
      if (response.data.success) {
        setProfile(response.data.data);
      }
    } catch (err) {
      setError('Failed to load profile');
      console.error('Error loading profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadQueueStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/duxwrap-test/queue');
      if (response.data.success) {
        setQueueStatus(response.data.data);
      }
    } catch (err) {
      console.error('Error loading queue status:', err);
    }
  };

  const visitProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('http://localhost:8000/api/duxwrap-test/visit', {
        profile_url: profileUrl
      });
      if (response.data.success) {
        setLastAction({
          type: 'Visit Profile',
          result: response.data.data,
          timestamp: new Date().toLocaleTimeString()
        });
        await loadQueueStatus(); // Refresh queue status
      }
    } catch (err) {
      setError('Failed to queue profile visit');
      console.error('Error visiting profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const sendConnectionRequest = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('http://localhost:8000/api/duxwrap-test/connect', {
        profile_url: profileUrl,
        message: connectionMessage
      });
      if (response.data.success) {
        setLastAction({
          type: 'Connection Request',
          result: response.data.data,
          timestamp: new Date().toLocaleTimeString()
        });
        await loadQueueStatus(); // Refresh queue status
      }
    } catch (err) {
      setError('Failed to queue connection request');
      console.error('Error sending connection request:', err);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('http://localhost:8000/api/duxwrap-test/message', {
        profile_url: profileUrl,
        message: message
      });
      if (response.data.success) {
        setLastAction({
          type: 'Direct Message',
          result: response.data.data,
          timestamp: new Date().toLocaleTimeString()
        });
        await loadQueueStatus(); // Refresh queue status
      }
    } catch (err) {
      setError('Failed to queue message');
      console.error('Error sending message:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearQueue = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('http://localhost:8000/api/duxwrap-test/clear-queue');
      if (response.data.success) {
        setLastAction({
          type: 'Clear Queue',
          result: response.data.data,
          timestamp: new Date().toLocaleTimeString()
        });
        await loadQueueStatus(); // Refresh queue status
      }
    } catch (err) {
      setError('Failed to clear queue');
      console.error('Error clearing queue:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    await loadProfile();
    await loadQueueStatus();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">DuxWrap Real Integration Test</h1>
        <p className="mt-1 text-sm text-gray-500">
          Test the real DuxSoup integration using DuxWrap
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-red-600 text-sm">{error}</div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profile Information */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                DuxSoup Profile
              </h3>
              <button
                onClick={refreshData}
                disabled={loading}
                className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
            
            {profile ? (
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <User className="h-5 w-5 text-blue-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {profile.firstName} {profile.lastName}
                    </p>
                    <p className="text-sm text-gray-500">{profile.email}</p>
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  <p>User ID: {profile.userid}</p>
                  <p>Created: {new Date(profile.created).toLocaleDateString()}</p>
                </div>
                <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ✅ Connected
                </div>
              </div>
            ) : (
              <div className="text-center py-4">
                <User className="mx-auto h-8 w-8 text-gray-400" />
                <p className="mt-2 text-sm text-gray-500">Loading profile...</p>
              </div>
            )}
          </div>
        </div>

        {/* Queue Status */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Automation Queue
            </h3>
            
            {queueStatus ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">Queue Size:</span>
                  <span className="text-sm text-gray-600">{queueStatus.size}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">Status:</span>
                  <span className={`text-sm px-2 py-1 rounded-full ${
                    queueStatus.status === 'idle' 
                      ? 'bg-gray-100 text-gray-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {queueStatus.status}
                  </span>
                </div>
                <div className="text-xs text-gray-500">
                  <p>Items in queue: {queueStatus.items.length}</p>
                </div>
              </div>
            ) : (
              <div className="text-center py-4">
                <MessageSquare className="mx-auto h-8 w-8 text-gray-400" />
                <p className="mt-2 text-sm text-gray-500">Loading queue status...</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Test Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Test Actions
          </h3>

          {/* Profile URL Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              LinkedIn Profile URL
            </label>
            <input
              type="url"
              value={profileUrl}
              onChange={(e) => setProfileUrl(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="https://linkedin.com/in/username"
            />
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <button
              onClick={visitProfile}
              disabled={loading || !profileUrl}
              className="flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="h-4 w-4 mr-2" />
              Visit Profile
            </button>

            <button
              onClick={sendConnectionRequest}
              disabled={loading || !profileUrl}
              className="flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <UserPlus className="h-4 w-4 mr-2" />
              Send Connection
            </button>
          </div>

          {/* Connection Message Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Connection Message
            </label>
            <textarea
              value={connectionMessage}
              onChange={(e) => setConnectionMessage(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Connection request message..."
            />
          </div>

          {/* Message Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Direct Message
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Direct message content..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={sendMessage}
              disabled={loading || !profileUrl || !message}
              className="flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <MessageSquare className="h-4 w-4 mr-2" />
              Send Message
            </button>

            <button
              onClick={clearQueue}
              disabled={loading}
              className="flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear Queue
            </button>
          </div>
        </div>
      </div>

      {/* Last Action Result */}
      {lastAction && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Last Action Result
            </h3>
            <div className="bg-green-50 border border-green-200 rounded-md p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-green-800">
                  {lastAction.type}
                </span>
                <span className="text-xs text-green-600">
                  {lastAction.timestamp}
                </span>
              </div>
              <div className="text-sm text-green-700">
                <p>Message ID: {lastAction.result.message_id}</p>
                <p>Action: {lastAction.result.action}</p>
                {lastAction.result.profile_url && (
                  <p>Profile: {lastAction.result.profile_url}</p>
                )}
                {lastAction.result.message && (
                  <p>Message: "{lastAction.result.message}"</p>
                )}
                <p>Queued at: {new Date(lastAction.result.queued_at).toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DuxWrapTest;
