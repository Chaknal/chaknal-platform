import React, { useState, useEffect } from 'react';
import { Users, BarChart3, MessageSquare, TrendingUp, Play, Pause, CheckCircle, Clock } from 'lucide-react';
import axios from 'axios';
import { logMockData } from '../utils/mockDataLogger';

function Dashboard({ currentClient, isAgency }) {
  const [stats, setStats] = useState({
    totalCampaigns: 0,
    activeCampaigns: 0,
    totalContacts: 0,
    totalMessages: 0,
    campaignsByStatus: [],
    recentActivity: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isAgency && currentClient) {
      fetchClientDashboardData();
    } else {
      fetchDashboardData();
    }
  }, [currentClient, isAgency]);

  const fetchClientDashboardData = async () => {
    try {
      setLoading(true);
      
      // Log mock data usage
      logMockData('Dashboard', 'client_dashboard_stats', {
        reason: 'CLIENT_SPECIFIC',
        client: currentClient?.name,
        note: 'Client-specific dashboard data'
      });
      
      // Mock data based on the selected client
      const clientStats = {
        totalCampaigns: currentClient.stats.campaigns,
        activeCampaigns: Math.floor(currentClient.stats.campaigns * 0.6), // 60% active
        totalContacts: currentClient.stats.contacts,
        totalMessages: Math.floor(currentClient.stats.contacts * 0.3), // 30% of contacts have messages
        campaignsByStatus: [
          { status: 'active', count: Math.floor(currentClient.stats.campaigns * 0.6), color: 'bg-green-500' },
          { status: 'paused', count: Math.floor(currentClient.stats.campaigns * 0.2), color: 'bg-yellow-500' },
          { status: 'draft', count: Math.floor(currentClient.stats.campaigns * 0.1), color: 'bg-gray-500' },
          { status: 'completed', count: Math.floor(currentClient.stats.campaigns * 0.1), color: 'bg-blue-500' }
        ],
        recentActivity: [
          { type: 'campaign_created', message: `New campaign created for ${currentClient.name}`, time: '2 hours ago' },
          { type: 'contact_added', message: `${Math.floor(currentClient.stats.contacts * 0.1)} new contacts added`, time: '4 hours ago' },
          { type: 'message_sent', message: `${Math.floor(currentClient.stats.contacts * 0.05)} messages sent`, time: '6 hours ago' },
          { type: 'duxsoup_update', message: 'DuxSoup settings updated', time: '1 day ago' }
        ]
      };
      
      setStats(clientStats);
    } catch (error) {
      setError('Failed to load client dashboard data');
      console.error('Error fetching client dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Try to fetch campaigns from the API endpoint, but fall back to mock data if it fails
      try {
        const campaignsResponse = await axios.get('http://localhost:8000/api/campaigns');
        const campaignsData = campaignsResponse.data;
        
        // Calculate stats from real campaign data
        const totalCampaigns = campaignsData.length;
        const activeCampaigns = campaignsData.filter(c => c.status === 'active').length;
        const pausedCampaigns = campaignsData.filter(c => c.status === 'paused').length;
        const draftCampaigns = campaignsData.filter(c => c.status === 'draft').length;
        const completedCampaigns = campaignsData.filter(c => c.status === 'completed').length;
        
        const realStats = {
          totalCampaigns,
          activeCampaigns,
          totalContacts: 20, // This would come from a contacts API
          totalMessages: 15, // This would come from a messages API
          campaignsByStatus: [
            { status: 'active', count: activeCampaigns, color: 'bg-green-500' },
            { status: 'paused', count: pausedCampaigns, color: 'bg-yellow-500' },
            { status: 'draft', count: draftCampaigns, color: 'bg-gray-500' },
            { status: 'completed', count: completedCampaigns, color: 'bg-blue-500' }
          ],
          recentActivity: [
            { type: 'campaign_created', message: `${totalCampaigns} campaigns available`, time: 'Just now' },
            { type: 'contact_added', message: '15 new contacts added to campaigns', time: '4 hours ago' },
            { type: 'message_sent', message: '20 messages sent successfully', time: '6 hours ago' },
            { type: 'webhook_received', message: 'New webhook event processed', time: '8 hours ago' }
          ]
        };
        
        setStats(realStats);
      } catch (apiError) {
        console.log('API call failed, using mock data:', apiError);
        
        // Log mock data usage
        logMockData('Dashboard', 'fallback_dashboard_stats', {
          reason: 'API_FAILURE',
          error: apiError.message,
          fallback: true
        });
        
        // Fall back to mock data if API fails
        const mockStats = {
          totalCampaigns: 3,
          activeCampaigns: 2,
          totalContacts: 25,
          totalMessages: 18,
          campaignsByStatus: [
            { status: 'active', count: 2, color: 'bg-green-500' },
            { status: 'paused', count: 1, color: 'bg-yellow-500' },
            { status: 'draft', count: 0, color: 'bg-gray-500' },
            { status: 'completed', count: 0, color: 'bg-blue-500' }
          ],
          recentActivity: [
            { type: 'campaign_created', message: '3 campaigns available', time: 'Just now' },
            { type: 'contact_added', message: '15 new contacts added to campaigns', time: '4 hours ago' },
            { type: 'message_sent', message: '20 messages sent successfully', time: '6 hours ago' },
            { type: 'webhook_received', message: 'New webhook event processed', time: '8 hours ago' }
          ]
        };
        setStats(mockStats);
      }
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="text-red-400">
            <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (isAgency && !currentClient) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No client selected</h3>
        <p className="mt-1 text-sm text-gray-500">
          Please select a client from the dropdown above to view their dashboard.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          {isAgency && currentClient ? `${currentClient.name} Dashboard` : 'Dashboard'}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {isAgency && currentClient 
            ? `Overview of ${currentClient.name}'s LinkedIn automation campaigns and performance`
            : 'Overview of your LinkedIn automation campaigns and performance'
          }
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Campaigns"
          value={stats.totalCampaigns}
          icon={BarChart3}
          color="bg-blue-500"
        />
        <StatCard
          title="Active Campaigns"
          value={stats.activeCampaigns}
          icon={Play}
          color="bg-green-500"
        />
        <StatCard
          title="Total Contacts"
          value={stats.totalContacts}
          icon={Users}
          color="bg-purple-500"
        />
        <StatCard
          title="Messages Sent"
          value={stats.totalMessages}
          icon={MessageSquare}
          color="bg-indigo-500"
        />
      </div>

      {/* Campaign Status Overview */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Campaign Status Overview
          </h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {stats.campaignsByStatus.map((status) => (
              <div key={status.status} className="text-center">
                <div className={`mx-auto flex items-center justify-center h-12 w-12 rounded-full ${status.color}`}>
                  {status.status === 'active' && <Play className="h-6 w-6 text-white" />}
                  {status.status === 'paused' && <Pause className="h-6 w-6 text-white" />}
                  {status.status === 'draft' && <Clock className="h-6 w-6 text-white" />}
                  {status.status === 'completed' && <CheckCircle className="h-6 w-6 text-white" />}
                </div>
                <div className="mt-2">
                  <p className="text-sm font-medium text-gray-900 capitalize">{status.status}</p>
                  <p className="text-2xl font-semibold text-gray-900">{status.count}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Recent Activity
          </h3>
          <div className="flow-root">
            <ul className="-mb-8">
              {stats.recentActivity.map((activity, index) => (
                <li key={index}>
                  <div className="relative pb-8">
                    {index !== stats.recentActivity.length - 1 && (
                      <span
                        className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                        aria-hidden="true"
                      />
                    )}
                    <div className="relative flex space-x-3">
                      <div>
                        <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                          <TrendingUp className="h-4 w-4 text-white" />
                        </span>
                      </div>
                      <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                          <p className="text-sm text-gray-500">{activity.message}</p>
                        </div>
                        <div className="text-right text-sm whitespace-nowrap text-gray-500">
                          <time>{activity.time}</time>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
              <BarChart3 className="mr-2 h-4 w-4" />
              Create Campaign
            </button>
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
              <Users className="mr-2 h-4 w-4" />
              Add Contacts
            </button>
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700">
              <MessageSquare className="mr-2 h-4 w-4" />
              Send Message
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color }) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={`inline-flex items-center justify-center h-8 w-8 rounded-md ${color}`}>
              <Icon className="h-5 w-5 text-white" />
            </div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd className="text-lg font-medium text-gray-900">{value}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
