import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, MessageSquare, Calendar, CheckCircle, Clock, Target, UserCheck, ExternalLink, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ClientSwitcher from './ClientSwitcher';
import { logMockData } from '../utils/mockDataLogger';

function Analytics({ currentClient, isAgency, onClientSwitch }) {
  const [meetingsData, setMeetingsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activityPeriod, setActivityPeriod] = useState('weekly'); // daily, weekly, monthly
  const [selectedUser, setSelectedUser] = useState('all'); // 'all' or specific user email
  const navigate = useNavigate();

  useEffect(() => {
    loadAnalyticsData();
  }, [currentClient, activityPeriod, selectedUser]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Load meetings data for analytics
      const meetingsResponse = await axios.get('http://localhost:8000/api/meetings/dashboard');
      if (meetingsResponse.data.success) {
        setMeetingsData(meetingsResponse.data.data);
      }
    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Available users for selection
  const availableUsers = [
    { email: 'all', name: 'All Users', isReal: false },
    { email: 'scampos@wallarm.com', name: 'Sercio Campos', isReal: true },
    { email: 'john.smith@marketingmasters.com', name: 'John Smith', isReal: false },
    { email: 'sarah.johnson@marketingmasters.com', name: 'Sarah Johnson', isReal: false },
    { email: 'michael.davis@marketingmasters.com', name: 'Michael Davis', isReal: false }
  ];

  // Get user-specific or aggregated campaign performance
  const getCampaignPerformance = () => {
    // Log mock data usage
    logMockData('Analytics', 'campaign_performance', {
      reason: 'ALWAYS_MOCK',
      selectedUser: selectedUser,
      note: 'Campaign performance metrics and drill-down data'
    });
    const baseCampaigns = [
      {
        name: 'Professional Outreach',
        all: { sent: 156, accepted: 89, responded: 34, meetings_booked: meetingsData ? meetingsData.stats.total_meetings_7d : 1 },
        'scampos@wallarm.com': { sent: 45, accepted: 28, responded: 12, meetings_booked: 1 },
        'john.smith@marketingmasters.com': { sent: 38, accepted: 22, responded: 8, meetings_booked: 0 },
        'sarah.johnson@marketingmasters.com': { sent: 42, accepted: 24, responded: 9, meetings_booked: 0 },
        'michael.davis@marketingmasters.com': { sent: 31, accepted: 15, responded: 5, meetings_booked: 0 }
      },
      {
        name: 'Q4 Lead Generation',
        all: { sent: 203, accepted: 127, responded: 45, meetings_booked: 3 },
        'scampos@wallarm.com': { sent: 58, accepted: 38, responded: 15, meetings_booked: 2 },
        'john.smith@marketingmasters.com': { sent: 52, accepted: 32, responded: 12, meetings_booked: 1 },
        'sarah.johnson@marketingmasters.com': { sent: 48, accepted: 29, responded: 10, meetings_booked: 0 },
        'michael.davis@marketingmasters.com': { sent: 45, accepted: 28, responded: 8, meetings_booked: 0 }
      },
      {
        name: 'Executive Outreach',
        all: { sent: 89, accepted: 34, responded: 12, meetings_booked: 2 },
        'scampos@wallarm.com': { sent: 25, accepted: 12, responded: 5, meetings_booked: 1 },
        'john.smith@marketingmasters.com': { sent: 22, accepted: 8, responded: 3, meetings_booked: 1 },
        'sarah.johnson@marketingmasters.com': { sent: 21, accepted: 7, responded: 2, meetings_booked: 0 },
        'michael.davis@marketingmasters.com': { sent: 21, accepted: 7, responded: 2, meetings_booked: 0 }
      }
    ];

    return baseCampaigns.map(campaign => {
      const data = campaign[selectedUser] || campaign.all;
      return {
        name: campaign.name,
        sent: data.sent,
        accepted: data.accepted,
        responded: data.responded,
        meetings_booked: data.meetings_booked,
        acceptance_rate: data.sent > 0 ? (data.accepted / data.sent * 100) : 0,
        response_rate: data.sent > 0 ? (data.responded / data.sent * 100) : 0,
        meeting_rate: data.sent > 0 ? (data.meetings_booked / data.sent * 100) : 0
      };
    });
  };

  const campaignPerformance = getCampaignPerformance();

  // Mock user activity data
  const getUserActivityData = () => {
    // Log mock data usage
    logMockData('Analytics', 'user_activity_data', {
      reason: 'ALWAYS_MOCK',
      period: activityPeriod,
      note: 'User activity breakdown table'
    });
    const baseUsers = [
      { name: 'Sercio Campos', email: 'scampos@wallarm.com', isReal: true },
      { name: 'John Smith', email: 'john.smith@marketingmasters.com', isReal: false },
      { name: 'Sarah Johnson', email: 'sarah.johnson@marketingmasters.com', isReal: false },
      { name: 'Michael Davis', email: 'michael.davis@marketingmasters.com', isReal: false }
    ];

    const periodMultiplier = activityPeriod === 'daily' ? 1 : activityPeriod === 'weekly' ? 7 : 30;
    
    return baseUsers.map((user, index) => {
      const baseActivity = user.isReal ? 8 : Math.floor(Math.random() * 15) + 5;
      return {
        ...user,
        messages_sent: Math.floor(baseActivity * periodMultiplier * (0.8 + Math.random() * 0.4)),
        connections_sent: Math.floor(baseActivity * periodMultiplier * 0.3 * (0.8 + Math.random() * 0.4)),
        responses_received: Math.floor(baseActivity * periodMultiplier * 0.15 * (0.8 + Math.random() * 0.4)),
        meetings_booked: user.isReal && meetingsData ? meetingsData.stats.total_meetings_7d : Math.floor(baseActivity * periodMultiplier * 0.02 * (0.8 + Math.random() * 0.4)),
        profile_visits: Math.floor(baseActivity * periodMultiplier * 2 * (0.8 + Math.random() * 0.4))
      };
    });
  };

  const userActivityData = getUserActivityData();

  const selectedUserName = availableUsers.find(u => u.email === selectedUser)?.name || 'All Users';

  // Navigate to contacts with specific filters
  const handleCampaignMetricClick = (campaign, metric) => {
    const filterState = {
      campaign: campaign.name,
      user: selectedUser,
      status: metric,
      fromAnalytics: true
    };
    
    navigate('/contacts', { state: filterState });
  };

  return (
    <div className="space-y-6">
      {/* Agency Client Switcher */}
      {isAgency && (
        <div className="p-4 bg-white rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-medium text-gray-900">Dashboard</h2>
              <p className="text-sm text-gray-500">
                {currentClient ? `Viewing analytics for ${currentClient.name}` : 'Select a client to view their analytics'}
              </p>
            </div>
            <ClientSwitcher 
              onClientSwitch={onClientSwitch}
              currentClient={currentClient}
            />
          </div>
        </div>
      )}

      {/* Show agency overview if no client selected */}
      {isAgency && !currentClient ? (
        <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
          <BarChart3 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Client</h3>
          <p className="text-gray-500">Choose a client from the dropdown above to view their analytics and performance data.</p>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between">
      <div>
              <div className="flex items-center space-x-4">
                <h1 className="text-2xl font-bold text-gray-900">
                  {isAgency && currentClient ? `${currentClient.name} Dashboard` : 'Dashboard'}
                </h1>
                <div className="relative">
                  <select
                    value={selectedUser}
                    onChange={(e) => setSelectedUser(e.target.value)}
                    className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    {availableUsers.map(user => (
                      <option key={user.email} value={user.email}>
                        {user.name} {user.isReal ? '(Real User)' : ''}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                </div>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                {selectedUser === 'all' 
                  ? 'Campaign performance, team activity, and business metrics' 
                  : `Performance dashboard for ${selectedUserName}`
                }
              </p>
            </div>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Reach</dt>
                  <dd className="text-lg font-medium text-gray-900">2,847</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserCheck className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Accepted</dt>
                  <dd className="text-lg font-medium text-gray-900">250</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <MessageSquare className="h-6 w-6 text-purple-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Responded</dt>
                  <dd className="text-lg font-medium text-gray-900">91</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Calendar className="h-6 w-6 text-orange-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Meetings</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {meetingsData ? meetingsData.stats.total_meetings_7d : loading ? '...' : '0'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-6 w-6 text-green-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Completed</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {meetingsData ? meetingsData.stats.completed_meetings_7d : loading ? '...' : '0'}
                  </dd>
                </dl>
      </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Target className="h-6 w-6 text-indigo-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Meeting Rate</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {meetingsData ? `${meetingsData.stats.conversion_rate.toFixed(1)}%` : loading ? '...' : '0%'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Campaign Performance Table */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
            Campaign Performance Breakdown
          </h3>
            <button
              onClick={() => navigate('/campaign-performance', { state: { selectedUser } })}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <span>View Detailed Analysis</span>
              <ExternalLink className="ml-2 h-4 w-4" />
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Campaign
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Accepted
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Responded
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Meetings Booked
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Accept Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Response Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Meeting Rate
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {campaignPerformance.map((campaign) => (
                  <tr key={campaign.name} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {campaign.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <button 
                        onClick={() => handleCampaignMetricClick(campaign, 'sent')}
                        className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                      >
                        {campaign.sent}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <button 
                          onClick={() => handleCampaignMetricClick(campaign, 'accepted')}
                          className="text-blue-600 hover:text-blue-800 hover:underline font-medium mr-2"
                        >
                          {campaign.accepted}
                        </button>
                        <span className="text-xs text-gray-500">({campaign.acceptance_rate.toFixed(1)}%)</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <button 
                          onClick={() => handleCampaignMetricClick(campaign, 'responded')}
                          className="text-blue-600 hover:text-blue-800 hover:underline font-medium mr-2"
                        >
                          {campaign.responded}
                        </button>
                        <span className="text-xs text-gray-500">({campaign.response_rate.toFixed(1)}%)</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <button 
                          onClick={() => handleCampaignMetricClick(campaign, 'meetings')}
                          className="text-blue-600 hover:text-blue-800 hover:underline font-medium mr-2"
                        >
                          {campaign.meetings_booked}
                        </button>
                        <span className="text-xs text-gray-500">({campaign.meeting_rate.toFixed(1)}%)</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{width: `${Math.min(campaign.acceptance_rate, 100)}%`}}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-900">{campaign.acceptance_rate.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full" 
                            style={{width: `${Math.min(campaign.response_rate, 100)}%`}}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-900">{campaign.response_rate.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{width: `${Math.min(campaign.meeting_rate * 10, 100)}%`}}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-900">{campaign.meeting_rate.toFixed(1)}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* User Activity Breakdown */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Team Activity Breakdown
            </h3>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-700">Period:</span>
              <select
                value={activityPeriod}
                onChange={(e) => setActivityPeriod(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Messages Sent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Connections
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Responses
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Meetings
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Profile Visits
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Response Rate
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {userActivityData.map((user) => {
                  const responseRate = user.messages_sent > 0 ? (user.responses_received / user.messages_sent * 100) : 0;
                  return (
                    <tr key={user.email} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-8 w-8">
                            <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
                              <Users className="h-4 w-4 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="flex items-center space-x-2">
                              <div className="text-sm font-medium text-gray-900">{user.name}</div>
                              {user.isReal && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                  Real User
                                </span>
                              )}
                            </div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.messages_sent}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.connections_sent}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.responses_received}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 text-orange-500 mr-1" />
                          {user.meetings_booked}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.profile_visits}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              className="bg-green-600 h-2 rounded-full" 
                              style={{width: `${Math.min(responseRate, 100)}%`}}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-900">{responseRate.toFixed(1)}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          
          <div className="mt-4 text-xs text-gray-500">
            Showing {activityPeriod} activity for {userActivityData.length} team members. 
            {activityPeriod === 'daily' && 'Data represents last 24 hours.'}
            {activityPeriod === 'weekly' && 'Data represents last 7 days.'}
            {activityPeriod === 'monthly' && 'Data represents last 30 days.'}
          </div>
        </div>
      </div>

      {/* Meeting Analytics Section */}
      {meetingsData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Upcoming Meetings
              </h3>
              {meetingsData.upcoming_meetings.length === 0 ? (
                <div className="text-center py-4">
                  <Calendar className="mx-auto h-8 w-8 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">No upcoming meetings</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {meetingsData.upcoming_meetings.slice(0, 5).map((meeting) => (
                    <div key={meeting.meeting_id} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{meeting.contact_name}</p>
                          <p className="text-xs text-gray-600">{meeting.contact_company}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {meeting.meeting_type.replace('_', ' ')}
                            </span>
                            <span className="text-xs text-gray-500">{meeting.duration_minutes} min</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-gray-900 font-medium">
                            {new Date(meeting.scheduled_date).toLocaleDateString()}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(meeting.scheduled_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Meeting Types Performance
              </h3>
              <div className="space-y-3">
                {Object.entries(
                  meetingsData.upcoming_meetings.concat(meetingsData.recent_meetings)
                    .reduce((acc, meeting) => {
                      acc[meeting.meeting_type] = (acc[meeting.meeting_type] || 0) + 1;
                      return acc;
                    }, {})
                ).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 capitalize">
                      {type.replace('_', ' ')}
                    </span>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-indigo-600 h-2 rounded-full" 
                          style={{width: `${(count / Math.max(meetingsData.upcoming_meetings.length + meetingsData.recent_meetings.length, 1)) * 100}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-8">{count}</span>
                    </div>
                  </div>
                ))}
                {meetingsData.upcoming_meetings.length + meetingsData.recent_meetings.length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-4">No meetings to analyze</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      </>
      )}
    </div>
  );
}

export default Analytics;