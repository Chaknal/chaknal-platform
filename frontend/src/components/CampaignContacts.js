import React, { useState, useEffect, useCallback } from 'react';
import { Users, Plus, Search, Mail, Linkedin, MapPin, Tag, Trash2, UserPlus } from 'lucide-react';
import axios from 'axios';
import ContactImport from './ContactImport';

function CampaignContacts({ campaignId, campaignName, onClose }) {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showImportModal, setShowImportModal] = useState(false);
  const [selectedContacts, setSelectedContacts] = useState([]);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [teamMembers, setTeamMembers] = useState([]);

  const fetchCampaignContacts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/campaigns/${campaignId}/contacts`);
      setContacts(response.data.contacts || []);
    } catch (err) {
      setError('Failed to fetch campaign contacts');
      console.error('Campaign contacts error:', err);
      // Fallback to mock data for demo
      setContacts([
        {
          id: 1,
          contact_id: 'contact_1',
          full_name: "James Wilson",
          email: "james.wilson@salesforce.com",
          company_name: "SalesForce Inc.",
          job_title: "Senior Sales Manager",
          location: "San Francisco, CA",
          status: "pending",
          assigned_to: null,
          data_source: "duxsoup",
          last_contact: "2024-01-15",
          linkedin_url: "https://linkedin.com/in/jameswilson"
        },
        {
          id: 2,
          contact_id: 'contact_2',
          full_name: "Maria Garcia",
          email: "maria.garcia@oracle.com",
          company_name: "Oracle Corp.",
          job_title: "Sales Director",
          location: "Austin, TX",
          status: "active",
          assigned_to: "john.doe@company.com",
          data_source: "zoominfo",
          last_contact: "2024-01-12",
          linkedin_url: "https://linkedin.com/in/mariagarcia"
        }
      ]);
    } finally {
      setLoading(false);
    }
  }, [campaignId]);

  useEffect(() => {
    if (campaignId) {
      fetchCampaignContacts();
      fetchTeamMembers();
    }
  }, [campaignId, fetchCampaignContacts]);

  const fetchTeamMembers = async () => {
    try {
      // Mock team members for now
      setTeamMembers([
        { id: 1, name: "John Doe", email: "john.doe@company.com", role: "Sales Rep" },
        { id: 2, name: "Jane Smith", email: "jane.smith@company.com", role: "Sales Manager" },
        { id: 3, name: "Mike Johnson", email: "mike.johnson@company.com", role: "Sales Rep" }
      ]);
    } catch (err) {
      console.error('Failed to fetch team members:', err);
    }
  };

  const handleImportComplete = (result) => {
    setShowImportModal(false);
    fetchCampaignContacts(); // Refresh the contact list
  };

  const handleContactSelect = (contactId) => {
    setSelectedContacts(prev => 
      prev.includes(contactId) 
        ? prev.filter(id => id !== contactId)
        : [...prev, contactId]
    );
  };

  const handleSelectAll = () => {
    if (selectedContacts.length === filteredContacts.length) {
      setSelectedContacts([]);
    } else {
      setSelectedContacts(filteredContacts.map(c => c.contact_id));
    }
  };

  const handleAssignContacts = async (assigneeEmail) => {
    try {
      await axios.post(`/api/campaigns/${campaignId}/contacts/assign`, {
        contact_ids: selectedContacts,
        assignee_email: assigneeEmail
      });
      
      setShowAssignModal(false);
      setSelectedContacts([]);
      fetchCampaignContacts(); // Refresh the list
    } catch (err) {
      setError('Failed to assign contacts');
    }
  };

  const handleRemoveContact = async (contactId) => {
    if (window.confirm('Are you sure you want to remove this contact from the campaign?')) {
      try {
        await axios.delete(`/api/campaigns/${campaignId}/contacts/${contactId}`);
        fetchCampaignContacts(); // Refresh the list
      } catch (err) {
        setError('Failed to remove contact');
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'paused': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return 'Active';
      case 'pending': return 'Pending';
      case 'completed': return 'Completed';
      case 'paused': return 'Paused';
      default: return 'Unknown';
    }
  };

  const filteredContacts = contacts.filter(contact => {
    const matchesSearch = contact.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         contact.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         contact.company_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || contact.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading contacts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Campaign Contacts: {campaignName}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {contacts.length} contacts • {filteredContacts.length} shown
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowImportModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Plus className="h-4 w-4 mr-2" />
                Import Contacts
              </button>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search contacts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 w-full"
                />
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="paused">Paused</option>
              </select>
              
              {selectedContacts.length > 0 && (
                <button
                  onClick={() => setShowAssignModal(true)}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  <UserPlus className="h-4 w-4 mr-2" />
                  Assign ({selectedContacts.length})
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Contact List */}
        <div className="flex-1 overflow-y-auto">
          {error && (
            <div className="px-6 py-4 bg-red-50 border-b border-red-200">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {filteredContacts.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No contacts found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm || filterStatus !== 'all' 
                  ? 'Try adjusting your search or filter criteria.'
                  : 'Get started by importing contacts to this campaign.'
                }
              </p>
              {!searchTerm && filterStatus === 'all' && (
                <div className="mt-6">
                  <button
                    onClick={() => setShowImportModal(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Import Contacts
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="px-6 py-4">
              <div className="flex items-center mb-4">
                <input
                  type="checkbox"
                  checked={selectedContacts.length === filteredContacts.length && filteredContacts.length > 0}
                  onChange={handleSelectAll}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-600">
                  Select all ({filteredContacts.length})
                </span>
              </div>

              <div className="space-y-3">
                {filteredContacts.map((contact) => (
                  <div
                    key={contact.contact_id}
                    className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <input
                      type="checkbox"
                      checked={selectedContacts.includes(contact.contact_id)}
                      onChange={() => handleContactSelect(contact.contact_id)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mr-4"
                    />
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="flex-shrink-0">
                            <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-sm font-medium text-blue-600">
                                {contact.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || '??'}
                              </span>
                            </div>
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {contact.full_name || 'Unknown Name'}
                            </p>
                            <p className="text-sm text-gray-500 truncate">
                              {contact.job_title} at {contact.company_name}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center space-x-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(contact.status)}`}>
                              {getStatusIcon(contact.status)} {contact.status}
                            </span>
                            {contact.assigned_to && (
                              <span className="text-xs text-gray-500">
                                Assigned to {contact.assigned_to}
                              </span>
                            )}
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            {contact.email && (
                              <a
                                href={`mailto:${contact.email}`}
                                className="text-gray-400 hover:text-blue-600"
                                title="Send email"
                              >
                                <Mail className="h-4 w-4" />
                              </a>
                            )}
                            {contact.linkedin_url && (
                              <a
                                href={contact.linkedin_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-gray-400 hover:text-blue-600"
                                title="View LinkedIn"
                              >
                                <Linkedin className="h-4 w-4" />
                              </a>
                            )}
                            <button
                              onClick={() => handleRemoveContact(contact.contact_id)}
                              className="text-gray-400 hover:text-red-600"
                              title="Remove from campaign"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                      
                      <div className="mt-2 flex items-center text-xs text-gray-500 space-x-4">
                        {contact.location && (
                          <div className="flex items-center">
                            <MapPin className="h-3 w-3 mr-1" />
                            {contact.location}
                          </div>
                        )}
                        {contact.data_source && (
                          <div className="flex items-center">
                            <Tag className="h-3 w-3 mr-1" />
                            {contact.data_source}
                          </div>
                        )}
                        {contact.last_contact && (
                          <div>
                            Last contact: {contact.last_contact}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Import Modal */}
        {showImportModal && (
          <ContactImport
            campaignId={campaignId}
            onImportComplete={handleImportComplete}
            onClose={() => setShowImportModal(false)}
          />
        )}

        {/* Assign Modal */}
        {showAssignModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Assign {selectedContacts.length} contacts
              </h3>
              <div className="space-y-3">
                {teamMembers.map((member) => (
                  <button
                    key={member.id}
                    onClick={() => handleAssignContacts(member.email)}
                    className="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <div className="font-medium text-gray-900">{member.name}</div>
                    <div className="text-sm text-gray-500">{member.email} • {member.role}</div>
                  </button>
                ))}
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowAssignModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CampaignContacts;
