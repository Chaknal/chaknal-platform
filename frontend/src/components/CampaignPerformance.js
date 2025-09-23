import React, { useState, useEffect } from 'react';
import { ArrowLeft, Users, MessageSquare, UserCheck, Calendar, Eye, Filter, Search } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

function CampaignPerformance({ currentClient, isAgency }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedCampaign, setSelectedCampaign] = useState('Professional Outreach');
  const [selectedMetric, setSelectedMetric] = useState('all'); // all, accepted, responded, meetings
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(location.state?.selectedUser || 'all');

  // Available users
  const availableUsers = [
    { email: 'all', name: 'All Users', isReal: false },
    { email: 'scampos@wallarm.com', name: 'Sercio Campos', isReal: true },
    { email: 'john.smith@marketingmasters.com', name: 'John Smith', isReal: false },
    { email: 'sarah.johnson@marketingmasters.com', name: 'Sarah Johnson', isReal: false },
    { email: 'michael.davis@marketingmasters.com', name: 'Michael Davis', isReal: false }
  ];

  // Campaign data with detailed contact information
  const campaignData = {
    'Professional Outreach': {
      description: 'Targeting senior professionals in tech industry',
      all: {
        contacts: [
          { name: 'Sergio Campos', title: 'VP of Engineering', company: 'TechCorp', linkedin: 'https://linkedin.com/in/sergio-campos-97b9b7362/', status: 'responded', meeting_booked: true, user: 'scampos@wallarm.com' },
          { name: 'Emily Rodriguez', title: 'CTO', company: 'DataFlow Inc', linkedin: 'https://linkedin.com/in/emily-rodriguez', status: 'accepted', meeting_booked: false, user: 'john.smith@marketingmasters.com' },
          { name: 'Michael Chen', title: 'Engineering Director', company: 'CloudBase', linkedin: 'https://linkedin.com/in/michael-chen', status: 'responded', meeting_booked: false, user: 'sarah.johnson@marketingmasters.com' },
          { name: 'Sarah Williams', title: 'Head of Product', company: 'InnovateTech', linkedin: 'https://linkedin.com/in/sarah-williams', status: 'accepted', meeting_booked: false, user: 'michael.davis@marketingmasters.com' },
          { name: 'David Kim', title: 'Senior Developer', company: 'CodeCraft', linkedin: 'https://linkedin.com/in/david-kim', status: 'sent', meeting_booked: false, user: 'scampos@wallarm.com' },
          { name: 'Lisa Thompson', title: 'Tech Lead', company: 'DevSolutions', linkedin: 'https://linkedin.com/in/lisa-thompson', status: 'accepted', meeting_booked: false, user: 'john.smith@marketingmasters.com' },
          { name: 'Robert Johnson', title: 'Software Architect', company: 'BuildTech', linkedin: 'https://linkedin.com/in/robert-johnson', status: 'sent', meeting_booked: false, user: 'sarah.johnson@marketingmasters.com' },
          { name: 'Amanda Davis', title: 'VP Technology', company: 'NextGen Systems', linkedin: 'https://linkedin.com/in/amanda-davis', status: 'responded', meeting_booked: false, user: 'michael.davis@marketingmasters.com' }
        ]
      }
    },
    'Q4 Lead Generation': {
      description: 'End of year sales push targeting decision makers',
      all: {
        contacts: [
          { name: 'James Wilson', title: 'CEO', company: 'GrowthCorp', linkedin: 'https://linkedin.com/in/james-wilson', status: 'responded', meeting_booked: true, user: 'scampos@wallarm.com' },
          { name: 'Maria Garcia', title: 'Sales Director', company: 'Revenue Inc', linkedin: 'https://linkedin.com/in/maria-garcia', status: 'accepted', meeting_booked: true, user: 'john.smith@marketingmasters.com' },
          { name: 'Kevin Brown', title: 'VP Sales', company: 'ScaleUp Ltd', linkedin: 'https://linkedin.com/in/kevin-brown', status: 'responded', meeting_booked: true, user: 'sarah.johnson@marketingmasters.com' },
          { name: 'Jennifer Lee', title: 'Business Development', company: 'Expand Co', linkedin: 'https://linkedin.com/in/jennifer-lee', status: 'accepted', meeting_booked: false, user: 'michael.davis@marketingmasters.com' },
          { name: 'Thomas Anderson', title: 'Chief Revenue Officer', company: 'ProfitMax', linkedin: 'https://linkedin.com/in/thomas-anderson', status: 'sent', meeting_booked: false, user: 'scampos@wallarm.com' }
        ]
      }
    },
    'Executive Outreach': {
      description: 'High-level executive targeting for enterprise deals',
      all: {
        contacts: [
          { name: 'Patricia Miller', title: 'CEO', company: 'Enterprise Solutions', linkedin: 'https://linkedin.com/in/patricia-miller', status: 'responded', meeting_booked: true, user: 'scampos@wallarm.com' },
          { name: 'Richard Taylor', title: 'President', company: 'Global Dynamics', linkedin: 'https://linkedin.com/in/richard-taylor', status: 'accepted', meeting_booked: true, user: 'john.smith@marketingmasters.com' },
          { name: 'Susan Clark', title: 'COO', company: 'OperateWell', linkedin: 'https://linkedin.com/in/susan-clark', status: 'sent', meeting_booked: false, user: 'sarah.johnson@marketingmasters.com' },
          { name: 'Mark Johnson', title: 'VP Strategy', company: 'Strategic Inc', linkedin: 'https://linkedin.com/in/mark-johnson', status: 'accepted', meeting_booked: false, user: 'michael.davis@marketingmasters.com' }
        ]
      }
    }
  };

  // Filter contacts based on selected user and metric
  const getFilteredContacts = () => {
    let contacts = campaignData[selectedCampaign]?.all.contacts || [];
    
    // Filter by user if not 'all'
    if (selectedUser !== 'all') {
      contacts = contacts.filter(contact => contact.user === selectedUser);
    }
    
    // Filter by metric
    if (selectedMetric === 'accepted') {
      contacts = contacts.filter(contact => contact.status === 'accepted' || contact.status === 'responded');
    } else if (selectedMetric === 'responded') {
      contacts = contacts.filter(contact => contact.status === 'responded');
    } else if (selectedMetric === 'meetings') {
      contacts = contacts.filter(contact => contact.meeting_booked);
    }
    
    // Filter by search term
    if (searchTerm) {
      contacts = contacts.filter(contact => 
        contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return contacts;
  };

  const filteredContacts = getFilteredContacts();

  // Get campaign stats
  const getCampaignStats = () => {
    const allContacts = campaignData[selectedCampaign]?.all.contacts || [];
    let contacts = selectedUser !== 'all' ? allContacts.filter(c => c.user === selectedUser) : allContacts;
    
    return {
      total: contacts.length,
      accepted: contacts.filter(c => c.status === 'accepted' || c.status === 'responded').length,
      responded: contacts.filter(c => c.status === 'responded').length,
      meetings: contacts.filter(c => c.meeting_booked).length
    };
  };

  const stats = getCampaignStats();

  const handleContactClick = (contact) => {
    // Navigate to contacts page with this specific contact
    navigate('/contacts', { 
      state: { 
        highlightContact: contact.linkedin,
        fromCampaign: selectedCampaign 
      } 
    });
  };

  const getStatusBadge = (status) => {
    const styles = {
      sent: 'bg-gray-100 text-gray-800',
      accepted: 'bg-blue-100 text-blue-800',
      responded: 'bg-green-100 text-green-800'
    };
    return styles[status] || styles.sent;
  };

  const getUserName = (email) => {
    const user = availableUsers.find(u => u.email === email);
    return user ? user.name : email;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/analytics')}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back to Analytics
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Campaign Performance Details</h1>
            <p className="text-sm text-gray-500">
              {isAgency && currentClient ? `${currentClient.name} - ` : ''}
              Detailed campaign analysis and contact drill-down
            </p>
          </div>
        </div>
      </div>

      {/* Campaign Selection and Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Campaign</label>
            <select
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {Object.keys(campaignData).map(campaign => (
                <option key={campaign} value={campaign}>{campaign}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">User Filter</label>
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Metric Filter</label>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Contacts</option>
              <option value="accepted">Accepted Only</option>
              <option value="responded">Responded Only</option>
              <option value="meetings">Meeting Booked</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search contacts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="mt-4 p-4 bg-gray-50 rounded-md">
          <h3 className="text-sm font-medium text-gray-900 mb-2">{selectedCampaign}</h3>
          <p className="text-sm text-gray-600 mb-3">{campaignData[selectedCampaign]?.description}</p>
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">{stats.total}</div>
              <div className="text-xs text-gray-500">Total Contacts</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-blue-600">{stats.accepted}</div>
              <div className="text-xs text-gray-500">Accepted</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-green-600">{stats.responded}</div>
              <div className="text-xs text-gray-500">Responded</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-orange-600">{stats.meetings}</div>
              <div className="text-xs text-gray-500">Meetings</div>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Results */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Contact Results ({filteredContacts.length})
            </h3>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Filter className="h-4 w-4" />
              <span>
                {selectedMetric === 'all' ? 'All contacts' : 
                 selectedMetric === 'accepted' ? 'Accepted connections' :
                 selectedMetric === 'responded' ? 'Responded to messages' :
                 'Booked meetings'}
              </span>
            </div>
          </div>

          {filteredContacts.length === 0 ? (
            <div className="text-center py-8">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No contacts found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your filters or search terms.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Assigned User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Meeting
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredContacts.map((contact, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center">
                              <Users className="h-5 w-5 text-white" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{contact.name}</div>
                            <div className="text-sm text-gray-500">{contact.title}</div>
                            <div className="text-sm text-gray-500">{contact.company}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(contact.status)}`}>
                          {contact.status.charAt(0).toUpperCase() + contact.status.slice(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center">
                          {contact.user === 'scampos@wallarm.com' && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2">
                              Real
                            </span>
                          )}
                          {getUserName(contact.user)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {contact.meeting_booked ? (
                          <div className="flex items-center text-green-600">
                            <Calendar className="h-4 w-4 mr-1" />
                            <span className="text-sm">Booked</span>
                          </div>
                        ) : (
                          <span className="text-sm text-gray-400">None</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => handleContactClick(contact)}
                          className="text-blue-600 hover:text-blue-900 flex items-center"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CampaignPerformance;
