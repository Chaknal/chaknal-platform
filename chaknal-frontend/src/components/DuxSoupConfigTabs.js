import React, { useState } from 'react';
import { Clock, AlertTriangle, Users, Filter, Zap, Bell, Settings, Globe } from 'lucide-react';
import { WebhookManager } from './WebhookManager';

// Rate Limits Tab Component
export const RateLimitsTab = ({ config, updateSetting, validationErrors = {} }) => {
  const settings = config.settings;

  return (
    <div className="space-y-6">
      <div className="flex items-center mb-4">
        <Clock className="h-6 w-6 text-blue-600 mr-2" />
        <h3 className="text-lg font-semibold text-gray-900">Rate Limits & Throttling</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Throttling Settings */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">Throttling</h4>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Throttle Time (seconds)
            </label>
            <input
              type="number"
              min="1"
              max="60"
              value={settings.throttle_time || 1}
              onChange={(e) => updateSetting('throttle_time', parseInt(e.target.value))}
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                validationErrors.throttle_time ? 'border-red-300' : 'border-gray-300'
              }`}
            />
            <p className="text-xs text-gray-500 mt-1">Seconds between actions</p>
            {validationErrors.throttle_time && (
              <p className="text-xs text-red-600 mt-1">{validationErrors.throttle_time}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Scan Throttle Time (ms)
            </label>
            <input
              type="number"
              min="1000"
              max="10000"
              value={settings.scan_throttle_time || 3000}
              onChange={(e) => updateSetting('scan_throttle_time', parseInt(e.target.value))}
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                validationErrors.scan_throttle_time ? 'border-red-300' : 'border-gray-300'
              }`}
            />
            <p className="text-xs text-gray-500 mt-1">Milliseconds between profile scans</p>
            {validationErrors.scan_throttle_time && (
              <p className="text-xs text-red-600 mt-1">{validationErrors.scan_throttle_time}</p>
            )}
          </div>
        </div>

        {/* Daily Limits */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">Daily Limits</h4>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Visits per Day
            </label>
            <input
              type="number"
              min="0"
              max="1000"
              value={settings.max_visits || 0}
              onChange={(e) => updateSetting('max_visits', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">0 = unlimited</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Invites per Day
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={settings.max_invites || 20}
              onChange={(e) => updateSetting('max_invites', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Messages per Day
            </label>
            <input
              type="number"
              min="0"
              max="500"
              value={settings.max_messages || 100}
              onChange={(e) => updateSetting('max_messages', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Enrolls per Day
            </label>
            <input
              type="number"
              min="0"
              max="1000"
              value={settings.max_enrolls || 200}
              onChange={(e) => updateSetting('max_enrolls', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Error Handling */}
      <div className="border-t pt-6">
        <div className="flex items-center mb-4">
          <AlertTriangle className="h-5 w-5 text-orange-600 mr-2" />
          <h4 className="text-md font-medium text-gray-900">Error Handling</h4>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              LinkedIn Limits Pause (days)
            </label>
            <input
              type="number"
              min="1"
              max="30"
              value={settings.linkedin_limits_nooze || 3}
              onChange={(e) => updateSetting('linkedin_limits_nooze', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="linkedin_limit_alert"
              checked={settings.linkedin_limit_alert || false}
              onChange={(e) => updateSetting('linkedin_limit_alert', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="linkedin_limit_alert" className="ml-2 block text-sm text-gray-900">
              Alert when LinkedIn limits hit
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="pause_on_invite_error"
              checked={settings.pause_on_invite_error || true}
              onChange={(e) => updateSetting('pause_on_invite_error', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="pause_on_invite_error" className="ml-2 block text-sm text-gray-900">
              Pause when invite errors occur
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Resume Delay on Error
            </label>
            <select
              value={settings.resume_delay_on_invite_error || '1d'}
              onChange={(e) => updateSetting('resume_delay_on_invite_error', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="1h">1 hour</option>
              <option value="1d">1 day</option>
              <option value="3d">3 days</option>
              <option value="7d">7 days</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};

// Filtering Tab Component
export const FilteringTab = ({ config, updateSetting, validationErrors = {} }) => {
  const settings = config.settings;

  return (
    <div className="space-y-6">
      <div className="flex items-center mb-4">
        <Filter className="h-6 w-6 text-blue-600 mr-2" />
        <h3 className="text-lg font-semibold text-gray-900">Profile Filtering</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Skip Conditions */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">Skip Conditions</h4>
          
          <div className="space-y-3">
            {[
              { key: 'skip_noname', label: 'Skip profiles without names' },
              { key: 'skip_noimage', label: 'Skip profiles without images' },
              { key: 'skip_incrm', label: 'Skip CRM contacts' },
              { key: 'skip_nopremium', label: 'Skip non-premium users' },
              { key: 'skip_3plus', label: 'Skip 3rd+ connections' },
              { key: 'skip_nolion', label: 'Skip profiles without LinkedIn Premium' },
              { key: 'skip_noinfluencer', label: 'Skip non-influencers' },
              { key: 'skip_nojobseeker', label: 'Skip job seekers' }
            ].map((item) => (
              <div key={item.key} className="flex items-center">
                <input
                  type="checkbox"
                  id={item.key}
                  checked={settings[item.key] || false}
                  onChange={(e) => updateSetting(item.key, e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor={item.key} className="ml-2 block text-sm text-gray-900">
                  {item.label}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Exclusion Rules */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">Exclusion Rules</h4>
          
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="exclude_blacklisted_action"
                checked={settings.exclude_blacklisted_action || true}
                onChange={(e) => updateSetting('exclude_blacklisted_action', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="exclude_blacklisted_action" className="ml-2 block text-sm text-gray-900">
                Exclude blacklisted profiles
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="exclude_tag_skipped_action"
                checked={settings.exclude_tag_skipped_action || false}
                onChange={(e) => updateSetting('exclude_tag_skipped_action', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="exclude_tag_skipped_action" className="ml-2 block text-sm text-gray-900">
                Exclude tagged profiles
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="exclude_low_connection_count_action"
                checked={settings.exclude_low_connection_count_action || false}
                onChange={(e) => updateSetting('exclude_low_connection_count_action', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="exclude_low_connection_count_action" className="ml-2 block text-sm text-gray-900">
                Exclude low connection counts
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Low Connection Threshold
              </label>
              <input
                type="number"
                min="0"
                max="10000"
                value={settings.exclude_low_connection_count_value || 100}
                onChange={(e) => updateSetting('exclude_low_connection_count_value', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Content Filtering */}
      <div className="border-t pt-6">
        <h4 className="text-md font-medium text-gray-900 mb-4">Content Filtering</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kill Characters
            </label>
            <textarea
              value={settings.kill_characters || ''}
              onChange={(e) => updateSetting('kill_characters', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Characters to remove from profiles"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kill Words
            </label>
            <textarea
              value={settings.kill_words || ''}
              onChange={(e) => updateSetting('kill_words', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Words that disqualify profiles (comma-separated)"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Automation Tab Component
export const AutomationTab = ({ config, updateSetting, validationErrors = {} }) => {
  const settings = config.settings;

  return (
    <div className="space-y-6">
      <div className="flex items-center mb-4">
        <Zap className="h-6 w-6 text-blue-600 mr-2" />
        <h3 className="text-lg font-semibold text-gray-900">Automation Settings</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Connection Settings */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">Connection Settings</h4>
          
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="auto_connect"
                checked={settings.auto_connect || false}
                onChange={(e) => updateSetting('auto_connect', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="auto_connect" className="ml-2 block text-sm text-gray-900">
                Auto-connect to profiles
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="auto_follow"
                checked={settings.auto_follow || false}
                onChange={(e) => updateSetting('auto_follow', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="auto_follow" className="ml-2 block text-sm text-gray-900">
                Auto-follow profiles
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="auto_disconnect"
                checked={settings.auto_disconnect || false}
                onChange={(e) => updateSetting('auto_disconnect', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="auto_disconnect" className="ml-2 block text-sm text-gray-900">
                Auto-disconnect from profiles
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="auto_endorse"
                checked={settings.auto_endorse || false}
                onChange={(e) => updateSetting('auto_endorse', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="auto_endorse" className="ml-2 block text-sm text-gray-900">
                Auto-endorse connections
              </label>
            </div>
          </div>

          {settings.auto_endorse && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Auto-endorse Target Count
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={settings.auto_endorse_target || 3}
                onChange={(e) => updateSetting('auto_endorse_target', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          )}
        </div>

        {/* Message Settings */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">Message Settings</h4>
          
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="auto_connect_message_flag"
                checked={settings.auto_connect_message_flag || false}
                onChange={(e) => updateSetting('auto_connect_message_flag', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="auto_connect_message_flag" className="ml-2 block text-sm text-gray-900">
                Send message with auto-connect
              </label>
            </div>

            {settings.auto_connect_message_flag && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Auto-connect Message
                </label>
                <textarea
                  value={settings.auto_connect_message_text || ''}
                  onChange={(e) => updateSetting('auto_connect_message_text', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Message to send with connection requests"
                />
              </div>
            )}

            <div className="flex items-center">
              <input
                type="checkbox"
                id="connected_message_flag"
                checked={settings.connected_message_flag || false}
                onChange={(e) => updateSetting('connected_message_flag', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="connected_message_flag" className="ml-2 block text-sm text-gray-900">
                Send message when connected
              </label>
            </div>

            {settings.connected_message_flag && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Connected Message
                </label>
                <textarea
                  value={settings.connected_message_text || ''}
                  onChange={(e) => updateSetting('connected_message_text', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Message to send after connection is accepted"
                />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Follow-up Settings */}
      <div className="border-t pt-6">
        <h4 className="text-md font-medium text-gray-900 mb-4">Follow-up Settings</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="followup_flag"
                checked={settings.followup_flag || true}
                onChange={(e) => updateSetting('followup_flag', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="followup_flag" className="ml-2 block text-sm text-gray-900">
                Enable follow-up messages
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="followup_for_all_flag"
                checked={settings.followup_for_all_flag || false}
                onChange={(e) => updateSetting('followup_for_all_flag', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="followup_for_all_flag" className="ml-2 block text-sm text-gray-900">
                Follow-up for all contacts
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Active Follow-up Campaign
            </label>
            <input
              type="text"
              value={settings.active_followup_campaign_id || 'default'}
              onChange={(e) => updateSetting('active_followup_campaign_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Campaign ID"
            />
          </div>
        </div>
      </div>

      {/* Auto-tagging */}
      <div className="border-t pt-6">
        <h4 className="text-md font-medium text-gray-900 mb-4">Auto-tagging</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="auto_tag_flag"
              checked={settings.auto_tag_flag || true}
              onChange={(e) => updateSetting('auto_tag_flag', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="auto_tag_flag" className="ml-2 block text-sm text-gray-900">
              Enable auto-tagging
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Auto-tag Value
            </label>
            <input
              type="text"
              value={settings.auto_tag_value || 'AMPED'}
              onChange={(e) => updateSetting('auto_tag_value', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Tag value"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Notifications Tab Component
export const NotificationsTab = ({ config, updateSetting, validationErrors = {} }) => {
  const settings = config.settings;

  return (
    <div className="space-y-6">
      <div className="flex items-center mb-4">
        <Bell className="h-6 w-6 text-blue-600 mr-2" />
        <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">Notification Types</h4>
          
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="warning_notifications"
                checked={settings.warning_notifications || true}
                onChange={(e) => updateSetting('warning_notifications', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="warning_notifications" className="ml-2 block text-sm text-gray-900">
                Warning notifications
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="action_notifications"
                checked={settings.action_notifications || true}
                onChange={(e) => updateSetting('action_notifications', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="action_notifications" className="ml-2 block text-sm text-gray-900">
                Action notifications
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="info_notifications"
                checked={settings.info_notifications || true}
                onChange={(e) => updateSetting('info_notifications', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="info_notifications" className="ml-2 block text-sm text-gray-900">
                Info notifications
              </label>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">Performance Settings</h4>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Skip Days
            </label>
            <input
              type="number"
              min="0"
              max="30"
              value={settings.skip_days || 0}
              onChange={(e) => updateSetting('skip_days', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Page Init Delay (ms)
            </label>
            <input
              type="number"
              min="1000"
              max="30000"
              value={settings.page_init_delay || 5000}
              onChange={(e) => updateSetting('page_init_delay', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Wait Minutes
            </label>
            <input
              type="number"
              min="1"
              max="60"
              value={settings.wait_minutes || 5}
              onChange={(e) => updateSetting('wait_minutes', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Wait After N Visits
            </label>
            <input
              type="number"
              min="1"
              max="100"
              value={settings.wait_visits || 20}
              onChange={(e) => updateSetting('wait_visits', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Page Load Time (ms)
            </label>
            <input
              type="number"
              min="5000"
              max="60000"
              value={settings.max_page_load_time || 20000}
              onChange={(e) => updateSetting('max_page_load_time', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Advanced Tab Component
export const AdvancedTab = ({ config, updateSetting, validationErrors = {} }) => {
  const settings = config.settings;

  return (
    <div className="space-y-6">
      <div className="flex items-center mb-4">
        <Settings className="h-6 w-6 text-blue-600 mr-2" />
        <h3 className="text-lg font-semibold text-gray-900">Advanced Settings</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Advanced Features */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">Advanced Features</h4>
          
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="buy_mail"
                checked={settings.buy_mail || false}
                onChange={(e) => updateSetting('buy_mail', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="buy_mail" className="ml-2 block text-sm text-gray-900">
                Buy email addresses
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="pre_visit_dialog"
                checked={settings.pre_visit_dialog || true}
                onChange={(e) => updateSetting('pre_visit_dialog', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="pre_visit_dialog" className="ml-2 block text-sm text-gray-900">
                Show pre-visit dialog
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="auto_save_as_lead"
                checked={settings.auto_save_as_lead || false}
                onChange={(e) => updateSetting('auto_save_as_lead', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="auto_save_as_lead" className="ml-2 block text-sm text-gray-900">
                Auto-save as lead
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="auto_pdf"
                checked={settings.auto_pdf || false}
                onChange={(e) => updateSetting('auto_pdf', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="auto_pdf" className="ml-2 block text-sm text-gray-900">
                Auto-generate PDF
              </label>
            </div>
          </div>
        </div>

        {/* UI Settings */}
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">UI Settings</h4>
          
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="minimised_tools"
                checked={settings.minimised_tools || false}
                onChange={(e) => updateSetting('minimised_tools', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="minimised_tools" className="ml-2 block text-sm text-gray-900">
                Minimized tools
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="background_mode"
                checked={settings.background_mode || true}
                onChange={(e) => updateSetting('background_mode', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="background_mode" className="ml-2 block text-sm text-gray-900">
                Background mode
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="managed_download"
                checked={settings.managed_download || true}
                onChange={(e) => updateSetting('managed_download', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="managed_download" className="ml-2 block text-sm text-gray-900">
                Managed download
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="hide_system_tags"
                checked={settings.hide_system_tags || true}
                onChange={(e) => updateSetting('hide_system_tags', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="hide_system_tags" className="ml-2 block text-sm text-gray-900">
                Hide system tags
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* InMail Settings */}
      <div className="border-t pt-6">
        <h4 className="text-md font-medium text-gray-900 mb-4">InMail Settings</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="send_inmail_flag"
              checked={settings.send_inmail_flag || false}
              onChange={(e) => updateSetting('send_inmail_flag', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="send_inmail_flag" className="ml-2 block text-sm text-gray-900">
              Send InMail messages
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Badge Display
            </label>
            <select
              value={settings.badge_display || 'nothing'}
              onChange={(e) => updateSetting('badge_display', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="nothing">Nothing</option>
              <option value="premium">Premium</option>
              <option value="influencer">Influencer</option>
            </select>
          </div>
        </div>

        {settings.send_inmail_flag && (
          <div className="mt-4 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                InMail Subject
              </label>
              <input
                type="text"
                value={settings.send_inmail_subject || ''}
                onChange={(e) => updateSetting('send_inmail_subject', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="InMail subject line"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                InMail Body
              </label>
              <textarea
                value={settings.send_inmail_body || ''}
                onChange={(e) => updateSetting('send_inmail_body', e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="InMail message body"
              />
            </div>
          </div>
        )}
      </div>

      {/* Webhooks & Integration */}
      <div className="border-t pt-6">
        <h4 className="text-md font-medium text-gray-900 mb-4">Webhooks & Integration</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="webhook_profile_flag"
                checked={settings.webhook_profile_flag || true}
                onChange={(e) => updateSetting('webhook_profile_flag', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="webhook_profile_flag" className="ml-2 block text-sm text-gray-900">
                Enable webhook for profile data
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="message_bridge_flag"
                checked={settings.message_bridge_flag || true}
                onChange={(e) => updateSetting('message_bridge_flag', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="message_bridge_flag" className="ml-2 block text-sm text-gray-900">
                Enable message bridge
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="remote_control_flag"
                checked={settings.remote_control_flag || true}
                onChange={(e) => updateSetting('remote_control_flag', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="remote_control_flag" className="ml-2 block text-sm text-gray-900">
                Enable remote control
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message Bridge Interval (seconds)
            </label>
            <input
              type="number"
              min="60"
              max="3600"
              value={settings.message_bridge_interval || 180}
              onChange={(e) => updateSetting('message_bridge_interval', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Webhook URLs Management */}
        <div className="mt-6">
          <h5 className="text-sm font-medium text-gray-900 mb-3">Webhook URLs</h5>
          <WebhookManager 
            webhooks={settings.webhooks || []} 
            updateSetting={updateSetting}
            validationErrors={validationErrors}
            duxsoupUserId={config.duxsoup_user_id}
          />
        </div>
      </div>
    </div>
  );
};
