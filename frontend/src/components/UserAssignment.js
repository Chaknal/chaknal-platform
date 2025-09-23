import React, { useState, useEffect, useCallback } from 'react';
import { Users, UserPlus, Play, CheckCircle, Clock, MessageCircle } from 'lucide-react';
import axios from 'axios';

function UserAssignment({ campaignId, onClose }) {
  const [users, setUsers] = useState([]);
  const [unassignedContacts, setUnassignedContacts] = useState([]);
  const [assignmentStats, setAssignmentStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedContacts, setSelectedContacts] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [showBulkAssign, setShowBulkAssign] = useState(false);
  const [bulkAssignType, setBulkAssignType] = useState('unassigned');
  const [bulkAssignStatus, setBulkAssignStatus] = useState('pending');
  const [showDetailedView, setShowDetailedView] = useState(false);
  const [assignedContacts, setAssignedContacts] = useState([]);
  const [filterUser, setFilterUser] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [launchingUsers, setLaunchingUsers] = useState(new Set());
  const [launchResults, setLaunchResults] = useState({});

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Generate mock data for demo purposes
      const mockUsers = [
        { id: 1, email: 'john.smith@company.com', name: 'John Smith' },
        { id: 2, email: 'sarah.johnson@company.com', name: 'Sarah Johnson' },
        { id: 3, email: 'michael.davis@company.com', name: 'Michael Davis' }
      ];
      setUsers(mockUsers);
      
      // Generate mock unassigned contacts
      const mockUnassignedContacts = generateMockContacts(15, 'unassigned');
      setUnassignedContacts(mockUnassignedContacts);
      
      // Generate mock assigned contacts
      const mockAssignedContacts = generateMockContacts(30, 'assigned');
      setAssignedContacts(mockAssignedContacts);
      
      // Generate mock assignment stats
      const mockStats = [
        { user_id: 1, user_email: 'john.smith@company.com', assigned_count: 10, pending_count: 5, completed_count: 3 },
        { user_id: 2, user_email: 'sarah.johnson@company.com', assigned_count: 8, pending_count: 4, completed_count: 2 },
        { user_id: 3, user_email: 'michael.davis@company.com', assigned_count: 12, pending_count: 6, completed_count: 4 }
      ];
      setAssignmentStats(mockStats);
      
    } catch (error) {
      console.error('Error generating mock assignment data:', error);
    } finally {
      setLoading(false);
    }
  }, [campaignId]);

  const generateMockContacts = (count, status) => {
    const contacts = [];
    const firstNames = ['John', 'Sarah', 'Michael', 'Emily', 'David', 'Lisa', 'Robert', 'Jennifer', 'William', 'Jessica'];
    const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'];
    const companies = ['TechCorp', 'InnovateLabs', 'DataFlow', 'CloudSync', 'NextGen', 'FutureTech', 'SmartSolutions', 'DigitalEdge'];
    const titles = ['Sales Manager', 'Marketing Director', 'VP Sales', 'CEO', 'CTO', 'VP Marketing', 'Sales Director', 'Business Development Manager'];
    
    for (let i = 0; i < count; i++) {
      const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
      const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
      const company = companies[Math.floor(Math.random() * companies.length)];
      const title = titles[Math.floor(Math.random() * titles.length)];
      
      contacts.push({
        contact_id: i + 1,
        first_name: firstName,
        last_name: lastName,
        full_name: `${firstName} ${lastName}`,
        company: company,
        title: title,
        linkedin_url: `https://linkedin.com/in/${firstName.toLowerCase()}-${lastName.toLowerCase()}-${Math.random().toString(36).substr(2, 9)}`,
        email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${company.toLowerCase()}.com`,
        status: status === 'assigned' ? ['pending', 'active', 'completed'][Math.floor(Math.random() * 3)] : 'unassigned',
        campaign_id: campaignId,
        assigned_user_id: status === 'assigned' ? Math.floor(Math.random() * 3) + 1 : null,
        created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
        last_activity: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
      });
    }
    
    return contacts;
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleContactSelect = (contactId) => {
    setSelectedContacts(prev => 
      prev.includes(contactId) 
        ? prev.filter(id => id !== contactId)
        : [...prev, contactId]
    );
  };

  const handleSelectAll = () => {
    if (selectedContacts.length === unassignedContacts.length) {
      setSelectedContacts([]);
    } else {
      setSelectedContacts(unassignedContacts.map(contact => contact.contact_id));
    }
  };

  const assignSelectedContacts = async () => {
    if (!selectedUser || selectedContacts.length === 0) {
      alert('Please select a user and at least one contact');
      return;
    }

    try {
      // Mock assignment - move contacts from unassigned to assigned
      const contactsToAssign = unassignedContacts.filter(contact => 
        selectedContacts.includes(contact.contact_id)
      );
      
      // Update unassigned contacts (remove assigned ones)
      setUnassignedContacts(prev => 
        prev.filter(contact => !selectedContacts.includes(contact.contact_id))
      );
      
      // Update assigned contacts (add newly assigned ones)
      const newlyAssigned = contactsToAssign.map(contact => ({
        ...contact,
        assigned_user_id: parseInt(selectedUser),
        status: 'pending'
      }));
      
      setAssignedContacts(prev => [...prev, ...newlyAssigned]);
      
      // Update assignment stats
      setAssignmentStats(prev => prev.map(stat => 
        stat.user_id === parseInt(selectedUser) 
          ? { ...stat, assigned_count: stat.assigned_count + selectedContacts.length }
          : stat
      ));
      
      alert(`Successfully assigned ${selectedContacts.length} contacts to user`);
      setSelectedContacts([]);
      setSelectedUser('');
    } catch (error) {
      console.error('Error assigning contacts:', error);
      alert('Failed to assign contacts');
    }
  };

  const handleBulkAssign = async () => {
    if (!selectedUser) {
      alert('Please select a user');
      return;
    }

    try {
      let contactsToAssign = [];
      
      if (bulkAssignType === 'unassigned') {
        contactsToAssign = unassignedContacts;
      } else if (bulkAssignType === 'by_status') {
        contactsToAssign = assignedContacts.filter(contact => contact.status === bulkAssignStatus);
      }
      
      if (contactsToAssign.length === 0) {
        alert('No contacts available for bulk assignment');
        return;
      }
      
      // Mock bulk assignment
      if (bulkAssignType === 'unassigned') {
        // Move all unassigned contacts to assigned
        setUnassignedContacts([]);
        const newlyAssigned = contactsToAssign.map(contact => ({
          ...contact,
          assigned_user_id: parseInt(selectedUser),
          status: 'pending'
        }));
        setAssignedContacts(prev => [...prev, ...newlyAssigned]);
      }
      
      // Update assignment stats
      setAssignmentStats(prev => prev.map(stat => 
        stat.user_id === parseInt(selectedUser) 
          ? { ...stat, assigned_count: stat.assigned_count + contactsToAssign.length }
          : stat
      ));
      
      alert(`Successfully bulk assigned ${contactsToAssign.length} contacts to user`);
      setShowBulkAssign(false);
      setSelectedUser('');
    } catch (error) {
      console.error('Error bulk assigning contacts:', error);
      alert('Failed to bulk assign contacts');
    }
  };

  const launchSequenceForUser = async (userId) => {
    try {
      // Add user to launching set
      setLaunchingUsers(prev => new Set([...prev, userId]));
      
      // Clear any previous results for this user
      setLaunchResults(prev => {
        const newResults = { ...prev };
        delete newResults[userId];
        return newResults;
      });

      const response = await axios.post(`/api/campaigns/${campaignId}/launch-sequence`, {
        user_id: userId
      });
      
      // Store success result
      setLaunchResults(prev => ({
        ...prev,
        [userId]: {
          success: true,
          message: response.data.message,
          launchedCount: response.data.launched_count || 0,
          timestamp: new Date().toLocaleTimeString()
        }
      }));
      
      // Refresh data after a short delay to show the result
      setTimeout(() => {
        fetchData();
      }, 1000);
      
      // Clear the result after 5 seconds
      setTimeout(() => {
        setLaunchResults(prev => {
          const newResults = { ...prev };
          delete newResults[userId];
          return newResults;
        });
      }, 5000);
      
    } catch (error) {
      console.error('Error launching sequence:', error);
      
      // Store error result
      setLaunchResults(prev => ({
        ...prev,
        [userId]: {
          success: false,
          message: error.response?.data?.detail || 'Failed to launch sequence',
          timestamp: new Date().toLocaleTimeString()
        }
      }));
      
      // Clear the error result after 5 seconds
      setTimeout(() => {
        setLaunchResults(prev => {
          const newResults = { ...prev };
          delete newResults[userId];
          return newResults;
        });
      }, 5000);
    } finally {
      // Remove user from launching set
      setLaunchingUsers(prev => {
        const newSet = new Set(prev);
        newSet.delete(userId);
        return newSet;
      });
    }
  };



  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span>Loading assignment data...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">User Assignment & Sequence Launcher</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <span className="sr-only">Close</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Assignment Statistics */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Assignment Statistics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {assignmentStats.map((stat) => (
                <div key={stat.user_id} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{stat.user_email}</h4>
                                            <div className="flex flex-col items-end space-y-1">
                          <button
                            onClick={() => launchSequenceForUser(stat.user_id)}
                            disabled={stat.pending_contacts === 0 || launchingUsers.has(stat.user_id)}
                            className={`px-3 py-1 rounded text-sm flex items-center space-x-1 ${
                              stat.pending_contacts === 0
                                ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                                : launchingUsers.has(stat.user_id)
                                ? 'bg-blue-600 text-white cursor-wait'
                                : 'bg-green-600 text-white hover:bg-green-700'
                            }`}
                          >
                            {launchingUsers.has(stat.user_id) ? (
                              <>
                                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                                <span>Launching...</span>
                              </>
                            ) : (
                              <>
                                <Play className="h-3 w-3" />
                                <span>{stat.pending_contacts === 0 ? 'No Pending' : 'Launch'}</span>
                              </>
                            )}
                          </button>
                          
                          {/* Show launch result */}
                          {launchResults[stat.user_id] && (
                            <div className={`text-xs px-2 py-1 rounded ${
                              launchResults[stat.user_id].success 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {launchResults[stat.user_id].success ? (
                                <div className="flex items-center space-x-1">
                                  <CheckCircle className="h-3 w-3" />
                                  <span>✓ {launchResults[stat.user_id].launchedCount} launched</span>
                                </div>
                              ) : (
                                <div className="flex items-center space-x-1">
                                  <span>✗ Failed</span>
                                </div>
                              )}
                              <div className="text-xs opacity-75">
                                {launchResults[stat.user_id].timestamp}
                              </div>
                            </div>
                          )}
                        </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center space-x-1">
                      <Users className="h-4 w-4 text-blue-600" />
                      <span>{stat.total_assigned} Total</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Clock className="h-4 w-4 text-yellow-600" />
                      <span>{stat.pending_contacts} Pending</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Play className="h-4 w-4 text-green-600" />
                      <span>{stat.active_contacts} Active</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>{stat.accepted_contacts} Accepted</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <MessageCircle className="h-4 w-4 text-purple-600" />
                      <span>{stat.responded_contacts} Responded</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span>{stat.completed_contacts} Completed</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Processed Contacts Summary */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Processed Contacts</h3>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="font-medium text-green-800">Completed Sequences</span>
              </div>
              <p className="text-sm text-green-700">
                Contacts that have been processed and moved out of the launch queue. 
                These contacts will not be included in future sequence launches.
              </p>
            </div>
          </div>

          {/* User Breakdown */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">User Assignment Breakdown</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {assignmentStats.map((stat) => {
                const totalContacts = unassignedContacts.length + assignedContacts.length;
                const assignedPercentage = totalContacts > 0 ? (stat.total_assigned / totalContacts * 100).toFixed(1) : 0;
                
                return (
                  <div key={stat.user_id} className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-gray-900">{stat.user_email.split('@')[0].replace(/\./g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                      <span className="text-sm text-gray-500">{assignedPercentage}%</span>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Total Assigned:</span>
                        <span className="font-medium">{stat.total_assigned}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Pending:</span>
                        <span className="font-medium text-yellow-600">{stat.pending_contacts}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Active:</span>
                        <span className="font-medium text-green-600">{stat.active_contacts}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Completed:</span>
                        <span className="font-medium text-blue-600">{stat.completed_contacts}</span>
                      </div>
                    </div>
                    
                    {/* Progress bar */}
                    <div className="mt-3">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                          style={{ width: `${assignedPercentage}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Assignment Overview & Detailed View */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Assignment Overview</h3>
              <button
                onClick={() => setShowDetailedView(!showDetailedView)}
                className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 flex items-center space-x-2"
              >
                <Users className="h-4 w-4" />
                <span>{showDetailedView ? 'Hide' : 'Show'} Detailed View</span>
              </button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">{unassignedContacts.length}</div>
                <div className="text-sm text-blue-800">Unassigned Contacts</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-600">{assignedContacts.length}</div>
                <div className="text-sm text-green-800">Assigned Contacts</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-2xl font-bold text-gray-600">{unassignedContacts.length + assignedContacts.length}</div>
                <div className="text-sm text-gray-800">Total Contacts</div>
              </div>
            </div>

            {/* Detailed View */}
            {showDetailedView && (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">
                      {filterUser === 'unassigned' 
                        ? 'Unassigned Contacts' 
                        : filterUser 
                          ? `Contacts Assigned to ${users.find(u => u.id === filterUser)?.name || 'User'}` 
                          : 'All Assigned Contacts'
                      }
                    </h4>
                    <div className="flex items-center space-x-4">
                      <select
                        value={filterUser}
                        onChange={(e) => setFilterUser(e.target.value)}
                        className="text-sm border border-gray-300 rounded px-2 py-1"
                      >
                        <option value="">All Users</option>
                        <option value="unassigned">Not Assigned</option>
                        {users.map(user => (
                          <option key={user.id} value={user.id}>{user.name}</option>
                        ))}
                      </select>
                      <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="text-sm border border-gray-300 rounded px-2 py-1"
                      >
                        <option value="">All Statuses</option>
                        <option value="pending">Pending</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="enrolled">Enrolled</option>
                        <option value="accepted">Accepted</option>
                        <option value="not_accepted">Not Accepted</option>
                        <option value="excepted">Excepted</option>
                        <option value="responded">Responded</option>
                        <option value="accepted_and_responded">Accepted and Responded</option>
                        <option value="no_response">No Response</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div className="max-h-96 overflow-y-auto">
                  {(filterUser === 'unassigned' ? unassignedContacts : assignedContacts).length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                      <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>
                        {filterUser === 'unassigned' 
                          ? 'No unassigned contacts found' 
                          : filterUser 
                            ? 'No contacts assigned to this user' 
                            : 'No contacts have been assigned yet'
                        }
                      </p>
                    </div>
                  ) : (
                    <div className="divide-y divide-gray-200">
                      {(filterUser === 'unassigned' ? unassignedContacts : assignedContacts)
                        .filter(contact => {
                          if (filterUser === 'unassigned') {
                            return !filterStatus || contact.status === filterStatus;
                          } else if (filterUser) {
                            return contact.assigned_to === filterUser && (!filterStatus || contact.status === filterStatus);
                          } else {
                            return !filterStatus || contact.status === filterStatus;
                          }
                        })
                        .map((contact) => (
                        <div key={contact.contact_id} className="px-4 py-3 hover:bg-gray-50">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="font-medium text-gray-900">{contact.full_name}</div>
                              <div className="text-sm text-gray-500">
                                {contact.job_title && contact.company_name 
                                  ? `${contact.job_title} at ${contact.company_name}`
                                  : contact.job_title || contact.company_name || 'Contact details not available'
                                }
                              </div>
                            </div>
                            <div className="flex items-center space-x-4 text-sm">
                              <div className="text-gray-500">
                                <span className="font-medium">Assigned to:</span> 
                                {filterUser === 'unassigned' ? (
                                  <span className="text-red-600">Not Assigned</span>
                                ) : (
                                  contact.assigned_to_name
                                )}
                              </div>
                              <div className="text-gray-500">
                                <span className="font-medium">Status:</span> 
                                <span className={`ml-1 px-2 py-1 rounded text-xs ${
                                  contact.status === 'active' ? 'bg-green-100 text-green-800' :
                                  contact.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                                  contact.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                  contact.status === 'enrolled' ? 'bg-purple-100 text-purple-800' :
                                  contact.status === 'accepted' ? 'bg-emerald-100 text-emerald-800' :
                                  contact.status === 'not_accepted' ? 'bg-red-100 text-red-800' :
                                  contact.status === 'excepted' ? 'bg-orange-100 text-orange-800' :
                                  contact.status === 'responded' ? 'bg-cyan-100 text-cyan-800' :
                                  contact.status === 'accepted_and_responded' ? 'bg-teal-100 text-teal-800' :
                                  contact.status === 'no_response' ? 'bg-gray-100 text-gray-600' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {contact.status === 'accepted_and_responded' ? 'Accepted & Responded' :
                                   contact.status === 'not_accepted' ? 'Not Accepted' :
                                   contact.status === 'no_response' ? 'No Response' :
                                   contact.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </span>
                              </div>
                              <div className="text-gray-500">
                                <span className="font-medium">Step:</span> {contact.sequence_step || 'N/A'}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Bulk Assignment */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Bulk Assignment</h3>
              <button
                onClick={() => setShowBulkAssign(!showBulkAssign)}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 flex items-center space-x-2"
              >
                <UserPlus className="h-4 w-4" />
                <span>Bulk Assign</span>
              </button>
            </div>

            {showBulkAssign && (
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Assign to User</label>
                    <select
                      value={selectedUser}
                      onChange={(e) => setSelectedUser(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="">Select User</option>
                      {users.map(user => (
                        <option key={user.id} value={user.id}>{user.name} ({user.email})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Assignment Type</label>
                    <select
                      value={bulkAssignType}
                      onChange={(e) => setBulkAssignType(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="unassigned">Unassigned Contacts</option>
                      <option value="all">All Contacts</option>
                      <option value="by_status">By Status</option>
                    </select>
                  </div>
                  {bulkAssignType === 'by_status' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Status Filter</label>
                      <select
                        value={bulkAssignStatus}
                        onChange={(e) => setBulkAssignStatus(e.target.value)}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      >
                        <option value="pending">Pending</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="blacklisted">Blacklisted</option>
                      </select>
                    </div>
                  )}
                </div>
                <div className="mt-4 flex space-x-2">
                  <button
                    onClick={handleBulkAssign}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  >
                    Assign All
                  </button>
                  <button
                    onClick={() => setShowBulkAssign(false)}
                    className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Individual Contact Assignment */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Individual Contact Assignment</h3>
            
            <div className="mb-4 flex items-center space-x-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">Assign to User</label>
                <select
                  value={selectedUser}
                  onChange={(e) => setSelectedUser(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Select User</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>{user.name} ({user.email})</option>
                  ))}
                </select>
              </div>
              <button
                onClick={assignSelectedContacts}
                disabled={!selectedUser || selectedContacts.length === 0}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Assign Selected ({selectedContacts.length})
              </button>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                <div className="flex items-center space-x-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedContacts.length === unassignedContacts.length && unassignedContacts.length > 0}
                      onChange={handleSelectAll}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm font-medium text-gray-700">Select All</span>
                  </label>
                  <span className="text-sm text-gray-500">
                    {unassignedContacts.length} unassigned contacts
                  </span>
                </div>
              </div>
              
              <div className="max-h-64 overflow-y-auto">
                {unassignedContacts.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>All contacts have been assigned to users</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {unassignedContacts.map((contact) => (
                      <div key={contact.contact_id} className="px-4 py-3 hover:bg-gray-50">
                        <div className="flex items-center space-x-4">
                          <input
                            type="checkbox"
                            checked={selectedContacts.includes(contact.contact_id)}
                            onChange={() => handleContactSelect(contact.contact_id)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <div className="flex-1">
                            <div className="font-medium text-gray-900">{contact.full_name}</div>
                            <div className="text-sm text-gray-500">
                              {contact.job_title && contact.company_name 
                                ? `${contact.job_title} at ${contact.company_name}`
                                : contact.job_title || contact.company_name || 'Contact details not available'
                              }
                            </div>
                          </div>
                          <div className="text-sm text-gray-500">
                            Status: <span className="capitalize">{contact.status}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UserAssignment;
