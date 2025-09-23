import React, { useState, useEffect } from 'react';
import { Plus, Play, Pause, Edit, Trash2, BarChart3, Users, MessageSquare, Calendar, Eye } from 'lucide-react';
import axios from 'axios';
import ContactImport from './ContactImport';
import CampaignContacts from './CampaignContacts';
import UserAssignment from './UserAssignment';

function Campaigns({ currentClient, isAgency }) {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    target_title: '',
    intent: '',
    initial_action: 'inmail',
    initial_message: '',
    initial_subject: '',
    follow_up_actions: [],
    delay_days: 1,
    random_delay: true,
    launch_date: '',
    end_date: '',
    // New follow-up message fields
    follow_up_action_1: 'none',
    follow_up_message_1: '',
    follow_up_subject_1: '',
    follow_up_delay_1: 3,
    follow_up_action_2: 'none',
    follow_up_message_2: '',
    follow_up_subject_2: '',
    follow_up_delay_2: 7,
    follow_up_action_3: 'none',
    follow_up_message_3: '',
    follow_up_subject_3: '',
    follow_up_delay_3: 14
  });
  const [allowCustomNames, setAllowCustomNames] = useState(false); // Admin setting
  const [isAdmin, setIsAdmin] = useState(false); // User role check
  const [formLoading, setFormLoading] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState(null);
  const [showContactsModal, setShowContactsModal] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [showUserAssignmentModal, setShowUserAssignmentModal] = useState(false);
  const [assignmentCampaignId, setAssignmentCampaignId] = useState(null);
  const [showImportContactsModal, setShowImportContactsModal] = useState(false);

  useEffect(() => {
    if (isAgency && currentClient) {
      fetchClientCampaigns();
    } else {
      fetchCampaigns();
    }
    // Check if user is admin (mock for now - in real app, get from auth context)
    setIsAdmin(true); // Mock admin status
  }, [currentClient, isAgency]);

  const fetchClientCampaigns = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Generate client-specific mock campaigns based on the selected client
      const clientCampaigns = generateClientCampaigns(currentClient);
      setCampaigns(clientCampaigns);
    } catch (err) {
      setError('Failed to fetch client campaigns');
      console.error('Client campaigns error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateClientCampaigns = (client) => {
    const baseCampaigns = [
      {
        id: 1,
        name: `${client.name} - Q4 Lead Generation`,
        status: "active",
        target_title: "Sales Manager",
        intent: "Generate qualified B2B sales leads",
        initial_action: "inmail",
        initial_subject: "Quick question about your sales process",
        initial_message: `Hi [Name], I noticed your role as Sales Manager at [Company]. I'd love to discuss how our sales automation tools could help your team increase productivity by 40%. Would you be open to a brief 15-minute call this week?`,
        follow_up_actions: [
          { action: "follow_up_message", delay_days: 3, message: `Hi [Name], following up on my InMail about sales automation. I understand you're busy, but I believe our solution could save your team 10+ hours per week. Worth a quick chat?` },
          { action: "view_profile", delay_days: 7 }
        ],
        delay_days: 2,
        random_delay: true,
        contacts_count: Math.floor(client.stats.contacts * 0.6),
        messages_sent: Math.floor(client.stats.contacts * 0.3),
        acceptance_rate: 23,
        reply_rate: 8,
        created_at: "2024-01-15",
        scheduled_start: "2024-01-20",
        end_date: "2024-02-20"
      },
      {
        id: 2,
        name: `${client.name} - Executive Outreach`,
        status: "paused",
        target_title: "CEO, CTO, VP Engineering",
        intent: "Connect with C-level executives",
        initial_action: "connect",
        initial_subject: "",
        initial_message: "",
        follow_up_actions: [
          { action: "message", delay_days: 1, message: `Hi [Name], thanks for connecting! I'd love to share how we've helped companies like [Company] reduce their operational costs by 30%. Would you be interested in a brief case study?` },
          { action: "follow_up_message", delay_days: 5, message: `Hi [Name], following up on our connection. I have a quick question about your current tech stack - are you using any automation tools for your operations?` }
        ],
        delay_days: 1,
        random_delay: false,
        contacts_count: Math.floor(client.stats.contacts * 0.4),
        messages_sent: Math.floor(client.stats.contacts * 0.2),
        acceptance_rate: 35,
        reply_rate: 12,
        created_at: "2024-01-10",
        scheduled_start: "2024-01-15",
        end_date: "2024-02-15"
      }
    ];

    return baseCampaigns;
  };

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Call the real API endpoint
      const response = await axios.get('http://localhost:8000/api/campaigns');
      
      // Transform the API response to match the expected format
      const transformedCampaigns = response.data.map(campaign => ({
        id: campaign.campaign_id,
        name: campaign.name,
        status: campaign.status,
        target_title: campaign.target_title,
        intent: campaign.intent,
        initial_action: campaign.initial_action,
        initial_subject: campaign.initial_subject,
        initial_message: campaign.initial_message,
        follow_up_actions: campaign.follow_up_actions || [],
        delay_days: campaign.delay_days,
        random_delay: campaign.random_delay,
        contacts_count: campaign.total_contacts || 0,
        messages_sent: 0, // This would come from campaign stats endpoint
        acceptance_rate: campaign.acceptance_rate || 0,
        reply_rate: campaign.reply_rate || 0,
        created_at: campaign.created_at,
        scheduled_start: campaign.scheduled_start,
        end_date: campaign.end_date,
        campaign_key: campaign.campaign_key
      }));
      
      setCampaigns(transformedCampaigns);
    } catch (err) {
      console.error('Campaigns API error, using mock data:', err);
      
      // Fallback to mock data if API fails
      const mockCampaigns = [
        {
          id: 1,
          name: "cony 011524 generate qualified b2b sales leads",
          status: "active",
          target_title: "Sales Manager",
          intent: "Generate qualified B2B sales leads",
          initial_action: "inmail",
          initial_subject: "Partnership Opportunity - Sales Solutions",
          initial_message: "Hi [Name], I noticed your role as Sales Manager at [Company]. I'd love to discuss how our sales automation tools could help your team increase productivity by 40%. Would you be open to a brief 15-minute call this week?",
          follow_up_actions: [
            { action: "follow_up_message", delay_days: 3, message: "Hi [Name], following up on my InMail about sales automation. I understand you're busy, but I believe our solution could save your team 10+ hours per week. Worth a quick chat?" },
            { action: "view_profile", delay_days: 7 }
          ],
          delay_days: 2,
          random_delay: true,
          contacts_count: 45,
          messages_sent: 120,
          acceptance_rate: 23,
          reply_rate: 8,
          created_at: "2024-01-15",
          scheduled_start: "2024-01-20",
          end_date: "2024-02-20"
        }
      ];
      setCampaigns(mockCampaigns);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <Play className="h-4 w-4" />;
      case 'paused': return <Pause className="h-4 w-4" />;
      case 'draft': return <Edit className="h-4 w-4" />;
      case 'completed': return <BarChart3 className="h-4 w-4" />;
      default: return <Edit className="h-4 w-4" />;
    }
  };

  // Generate campaign name based on company domain, date, and intent
  const generateCampaignName = (companyDomain = 'company.com', intent = '') => {
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const year = String(now.getFullYear()).slice(-2);
    const dateStr = `${month}${day}${year}`;
    
    // Extract first 2 and last 2 letters from domain (before .com)
    const domainName = companyDomain.split('.')[0];
    const firstTwo = domainName.substring(0, 2).toLowerCase();
    const lastTwo = domainName.substring(Math.max(0, domainName.length - 2)).toLowerCase();
    
    // Clean up intent - take full intent and make lowercase
    const cleanIntent = intent
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '') // Remove special characters
      .replace(/\s+/g, ' ') // Replace multiple spaces with single space
      .trim();
    
    return `${firstTwo}${lastTwo} ${dateStr} ${cleanIntent}`;
  };



  const handleFormChange = (e) => {
    const newFormData = {
      ...formData,
      [e.target.name]: e.target.value
    };
    
    setFormData(newFormData);
    
    // Auto-update campaign name when intent changes (if custom names are disabled)
    if (e.target.name === 'intent' && !allowCustomNames && !editingCampaign) {
      const generatedName = generateCampaignName('company.com', e.target.value);
      setFormData(prev => ({
        ...prev,
        name: generatedName
      }));
    }
  };

  const addFollowUpAction = () => {
    // Determine the default action based on workflow logic
    let defaultAction = 'follow_up_message';
    
    // If initial action is not connection_request, first follow-up must be connection_request
    if (formData.initial_action !== 'connection_request' && formData.follow_up_actions.length === 0) {
      defaultAction = 'connection_request';
    }
    
    setFormData({
      ...formData,
      follow_up_actions: [...formData.follow_up_actions, { 
        action: defaultAction, 
        delay_days: 1,
        message: '',
        subject: ''
      }]
    });
  };

  const removeFollowUpAction = (index) => {
    setFormData({
      ...formData,
      follow_up_actions: formData.follow_up_actions.filter((_, i) => i !== index)
    });
  };

  const updateFollowUpAction = (index, field, value) => {
    const updatedActions = [...formData.follow_up_actions];
    updatedActions[index] = { ...updatedActions[index], [field]: value };
    setFormData({
      ...formData,
      follow_up_actions: updatedActions
    });
  };

  // Check if connection request has already been used
  const hasConnectionRequestBeenUsed = () => {
    return formData.initial_action === 'connection_request' || 
           formData.follow_up_actions.some(action => action.action === 'connection_request');
  };

  // Get available follow-up actions based on workflow logic
  const getAvailableFollowUpActions = () => {
    const actions = [
      { value: 'follow_up_message', label: 'Follow-up Message' },
      { value: 'view_profile', label: 'View Profile' }
    ];
    
    // Only add connection_request if it hasn't been used yet
    if (!hasConnectionRequestBeenUsed()) {
      actions.unshift({ value: 'connection_request', label: 'Send Connection Request' });
    }
    
    return actions;
  };

  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    setFormLoading(true);

    try {
      // Call the real API to create the campaign
      const campaignData = {
        name: formData.name,
        description: formData.intent, // Using intent as description for now
        target_title: formData.target_title,
        intent: formData.intent,
        dux_user_id: 'default_user', // This should come from auth context
        initial_action: formData.initial_action,
        initial_message: formData.initial_message,
        initial_subject: formData.initial_subject,
        follow_up_actions: formData.follow_up_actions,
        delay_days: formData.delay_days,
        random_delay: formData.random_delay,
        scheduled_start: formData.launch_date ? new Date(formData.launch_date).toISOString() : new Date().toISOString(),
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        // New follow-up action fields
        follow_up_action_1: formData.follow_up_action_1,
        follow_up_message_1: formData.follow_up_message_1,
        follow_up_subject_1: formData.follow_up_subject_1,
        follow_up_delay_1: formData.follow_up_delay_1,
        follow_up_action_2: formData.follow_up_action_2,
        follow_up_message_2: formData.follow_up_message_2,
        follow_up_subject_2: formData.follow_up_subject_2,
        follow_up_delay_2: formData.follow_up_delay_2,
        follow_up_action_3: formData.follow_up_action_3,
        follow_up_message_3: formData.follow_up_message_3,
        follow_up_subject_3: formData.follow_up_subject_3,
        follow_up_delay_3: formData.follow_up_delay_3
      };

      const response = await axios.post('/api/campaigns', campaignData);
      
      // Transform the response to match the expected format
      const newCampaign = {
        id: response.data.campaign_id,
        name: response.data.name,
        status: response.data.status,
        target_title: response.data.target_title,
        intent: response.data.intent,
        initial_action: response.data.initial_action,
        initial_message: response.data.initial_message,
        initial_subject: response.data.initial_subject,
        follow_up_actions: response.data.follow_up_actions || [],
        delay_days: response.data.delay_days,
        random_delay: response.data.random_delay,
        contacts_count: 0,
        messages_sent: 0,
        acceptance_rate: 0,
        reply_rate: 0,
        created_at: response.data.created_at,
        scheduled_start: response.data.scheduled_start,
        end_date: response.data.end_date,
        campaign_key: response.data.campaign_key
      };

      setCampaigns([...campaigns, newCampaign]);
      
      // Reset form and close modal
      setFormData({ 
        name: allowCustomNames ? '' : generateCampaignName('company.com', ''), 
        target_title: '', 
        intent: '',
        initial_action: 'inmail',
        initial_message: '',
        initial_subject: '',
        follow_up_actions: [],
        delay_days: 1,
        random_delay: true,
        launch_date: '',
        end_date: ''
      });
      setShowCreateForm(false);
      
      // Show success message
      alert('Campaign created successfully!');
      
    } catch (err) {
      console.error('Error creating campaign:', err);
      alert('Failed to create campaign. Please try again.');
    } finally {
      setFormLoading(false);
    }
  };

  const closeModal = () => {
    setShowCreateForm(false);
    setEditingCampaign(null);
    setFormData({ 
      name: allowCustomNames ? '' : generateCampaignName('company.com', ''), 
      target_title: '', 
      intent: '',
      initial_action: 'inmail',
      initial_message: '',
      initial_subject: '',
      follow_up_actions: [],
      delay_days: 1,
      random_delay: true
    });
  };

  const handleEditCampaign = (campaign) => {
    setEditingCampaign(campaign);
    setFormData({
      name: campaign.name,
      target_title: campaign.target_title,
      intent: campaign.intent,
      initial_action: campaign.initial_action || 'inmail',
      initial_message: campaign.initial_message || '',
      initial_subject: campaign.initial_subject || '',
      follow_up_actions: campaign.follow_up_actions || [],
      delay_days: campaign.delay_days || 1,
      random_delay: campaign.random_delay !== undefined ? campaign.random_delay : true,
      launch_date: campaign.scheduled_start ? new Date(campaign.scheduled_start).toISOString().split('T')[0] : '',
      end_date: campaign.end_date ? new Date(campaign.end_date).toISOString().split('T')[0] : ''
    });
    setShowCreateForm(true);
  };

  const handleDeleteCampaign = async (campaignId) => {
    if (window.confirm('Are you sure you want to delete this campaign? This action cannot be undone.')) {
      try {
        // Call the real API to delete the campaign
        await axios.delete(`/api/campaigns/${campaignId}`);
        
        // Remove it from local state
        setCampaigns(campaigns.filter(c => c.id !== campaignId));
        alert('Campaign deleted successfully!');
      } catch (err) {
        console.error('Error deleting campaign:', err);
        alert('Failed to delete campaign. Please try again.');
      }
    }
  };

  const handleViewContacts = (campaign) => {
    setSelectedCampaign(campaign);
    setShowContactsModal(true);
  };

  const handleAssignUsers = (campaign) => {
    setAssignmentCampaignId(campaign.id);
    setShowUserAssignmentModal(true);
  };

  const handleUpdateCampaign = async (e) => {
    e.preventDefault();
    setFormLoading(true);

    try {
      // Call the real API to update the campaign
      const campaignData = {
        name: formData.name,
        description: formData.intent, // Using intent as description for now
        target_title: formData.target_title,
        intent: formData.intent,
        initial_action: formData.initial_action,
        initial_message: formData.initial_message,
        initial_subject: formData.initial_subject,
        follow_up_actions: formData.follow_up_actions,
        delay_days: formData.delay_days,
        random_delay: formData.random_delay
      };

      const response = await axios.put(`/api/campaigns/${editingCampaign.id}`, campaignData);
      
      // Update the campaign in the local state
      const updatedCampaigns = campaigns.map(c => 
        c.id === editingCampaign.id 
          ? { 
              ...c, 
              name: response.data.name,
              target_title: response.data.target_title,
              intent: response.data.intent,
              initial_action: response.data.initial_action,
              initial_message: response.data.initial_message,
              initial_subject: response.data.initial_subject,
              follow_up_actions: response.data.follow_up_actions || [],
              delay_days: response.data.delay_days,
              random_delay: response.data.random_delay
            }
          : c
      );
      
      setCampaigns(updatedCampaigns);
      
      // Reset form and close modal
      setFormData({ 
        name: allowCustomNames ? '' : generateCampaignName('company.com', ''), 
        target_title: '', 
        intent: '',
        initial_action: 'inmail',
        initial_message: '',
        initial_subject: '',
        follow_up_actions: [],
        delay_days: 1,
        random_delay: true,
        launch_date: '',
        end_date: ''
      });
      setEditingCampaign(null);
      setShowCreateForm(false);
      
      alert('Campaign updated successfully!');
      
    } catch (err) {
      console.error('Error updating campaign:', err);
      alert('Failed to update campaign. Please try again.');
    } finally {
      setFormLoading(false);
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
          Please select a client from the dropdown above to view their campaigns.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isAgency && currentClient ? `${currentClient.name} Campaigns` : 'Campaigns'}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {isAgency && currentClient 
              ? `Manage ${currentClient.name}'s LinkedIn automation campaigns`
              : 'Manage your LinkedIn automation campaigns'
            }
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => {
              if (campaigns.length === 0) {
                alert('Please create a campaign first before importing contacts.');
                return;
              }
              // Select the first campaign if none is selected
              if (!selectedCampaign && campaigns.length > 0) {
                setSelectedCampaign(campaigns[0]);
              }
              setShowImportContactsModal(true);
            }}
            disabled={campaigns.length === 0}
            className={`inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md ${
              campaigns.length === 0 
                ? 'border-gray-200 text-gray-400 bg-gray-100 cursor-not-allowed'
                : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
            }`}
          >
            <Users className="mr-2 h-4 w-4" />
            Import Contacts
          </button>
          <button
            onClick={() => setShowCreateForm(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="mr-2 h-4 w-4" />
            Create Campaign
          </button>
        </div>
      </div>

      {/* Campaign Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BarChart3 className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Campaigns</dt>
                  <dd className="text-lg font-medium text-gray-900">{campaigns.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Play className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Campaigns</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {campaigns.filter(c => c.status === 'active').length}
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
                <Users className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Contacts</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {campaigns.reduce((sum, c) => sum + c.contacts_count, 0)}
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
                  <dt className="text-sm font-medium text-gray-500 truncate">Messages Sent</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {campaigns.reduce((sum, c) => sum + c.messages_sent, 0)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Campaigns List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {campaigns.map((campaign) => (
            <li key={campaign.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <BarChart3 className="h-6 w-6 text-blue-600" />
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <h3 className="text-lg font-medium text-gray-900">{campaign.name}</h3>
                        <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(campaign.status)}`}>
                          {getStatusIcon(campaign.status)}
                          <span className="ml-1 capitalize">{campaign.status}</span>
                        </span>
                      </div>
                      <div className="mt-1 flex items-center text-sm text-gray-500">
                        <span>Target: {campaign.target_title}</span>
                        <span className="mx-2">•</span>
                        <span>{campaign.intent}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Contacts</div>
                      <div className="text-lg font-medium text-gray-900">{campaign.contacts_count}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Acceptance</div>
                      <div className="text-lg font-medium text-gray-900">{campaign.acceptance_rate}%</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Reply Rate</div>
                      <div className="text-lg font-medium text-gray-900">{campaign.reply_rate}%</div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-4 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <div className="flex items-center text-sm text-gray-500">
                      <Calendar className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                      <p>
                        Created {campaign.created_at} • 
                        {campaign.status === 'active' ? ` Started ${campaign.scheduled_start}` : ` Scheduled ${campaign.scheduled_start}`}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center text-sm sm:mt-0">
                    <ContactImport 
                      campaignId={campaign.id} 
                      onImportComplete={() => {
                        // Refresh campaigns or show success message
                        console.log('Contacts imported successfully');
                      }}
                    />
                    <button 
                      onClick={() => handleViewContacts(campaign)}
                      className="text-green-600 hover:text-green-500 mr-4 ml-2"
                      title="View contacts"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button 
                      onClick={() => handleAssignUsers(campaign)}
                      className="text-purple-600 hover:text-purple-500 mr-4"
                      title="Assign users to contacts"
                    >
                      <Users className="h-4 w-4" />
                    </button>
                    <button 
                      onClick={() => handleEditCampaign(campaign)}
                      className="text-blue-600 hover:text-blue-500 mr-4"
                      title="Edit campaign"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button 
                      onClick={() => handleDeleteCampaign(campaign.id)}
                      className="text-red-600 hover:text-red-500"
                      title="Delete campaign"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Create Campaign Form (Modal) */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {editingCampaign ? 'Edit Campaign' : 'Create New Campaign'}
                </h3>
                <button
                  type="button"
                  onClick={() => document.getElementById('follow-up-actions')?.scrollIntoView({ behavior: 'smooth' })}
                  className="text-sm text-blue-600 hover:text-blue-500 bg-blue-50 px-3 py-1 rounded border border-blue-200"
                >
                  Jump to Follow-up Actions ↓
                </button>
              </div>
              <form onSubmit={editingCampaign ? handleUpdateCampaign : handleCreateCampaign} className="space-y-4">
                {/* Admin Controls */}
                {isAdmin && (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium text-yellow-800">Admin Settings</h4>
                        <p className="text-xs text-yellow-700">Control campaign naming for all users</p>
                      </div>
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="allowCustomNames"
                          checked={allowCustomNames}
                          onChange={(e) => setAllowCustomNames(e.target.checked)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label htmlFor="allowCustomNames" className="ml-2 text-sm text-yellow-800">
                          Allow Custom Names
                        </label>
                      </div>
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Campaign Name
                    {!allowCustomNames && (
                      <span className="text-xs text-gray-500 ml-2">(Auto-generated)</span>
                    )}
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleFormChange}
                    required
                    disabled={!allowCustomNames && !editingCampaign}
                    className={`mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                      !allowCustomNames && !editingCampaign ? 'bg-gray-100 text-gray-500' : ''
                    }`}
                    placeholder={allowCustomNames ? "Enter campaign name" : "Auto-generated based on company and date"}
                  />
                  {!allowCustomNames && !editingCampaign && (
                    <p className="mt-1 text-xs text-gray-500">
                      Format: [First 2 letters][Last 2 letters] [MMDDYY] [full intent] (e.g., "cony 090225 invite to dinner in new york")
                    </p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Target Title</label>
                  <input
                    type="text"
                    name="target_title"
                    value={formData.target_title}
                    onChange={handleFormChange}
                    required
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., Sales Manager"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Intent</label>
                  <textarea
                    name="intent"
                    value={formData.intent}
                    onChange={handleFormChange}
                    required
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    rows="2"
                    placeholder="Describe your campaign goal"
                  />
                </div>

                {/* Campaign Dates */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Launch Date</label>
                    <input
                      type="date"
                      name="launch_date"
                      value={formData.launch_date}
                      onChange={handleFormChange}
                      required
                      min={new Date().toISOString().split('T')[0]}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="mt-1 text-xs text-gray-500">When the campaign should start</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">End Date</label>
                    <input
                      type="date"
                      name="end_date"
                      value={formData.end_date}
                      onChange={handleFormChange}
                      required
                      min={formData.launch_date || new Date().toISOString().split('T')[0]}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="mt-1 text-xs text-gray-500">No messages will be sent after this date</p>
                  </div>
                </div>

                {/* Initial Action */}
                <div>
                  <label className="block text-sm font-medium text-gray-700">Initial Action</label>
                  <select
                    name="initial_action"
                    value={formData.initial_action}
                    onChange={handleFormChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="inmail">Send InMail</option>
                    <option value="connection_request">Send Connection Request</option>
                    <option value="message">Send Follow-up Message</option>
                    <option value="email">Send Email</option>
                    <option value="view_profile">View Profile</option>
                  </select>
                </div>

                {/* Initial Message Content - Show for messaging actions */}
                {(formData.initial_action === 'inmail' || formData.initial_action === 'email' || formData.initial_action === 'connection_request' || formData.initial_action === 'message') && (
                  <>
                    {/* Subject Line - Required for InMail and Email */}
                    {(formData.initial_action === 'inmail' || formData.initial_action === 'email') && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Subject Line {formData.initial_action === 'inmail' ? '(Required for InMail)' : '(Required for Email)'}
                        </label>
                        <input
                          type="text"
                          name="initial_subject"
                          value={formData.initial_subject}
                          onChange={handleFormChange}
                          required
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder={formData.initial_action === 'inmail' ? 'Enter InMail subject line' : 'Enter email subject line'}
                        />
                      </div>
                    )}

                    {/* Message Content */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        {formData.initial_action === 'inmail' ? 'InMail Message' : 
                         formData.initial_action === 'email' ? 'Email Content' : 
                         formData.initial_action === 'message' ? 'Follow-up Message' :
                         'Connection Request Message'}
                      </label>
                      <textarea
                        name="initial_message"
                        value={formData.initial_message}
                        onChange={handleFormChange}
                        required
                        rows="4"
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder={
                          formData.initial_action === 'inmail' ? 'Enter your InMail message content...' :
                          formData.initial_action === 'email' ? 'Enter your email content...' :
                          formData.initial_action === 'message' ? 'Enter your follow-up message...' :
                          'Enter your connection request message...'
                        }
                      />
                      <p className="mt-1 text-xs text-gray-500">
                        {formData.initial_action === 'inmail' ? 'InMail messages have a 200 character limit' :
                         formData.initial_action === 'email' ? 'Keep email content professional and concise' :
                         formData.initial_action === 'message' ? 'Follow-up messages should be personalized and engaging' :
                         'Connection request messages are limited to 300 characters'}
                      </p>
                    </div>
                  </>
                )}

                {/* Follow-up Actions Configuration - Always visible */}
                <div id="follow-up-actions" className="border-t border-gray-200 pt-6 mt-6">
                  <div className="flex justify-between items-center mb-4">
                    <label className="block text-lg font-semibold text-gray-900">
                      🔄 Follow-up Actions Configuration
                    </label>
                    <div className="text-xs text-gray-500 bg-yellow-100 px-2 py-1 rounded">
                      Scroll down to see all options
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    {/* Follow-up Action 1 */}
                    {formData.follow_up_action_1 !== 'none' && (
                    <div className="border-2 border-blue-300 rounded-lg p-4 bg-blue-50 shadow-md hover:shadow-lg transition-shadow">
                      <div className="flex justify-between items-center mb-3">
                        <h4 className="text-sm font-medium text-gray-700">Follow-up Action 1 (Optional)</h4>
                        <div className="flex items-center space-x-2">
                          <button
                            type="button"
                            onClick={() => setFormData({
                              ...formData,
                              follow_up_action_1: 'none',
                              follow_up_message_1: '',
                              follow_up_subject_1: '',
                              follow_up_delay_1: 3
                            })}
                            className="text-red-600 hover:text-red-500 text-xs px-2 py-1 border border-red-300 rounded hover:bg-red-50"
                          >
                            Delete Step
                          </button>
                          <label className="text-xs text-gray-500">Delay:</label>
                          <input
                            type="number"
                            min="1"
                            max="30"
                            value={formData.follow_up_delay_1 || 3}
                            onChange={(e) => setFormData({...formData, follow_up_delay_1: parseInt(e.target.value) || 3})}
                            className="w-16 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                          <span className="text-xs text-gray-500">days</span>
                        </div>
                      </div>
                      
                      {/* Action Type Selector */}
                      <div className="mb-3">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Action Type:</label>
                        <select
                          name="follow_up_action_1"
                          value={formData.follow_up_action_1 || 'none'}
                          onChange={handleFormChange}
                          className="w-full border-2 border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white"
                        >
                          <option value="none">-- Select Action Type --</option>
                          <option value="message">Send Follow-up Message</option>
                          <option value="connection_request">Send Connection Request</option>
                          <option value="inmail">Send InMail</option>
                          <option value="profile_view">View Profile</option>
                        </select>
                        <p className="mt-1 text-xs text-gray-500">
                          Current selection: {formData.follow_up_action_1 || 'none'}
                        </p>
                      </div>

                      {/* Message Content - Show only for message and inmail */}
                      {(formData.follow_up_action_1 === 'message' || formData.follow_up_action_1 === 'inmail') && formData.follow_up_action_1 !== 'none' && (
                        <>
                          {/* Subject Line for InMail */}
                          {formData.follow_up_action_1 === 'inmail' && (
                            <div className="mb-3">
                              <label className="block text-xs font-medium text-gray-600 mb-1">InMail Subject:</label>
                              <input
                                type="text"
                                name="follow_up_subject_1"
                                value={formData.follow_up_subject_1 || ''}
                                onChange={handleFormChange}
                                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                placeholder="Enter InMail subject line"
                              />
                            </div>
                          )}
                          
                          <textarea
                            name="follow_up_message_1"
                            value={formData.follow_up_message_1 || ''}
                            onChange={handleFormChange}
                            rows="3"
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            placeholder={
                              formData.follow_up_action_1 === 'inmail' ? 'Enter your InMail message...' :
                              'Enter your follow-up message...'
                            }
                          />
                        </>
                      )}
                      
                      <p className="mt-1 text-xs text-gray-500">
                        {formData.follow_up_action_1 === 'message' && 'This message will be sent after the initial action is completed'}
                        {formData.follow_up_action_1 === 'connection_request' && 'Connection request will be sent (only if not already connected)'}
                        {formData.follow_up_action_1 === 'inmail' && 'InMail will be sent to the contact'}
                        {formData.follow_up_action_1 === 'profile_view' && 'Profile will be viewed to show interest'}
                      </p>
                    </div>
                    )}

                    {/* Follow-up Action 2 */}
                    {formData.follow_up_action_2 !== 'none' && (
                    <div className="border-2 border-green-300 rounded-lg p-4 bg-green-50 shadow-md hover:shadow-lg transition-shadow">
                      <div className="flex justify-between items-center mb-3">
                        <h4 className="text-sm font-medium text-gray-700">Follow-up Action 2 (Optional)</h4>
                        <div className="flex items-center space-x-2">
                          <button
                            type="button"
                            onClick={() => setFormData({
                              ...formData,
                              follow_up_action_2: 'none',
                              follow_up_message_2: '',
                              follow_up_subject_2: '',
                              follow_up_delay_2: 7
                            })}
                            className="text-red-600 hover:text-red-500 text-xs px-2 py-1 border border-red-300 rounded hover:bg-red-50"
                          >
                            Delete Step
                          </button>
                          <label className="text-xs text-gray-500">Delay:</label>
                          <input
                            type="number"
                            min="1"
                            max="30"
                            value={formData.follow_up_delay_2 || 7}
                            onChange={(e) => setFormData({...formData, follow_up_delay_2: parseInt(e.target.value) || 7})}
                            className="w-16 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                          <span className="text-xs text-gray-500">days</span>
                        </div>
                      </div>
                      
                      {/* Action Type Selector */}
                      <div className="mb-3">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Action Type:</label>
                        <select
                          name="follow_up_action_2"
                          value={formData.follow_up_action_2 || 'none'}
                          onChange={handleFormChange}
                          className="w-full border-2 border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white"
                        >
                          <option value="none">-- Select Action Type --</option>
                          <option value="message">Send Follow-up Message</option>
                          <option value="connection_request">Send Connection Request</option>
                          <option value="inmail">Send InMail</option>
                          <option value="profile_view">View Profile</option>
                        </select>
                        <p className="mt-1 text-xs text-gray-500">
                          Current selection: {formData.follow_up_action_2 || 'none'}
                        </p>
                      </div>

                      {/* Message Content - Show only for message and inmail */}
                      {(formData.follow_up_action_2 === 'message' || formData.follow_up_action_2 === 'inmail') && formData.follow_up_action_2 !== 'none' && (
                        <>
                          {/* Subject Line for InMail */}
                          {formData.follow_up_action_2 === 'inmail' && (
                            <div className="mb-3">
                              <label className="block text-xs font-medium text-gray-600 mb-1">InMail Subject:</label>
                              <input
                                type="text"
                                name="follow_up_subject_2"
                                value={formData.follow_up_subject_2 || ''}
                                onChange={handleFormChange}
                                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                placeholder="Enter InMail subject line"
                              />
                            </div>
                          )}
                          
                          <textarea
                            name="follow_up_message_2"
                            value={formData.follow_up_message_2 || ''}
                            onChange={handleFormChange}
                            rows="3"
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            placeholder={
                              formData.follow_up_action_2 === 'inmail' ? 'Enter your InMail message...' :
                              'Enter your follow-up message...'
                            }
                          />
                        </>
                      )}
                      
                      <p className="mt-1 text-xs text-gray-500">
                        {formData.follow_up_action_2 === 'message' && 'This message will be sent if there\'s no response to the first follow-up'}
                        {formData.follow_up_action_2 === 'connection_request' && 'Connection request will be sent (only if not already connected)'}
                        {formData.follow_up_action_2 === 'inmail' && 'InMail will be sent to the contact'}
                        {formData.follow_up_action_2 === 'profile_view' && 'Profile will be viewed to show interest'}
                      </p>
                    </div>
                    )}

                    {/* Follow-up Action 3 */}
                    {formData.follow_up_action_3 !== 'none' && (
                    <div className="border-2 border-purple-300 rounded-lg p-4 bg-purple-50 shadow-md hover:shadow-lg transition-shadow">
                      <div className="flex justify-between items-center mb-3">
                        <h4 className="text-sm font-medium text-gray-700">Follow-up Action 3 (Optional)</h4>
                        <div className="flex items-center space-x-2">
                          <button
                            type="button"
                            onClick={() => setFormData({
                              ...formData,
                              follow_up_action_3: 'none',
                              follow_up_message_3: '',
                              follow_up_subject_3: '',
                              follow_up_delay_3: 14
                            })}
                            className="text-red-600 hover:text-red-500 text-xs px-2 py-1 border border-red-300 rounded hover:bg-red-50"
                          >
                            Delete Step
                          </button>
                          <label className="text-xs text-gray-500">Delay:</label>
                          <input
                            type="number"
                            min="1"
                            max="30"
                            value={formData.follow_up_delay_3 || 14}
                            onChange={(e) => setFormData({...formData, follow_up_delay_3: parseInt(e.target.value) || 14})}
                            className="w-16 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                          <span className="text-xs text-gray-500">days</span>
                        </div>
                      </div>
                      
                      {/* Action Type Selector */}
                      <div className="mb-3">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Action Type:</label>
                        <select
                          name="follow_up_action_3"
                          value={formData.follow_up_action_3 || 'none'}
                          onChange={handleFormChange}
                          className="w-full border-2 border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white"
                        >
                          <option value="none">-- Select Action Type --</option>
                          <option value="message">Send Follow-up Message</option>
                          <option value="connection_request">Send Connection Request</option>
                          <option value="inmail">Send InMail</option>
                          <option value="profile_view">View Profile</option>
                        </select>
                        <p className="mt-1 text-xs text-gray-500">
                          Current selection: {formData.follow_up_action_3 || 'none'}
                        </p>
                      </div>

                      {/* Message Content - Show only for message and inmail */}
                      {(formData.follow_up_action_3 === 'message' || formData.follow_up_action_3 === 'inmail') && formData.follow_up_action_3 !== 'none' && (
                        <>
                          {/* Subject Line for InMail */}
                          {formData.follow_up_action_3 === 'inmail' && (
                            <div className="mb-3">
                              <label className="block text-xs font-medium text-gray-600 mb-1">InMail Subject:</label>
                              <input
                                type="text"
                                name="follow_up_subject_3"
                                value={formData.follow_up_subject_3 || ''}
                                onChange={handleFormChange}
                                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                placeholder="Enter InMail subject line"
                              />
                            </div>
                          )}
                          
                          <textarea
                            name="follow_up_message_3"
                            value={formData.follow_up_message_3 || ''}
                            onChange={handleFormChange}
                            rows="3"
                            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            placeholder={
                              formData.follow_up_action_3 === 'inmail' ? 'Enter your InMail message...' :
                              'Enter your follow-up message...'
                            }
                          />
                        </>
                      )}
                      
                      <p className="mt-1 text-xs text-gray-500">
                        {formData.follow_up_action_3 === 'message' && 'Final follow-up message for non-responsive contacts'}
                        {formData.follow_up_action_3 === 'connection_request' && 'Connection request will be sent (only if not already connected)'}
                        {formData.follow_up_action_3 === 'inmail' && 'InMail will be sent to the contact'}
                        {formData.follow_up_action_3 === 'profile_view' && 'Profile will be viewed to show interest'}
                      </p>
                    </div>
                  )}

                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                    <p className="text-xs text-blue-700">
                      <strong>💡 Pro Tip:</strong> Use personalized placeholders like {"{first_name}"}, {"{company}"}, {"{title}"} 
                      in your messages. These will be automatically replaced with contact information.
                    </p>
                  </div>

                  {/* Add Follow-up Action Buttons */}
                  <div className="flex flex-wrap gap-2 mt-4">
                    {formData.follow_up_action_1 === 'none' && (
                      <button
                        type="button"
                        onClick={() => setFormData({
                          ...formData,
                          follow_up_action_1: 'message'
                        })}
                        className="px-3 py-2 text-sm bg-blue-100 text-blue-700 border border-blue-300 rounded-md hover:bg-blue-200 transition-colors"
                      >
                        + Add Follow-up Action 1
                      </button>
                    )}
                    {formData.follow_up_action_2 === 'none' && formData.follow_up_action_1 !== 'none' && (
                      <button
                        type="button"
                        onClick={() => setFormData({
                          ...formData,
                          follow_up_action_2: 'message'
                        })}
                        className="px-3 py-2 text-sm bg-green-100 text-green-700 border border-green-300 rounded-md hover:bg-green-200 transition-colors"
                      >
                        + Add Follow-up Action 2
                      </button>
                    )}
                    {formData.follow_up_action_3 === 'none' && formData.follow_up_action_2 !== 'none' && (
                      <button
                        type="button"
                        onClick={() => setFormData({
                          ...formData,
                          follow_up_action_3: 'message'
                        })}
                        className="px-3 py-2 text-sm bg-purple-100 text-purple-700 border border-purple-300 rounded-md hover:bg-purple-200 transition-colors"
                      >
                        + Add Follow-up Action 3
                      </button>
                    )}
                  </div>

                  {/* Follow-up Actions Summary */}
                  <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-md">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">📋 Follow-up Actions Summary:</h5>
                    <div className="text-xs text-gray-600 space-y-1">
                      {formData.follow_up_action_1 && formData.follow_up_action_1 !== 'none' && (
                        <div>• Action 1: {formData.follow_up_action_1.replace('_', ' ')} (after {formData.follow_up_delay_1 || 3} days)</div>
                      )}
                      {formData.follow_up_action_2 && formData.follow_up_action_2 !== 'none' && (
                        <div>• Action 2: {formData.follow_up_action_2.replace('_', ' ')} (after {formData.follow_up_delay_2 || 7} days)</div>
                      )}
                      {formData.follow_up_action_3 && formData.follow_up_action_3 !== 'none' && (
                        <div>• Action 3: {formData.follow_up_action_3.replace('_', ' ')} (after {formData.follow_up_delay_3 || 14} days)</div>
                      )}
                      {(!formData.follow_up_action_1 || formData.follow_up_action_1 === 'none') && 
                       (!formData.follow_up_action_2 || formData.follow_up_action_2 === 'none') && 
                       (!formData.follow_up_action_3 || formData.follow_up_action_3 === 'none') && (
                        <div className="text-gray-500 italic">No follow-up actions configured</div>
                      )}
                    </div>
                  </div>

                  {/* Debug Information */}
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">🔍 Debug Info:</h5>
                    <div className="text-xs text-gray-600 space-y-1">
                      <div>follow_up_action_1: "{formData.follow_up_action_1}"</div>
                      <div>follow_up_action_2: "{formData.follow_up_action_2}"</div>
                      <div>follow_up_action_3: "{formData.follow_up_action_3}"</div>
                      <div>Form data keys: {Object.keys(formData).filter(k => k.includes('follow_up')).join(', ')}</div>
                    </div>
                  </div>
                </div>

                {/* Advanced Follow-up Actions */}
                <div>
                  <div className="flex justify-between items-center">
                    <label className="block text-sm font-medium text-gray-700">Advanced Follow-up Actions</label>
                    <button
                      type="button"
                      onClick={addFollowUpAction}
                      className="text-sm text-blue-600 hover:text-blue-500"
                    >
                      + Add Custom Action
                    </button>
                  </div>
                  
                  {/* Workflow Logic Explanation */}
                  {formData.initial_action !== 'connection_request' && formData.follow_up_actions.length === 0 && (
                    <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-md">
                      <p className="text-xs text-blue-700">
                        <strong>Note:</strong> Since your initial action is not a connection request, 
                        your first follow-up will automatically be set to "Send Connection Request" 
                        (you can only send one connection request per contact).
                      </p>
                    </div>
                  )}
                  
                  {hasConnectionRequestBeenUsed() && (
                    <div className="mt-2 p-2 bg-gray-50 border border-gray-200 rounded-md">
                      <p className="text-xs text-gray-600">
                        <strong>Note:</strong> Connection request has already been used in this campaign. 
                        Only follow-up messages and profile views are available for additional steps.
                      </p>
                    </div>
                  )}
                  
                  {formData.follow_up_actions.map((action, index) => (
                    <div key={index} className="mt-2 p-3 border border-gray-200 rounded-md bg-gray-50">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-gray-700">Follow-up #{index + 1}</span>
                        <button
                          type="button"
                          onClick={() => removeFollowUpAction(index)}
                          className="text-red-600 hover:text-red-500 text-sm"
                        >
                          Remove
                        </button>
                      </div>
                      <div className="grid grid-cols-2 gap-2 mb-2">
                        <select
                          value={action.action}
                          onChange={(e) => updateFollowUpAction(index, 'action', e.target.value)}
                          className="border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          {getAvailableFollowUpActions().map(option => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                        <div className="flex items-center space-x-2">
                          <input
                            type="number"
                            min="1"
                            max="99"
                            value={action.delay_days}
                            onChange={(e) => updateFollowUpAction(index, 'delay_days', parseInt(e.target.value))}
                            className="border border-gray-300 rounded-md px-2 py-1 text-sm w-16 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                          <span className="text-xs text-gray-500">days</span>
                        </div>
                      </div>
                      
                      {/* Message content for messaging actions */}
                      {(action.action === 'follow_up_message' || action.action === 'connection_request') && (
                        <div className="space-y-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-600">
                              {action.action === 'connection_request' ? 'Connection Request Message' : 'Follow-up Message'}
                            </label>
                            <textarea
                              value={action.message || ''}
                              onChange={(e) => updateFollowUpAction(index, 'message', e.target.value)}
                              rows="2"
                              className="mt-1 block w-full border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                              placeholder={
                                action.action === 'connection_request' 
                                  ? 'Enter your connection request message...' 
                                  : 'Enter your follow-up message...'
                              }
                            />
                            <p className="mt-1 text-xs text-gray-500">
                              {action.action === 'connection_request' 
                                ? 'Connection request messages are limited to 300 characters'
                                : 'Keep your follow-up message professional and concise'
                              }
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                </div>

                {/* Delay Settings */}
                <div>
                  <label className="block text-sm font-medium text-gray-700">Delay Between Actions</label>
                  <div className="mt-1 flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <input
                        type="number"
                        name="delay_days"
                        min="1"
                        max="99"
                        value={formData.delay_days}
                        onChange={handleFormChange}
                        className="border border-gray-300 rounded-md px-3 py-2 w-20 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                      <span className="text-sm text-gray-500">days</span>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        name="random_delay"
                        checked={formData.random_delay}
                        onChange={(e) => setFormData({...formData, random_delay: e.target.checked})}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label className="ml-2 text-sm text-gray-700">Add random time variation</label>
                    </div>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    Random variation helps avoid detection by LinkedIn's automation detection
                  </p>
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={closeModal}
                    disabled={formLoading}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={formLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {formLoading ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        {editingCampaign ? 'Updating...' : 'Creating...'}
                      </div>
                    ) : (
                      editingCampaign ? 'Update Campaign' : 'Create Campaign'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Campaign Contacts Modal */}
      {showContactsModal && selectedCampaign && (
        <CampaignContacts
          campaignId={selectedCampaign.id}
          campaignName={selectedCampaign.name}
          onClose={() => {
            setShowContactsModal(false);
            setSelectedCampaign(null);
          }}
        />
      )}

      {/* User Assignment Modal */}
      {showUserAssignmentModal && assignmentCampaignId && (
        <UserAssignment
          campaignId={assignmentCampaignId}
          onClose={() => {
            setShowUserAssignmentModal(false);
            setAssignmentCampaignId(null);
            // Don't refresh campaigns - UserAssignment is isolated
          }}
        />
      )}

      {/* Import Contacts Modal */}
      {showImportContactsModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">Import Contacts</h3>
                  {selectedCampaign && (
                    <p className="text-sm text-gray-500 mt-1">
                      Adding contacts to: <span className="font-medium">{selectedCampaign.name}</span>
                    </p>
                  )}
                </div>
                <button
                  onClick={() => setShowImportContactsModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <ContactImport 
                campaignId={selectedCampaign?.id || "new-campaign"}
                onImportComplete={() => {
                  setShowImportContactsModal(false);
                  // Optionally refresh campaigns or show success message
                  console.log('Contacts imported successfully');
                }}
                onClose={() => setShowImportContactsModal(false)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Campaigns;