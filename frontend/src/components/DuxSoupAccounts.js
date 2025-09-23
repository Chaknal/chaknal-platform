import React, { useState, useEffect, useRef } from 'react';
import { 
  Plus, 
  Upload, 
  Download, 
  Edit, 
  Trash2, 
  Eye, 
  CheckCircle, 
  XCircle,
  Mail,
  Key,
  User,
  Building,
  Calendar,
  AlertCircle
} from 'lucide-react';
import axios from 'axios';

function DuxSoupAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 0
  });

  // Form state for adding/editing accounts
  const [formData, setFormData] = useState({
    dux_soup_user_id: '',
    dux_soup_auth_key: '',
    email: '',
    first_name: '',
    last_name: '',
    user_id: ''
  });

  // Bulk import state
  const [selectedFile, setSelectedFile] = useState(null);
  const [bulkLoading, setBulkLoading] = useState(false);
  const [bulkError, setBulkError] = useState(null);
  const [bulkStep, setBulkStep] = useState(1); // 1: Upload, 2: Preview, 3: Import
  const [previewData, setPreviewData] = useState(null);
  const [fieldMapping, setFieldMapping] = useState({});
  const fileInputRef = useRef(null);

  // Required fields for DuxSoup accounts
  const requiredFields = [
    { key: 'dux_soup_user_id', label: 'DuxSoup User ID', required: true },
    { key: 'dux_soup_auth_key', label: 'DuxSoup Auth Key', required: true },
    { key: 'email', label: 'Email', required: true },
    { key: 'first_name', label: 'First Name', required: true },
    { key: 'last_name', label: 'Last Name', required: true }
  ];

  // Fetch DuxSoup accounts
  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        per_page: pagination.per_page.toString()
      });
      
      if (searchTerm) params.append('search', searchTerm);

      const response = await axios.get(`https://platform.chaknal.com/api/duxsoup-accounts?${params}`);
      setAccounts(response.data.accounts || []);
      setPagination(prev => ({
        ...prev,
        total: response.data.total || 0,
        total_pages: response.data.total_pages || 0
      }));
    } catch (error) {
      console.error('Error fetching DuxSoup accounts:', error);
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, [pagination.page, searchTerm]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingAccount) {
        // Update existing account
        await axios.put(`https://platform.chaknal.com/api/duxsoup-accounts/${editingAccount.id}`, formData);
      } else {
        // Create new account
        await axios.post('https://platform.chaknal.com/api/duxsoup-accounts', formData);
      }
      
      setShowAddModal(false);
      setEditingAccount(null);
      setFormData({
        dux_soup_user_id: '',
        dux_soup_auth_key: '',
        email: '',
        first_name: '',
        last_name: '',
        user_id: ''
      });
      fetchAccounts();
    } catch (error) {
      console.error('Error saving DuxSoup account:', error);
      alert('Failed to save DuxSoup account. Please try again.');
    }
  };

  // Handle file selection
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setBulkError(null);
      setBulkStep(1);
      setPreviewData(null);
      setFieldMapping({});
    }
  };

  // Handle file preview
  const handlePreview = async () => {
    if (!selectedFile) {
      setBulkError('Please select a file first');
      return;
    }

    setBulkLoading(true);
    setBulkError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post('http://localhost:8000/api/duxsoup-accounts/bulk-preview', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setPreviewData(response.data);
      
      // Auto-map fields based on column names
      const autoMapping = {};
      if (response.data.columns) {
        response.data.columns.forEach(column => {
          const field = requiredFields.find(f => 
            column.toLowerCase().includes(f.key.toLowerCase()) ||
            column.toLowerCase().includes(f.label.toLowerCase().replace(/\s+/g, ''))
          );
          if (field) {
            autoMapping[field.key] = column;
          }
        });
      }
      setFieldMapping(autoMapping);
      setBulkStep(2);
    } catch (error) {
      console.error('Error previewing file:', error);
      setBulkError(error.response?.data?.detail || 'Failed to preview file. Please check your file format.');
    } finally {
      setBulkLoading(false);
    }
  };

  // Handle bulk import
  const handleBulkImport = async () => {
    if (!selectedFile) {
      setBulkError('Please select a file first');
      return;
    }

    setBulkLoading(true);
    setBulkError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('field_mapping', JSON.stringify(fieldMapping));

      const response = await axios.post('http://localhost:8000/api/duxsoup-accounts/bulk-import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setShowBulkModal(false);
      setSelectedFile(null);
      setBulkStep(1);
      setPreviewData(null);
      setFieldMapping({});
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      fetchAccounts();
      alert(`Successfully imported ${response.data.imported_count || 0} DuxSoup accounts!`);
    } catch (error) {
      console.error('Error importing DuxSoup accounts:', error);
      setBulkError(error.response?.data?.detail || 'Failed to import DuxSoup accounts. Please check your file format.');
    } finally {
      setBulkLoading(false);
    }
  };

  // Download template for bulk import
  const downloadTemplate = () => {
    const templateData = [
      'dux_soup_user_id,dux_soup_auth_key,email,first_name,last_name',
      '12345,abc123def456,john.doe@example.com,John,Doe',
      '67890,ghi789jkl012,jane.smith@example.com,Jane,Smith',
      '11111,mno345pqr678,bob.wilson@example.com,Bob,Wilson'
    ].join('\n');

    const blob = new Blob([templateData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'duxsoup_accounts_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  // Handle account deletion
  const handleDelete = async (accountId) => {
    if (!window.confirm('Are you sure you want to delete this DuxSoup account?')) return;
    
    try {
      await axios.delete(`http://localhost:8000/api/duxsoup-accounts/${accountId}`);
      fetchAccounts();
    } catch (error) {
      console.error('Error deleting DuxSoup account:', error);
      alert('Failed to delete DuxSoup account. Please try again.');
    }
  };

  // Handle edit account
  const handleEdit = (account) => {
    setEditingAccount(account);
    setFormData({
      dux_soup_user_id: account.dux_soup_user_id || '',
      dux_soup_auth_key: account.dux_soup_auth_key || '',
      email: account.email || '',
      first_name: account.first_name || '',
      last_name: account.last_name || '',
      user_id: account.user_id || ''
    });
    setShowAddModal(true);
  };

  // Handle add new account
  const handleAddNew = () => {
    setEditingAccount(null);
    setFormData({
      dux_soup_user_id: '',
      dux_soup_auth_key: '',
      email: '',
      first_name: '',
      last_name: '',
      user_id: ''
    });
    setShowAddModal(true);
  };


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">DuxSoup Accounts</h2>
          <p className="text-gray-600">Manage DuxSoup user IDs and authentication keys</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowBulkModal(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Upload className="h-4 w-4 mr-2" />
            Bulk Import
          </button>
          <button
            onClick={handleAddNew}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Account
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by email, name, or DuxSoup ID..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={downloadTemplate}
            className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <Download className="h-4 w-4 mr-2" />
            Download Template
          </button>
        </div>
      </div>

      {/* Accounts Table */}
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
                <div className="col-span-3">Account Info</div>
                <div className="col-span-2">DuxSoup ID</div>
                <div className="col-span-2">Auth Key</div>
                <div className="col-span-2">User</div>
                <div className="col-span-2">Created</div>
                <div className="col-span-1">Actions</div>
              </div>
            </div>

            {/* Table Body */}
            <div className="divide-y divide-gray-200">
              {accounts.map((account) => (
                <div key={account.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="grid grid-cols-12 gap-4 items-center">
                    {/* Account Info */}
                    <div className="col-span-3">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                            <User className="h-5 w-5 text-green-600" />
                          </div>
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {account.first_name} {account.last_name}
                          </p>
                          <p className="text-sm text-gray-500 truncate flex items-center">
                            <Mail className="h-3 w-3 mr-1" />
                            {account.email}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* DuxSoup ID */}
                    <div className="col-span-2">
                      <div className="text-sm text-gray-900 font-mono">
                        {account.dux_soup_user_id}
                      </div>
                    </div>

                    {/* Auth Key */}
                    <div className="col-span-2">
                      <div className="text-sm text-gray-900 font-mono">
                        {account.dux_soup_auth_key ? 
                          `${account.dux_soup_auth_key.substring(0, 8)}...` : 
                          'Not set'
                        }
                      </div>
                    </div>

                    {/* User */}
                    <div className="col-span-2">
                      <div className="text-sm text-gray-900">
                        {account.user_id ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Linked
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            <XCircle className="h-3 w-3 mr-1" />
                            Unlinked
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Created Date */}
                    <div className="col-span-2">
                      <div className="flex items-center text-sm text-gray-500">
                        <Calendar className="h-4 w-4 mr-2" />
                        {new Date(account.created_at).toLocaleDateString()}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="col-span-1">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleEdit(account)}
                          className="text-gray-400 hover:text-blue-600"
                          title="Edit Account"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(account.id)}
                          className="text-gray-400 hover:text-red-600"
                          title="Delete Account"
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
            {accounts.length === 0 && (
              <div className="text-center py-12">
                <User className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No DuxSoup accounts found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Get started by adding your first DuxSoup account.
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
            Showing {((pagination.page - 1) * pagination.per_page) + 1} to {Math.min(pagination.page * pagination.per_page, pagination.total)} of {pagination.total} accounts
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

      {/* Add/Edit Account Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {editingAccount ? 'Edit DuxSoup Account' : 'Add DuxSoup Account'}
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

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    DuxSoup User ID *
                  </label>
                  <input
                    type="text"
                    value={formData.dux_soup_user_id}
                    onChange={(e) => setFormData(prev => ({ ...prev, dux_soup_user_id: e.target.value }))}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    DuxSoup Auth Key *
                  </label>
                  <input
                    type="text"
                    value={formData.dux_soup_auth_key}
                    onChange={(e) => setFormData(prev => ({ ...prev, dux_soup_auth_key: e.target.value }))}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Link to User (Optional)
                  </label>
                  <input
                    type="text"
                    value={formData.user_id}
                    onChange={(e) => setFormData(prev => ({ ...prev, user_id: e.target.value }))}
                    placeholder="User ID to link this account"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
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
                    {editingAccount ? 'Update Account' : 'Add Account'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Bulk Import Modal */}
      {showBulkModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-2xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Bulk Import DuxSoup Accounts</h3>
                <button
                  onClick={() => setShowBulkModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                {/* Step 1: File Upload */}
                {bulkStep === 1 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Upload File
                    </label>
                  <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-gray-400 transition-colors">
                    <div className="space-y-1 text-center">
                      <Upload className="mx-auto h-12 w-12 text-gray-400" />
                      <div className="flex text-sm text-gray-600">
                        <label
                          htmlFor="file-upload"
                          className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                        >
                          <span>Upload a file</span>
                          <input
                            id="file-upload"
                            name="file-upload"
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileSelect}
                            accept=".csv,.xlsx,.xls,.json"
                            className="sr-only"
                          />
                        </label>
                        <p className="pl-1">or drag and drop</p>
                      </div>
                      <p className="text-xs text-gray-500">
                        CSV, Excel, or JSON files up to 10MB
                      </p>
                    </div>
                  </div>
                  {selectedFile && (
                    <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center">
                        <CheckCircle className="h-5 w-5 text-green-400" />
                        <div className="ml-3">
                          <p className="text-sm font-medium text-green-800">
                            File selected: {selectedFile.name}
                          </p>
                          <p className="text-sm text-green-600">
                            Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                  {bulkError && (
                    <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-center">
                        <AlertCircle className="h-5 w-5 text-red-400" />
                        <div className="ml-3">
                          <p className="text-sm font-medium text-red-800">
                            {bulkError}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                  </div>
                )}

                {/* Step 2: Preview and Field Mapping */}
                {bulkStep === 2 && previewData && (
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-3">Field Mapping</h4>
                      <p className="text-sm text-gray-600 mb-4">
                        Map your file columns to the required DuxSoup account fields:
                      </p>
                      
                      <div className="space-y-3">
                        {requiredFields.map(field => (
                          <div key={field.key} className="flex items-center space-x-3">
                            <div className="w-1/3">
                              <label className="block text-sm font-medium text-gray-700">
                                {field.label}
                                {field.required && <span className="text-red-500 ml-1">*</span>}
                              </label>
                            </div>
                            <div className="w-2/3">
                              <select
                                value={fieldMapping[field.key] || ''}
                                onChange={(e) => setFieldMapping(prev => ({
                                  ...prev,
                                  [field.key]: e.target.value
                                }))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              >
                                <option value="">Select column...</option>
                                {previewData.columns?.map(column => (
                                  <option key={column} value={column}>
                                    {column}
                                  </option>
                                ))}
                              </select>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-3">Data Preview</h4>
                      <div className="max-h-40 overflow-y-auto border border-gray-200 rounded-lg">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              {previewData.columns?.slice(0, 5).map(column => (
                                <th key={column} className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                  {column}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {previewData.sample_data?.slice(0, 3).map((row, index) => (
                              <tr key={index}>
                                {previewData.columns?.slice(0, 5).map(column => (
                                  <td key={column} className="px-3 py-2 text-sm text-gray-900">
                                    {row[column] || '-'}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">
                        Showing first 3 rows of {previewData.total_rows || 0} total rows
                      </p>
                    </div>
                  </div>
                )}

                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex">
                    <AlertCircle className="h-5 w-5 text-blue-400" />
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-blue-800">File Requirements</h3>
                      <div className="mt-2 text-sm text-blue-700">
                        <p className="mb-2">Your file must include these columns:</p>
                        <ul className="list-disc list-inside mb-2">
                          <li><code>dux_soup_user_id</code> - DuxSoup user ID</li>
                          <li><code>dux_soup_auth_key</code> - DuxSoup authentication key</li>
                          <li><code>email</code> - User email address</li>
                          <li><code>first_name</code> - User's first name</li>
                          <li><code>last_name</code> - User's last name</li>
                        </ul>
                        <p className="text-xs">
                          💡 <strong>Tip:</strong> You can export from Excel/Google Sheets as CSV, or use the template below.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Modal Actions */}
                <div className="flex items-center justify-between mt-6">
                  <div className="flex space-x-3">
                    <button
                      onClick={downloadTemplate}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                    >
                      Download Template
                    </button>
                    {bulkStep === 2 && (
                      <button
                        onClick={() => setBulkStep(1)}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                      >
                        Back
                      </button>
                    )}
                  </div>
                  
                  <div className="flex space-x-3">
                    <button
                      onClick={() => {
                        setShowBulkModal(false);
                        setBulkStep(1);
                        setSelectedFile(null);
                        setPreviewData(null);
                        setFieldMapping({});
                        if (fileInputRef.current) {
                          fileInputRef.current.value = '';
                        }
                      }}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                    >
                      Cancel
                    </button>
                    
                    {bulkStep === 1 ? (
                      <button
                        onClick={handlePreview}
                        disabled={!selectedFile || bulkLoading}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {bulkLoading ? 'Previewing...' : 'Preview & Map Fields'}
                      </button>
                    ) : (
                      <button
                        onClick={handleBulkImport}
                        disabled={bulkLoading || !Object.values(fieldMapping).some(v => v)}
                        className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {bulkLoading ? 'Importing...' : 'Import Accounts'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DuxSoupAccounts;


