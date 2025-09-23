import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronDown, Building2, Users, BarChart3, Activity } from 'lucide-react';
import { logMockData } from '../utils/mockDataLogger';

const ClientSwitcher = ({ onClientSwitch, currentClient }) => {
  const navigate = useNavigate();
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      // Log mock data usage
      logMockData('ClientSwitcher', 'client_list', {
        reason: 'ALWAYS_MOCK',
        note: 'No API endpoint exists yet'
      });
      
      // Mock data for demo purposes
      const mockClients = [
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
      ];
      
      setClients(mockClients);
      // Set first client as default if none selected
      if (!currentClient && mockClients.length > 0) {
        onClientSwitch(mockClients[0]);
      }
    } catch (error) {
      console.error('Error fetching clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClientSelect = async (client) => {
    try {
      // Switch the client data
      onClientSwitch(client);
      setIsOpen(false);
      
      // Navigate to the dashboard to show the selected client's data
      navigate('/');
    } catch (error) {
      console.error('Error switching client:', error);
    }
  };

  if (loading) {
    return (
      <div className="client-switcher">
        <div className="client-select-skeleton">
          <div className="skeleton-line w-48 h-8"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="client-switcher relative">
      <div className="flex items-center space-x-3">
        <Building2 className="h-5 w-5 text-gray-600" />
        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-w-[200px]"
          >
            <div className="flex-1 text-left">
              {currentClient ? (
                <div>
                  <div className="font-medium text-gray-900">{currentClient.name}</div>
                  <div className="text-sm text-gray-500">
                    {currentClient.stats?.dux_accounts || 0} DuxSoup accounts
                  </div>
                </div>
              ) : (
                <div className="text-gray-500">Select Client</div>
              )}
            </div>
            <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>

          {isOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
              {clients.length === 0 ? (
                <div className="px-4 py-3 text-gray-500 text-center">
                  No clients available
                </div>
              ) : (
                clients.map((client) => (
                  <button
                    key={client.id}
                    onClick={() => handleClientSelect(client)}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                      currentClient?.id === client.id ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{client.name}</div>
                        <div className="text-sm text-gray-500">{client.domain}</div>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Users className="h-3 w-3" />
                          <span>{client.stats?.dux_accounts || 0}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <BarChart3 className="h-3 w-3" />
                          <span>{client.stats?.campaigns || 0}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Activity className="h-3 w-3" />
                          <span>{client.stats?.contacts || 0}</span>
                        </div>
                      </div>
                    </div>
                    <div className="mt-1 text-xs text-gray-400">
                      Access: {client.access_level}
                    </div>
                  </button>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Client Info Display */}
      {currentClient && (
        <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
          <div className="flex items-center space-x-1">
            <Users className="h-4 w-4" />
            <span>{currentClient.stats?.dux_accounts || 0} DuxSoup accounts</span>
          </div>
          <div className="flex items-center space-x-1">
            <BarChart3 className="h-4 w-4" />
            <span>{currentClient.stats?.campaigns || 0} campaigns</span>
          </div>
          <div className="flex items-center space-x-1">
            <Activity className="h-4 w-4" />
            <span>{currentClient.stats?.contacts || 0} contacts</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientSwitcher;
