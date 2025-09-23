import React, { useState, useEffect } from 'react';
import { 
  UserPlus, 
  Users, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Eye, 
  CheckCircle, 
  XCircle,
  Mail,
  Phone,
  Building,
  Calendar,
  MoreVertical,
  Plus,
  Key,
  Settings
} from 'lucide-react';
import axios from 'axios';
import DuxSoupAccounts from './DuxSoupAccounts';
import { logMockData, shouldUseMockData } from '../utils/mockDataLogger';

function UserManagement() {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0
  });

  // Form state for adding/editing users
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirm_password: '',
    first_name: '',
    last_name: '',
    company_name: '',
    company_domain: '',
    phone: '',
    role: 'user'
  });

  // Fetch users
  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        per_page: pagination.per_page.toString()
      });
      
      if (searchTerm) params.append('search', searchTerm);
      if (roleFilter) params.append('role', roleFilter);

      const response = await axios.get(`/api/users?${params}`);
      setUsers(response.data.users);
      setPagination(prev => ({
        ...prev,
        total: response.data.total,
        total_pages: response.data.total_pages
      }));
    } catch (error) {
      console.error('Error fetching users from database:', error);
      
      // Log mock data usage
      logMockData('UserManagement', 'user_list', {
        reason: 'API_FAILURE',
        error: error.message,
        fallback: true
      });
      
      // Fallback to mock data for demo purposes
      const mockUsers = [
        {
          id: '1',
          email: 'sercio.campos@wallarm.com',
          first_name: 'Sercio',
          last_name: 'Campos',
          is_active: true,
          is_verified: true,
          role: 'user',
          company_name: 'Marketing Masters',
          company_domain: 'marketingmasters.com',
          phone: '+1-555-0123',
          created_at: '2025-09-10T10:00:00Z',
          updated_at: '2025-09-17T15:30:00Z'
        },
        {
          id: '2',
          email: 'shayne.stubbs@attimis.co',
          first_name: 'Shayne',
          last_name: 'Stubbs',
          is_active: true,
          is_verified: true,
          role: 'admin',
          company_name: 'Attimis Solutions',
          company_domain: 'attimis.co',
          phone: '+1-555-0456',
          created_at: '2025-09-08T14:20:00Z',
          updated_at: '2025-09-16T09:15:00Z'
        },
        {
          id: '3',
          email: 'john.smith@techcorp.com',
          first_name: 'John',
          last_name: 'Smith',
          is_active: true,
          is_verified: true,
          role: 'user',
          company_name: 'TechCorp Solutions',
          company_domain: 'techcorp.com',
          phone: '+1-555-0789',
          created_at: '2025-09-12T11:45:00Z',
          updated_at: '2025-09-17T16:20:00Z'
        },
        {
          id: '4',
          email: 'sarah.johnson@salesforcepro.com',
          first_name: 'Sarah',
          last_name: 'Johnson',
          is_active: false,
          is_verified: true,
          role: 'manager',
          company_name: 'SalesForce Pro',
          company_domain: 'salesforcepro.com',
          phone: '+1-555-0321',
          created_at: '2025-09-05T08:30:00Z',
          updated_at: '2025-09-15T12:10:00Z'
        },
        {
          id: '5',
          email: 'mike.davis@marketingmasters.com',
          first_name: 'Mike',
          last_name: 'Davis',
          is_active: true,
          is_verified: false,
          role: 'user',
          company_name: 'Marketing Masters',
          company_domain: 'marketingmasters.com',
          phone: '+1-555-0654',
          created_at: '2025-09-14T16:00:00Z',
          updated_at: '2025-09-17T10:45:00Z'
        }
      ];

      // Filter mock data based on search and role filters
      let filteredUsers = mockUsers;
      
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        filteredUsers = filteredUsers.filter(user => 
          user.first_name.toLowerCase().includes(searchLower) ||
          user.last_name.toLowerCase().includes(searchLower) ||
          user.email.toLowerCase().includes(searchLower)
        );
      }
      
      if (roleFilter) {
        filteredUsers = filteredUsers.filter(user => user.role === roleFilter);
      }

      setUsers(filteredUsers);
      setPagination(prev => ({
        ...prev,
        total: filteredUsers.length,
        total_pages: Math.ceil(filteredUsers.length / prev.per_page)
      }));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [pagination.page, searchTerm, roleFilter]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        // Update existing user
        await axios.put(`/api/users/${editingUser.id}`, formData);
      } else {
        // Create new user
        await axios.post('/api/users/register', formData);
      }
      
      setShowAddModal(false);
      setEditingUser(null);
      setFormData({
        email: '',
        password: '',
        confirm_password: '',
        first_name: '',
        last_name: '',
        company_name: '',
        company_domain: '',
        phone: '',
        role: 'user'
      });
      fetchUsers();
    } catch (error) {
      console.error('Error saving user, updating mock data:', error);
      
      if (editingUser) {
        // Update existing user in mock data
        setUsers(prevUsers => 
          prevUsers.map(user => 
            user.id === editingUser.id 
              ? {
                  ...user,
                  email: formData.email,
                  first_name: formData.first_name,
                  last_name: formData.last_name,
                  role: formData.role,
                  company_name: formData.company_name,
                  company_domain: formData.company_domain,
                  phone: formData.phone,
                  updated_at: new Date().toISOString()
                }
              : user
          )
        );
        
        alert('User updated successfully (demo mode)!');
      } else {
        // Add new user to mock data
        const newUser = {
          id: Date.now().toString(), // Simple ID generation for demo
          email: formData.email,
          first_name: formData.first_name,
          last_name: formData.last_name,
          is_active: true,
          is_verified: false,
          role: formData.role,
          company_name: formData.company_name,
          company_domain: formData.company_domain,
          phone: formData.phone,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setUsers(prevUsers => [newUser, ...prevUsers]);
        setPagination(prev => ({
          ...prev,
          total: prev.total + 1,
          total_pages: Math.ceil((prev.total + 1) / prev.per_page)
        }));
        
        alert('User added successfully (demo mode)!');
      }
      
      setShowAddModal(false);
      setEditingUser(null);
      setFormData({
        email: '',
        password: '',
        confirm_password: '',
        first_name: '',
        last_name: '',
        company_name: '',
        company_domain: '',
        phone: '',
        role: 'user'
      });
    }
  };

  // Handle user deletion
  const handleDelete = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      await axios.delete(`/api/users/${userId}`);
      fetchUsers();
    } catch (error) {
      console.error('Error deleting user, removing from mock data:', error);
      
      // For demo purposes, remove the user from the current users list
      setUsers(prevUsers => prevUsers.filter(user => user.id !== userId));
      setPagination(prev => ({
        ...prev,
        total: Math.max(0, prev.total - 1),
        total_pages: Math.ceil(Math.max(0, prev.total - 1) / prev.per_page)
      }));
      
      alert('User deleted successfully (demo mode)!');
    }
  };

  // Handle edit user
  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      email: user.email,
      password: '',
      confirm_password: '',
      first_name: user.first_name,
      last_name: user.last_name,
      company_name: user.company_name || '',
      company_domain: user.company_domain || '',
      phone: user.phone || '',
      role: user.role
    });
    setShowAddModal(true);
  };

  // Handle add new user
  const handleAddNew = () => {
    setEditingUser(null);
    setFormData({
      email: '',
      password: '',
      confirm_password: '',
      first_name: '',
      last_name: '',
      company_name: '',
      company_domain: '',
      phone: '',
      role: 'user'
    });
    setShowAddModal(true);
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'manager': return 'bg-blue-100 text-blue-800';
      case 'user': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage users and their access to the platform</p>
        </div>
        {activeTab === 'users' && (
          <button
            onClick={handleAddNew}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add User
          </button>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('users')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'users'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Users className="h-4 w-4 inline mr-2" />
            Users
          </button>
          <button
            onClick={() => setActiveTab('duxsoup')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'duxsoup'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Key className="h-4 w-4 inline mr-2" />
            DuxSoup Accounts
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'duxsoup' ? (
        <DuxSoupAccounts />
      ) : (
        <>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by name or email..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="manager">Manager</option>
              <option value="user">User</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('');
                setRoleFilter('');
              }}
              className="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Users Table */}
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
                <div className="col-span-3">User</div>
                <div className="col-span-2">Email</div>
                <div className="col-span-2">Company</div>
                <div className="col-span-1">Role</div>
                <div className="col-span-1">Status</div>
                <div className="col-span-2">Created</div>
                <div className="col-span-1">Actions</div>
              </div>
            </div>

            {/* Table Body */}
            <div className="divide-y divide-gray-200">
              {users.map((user) => (
                <div key={user.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="grid grid-cols-12 gap-4 items-center">
                    {/* User Info */}
                    <div className="col-span-3">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-sm font-medium text-blue-600">
                              {user.first_name?.[0]}{user.last_name?.[0]}
                            </span>
                          </div>
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {user.first_name} {user.last_name}
                          </p>
                          <p className="text-sm text-gray-500 truncate">
                            {user.phone && (
                              <span className="flex items-center">
                                <Phone className="h-3 w-3 mr-1" />
                                {user.phone}
                              </span>
                            )}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Email */}
                    <div className="col-span-2">
                      <div className="flex items-center text-sm text-gray-900">
                        <Mail className="h-4 w-4 mr-2 text-gray-400" />
                        {user.email}
                      </div>
                    </div>

                    {/* Company */}
                    <div className="col-span-2">
                      <div className="text-sm text-gray-900">
                        {user.company_name && (
                          <div className="flex items-center">
                            <Building className="h-4 w-4 mr-2 text-gray-400" />
                            <div>
                              <div className="font-medium">{user.company_name}</div>
                              {user.company_domain && (
                                <div className="text-gray-500 text-xs">{user.company_domain}</div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Role */}
                    <div className="col-span-1">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                        {user.role}
                      </span>
                    </div>

                    {/* Status */}
                    <div className="col-span-1">
                      <div className="flex items-center">
                        {user.is_active ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="ml-1 text-sm text-gray-900">
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>

                    {/* Created Date */}
                    <div className="col-span-2">
                      <div className="flex items-center text-sm text-gray-500">
                        <Calendar className="h-4 w-4 mr-2" />
                        {new Date(user.created_at).toLocaleDateString()}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="col-span-1">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleEdit(user)}
                          className="text-gray-400 hover:text-blue-600"
                          title="Edit User"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(user.id)}
                          className="text-gray-400 hover:text-red-600"
                          title="Delete User"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Empty State */}
            {users.length === 0 && (
              <div className="text-center py-12">
                <Users className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your search or filter criteria.
                </p>
              </div>
            )}
          </>
        )}
      </div>

      {/* Pagination */}
      {pagination.total_pages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {((pagination.page - 1) * pagination.per_page) + 1} to {Math.min(pagination.page * pagination.per_page, pagination.total)} of {pagination.total} users
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
              disabled={pagination.page === 1}
              className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-3 py-2 text-sm text-gray-700">
              Page {pagination.page} of {pagination.total_pages}
            </span>
            <button
              onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
              disabled={pagination.page === pagination.total_pages}
              className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Add/Edit User Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {editingUser ? 'Edit User' : 'Add New User'}
                </h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      First Name *
                    </label>
                    <input
                      type="text"
                      value={formData.first_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, first_name: e.target.value }))}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      value={formData.last_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, last_name: e.target.value }))}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {!editingUser && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Password *
                      </label>
                      <input
                        type="password"
                        value={formData.password}
                        onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                        required={!editingUser}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Confirm Password *
                      </label>
                      <input
                        type="password"
                        value={formData.confirm_password}
                        onChange={(e) => setFormData(prev => ({ ...prev, confirm_password: e.target.value }))}
                        required={!editingUser}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Role
                  </label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="user">User</option>
                    <option value="manager">Manager</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Company Name
                    </label>
                    <input
                      type="text"
                      value={formData.company_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, company_name: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Company Domain
                    </label>
                    <input
                      type="text"
                      value={formData.company_domain}
                      onChange={(e) => setFormData(prev => ({ ...prev, company_domain: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Modal Actions */}
                <div className="flex items-center justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    {editingUser ? 'Update User' : 'Add User'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
        </>
      )}
    </div>
  );
}

export default UserManagement;
