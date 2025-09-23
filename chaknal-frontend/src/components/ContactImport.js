import React, { useState, useRef } from 'react';
import { Upload, CheckCircle, AlertCircle, X, Eye } from 'lucide-react';
import axios from 'axios';

function ContactImport({ campaignId, onImportComplete }) {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState(1); // 1: Upload, 2: Preview, 3: Assign, 4: Complete
  const [selectedFile, setSelectedFile] = useState(null);
  const [dataSource, setDataSource] = useState('duxsoup');
  const [previewData, setPreviewData] = useState(null);
  const [fieldMapping, setFieldMapping] = useState({});
  const [assignToTeam, setAssignToTeam] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const dataSources = [
    { value: 'duxsoup', label: 'DuxSoup Scan', description: 'LinkedIn profile data from DuxSoup' },
    { value: 'zoominfo', label: 'ZoomInfo', description: 'B2B contact database export' },
    { value: 'apollo', label: 'Apollo', description: 'Sales intelligence platform export' },
    { value: 'custom', label: 'Custom CSV/Excel', description: 'Any CSV or Excel file' }
  ];

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDragEnter = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(false);
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      // Validate file type
      const allowedTypes = [
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ];
      
      if (allowedTypes.includes(file.type) || file.name.endsWith('.csv') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        setSelectedFile(file);
        setError(null);
      } else {
        setError('Please upload a CSV or Excel file');
      }
    }
  };

  const handlePreview = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('source', dataSource);
      if (Object.keys(fieldMapping).length > 0) {
        formData.append('field_mapping', JSON.stringify(fieldMapping));
      }

      const response = await axios.post(
        `/api/campaigns/${campaignId}/contacts/import/preview`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setPreviewData(response.data);
      
      // Auto-map common field names
      const autoMapping = {};
      if (response.data.available_fields) {
        const fields = response.data.available_fields;
        
        // Common mappings
        const mappings = {
          'first_name': ['first name', 'firstname', 'fname', 'given name'],
          'last_name': ['last name', 'lastname', 'lname', 'surname', 'family name'],
          'email': ['email', 'email address', 'e-mail'],
          'company_name': ['company', 'company name', 'organization', 'org', 'employer'],
          'job_title': ['title', 'job title', 'position', 'role', 'designation'],
          'linkedin_url': ['linkedin', 'linkedin url', 'linkedin profile', 'profile', 'linkedin profile url'],
          'phone': ['phone', 'phone number', 'telephone', 'mobile', 'cell'],
          'location': ['location', 'city', 'address', 'country', 'state']
        };
        
        Object.keys(mappings).forEach(targetField => {
          const possibleNames = mappings[targetField];
          const matchedField = fields.find(field => 
            possibleNames.some(name => 
              field.toLowerCase().replace(/[_\s-]/g, '') === name.replace(/[_\s-]/g, '')
            )
          );
          if (matchedField) {
            autoMapping[targetField] = matchedField;
          }
        });
      }
      
      setFieldMapping(autoMapping);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to preview file');
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('source', dataSource);
      formData.append('assign_to_team', assignToTeam);
      if (Object.keys(fieldMapping).length > 0) {
        formData.append('field_mapping', JSON.stringify(fieldMapping));
      }

      const response = await axios.post(
        `/api/campaigns/${campaignId}/contacts/import`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setImportResult(response.data);
      setStep(4);
      
      if (onImportComplete) {
        onImportComplete(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to import contacts');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setStep(1);
    setSelectedFile(null);
    setPreviewData(null);
    setFieldMapping({});
    setImportResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const closeModal = () => {
    setIsOpen(false);
    resetForm();
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
      >
        <Upload className="h-4 w-4" />
        Import Contacts
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Import Contacts</h2>
              <button
                onClick={closeModal}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Step 1: File Upload */}
            {step === 1 && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data Source
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    {dataSources.map((source) => (
                      <div
                        key={source.value}
                        className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                          dataSource === source.value
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setDataSource(source.value)}
                      >
                        <div className="font-medium">{source.label}</div>
                        <div className="text-sm text-gray-600">{source.description}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload File
                  </label>
                  <div
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
                      isDragOver 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    onClick={() => fileInputRef.current?.click()}
                    onDragOver={handleDragOver}
                    onDragEnter={handleDragEnter}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                  >
                    <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-lg font-medium text-gray-700">
                      {selectedFile ? selectedFile.name : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      CSV or Excel files only
                    </p>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".csv,.xlsx,.xls"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                  </div>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-red-500" />
                    <span className="text-red-700">{error}</span>
                  </div>
                )}

                <div className="flex justify-end gap-3">
                  <button
                    onClick={closeModal}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handlePreview}
                    disabled={!selectedFile || loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                    Preview Import
                  </button>
                </div>
              </div>
            )}

            {/* Step 2: Preview */}
            {step === 2 && previewData && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-medium text-blue-900 mb-2">Import Preview</h3>
                  <p className="text-blue-700">
                    Found {previewData.total_rows} contacts. Here's a preview of the first 10:
                  </p>
                </div>



                <div className="overflow-x-auto">
                  <table className="min-w-full bg-white border border-gray-200 rounded-lg">
                    <thead className="bg-gray-50">
                      <tr>
                        {previewData.preview && previewData.preview.length > 0 ? (
                          Object.keys(previewData.preview[0] || {}).map((field) => (
                            <th key={field} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              {field.replace(/_/g, ' ')}
                            </th>
                          ))
                        ) : (
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            No data available
                          </th>
                        )}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {previewData.preview && previewData.preview.length > 0 ? (
                        previewData.preview.map((row, index) => (
                          <tr key={index}>
                            {Object.values(row).map((value, cellIndex) => (
                              <td key={cellIndex} className="px-4 py-3 text-sm text-gray-900">
                                {value || '-'}
                              </td>
                            ))}
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={previewData.available_fields?.length || 1} className="px-4 py-8 text-center text-gray-500">
                            No preview data available - Preview length: {previewData.preview?.length || 0}
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Field Mapping Section */}
                {previewData.available_fields && previewData.available_fields.length > 0 && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-3">Map CSV Columns to Contact Fields</h4>
                    <div className="space-y-3">
                      {[
                        { key: 'first_name', label: 'First Name', required: true },
                        { key: 'last_name', label: 'Last Name', required: true },
                        { key: 'email', label: 'Email', required: false },
                        { key: 'company_name', label: 'Company', required: false },
                        { key: 'job_title', label: 'Job Title', required: false },
                        { key: 'linkedin_url', label: 'LinkedIn URL', required: false },
                        { key: 'phone', label: 'Phone', required: false },
                        { key: 'location', label: 'Location', required: false }
                      ].map((field) => (
                        <div key={field.key} className="flex items-center gap-3">
                          <div className="w-32 text-sm font-medium text-gray-700">
                            {field.label}
                            {field.required && <span className="text-red-500 ml-1">*</span>}
                          </div>
                          <div className="flex-1">
                            <select
                              value={fieldMapping[field.key] || ''}
                              onChange={(e) => setFieldMapping(prev => ({
                                ...prev,
                                [field.key]: e.target.value
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                              <option value="">Select CSV column...</option>
                              {previewData.available_fields.map((csvField) => (
                                <option key={csvField} value={csvField}>
                                  {csvField}
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-3">
                      * Required fields. LinkedIn URL is recommended for contact matching.
                    </p>
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="assignToTeam"
                    checked={assignToTeam}
                    onChange={(e) => setAssignToTeam(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="assignToTeam" className="text-sm text-gray-700">
                    Automatically assign contacts to team members
                  </label>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-red-500" />
                    <span className="text-red-700">{error}</span>
                  </div>
                )}

                <div className="flex justify-end gap-3">
                  <button
                    onClick={() => setStep(1)}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Back
                  </button>
                  <button
                    onClick={handleImport}
                    disabled={loading}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {loading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <CheckCircle className="h-4 w-4" />
                    )}
                    Import {previewData.total_rows} Contacts
                  </button>
                </div>
              </div>
            )}

            {/* Step 4: Complete */}
            {step === 4 && importResult && (
              <div className="space-y-6">
                <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                  <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-green-900 mb-2">
                    Import Complete!
                  </h3>
                  <p className="text-green-700">
                    Successfully imported {importResult.total_processed} contacts
                  </p>
                  {importResult.errors.length > 0 && (
                    <p className="text-yellow-700 mt-2">
                      {importResult.errors.length} contacts had errors and were skipped
                    </p>
                  )}
                </div>

                {importResult.errors.length > 0 && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h4 className="font-medium text-yellow-900 mb-2">Import Errors:</h4>
                    <ul className="text-sm text-yellow-700 space-y-1">
                      {importResult.errors.slice(0, 10).map((error, index) => (
                        <li key={index}>• {error}</li>
                      ))}
                      {importResult.errors.length > 10 && (
                        <li>• ... and {importResult.errors.length - 10} more errors</li>
                      )}
                    </ul>
                  </div>
                )}

                <div className="flex justify-end gap-3">
                  <button
                    onClick={closeModal}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Done
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

export default ContactImport;
