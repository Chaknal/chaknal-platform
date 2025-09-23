import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Building2, 
  Users, 
  BarChart3, 
  MessageSquare, 
  Activity, 
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Eye
} from 'lucide-react';

const AgencyOverview = ({ onClientSelect }) => {
  const navigate = useNavigate();
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOverview();
  }, []);

  const handleClientSelect = (client) => {
    onClientSelect(client);
    navigate('/');
  };

  const fetchOverview = async () => {
    try {
      // Mock data for demo purposes
      const mockOverview = {
        total_clients: 3,
        total_dux_accounts: 3,
        total_campaigns: 6,
        total_messages: 0,
        clients: [
          {
            id: "1",
            name: "TechCorp Solutions",
            domain: "techcorp-demo.com",
            access_level: "full",
            stats: {
              dux_accounts: 1,
              campaigns: 2,
              contacts: 87,
              messages: 0
            }
          },
          {
            id: "2", 
            name: "Marketing Masters",
            domain: "marketingmasters-demo.com",
            access_level: "full",
            stats: {
              dux_accounts: 1,
              campaigns: 2,
              contacts: 70,
              messages: 0
            }
          },
          {
            id: "3",
            name: "SalesForce Pro", 
            domain: "salesforcepro-demo.com",
            access_level: "full",
            stats: {
              dux_accounts: 1,
              campaigns: 2,
              contacts: 81,
              messages: 0
            }
          }
        ],
        recent_activity: [
          {
            id: "1",
            description: "Created new campaign: Q4 Lead Generation",
            client_name: "TechCorp Solutions",
            created_at: "2025-09-10T15:28:54Z"
          },
          {
            id: "2",
            description: "Updated DuxSoup settings for Marketing Masters",
            client_name: "Marketing Masters", 
            created_at: "2025-09-10T15:28:54Z"
          },
          {
            id: "3",
            description: "Added 81 new contacts to SalesForce Pro",
            client_name: "SalesForce Pro",
            created_at: "2025-09-10T15:28:54Z"
          }
        ]
      };
      
      setOverview(mockOverview);
    } catch (error) {
      console.error('Error fetching agency overview:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'inactive': return 'text-red-600 bg-red-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4" />;
      case 'inactive': return <AlertCircle className="h-4 w-4" />;
      case 'warning': return <Clock className="h-4 w-4" />;
      default: return <Eye className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="agency-overview">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="skeleton-line h-4 w-20 mb-2"></div>
              <div className="skeleton-line h-8 w-16"></div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="skeleton-line h-6 w-32 mb-4"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="skeleton-line h-16 w-full"></div>
              ))}
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="skeleton-line h-6 w-32 mb-4"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="skeleton-line h-12 w-full"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="agency-overview">
        <div className="text-center py-12">
          <Building2 className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No clients found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Start by adding clients to your agency account.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="agency-overview">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Building2 className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Clients</p>
              <p className="text-2xl font-semibold text-gray-900">{overview.total_clients}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">DuxSoup Accounts</p>
              <p className="text-2xl font-semibold text-gray-900">{overview.total_dux_accounts}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BarChart3 className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Campaigns</p>
              <p className="text-2xl font-semibold text-gray-900">{overview.total_campaigns}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <MessageSquare className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Messages</p>
              <p className="text-2xl font-semibold text-gray-900">{overview.total_messages}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Clients List */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Your Clients</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {overview.clients.map((client) => (
              <div key={client.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <Building2 className="h-5 w-5 text-gray-400" />
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{client.name}</h4>
                        <p className="text-sm text-gray-500">{client.domain}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">
                        {client.stats.dux_accounts} accounts
                      </div>
                      <div className="text-sm text-gray-500">
                        {client.stats.campaigns} campaigns
                      </div>
                    </div>
                    <button
                      onClick={() => handleClientSelect(client)}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      Manage
                    </button>
                  </div>
                </div>
                <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor('active')}`}>
                    {getStatusIcon('active')}
                    <span className="ml-1">{client.access_level}</span>
                  </span>
                  <span>{client.stats.contacts} contacts</span>
                  <span>{client.stats.messages} messages</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {overview.recent_activity.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                <Activity className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                <p>No recent activity</p>
              </div>
            ) : (
              overview.recent_activity.map((activity) => (
                <div key={activity.id} className="px-6 py-4">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <Activity className="h-4 w-4 text-blue-600" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900">{activity.description}</p>
                      <p className="text-sm text-gray-500">
                        {activity.client_name} • {new Date(activity.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgencyOverview;
