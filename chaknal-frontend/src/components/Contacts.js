import React, { useState, useEffect, useCallback } from 'react';
import { 
  Users, 
  Search, 
  Filter, 
  Download, 
  Eye, 
  MessageCircle, 
  CheckCircle, 
  Clock, 
  X,
  ChevronDown,
  ChevronUp,
  Plus,
  UserPlus,
  CheckSquare,
  Square
} from 'lucide-react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import { logMockData } from '../utils/mockDataLogger';

function Contacts({ currentClient, isAgency }) {
  const location = useLocation();
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [highlightedContact, setHighlightedContact] = useState(location.state?.highlightContact || null);
  const [filterOptions, setFilterOptions] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [pagination, setPagination] = useState({
    limit: 50,
    offset: 0,
    total: 0
  });
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  
  // Bulk selection and enrollment state
  const [selectedContacts, setSelectedContacts] = useState(new Set());
  const [showEnrollmentModal, setShowEnrollmentModal] = useState(false);
  const [enrollmentData, setEnrollmentData] = useState({
    campaign_id: '',
    assigned_to: '',
    status: 'pending',
    tags: []
  });
  const [enrollmentLoading, setEnrollmentLoading] = useState(false);
  
  // Add contact modal state
  const [showAddContactModal, setShowAddContactModal] = useState(false);
  const [addContactData, setAddContactData] = useState({
    name: '',
    email: '',
    company: '',
    title: '',
    linkedin_url: ''
  });
  const [addContactLoading, setAddContactLoading] = useState(false);

  // Fetch contacts
  const fetchContacts = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: pagination.limit.toString(),
        offset: pagination.offset.toString(),
        sort_by: sortBy,
        sort_order: sortOrder,
        ...filters
      });
      
      if (searchTerm) {
        params.append('search', searchTerm);
      }

      const response = await axios.get(`/api/contacts?${params}`);
      setContacts(response.data);
      
      // Update pagination total (this would need to be returned from API)
      setPagination(prev => ({ ...prev, total: response.data.length }));
    } catch (error) {
      console.error('Error fetching contacts:', error);
    } finally {
      setLoading(false);
    }
  }, [pagination.limit, pagination.offset, sortBy, sortOrder, filters, searchTerm]);

  // Fetch filter options
  const fetchFilterOptions = useCallback(async () => {
    try {
      const response = await axios.get('/api/contacts/filters');
      setFilterOptions(response.data);
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  }, []);

  // Fetch client-specific contacts
  const fetchClientContacts = useCallback(async () => {
    try {
      setLoading(true);
      
      // Fetch real contacts from database
      const apiParams = {
        limit: pagination.limit.toString(),
        offset: pagination.offset.toString(),
        sort_by: sortBy,
        sort_order: sortOrder
      };
      
      // Map filters to API parameters
      if (filters.campaign || filters.campaign_name) {
        apiParams.campaign = filters.campaign || filters.campaign_name;
      }
      if (filters.assigned_user || filters.owner_id) {
        apiParams.assigned_user = filters.assigned_user || filters.owner_id;
      }
      if (filters.status) {
        apiParams.status = filters.status;
      }
      if (filters.has_meeting) {
        apiParams.has_meeting = filters.has_meeting;
      }
      
      const params = new URLSearchParams(apiParams);
      
      if (searchTerm) {
        params.append('search', searchTerm);
      }

      const response = await axios.get(`http://localhost:8000/api/contacts/campaign-data?${params}`);
      
      if (response.data.success) {
        setContacts(response.data.data);
        setPagination(prev => ({ ...prev, total: response.data.total || response.data.data.length }));
      } else {
        // Log mock data usage
        logMockData('Contacts', 'client_contacts_fallback', {
          reason: 'API_FALLBACK',
          client: currentClient?.name,
          note: 'API response but fallback to mock data'
        });
        
        // Fallback to mock data if API fails
        let clientContacts = generateClientContacts(currentClient);
        clientContacts = applyFiltersToContacts(clientContacts, filters, searchTerm);
        setContacts(clientContacts);
        setPagination(prev => ({ ...prev, total: clientContacts.length }));
      }
    } catch (error) {
      console.error('Error fetching client contacts:', error);
      
      // Log mock data usage
      logMockData('Contacts', 'client_contacts_error', {
        reason: 'API_ERROR',
        client: currentClient?.name,
        error: error.message,
        fallback: true
      });
      
      // Fallback to mock data if API fails
      let clientContacts = generateClientContacts(currentClient);
      clientContacts = applyFiltersToContacts(clientContacts, filters, searchTerm);
      setContacts(clientContacts);
      setPagination(prev => ({ ...prev, total: clientContacts.length }));
    } finally {
      setLoading(false);
    }
  }, [currentClient, filters, searchTerm, pagination.limit, pagination.offset, sortBy, sortOrder]);

  const generateClientContacts = (client) => {
    const contacts = [];
    
    // Define specific contacts that match our Analytics data
    const campaignContacts = [
      // Professional Outreach Campaign
      { name: 'Sergio Campos', title: 'VP of Engineering', company: 'TechCorp', linkedin: 'https://linkedin.com/in/sergio-campos-97b9b7362/', status: 'responded', campaign: 'Professional Outreach', user: 'scampos@wallarm.com', has_meeting: true },
      { name: 'Emily Rodriguez', title: 'CTO', company: 'DataFlow Inc', linkedin: 'https://linkedin.com/in/emily-rodriguez', status: 'accepted', campaign: 'Professional Outreach', user: 'john.smith@marketingmasters.com', has_meeting: false },
      { name: 'Michael Chen', title: 'Engineering Director', company: 'CloudBase', linkedin: 'https://linkedin.com/in/michael-chen', status: 'responded', campaign: 'Professional Outreach', user: 'sarah.johnson@marketingmasters.com', has_meeting: false },
      { name: 'Sarah Williams', title: 'Head of Product', company: 'InnovateTech', linkedin: 'https://linkedin.com/in/sarah-williams', status: 'accepted', campaign: 'Professional Outreach', user: 'michael.davis@marketingmasters.com', has_meeting: false },
      { name: 'David Kim', title: 'Senior Developer', company: 'CodeCraft', linkedin: 'https://linkedin.com/in/david-kim', status: 'sent', campaign: 'Professional Outreach', user: 'scampos@wallarm.com', has_meeting: false },
      
      // Q4 Lead Generation Campaign
      { name: 'James Wilson', title: 'CEO', company: 'GrowthCorp', linkedin: 'https://linkedin.com/in/james-wilson', status: 'responded', campaign: 'Q4 Lead Generation', user: 'scampos@wallarm.com', has_meeting: true },
      { name: 'Maria Garcia', title: 'Sales Director', company: 'Revenue Inc', linkedin: 'https://linkedin.com/in/maria-garcia', status: 'accepted', campaign: 'Q4 Lead Generation', user: 'john.smith@marketingmasters.com', has_meeting: true },
      { name: 'Kevin Brown', title: 'VP Sales', company: 'ScaleUp Ltd', linkedin: 'https://linkedin.com/in/kevin-brown', status: 'responded', campaign: 'Q4 Lead Generation', user: 'sarah.johnson@marketingmasters.com', has_meeting: true },
      { name: 'Jennifer Lee', title: 'Business Development', company: 'Expand Co', linkedin: 'https://linkedin.com/in/jennifer-lee', status: 'accepted', campaign: 'Q4 Lead Generation', user: 'michael.davis@marketingmasters.com', has_meeting: false },
      
      // Executive Outreach Campaign  
      { name: 'Patricia Miller', title: 'CEO', company: 'Enterprise Solutions', linkedin: 'https://linkedin.com/in/patricia-miller', status: 'responded', campaign: 'Executive Outreach', user: 'scampos@wallarm.com', has_meeting: true },
      { name: 'Richard Taylor', title: 'President', company: 'Global Dynamics', linkedin: 'https://linkedin.com/in/richard-taylor', status: 'accepted', campaign: 'Executive Outreach', user: 'john.smith@marketingmasters.com', has_meeting: true },
      { name: 'Susan Clark', title: 'COO', company: 'OperateWell', linkedin: 'https://linkedin.com/in/susan-clark', status: 'sent', campaign: 'Executive Outreach', user: 'sarah.johnson@marketingmasters.com', has_meeting: false },
      { name: 'Mark Johnson', title: 'VP Strategy', company: 'Strategic Inc', linkedin: 'https://linkedin.com/in/mark-johnson', status: 'accepted', campaign: 'Executive Outreach', user: 'michael.davis@marketingmasters.com', has_meeting: false }
    ];
    
    // Add the specific contacts
    campaignContacts.forEach((contact, index) => {
      const [firstName, lastName] = contact.name.split(' ');
      contacts.push({
        contact_id: index + 1,
        first_name: firstName,
        last_name: lastName,
        full_name: contact.name,
        company: contact.company,
        title: contact.title,
        linkedin_url: contact.linkedin,
        email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${contact.company.toLowerCase().replace(/\s+/g, '')}.com`,
        status: contact.status,
        campaign: contact.campaign,
        assigned_user: contact.user,
        has_meeting: contact.has_meeting,
        created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
        last_activity: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
      });
    });
    
    // Add some additional random contacts to reach the client's contact count
    const additionalCount = Math.max(0, Math.min(client.stats.contacts - campaignContacts.length, 30));
    const firstNames = ['Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Jamie', 'Riley', 'Avery', 'Quinn', 'Sage'];
    const lastNames = ['Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson'];
    const companies = ['TechFlow', 'InnovateNow', 'DataSync', 'CloudTech', 'NextWave', 'FutureGen', 'SmartBiz', 'DigitalPro'];
    const titles = ['Manager', 'Director', 'VP', 'Senior Manager', 'Lead', 'Principal', 'Head of Operations', 'Chief Officer'];
    const campaigns = ['Professional Outreach', 'Q4 Lead Generation', 'Executive Outreach'];
    const users = ['scampos@wallarm.com', 'john.smith@marketingmasters.com', 'sarah.johnson@marketingmasters.com', 'michael.davis@marketingmasters.com'];
    const statuses = ['sent', 'accepted', 'responded'];
    
    for (let i = 0; i < additionalCount; i++) {
      const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
      const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
      const company = companies[Math.floor(Math.random() * companies.length)];
      const title = titles[Math.floor(Math.random() * titles.length)];
      const campaign = campaigns[Math.floor(Math.random() * campaigns.length)];
      const user = users[Math.floor(Math.random() * users.length)];
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      
      contacts.push({
        contact_id: campaignContacts.length + i + 1,
        first_name: firstName,
        last_name: lastName,
        full_name: `${firstName} ${lastName}`,
        company: company,
        title: title,
        linkedin_url: `https://linkedin.com/in/${firstName.toLowerCase()}-${lastName.toLowerCase()}-${Math.random().toString(36).substr(2, 9)}`,
        email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${company.toLowerCase()}.com`,
        status: status,
        campaign: campaign,
        assigned_user: user,
        has_meeting: Math.random() < 0.1, // 10% chance of having a meeting
        created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
        last_activity: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
      });
    }
    
    return contacts;
  };

  // Apply filters to contacts array
  const applyFiltersToContacts = (contacts, filters, searchTerm) => {
    let filteredContacts = [...contacts];

    // Apply search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filteredContacts = filteredContacts.filter(contact =>
        contact.full_name.toLowerCase().includes(term) ||
        contact.company.toLowerCase().includes(term) ||
        contact.title.toLowerCase().includes(term) ||
        contact.email.toLowerCase().includes(term)
      );
    }

    // Apply filters
    Object.entries(filters).forEach(([key, value]) => {
      if (!value) return;

      switch (key) {
        case 'campaign':
          filteredContacts = filteredContacts.filter(contact => 
            contact.campaign === value
          );
          break;
        case 'assigned_user':
          filteredContacts = filteredContacts.filter(contact => 
            contact.assigned_user === value
          );
          break;
        case 'status':
          if (value.includes(',')) {
            // Multiple statuses (e.g., "accepted,responded")
            const statuses = value.split(',');
            filteredContacts = filteredContacts.filter(contact => 
              statuses.includes(contact.status)
            );
          } else {
            filteredContacts = filteredContacts.filter(contact => 
              contact.status === value
            );
          }
          break;
        case 'has_meeting':
          if (value === 'true') {
            filteredContacts = filteredContacts.filter(contact => 
              contact.has_meeting === true
            );
          }
          break;
        default:
          break;
      }
    });

    return filteredContacts;
  };

  useEffect(() => {
    fetchFilterOptions();
  }, [fetchFilterOptions]);

  useEffect(() => {
    // Don't fetch initially if we're coming from Analytics - let the analytics effect handle it
    if (location.state?.fromAnalytics) {
      return;
    }
    if (isAgency && currentClient) {
      fetchClientContacts();
    } else {
      fetchContacts();
    }
  }, [currentClient, isAgency]);

  // Handle analytics navigation with filters
  useEffect(() => {
    if (location.state?.fromAnalytics) {
      const { campaign, user, status } = location.state;
      
      // Apply filters based on analytics selection
      const newFilters = {};
      
      if (campaign && campaign !== 'all') {
        // Set both for API and UI compatibility
        newFilters.campaign = campaign;
        newFilters.campaign_name = campaign;
      }
      
      if (user && user !== 'all') {
        // Set both for API and UI compatibility  
        newFilters.assigned_user = user;
        newFilters.owner_id = user;
      }
      
      if (status === 'accepted') {
        newFilters.status = 'accepted,responded'; // Show both accepted and responded
      } else if (status === 'responded') {
        newFilters.status = 'responded';
      } else if (status === 'meetings') {
        newFilters.has_meeting = 'true';
      } else if (status === 'sent') {
        newFilters.status = 'sent,accepted,responded'; // Show all contacted
      }
      
      setFilters(newFilters);
      setShowFilters(true); // Show filters panel so user can see what's applied
      
      // Clear the location state to prevent re-applying filters
      window.history.replaceState({}, document.title, window.location.pathname);
      
    }
  }, [location.state]);

  // Refetch when filters change
  useEffect(() => {
    if (Object.keys(filters).length > 0) {
      if (isAgency && currentClient) {
        fetchClientContacts();
      } else {
        fetchContacts();
      }
    }
  }, [filters]);

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value || undefined
    }));
    setPagination(prev => ({ ...prev, offset: 0 }));
  };

  // Bulk selection functions
  const toggleContactSelection = (contactId) => {
    setSelectedContacts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(contactId)) {
        newSet.delete(contactId);
      } else {
        newSet.add(contactId);
      }
      return newSet;
    });
  };

  const selectAllContacts = () => {
    setSelectedContacts(new Set(contacts.map(contact => contact.contact_id)));
  };

  const clearSelection = () => {
    setSelectedContacts(new Set());
  };

  const isAllSelected = selectedContacts.size === contacts.length && contacts.length > 0;
  const isPartiallySelected = selectedContacts.size > 0 && selectedContacts.size < contacts.length;

  // Bulk enrollment functions
  const handleBulkEnrollment = async () => {
    if (selectedContacts.size === 0) {
      alert('Please select contacts to enroll');
      return;
    }

    if (!enrollmentData.campaign_id) {
      alert('Please select a campaign');
      return;
    }

    try {
      setEnrollmentLoading(true);
      const response = await axios.post('/api/contacts/bulk-enroll', {
        contact_ids: Array.from(selectedContacts),
        campaign_id: enrollmentData.campaign_id,
        assigned_to: enrollmentData.assigned_to || null,
        status: enrollmentData.status,
        tags: enrollmentData.tags
      });

      if (response.data.success) {
        alert(`Successfully enrolled ${response.data.enrolled_count} contacts. ${response.data.skipped_count} were already enrolled.`);
        setShowEnrollmentModal(false);
        setSelectedContacts(new Set());
        setEnrollmentData({
          campaign_id: '',
          assigned_to: '',
          status: 'pending',
          tags: []
        });
        // Refresh contacts to show updated data
        fetchContacts();
      } else {
        alert(`Enrollment completed with errors: ${response.data.errors.join(', ')}`);
      }
    } catch (error) {
      console.error('Bulk enrollment error:', error);
      alert('Failed to enroll contacts. Please try again.');
    } finally {
      setEnrollmentLoading(false);
    }
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({});
    setSearchTerm('');
    setPagination(prev => ({ ...prev, offset: 0 }));
  };

  // Handle sorting
  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  // Get status badge styling
  const getStatusBadge = (status) => {
    const statusStyles = {
      pending: 'bg-yellow-100 text-yellow-800',
      active: 'bg-blue-100 text-blue-800',
      accepted: 'bg-green-100 text-green-800',
      responded: 'bg-purple-100 text-purple-800',
      completed: 'bg-green-100 text-green-800',
      not_accepted: 'bg-red-100 text-red-800',
      blacklisted: 'bg-gray-100 text-gray-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  // Get status icon
  const getStatusIcon = (status) => {
    const icons = {
      pending: <Clock className="h-4 w-4" />,
      active: <Users className="h-4 w-4" />,
      accepted: <CheckCircle className="h-4 w-4" />,
      responded: <MessageCircle className="h-4 w-4" />,
      completed: <CheckCircle className="h-4 w-4" />,
      not_accepted: <X className="h-4 w-4" />,
      blacklisted: <X className="h-4 w-4" />
    };
    
    return icons[status] || <Users className="h-4 w-4" />;
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Contacts</h1>
            <p className="text-gray-600">Manage and filter all contacts in your campaigns</p>
          </div>
          <button
            onClick={() => setShowAddContactModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Contact
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search contacts by name, company, or job title..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Filter className="h-4 w-4" />
            <span>Filters</span>
            {showFilters ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>

          {/* Clear Filters */}
          <button
            onClick={clearFilters}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Clear
          </button>
        </div>

        {/* Filter Options */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Statuses</option>
                  <option value="sent">Sent</option>
                  <option value="accepted">Accepted</option>
                  <option value="responded">Responded</option>
                  <option value="accepted,responded">Accepted + Responded</option>
                  <option value="sent,accepted,responded">All Contacted</option>
                  {filterOptions.statuses?.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>

              {/* Owner Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Owner</label>
                <select
                  value={filters.owner_id || filters.assigned_user || ''}
                  onChange={(e) => handleFilterChange('assigned_user', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Owners</option>
                  <option value="scampos@wallarm.com">Sercio Campos (Real User)</option>
                  <option value="john.smith@marketingmasters.com">John Smith</option>
                  <option value="sarah.johnson@marketingmasters.com">Sarah Johnson</option>
                  <option value="michael.davis@marketingmasters.com">Michael Davis</option>
                  {filterOptions.users?.map(user => (
                    <option key={user.id || user.email} value={user.email || user.id}>{user.email || user.name}</option>
                  ))}
                </select>
              </div>

              {/* Campaign Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Campaign</label>
                <select
                  value={filters.campaign_name || filters.campaign || ''}
                  onChange={(e) => handleFilterChange('campaign_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Campaigns</option>
                  <option value="Professional Outreach">Professional Outreach</option>
                  <option value="Q4 Lead Generation">Q4 Lead Generation</option>
                  <option value="Executive Outreach">Executive Outreach</option>
                  {filterOptions.campaigns?.map(campaign => (
                    <option key={campaign.id || campaign.name} value={campaign.name || campaign.id}>
                      {campaign.name} ({campaign.status || 'active'})
                    </option>
                  ))}
                </select>
              </div>

              {/* Company Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
                <select
                  value={filters.company_name || ''}
                  onChange={(e) => handleFilterChange('company_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Companies</option>
                  {filterOptions.companies?.map(company => (
                    <option key={company} value={company}>{company}</option>
                  ))}
                </select>
              </div>

              {/* Industry Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Industry</label>
                <select
                  value={filters.industry || ''}
                  onChange={(e) => handleFilterChange('industry', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Industries</option>
                  {filterOptions.industries?.map(industry => (
                    <option key={industry} value={industry}>{industry}</option>
                  ))}
                </select>
              </div>
            </div>
            
            {/* Advanced Status Filters */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Advanced Status Filters</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Accepted Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Connection Status</label>
                  <select
                    value={filters.has_accepted === true ? 'accepted' : filters.has_accepted === false ? 'not_accepted' : ''}
                    onChange={(e) => {
                      const value = e.target.value === 'accepted' ? true : e.target.value === 'not_accepted' ? false : undefined;
                      handleFilterChange('has_accepted', value);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Connections</option>
                    <option value="accepted">Accepted</option>
                    <option value="not_accepted">Not Accepted</option>
                  </select>
                </div>

                {/* Reply Status Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Reply Status</label>
                  <select
                    value={filters.has_replied === true ? 'replied' : filters.has_replied === false ? 'not_replied' : ''}
                    onChange={(e) => {
                      const value = e.target.value === 'replied' ? true : e.target.value === 'not_replied' ? false : undefined;
                      handleFilterChange('has_replied', value);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Replies</option>
                    <option value="replied">Replied</option>
                    <option value="not_replied">Not Replied</option>
                  </select>
                </div>

                {/* Accepted Only Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quick Filters</label>
                  <select
                    value={filters.accepted_only ? 'accepted_only' : filters.replied_only ? 'replied_only' : ''}
                    onChange={(e) => {
                      if (e.target.value === 'accepted_only') {
                        handleFilterChange('accepted_only', true);
                        handleFilterChange('replied_only', undefined);
                      } else if (e.target.value === 'replied_only') {
                        handleFilterChange('replied_only', true);
                        handleFilterChange('accepted_only', undefined);
                      } else {
                        handleFilterChange('accepted_only', undefined);
                        handleFilterChange('replied_only', undefined);
                      }
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Contacts</option>
                    <option value="accepted_only">Accepted, No Reply</option>
                    <option value="replied_only">Has Replied</option>
                  </select>
                </div>

                {/* Location Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                  <select
                    value={filters.location || ''}
                    onChange={(e) => handleFilterChange('location', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Locations</option>
                    {filterOptions.locations?.map(location => (
                      <option key={location} value={location}>{location}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bulk Actions Bar */}
      {selectedContacts.size > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-blue-900">
                {selectedContacts.size} contact{selectedContacts.size !== 1 ? 's' : ''} selected
              </span>
              <button
                onClick={clearSelection}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Clear selection
              </button>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowEnrollmentModal(true)}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <UserPlus className="h-4 w-4 mr-2" />
                Enroll in Campaign
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Contacts Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {/* Table Header */}
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-700">
                <div className="col-span-1">
                  <button
                    onClick={isAllSelected ? clearSelection : selectAllContacts}
                    className="flex items-center space-x-2 hover:text-gray-900"
                  >
                    {isAllSelected ? (
                      <CheckSquare className="h-4 w-4 text-blue-600" />
                    ) : isPartiallySelected ? (
                      <div className="h-4 w-4 border-2 border-gray-400 rounded bg-blue-100"></div>
                    ) : (
                      <Square className="h-4 w-4 text-gray-400" />
                    )}
                    <span>Select</span>
                  </button>
                </div>
                <div className="col-span-3">
                  <button
                    onClick={() => handleSort('first_name')}
                    className="flex items-center space-x-1 hover:text-gray-900"
                  >
                    <span>Contact</span>
                    {sortBy === 'first_name' && (
                      <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </button>
                </div>
                <div className="col-span-2">
                  <button
                    onClick={() => handleSort('company_name')}
                    className="flex items-center space-x-1 hover:text-gray-900"
                  >
                    <span>Company</span>
                    {sortBy === 'company_name' && (
                      <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </button>
                </div>
                <div className="col-span-2">
                  <button
                    onClick={() => handleSort('job_title')}
                    className="flex items-center space-x-1 hover:text-gray-900"
                  >
                    <span>Job Title</span>
                    {sortBy === 'job_title' && (
                      <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </button>
                </div>
                <div className="col-span-2">Status</div>
                <div className="col-span-2">Owner</div>
                <div className="col-span-1">Actions</div>
              </div>
            </div>

            {/* Table Body */}
            <div className="divide-y divide-gray-200">
              {contacts.map((contact) => (
                <div key={contact.contact_id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="grid grid-cols-12 gap-4 items-center">
                    {/* Selection Checkbox */}
                    <div className="col-span-1">
                      <button
                        onClick={() => toggleContactSelection(contact.contact_id)}
                        className="flex items-center space-x-2 hover:text-gray-900"
                      >
                        {selectedContacts.has(contact.contact_id) ? (
                          <CheckSquare className="h-4 w-4 text-blue-600" />
                        ) : (
                          <Square className="h-4 w-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {/* Contact Info */}
                    <div className="col-span-3">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-sm font-medium text-blue-600">
                              {contact.first_name?.[0]}{contact.last_name?.[0]}
                            </span>
                          </div>
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {contact.full_name}
                          </p>
                          <p className="text-sm text-gray-500 truncate">
                            {contact.email || 'No email'}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Company */}
                    <div className="col-span-2">
                      <p className="text-sm text-gray-900 truncate">
                        {contact.company_name || 'N/A'}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {contact.industry || 'N/A'}
                      </p>
                    </div>

                    {/* Job Title */}
                    <div className="col-span-2">
                      <p className="text-sm text-gray-900 truncate">
                        {contact.job_title || 'N/A'}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {contact.location || 'N/A'}
                      </p>
                    </div>

                    {/* Status */}
                    <div className="col-span-2">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(contact.current_status)}
                        {getStatusBadge(contact.current_status)}
                      </div>
                    </div>

                    {/* Owner */}
                    <div className="col-span-2">
                      <p className="text-sm text-gray-900 truncate">
                        {contact.assigned_user_email || 'Unassigned'}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {contact.current_campaign_name || 'No campaign'}
                      </p>
                    </div>

                    {/* Actions */}
                    <div className="col-span-1">
                      <div className="flex items-center space-x-2">
                        <button
                          className="text-gray-400 hover:text-gray-600"
                          title="View Details"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          className="text-gray-400 hover:text-gray-600"
                          title="Send Message"
                        >
                          <MessageCircle className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Empty State */}
            {contacts.length === 0 && (
              <div className="text-center py-12">
                <Users className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No contacts found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your search or filter criteria.
                </p>
              </div>
            )}
          </>
        )}
      </div>

      {/* Pagination */}
      {contacts.length > 0 && (
        <div className="mt-6 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {pagination.offset + 1} to {Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total} contacts
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPagination(prev => ({ ...prev, offset: Math.max(0, prev.offset - prev.limit) }))}
              disabled={pagination.offset === 0}
              className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setPagination(prev => ({ ...prev, offset: prev.offset + prev.limit }))}
              disabled={pagination.offset + pagination.limit >= pagination.total}
              className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Bulk Enrollment Modal */}
      {showEnrollmentModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Enroll {selectedContacts.size} Contact{selectedContacts.size !== 1 ? 's' : ''} in Campaign
                </h3>
                <button
                  onClick={() => setShowEnrollmentModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                {/* Campaign Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Campaign *
                  </label>
                  <select
                    value={enrollmentData.campaign_id}
                    onChange={(e) => setEnrollmentData(prev => ({ ...prev, campaign_id: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select a campaign</option>
                    {filterOptions.campaigns?.map(campaign => (
                      <option key={campaign.id} value={campaign.id}>
                        {campaign.name} ({campaign.status})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Assigned User */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Assign to User
                  </label>
                  <select
                    value={enrollmentData.assigned_to}
                    onChange={(e) => setEnrollmentData(prev => ({ ...prev, assigned_to: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">No assignment</option>
                    {filterOptions.users?.map(user => (
                      <option key={user.id} value={user.id}>
                        {user.email}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Status */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    value={enrollmentData.status}
                    onChange={(e) => setEnrollmentData(prev => ({ ...prev, status: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="pending">Pending</option>
                    <option value="accepted">Accepted</option>
                    <option value="completed">Completed</option>
                    <option value="blacklisted">Blacklisted</option>
                  </select>
                </div>

                {/* Tags */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={enrollmentData.tags.join(', ')}
                    onChange={(e) => setEnrollmentData(prev => ({ 
                      ...prev, 
                      tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag)
                    }))}
                    placeholder="e.g., high-priority, follow-up"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Modal Actions */}
              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowEnrollmentModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                >
                  Cancel
                </button>
                <button
                  onClick={handleBulkEnrollment}
                  disabled={enrollmentLoading || !enrollmentData.campaign_id}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {enrollmentLoading ? 'Enrolling...' : 'Enroll Contacts'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Contacts;