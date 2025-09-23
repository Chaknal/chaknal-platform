import React, { useState, useEffect } from 'react';
import { BarChart3, Users, MessageSquare, Calendar, Target, UserCheck, ExternalLink, ChevronDown, Filter, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function CampaignsNew({ currentClient, isAgency }) {
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState('all');
  const [selectedCompany, setSelectedCompany] = useState('all');
  const [selectedPerson, setSelectedPerson] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const navigate = useNavigate();

  // Available filter options
  const availableUsers = [
    { email: 'all', name: 'All Users', isReal: false },
    { email: 'scampos@wallarm.com', name: 'Sercio Campos', isReal: true },
    { email: 'john.smith@marketingmasters.com', name: 'John Smith', isReal: false },
    { email: 'sarah.johnson@marketingmasters.com', name: 'Sarah Johnson', isReal: false },
    { email: 'michael.davis@marketingmasters.com', name: 'Michael Davis', isReal: false }
  ];

  const availableCompanies = [
    'All Companies', 'TechCorp', 'DataFlow Inc', 'CloudBase', 'InnovateTech', 'CodeCraft', 
    'DevSolutions', 'BuildTech', 'NextGen Systems', 'GrowthCorp', 'Revenue Inc', 'ScaleUp Ltd',
    'Expand Co', 'ProfitMax', 'Enterprise Solutions', 'Global Dynamics', 'OperateWell', 'Strategic Inc'
  ];

  useEffect(() => {
    setLoading(false);
  }, [selectedUser, selectedCompany, selectedPerson, currentClient]);

  // Get campaign performance data with filtering
  const getCampaignData = () => {
    const baseCampaigns = [
      {
        name: 'Professional Outreach',
        description: 'Targeting senior professionals in tech industry',
        all: { sent: 157, accepted: 90, responded: 35, meetings_booked: 1 },
        'scampos@wallarm.com': { sent: 45, accepted: 28, responded: 12, meetings_booked: 1 },
        'john.smith@marketingmasters.com': { sent: 38, accepted: 22, responded: 8, meetings_booked: 0 },
        'sarah.johnson@marketingmasters.com': { sent: 42, accepted: 24, responded: 9, meetings_booked: 0 },
        'michael.davis@marketingmasters.com': { sent: 31, accepted: 15, responded: 5, meetings_booked: 0 }
      },
      {
        name: 'Q4 Lead Generation',
        description: 'End of year sales push targeting decision makers',
        all: { sent: 203, accepted: 127, responded: 45, meetings_booked: 3 },
        'scampos@wallarm.com': { sent: 58, accepted: 38, responded: 15, meetings_booked: 2 },
        'john.smith@marketingmasters.com': { sent: 52, accepted: 32, responded: 12, meetings_booked: 1 },
        'sarah.johnson@marketingmasters.com': { sent: 48, accepted: 29, responded: 10, meetings_booked: 0 },
        'michael.davis@marketingmasters.com': { sent: 45, accepted: 28, responded: 8, meetings_booked: 0 }
      },
      {
        name: 'Executive Outreach',
        description: 'High-level executive targeting for enterprise deals',
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
        description: campaign.description,
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

  const campaignData = getCampaignData();

  // Filter campaigns based on search and company filter
  const filteredCampaigns = campaignData.filter(campaign => {
    if (searchTerm && !campaign.name.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    // Company and person filtering would require more detailed data
    return true;
  });

  // Navigate to contacts with campaign filter
  const handleCampaignMetricClick = (campaign, metric) => {
    const filterState = {
      campaign: campaign.name,
      user: selectedUser,
      status: metric,
      fromAnalytics: true
    };
    
    navigate('/contacts', { state: filterState });
  };

  // Navigate to campaign details
  const handleCampaignNameClick = (campaign) => {
    navigate('/campaign-performance', { 
      state: { 
        selectedCampaign: campaign.name,
        selectedUser: selectedUser 
      } 
    });
  };

  const selectedUserName = availableUsers.find(u => u.email === selectedUser)?.name || 'All Users';

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="mt-1 text-sm text-gray-500">Loading campaign performance data...</p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Filters */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isAgency && currentClient ? `${currentClient.name} Campaigns` : 'Campaigns'}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Campaign performance breakdown and management
          </p>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Filter className="h-4 w-4 mr-2" />
          Filters
          <ChevronDown className="ml-2 h-4 w-4" />
        </button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="bg-white shadow rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* User Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Team Member</label>
              <select
                value={selectedUser}
                onChange={(e) => setSelectedUser(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {availableUsers.map(user => (
                  <option key={user.email} value={user.email}>
                    {user.name} {user.isReal ? '(Real User)' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Company Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Company</label>
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {availableCompanies.map(company => (
                  <option key={company} value={company.toLowerCase().replace(/\s+/g, '_')}>
                    {company}
                  </option>
                ))}
              </select>
            </div>

            {/* Person Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Contact Person</label>
              <select
                value={selectedPerson}
                onChange={(e) => setSelectedPerson(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Contacts</option>
                <option value="sergio_campos">Sergio Campos (Real Contact)</option>
                <option value="responded_only">Responded Contacts Only</option>
                <option value="meeting_booked">Meeting Booked Only</option>
              </select>
            </div>

            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search campaigns..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-600">
            Showing {selectedUser === 'all' ? 'all team members' : selectedUserName} • 
            {selectedCompany === 'all' ? ' All companies' : ` ${selectedCompany}`} • 
            {filteredCampaigns.length} campaigns
          </div>
        </div>
      )}

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
                {filteredCampaigns.map((campaign) => (
                  <tr key={campaign.name} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col">
                        <button
                          onClick={() => handleCampaignNameClick(campaign)}
                          className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline text-left"
                        >
                          {campaign.name}
                        </button>
                        <span className="text-xs text-gray-500">{campaign.description}</span>
                      </div>
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

          {filteredCampaigns.length === 0 && (
            <div className="text-center py-8">
              <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No campaigns found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your filters or search terms.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BarChart3 className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Campaigns</dt>
                  <dd className="text-lg font-medium text-gray-900">{filteredCampaigns.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Users className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Contacts</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {filteredCampaigns.reduce((sum, campaign) => sum + campaign.sent, 0)}
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
                <MessageSquare className="h-6 w-6 text-purple-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Responses</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {filteredCampaigns.reduce((sum, campaign) => sum + campaign.responded, 0)}
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
                <Calendar className="h-6 w-6 text-orange-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Meetings</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {filteredCampaigns.reduce((sum, campaign) => sum + campaign.meetings_booked, 0)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CampaignsNew;
