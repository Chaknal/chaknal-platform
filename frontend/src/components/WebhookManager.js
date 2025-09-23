import React, { useState } from 'react';
import { Plus, Trash2, Link, Copy, Check, Play } from 'lucide-react';

export const WebhookManager = ({ webhooks, updateSetting, validationErrors = {}, duxsoupUserId }) => {
  const [newWebhook, setNewWebhook] = useState({ url: '', events: [], enabled: true });
  const [copiedUrl, setCopiedUrl] = useState('');
  const [testingWebhook, setTestingWebhook] = useState('');

  const addWebhook = () => {
    if (!newWebhook.url.trim()) return;
    
    const webhook = {
      id: Date.now().toString(),
      url: newWebhook.url.trim(),
      events: newWebhook.events,
      enabled: newWebhook.enabled,
      created_at: new Date().toISOString()
    };
    
    const updatedWebhooks = [...webhooks, webhook];
    updateSetting('webhooks', updatedWebhooks);
    setNewWebhook({ url: '', events: [], enabled: true });
  };

  const removeWebhook = (webhookId) => {
    const updatedWebhooks = webhooks.filter(w => w.id !== webhookId);
    updateSetting('webhooks', updatedWebhooks);
  };

  const toggleWebhook = (webhookId) => {
    const updatedWebhooks = webhooks.map(w => 
      w.id === webhookId ? { ...w, enabled: !w.enabled } : w
    );
    updateSetting('webhooks', updatedWebhooks);
  };

  const updateWebhookEvents = (webhookId, events) => {
    const updatedWebhooks = webhooks.map(w => 
      w.id === webhookId ? { ...w, events } : w
    );
    updateSetting('webhooks', updatedWebhooks);
  };

  const copyToClipboard = async (url) => {
    try {
      await navigator.clipboard.writeText(url);
      setCopiedUrl(url);
      setTimeout(() => setCopiedUrl(''), 2000);
    } catch (err) {
      console.error('Failed to copy URL:', err);
    }
  };

  const testWebhook = async (webhookUrl) => {
    if (!duxsoupUserId) return;
    
    setTestingWebhook(webhookUrl);
    try {
      const response = await fetch(`/api/duxsoup-config/${duxsoupUserId}/test-webhook?webhook_url=${encodeURIComponent(webhookUrl)}`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.success) {
        alert(`✅ Webhook test successful!\nStatus: ${result.response_status}\nMessage: ${result.message}`);
      } else {
        alert(`❌ Webhook test failed!\nMessage: ${result.message}`);
      }
    } catch (err) {
      alert(`❌ Webhook test failed!\nError: ${err.message}`);
    } finally {
      setTestingWebhook('');
    }
  };

  const webhookEvents = [
    { id: 'visit', label: 'Profile Visit', description: 'When a profile is visited' },
    { id: 'scan', label: 'Profile Scan', description: 'When a profile is scanned' },
    { id: 'action', label: 'Action Performed', description: 'When an action is performed (connect, message, etc.)' },
    { id: 'message', label: 'Message Event', description: 'When a message is sent or received' },
    { id: 'rc', label: 'Remote Control', description: 'Remote control events' }
  ];

  return (
    <div className="space-y-4">
      {/* Add New Webhook */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h6 className="text-sm font-medium text-gray-900 mb-3">Add New Webhook URL</h6>
        
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Webhook URL
            </label>
            <div className="flex space-x-2">
              <input
                type="url"
                value={newWebhook.url}
                onChange={(e) => setNewWebhook({ ...newWebhook, url: e.target.value })}
                placeholder="https://your-server.com/webhook"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                onClick={addWebhook}
                disabled={!newWebhook.url.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <Plus className="h-4 w-4 mr-1" />
                Add
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Events to Send
            </label>
            <div className="grid grid-cols-2 gap-2">
              {webhookEvents.map(event => (
                <label key={event.id} className="flex items-start space-x-2">
                  <input
                    type="checkbox"
                    checked={newWebhook.events.includes(event.id)}
                    onChange={(e) => {
                      const events = e.target.checked
                        ? [...newWebhook.events, event.id]
                        : newWebhook.events.filter(id => id !== event.id);
                      setNewWebhook({ ...newWebhook, events });
                    }}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <div>
                    <div className="text-sm font-medium text-gray-900">{event.label}</div>
                    <div className="text-xs text-gray-500">{event.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="new_webhook_enabled"
              checked={newWebhook.enabled}
              onChange={(e) => setNewWebhook({ ...newWebhook, enabled: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="new_webhook_enabled" className="ml-2 block text-sm text-gray-900">
              Enable this webhook
            </label>
          </div>
        </div>
      </div>

      {/* Existing Webhooks */}
      <div>
        <h6 className="text-sm font-medium text-gray-900 mb-3">
          Configured Webhooks ({webhooks.length})
        </h6>
        
        {webhooks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Link className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No webhooks configured</h3>
            <p className="mt-1 text-sm text-gray-500">
              Add a webhook URL above to receive real-time notifications from DuxSoup.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {webhooks.map((webhook) => (
              <div key={webhook.id} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <div className={`w-2 h-2 rounded-full ${webhook.enabled ? 'bg-green-500' : 'bg-gray-400'}`} />
                      <span className="text-sm font-medium text-gray-900">
                        {webhook.enabled ? 'Active' : 'Disabled'}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2 mb-2">
                      <code className="text-sm bg-gray-100 px-2 py-1 rounded font-mono">
                        {webhook.url}
                      </code>
                      <button
                        onClick={() => copyToClipboard(webhook.url)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                        title="Copy URL"
                      >
                        {copiedUrl === webhook.url ? (
                          <Check className="h-4 w-4 text-green-600" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </button>
                      <button
                        onClick={() => testWebhook(webhook.url)}
                        disabled={testingWebhook === webhook.url}
                        className="p-1 text-blue-400 hover:text-blue-600 disabled:opacity-50"
                        title="Test webhook"
                      >
                        {testingWebhook === webhook.url ? (
                          <div className="h-4 w-4 animate-spin border-2 border-blue-600 border-t-transparent rounded-full" />
                        ) : (
                          <Play className="h-4 w-4" />
                        )}
                      </button>
                    </div>

                    <div className="text-xs text-gray-500 mb-2">
                      Events: {webhook.events.length > 0 ? webhook.events.join(', ') : 'None selected'}
                    </div>

                    <div className="text-xs text-gray-400">
                      Added: {new Date(webhook.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleWebhook(webhook.id)}
                      className={`px-3 py-1 text-xs rounded-md ${
                        webhook.enabled
                          ? 'bg-red-100 text-red-700 hover:bg-red-200'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      {webhook.enabled ? 'Disable' : 'Enable'}
                    </button>
                    <button
                      onClick={() => removeWebhook(webhook.id)}
                      className="p-1 text-red-400 hover:text-red-600"
                      title="Remove webhook"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Event Selection for Existing Webhook */}
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <label className="block text-xs font-medium text-gray-700 mb-2">
                    Events to Send
                  </label>
                  <div className="grid grid-cols-2 gap-1">
                    {webhookEvents.map(event => (
                      <label key={event.id} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={webhook.events.includes(event.id)}
                          onChange={(e) => {
                            const events = e.target.checked
                              ? [...webhook.events, event.id]
                              : webhook.events.filter(id => id !== event.id);
                            updateWebhookEvents(webhook.id, events);
                          }}
                          className="h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="text-xs text-gray-700">{event.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Webhook Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h6 className="text-sm font-medium text-blue-900 mb-2">Webhook Information</h6>
        <div className="text-sm text-blue-800 space-y-1">
          <p>• Webhooks will send POST requests to your configured URLs</p>
          <p>• Each webhook payload includes event type, timestamp, and relevant data</p>
          <p>• Failed webhook deliveries will be retried up to 3 times</p>
          <p>• Webhooks are sent asynchronously and won't block DuxSoup operations</p>
        </div>
      </div>
    </div>
  );
};
