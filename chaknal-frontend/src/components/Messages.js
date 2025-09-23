import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, Inbox, Archive, User, Building, Clock, ChevronRight, UserPlus, Calendar, XCircle } from 'lucide-react';
import axios from 'axios';
import { logMockData } from '../utils/mockDataLogger';

function Messages({ currentClient, isAgency }) {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [connections, setConnections] = useState([]);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [sendingReply, setSendingReply] = useState(false);
  const [showNewConversation, setShowNewConversation] = useState(false);
  const [showBookMeeting, setShowBookMeeting] = useState(false);
  const [meetingData, setMeetingData] = useState({
    meeting_type: 'call',
    scheduled_date: '',
    duration_minutes: 30,
    agenda: ''
  });

  useEffect(() => {
    if (isAgency && currentClient) {
      fetchClientUsers();
    } else {
      fetchUsers();
    }
  }, [currentClient, isAgency]);

  const fetchClientUsers = async () => {
    try {
      setLoading(true);
      
      // Log mock data usage
      logMockData('Messages', 'client_users', {
        reason: 'CLIENT_SPECIFIC',
        client: currentClient?.name,
        note: 'Client-specific user list'
      });
      
      // Generate mock users for the selected client
      const mockUsers = generateClientUsers(currentClient);
      setUsers(mockUsers);
    } catch (err) {
      setError('Failed to load users');
      console.error('Error fetching client users:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      
      // Log mock data usage
      logMockData('Messages', 'default_users', {
        reason: 'NON_AGENCY_MODE',
        note: 'Default user list for non-agency mode'
      });
      
      // Generate mock users for non-agency mode
      const mockUsers = [
        { id: 1, name: 'John Smith', email: 'john.smith@company.com', role: 'Sales Manager' },
        { id: 2, name: 'Sarah Johnson', email: 'sarah.johnson@company.com', role: 'Marketing Director' },
        { id: 3, name: 'Michael Davis', email: 'michael.davis@company.com', role: 'VP Sales' }
      ];
      setUsers(mockUsers);
    } catch (err) {
      setError('Failed to load users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateClientUsers = (client) => {
    const users = [];
    
    // ALWAYS add Sercio Campos as first user for Marketing Masters
    if (client && (client.name === 'Marketing Masters' || client.name.includes('Marketing'))) {
      users.push({
        id: 1,
        name: 'Sercio Campos',
        email: 'scampos@wallarm.com',
        role: 'Security Engineer',
        client_id: client.id,
        isRealUser: true
      });
      
      console.log('✅ Added Sercio Campos to Marketing Masters users');
    }
    
    // Generate additional mock users (always include some standard users)
    const standardUsers = [
      { firstName: 'John', lastName: 'Smith', role: 'Sales Manager' },
      { firstName: 'Sarah', lastName: 'Johnson', role: 'Marketing Director' },
      { firstName: 'Michael', lastName: 'Davis', role: 'VP Sales' }
    ];
    
    standardUsers.forEach((userData, i) => {
      users.push({
        id: users.length + 1,
        name: `${userData.firstName} ${userData.lastName}`,
        email: `${userData.firstName.toLowerCase()}.${userData.lastName.toLowerCase()}@${client.domain}`,
        role: userData.role,
        client_id: client.id,
        isRealUser: false
      });
    });
    
    console.log('✅ Generated', users.length, 'users for', client.name, ':', users.map(u => u.name));
    return users;
  };

  const fetchUserConnections = async (userId) => {
    try {
      setLoading(true);
      
      // Log mock data usage
      logMockData('Messages', 'user_connections', {
        reason: 'ALWAYS_MOCK',
        userId: userId,
        note: 'First-degree LinkedIn connections'
      });
      
      // Generate mock first-degree connections for the selected user
      const mockConnections = generateUserConnections(userId);
      setConnections(mockConnections);
    } catch (err) {
      setError('Failed to load connections');
      console.error('Error fetching connections:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateUserConnections = (userId) => {
    const connections = [];
    
    // ALWAYS add Sergio as EXISTING first-degree connection for Marketing Masters
    if (isAgency && currentClient && currentClient.name === 'Marketing Masters') {
      connections.push({
        id: 1,
        name: 'Sergio Campos',
        company: 'Wallarm', 
        title: 'Security Professional',
        linkedin_url: 'https://www.linkedin.com/in/sergio-campos-97b9b7362/',
        profile_image: 'https://ui-avatars.com/api/?name=Sergio+Campos&background=ff6600&color=fff',
        connection_date: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(), // Connected 45 days ago
        has_conversation: true, // ALREADY HAS CONVERSATION - they're connected
        sequence_id: 1,
        sequence_name: 'Professional Outreach',
        isRealTarget: true,
        email: 'sergio.campos@example.com' // LinkedIn profile owner
      });
    }
    
    // Generate additional mock connections
    const connectionCount = Math.floor(Math.random() * 15) + 8; // 8-23 additional connections
    const firstNames = ['Alex', 'Maria', 'James', 'Jennifer', 'Robert', 'Lisa', 'David', 'Sarah', 'Chris', 'Amanda'];
    const lastNames = ['Garcia', 'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson'];
    const companies = ['Microsoft', 'Google', 'Apple', 'Amazon', 'Meta', 'Netflix', 'Tesla', 'Uber', 'Airbnb', 'Spotify'];
    const titles = ['Software Engineer', 'Product Manager', 'Designer', 'Data Scientist', 'Marketing Manager', 'Sales Director', 'CEO', 'CTO', 'VP Engineering', 'Business Analyst'];
    
    for (let i = 0; i < connectionCount; i++) {
      const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
      const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
      const company = companies[Math.floor(Math.random() * companies.length)];
      const title = titles[Math.floor(Math.random() * titles.length)];
      
      connections.push({
        id: connections.length + 1,
        name: `${firstName} ${lastName}`,
        company: company,
        title: title,
        linkedin_url: `https://linkedin.com/in/${firstName.toLowerCase()}-${lastName.toLowerCase()}-${Math.random().toString(36).substr(2, 9)}`,
        profile_image: `https://ui-avatars.com/api/?name=${firstName}+${lastName}&background=random`,
        connection_date: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
        has_conversation: Math.random() > 0.7, // 30% chance of having a conversation
        sequence_id: Math.random() > 0.5 ? Math.floor(Math.random() * 2) + 1 : null,
        sequence_name: Math.random() > 0.5 ? ['Q4 Lead Generation', 'Executive Outreach'][Math.floor(Math.random() * 2)] : null,
        isRealUser: false
      });
    }
    
    return connections;
  };

  const handleUserSelect = (user) => {
    setSelectedUser(user);
    setSelectedConnection(null);
    setSelectedConversation(null);
    setMessages([]);
    fetchUserConnections(user.id);
  };

  const handleConnectionSelect = (connection) => {
    setSelectedConnection(connection);
    if (connection.has_conversation) {
      // Generate mock conversation data
      const conversation = {
        id: connection.id,
        contact_id: connection.id,
        contact_name: connection.name,
        contact_company: connection.company,
        contact_title: connection.title,
        sequence_id: connection.sequence_id,
        sequence_name: connection.sequence_name,
        last_message: "Thanks for connecting! I'd love to discuss how we can help your team...",
        last_message_time: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        unread_count: Math.floor(Math.random() * 3)
      };
      setSelectedConversation(conversation);
      loadRealConversation(connection);
    } else {
      setSelectedConversation(null);
      setMessages([]);
    }
  };

  const loadRealConversation = async (connection) => {
    try {
      // Load real conversation history for Sergio Campos
      if (connection.isRealTarget && connection.name === 'Sergio Campos') {
        const response = await axios.get('http://localhost:8000/api/real-conversation/sergio-sercio');
        
        if (response.data.success && response.data.data.messages.length > 0) {
          console.log('✅ Loaded real conversation history from database:', response.data.data.messages.length, 'messages');
          setMessages(response.data.data.messages);
          return;
        } else {
          console.log('⚠️ No real conversation history found, using mock data');
        }
      }
      
      // Fallback to mock conversation for other connections
      generateMockMessages(connection);
      
    } catch (error) {
      console.error('❌ Failed to load real conversation, using mock data:', error);
      generateMockMessages(connection);
    }
  };

  const generateMockMessages = (connection) => {
    // Log mock data usage
    logMockData('Messages', 'conversation_history', {
      reason: 'MOCK_CONVERSATION',
      connection: connection.name,
      note: 'Generated conversation history'
    });
    
    const messages = [];
    
    // Special conversation for Sergio Campos (real target) - fallback if database fails
    if (connection.isRealTarget && connection.name === 'Sergio Campos') {
      const conversationHistory = [
        {
          id: 1,
          sender: 'user',
          sender_name: selectedUser.name,
          content: "Hi Sergio! Thanks for connecting. I'm Sercio from Wallarm. I'd love to learn more about your work and discuss potential collaboration opportunities.",
          timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days ago
          sequence_step: 'initial_outreach'
        },
        {
          id: 2,
          sender: 'contact',
          sender_name: connection.name,
          content: "Hi Sercio! Nice to connect with you. I'm always interested in discussing security and collaboration opportunities. What kind of work are you doing at Wallarm?",
          timestamp: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(), // 6 days ago
          sequence_step: null
        },
        {
          id: 3,
          sender: 'user',
          sender_name: selectedUser.name,
          content: "Great to hear from you! At Wallarm, I focus on application security and API protection. I noticed your LinkedIn profile and thought there might be some interesting synergies between our work. Would you be open to a brief call this week?",
          timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
          sequence_step: 'follow_up_1'
        },
        {
          id: 4,
          sender: 'contact',
          sender_name: connection.name,
          content: "That sounds really interesting! I'd definitely be open to learning more about what you're working on. How about we schedule something for later this week?",
          timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
          sequence_step: null
        }
      ];
      
      setMessages(conversationHistory);
      return;
    }
    
    // Generate regular mock messages for other connections
    const messageCount = Math.floor(Math.random() * 5) + 2; // 2-6 messages
    
    for (let i = 0; i < messageCount; i++) {
      const isFromUser = i % 2 === 0;
      const messageTexts = [
        "Hi! Thanks for connecting. I'd love to learn more about your role at " + connection.company + ".",
        "I noticed your experience in " + connection.title + ". Would you be open to a brief call this week?",
        "I have some ideas that might be relevant to your team. Worth a quick chat?",
        "Thanks for your time! I'll follow up with more details.",
        "Looking forward to our conversation!"
      ];
      
      messages.push({
        id: i + 1,
        sender: isFromUser ? 'user' : 'contact',
        sender_name: isFromUser ? selectedUser.name : connection.name,
        content: messageTexts[i % messageTexts.length],
        timestamp: new Date(Date.now() - (messageCount - i) * 24 * 60 * 60 * 1000).toISOString(),
        sequence_step: isFromUser ? (i === 0 ? 'initial' : `follow_up_${i}`) : null
      });
    }
    
    setMessages(messages);
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInHours < 168) {
      return `${Math.floor(diffInHours / 24)}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const handleSendConnectionRequest = async (connection) => {
    try {
      let connectionMessage;
      
      if (selectedUser && selectedUser.name === 'Sercio Campos' && connection.isRealTarget) {
        connectionMessage = `Hi Sergio! I'm Sercio from Wallarm. I'd love to connect and discuss potential collaboration opportunities. Looking forward to hearing from you!`;
      } else if (connection.isRealTarget && connection.name === 'Sergio Campos') {
        connectionMessage = `Hi Sergio! I'd love to connect and discuss potential opportunities. Looking forward to hearing from you!`;
      } else {
        connectionMessage = `Hi ${connection.name.split(' ')[0]}! I'd like to connect with you.`;
      }
      
      const response = await axios.post('http://localhost:8000/api/duxwrap-test/connect', {
        profile_url: connection.linkedin_url,
        message: connectionMessage
      });

      if (response.data.success) {
        console.log('✅ Connection request queued successfully:', response.data.data);
        
        if (connection.isRealTarget) {
          alert(`🚀 REAL connection request sent from ${selectedUser.name} to ${connection.name}!\n\nFrom: ${selectedUser.email}\nTo LinkedIn: ${connection.linkedin_url}\nDuxSoup Message ID: ${response.data.data.message_id}\n\nMessage: "${connectionMessage}"`);
        } else {
          alert(`Connection request sent to ${connection.name}!`);
        }
        
        // Update the connection to show it has a conversation now
        const updatedConnections = connections.map(conn => 
          conn.id === connection.id 
            ? { ...conn, has_conversation: true, sequence_name: connection.isRealTarget ? 'Sercio → Sergio Outreach' : 'Manual Connection' }
            : conn
        );
        setConnections(updatedConnections);
      } else {
        throw new Error('Failed to queue connection request');
      }
    } catch (error) {
      console.error('❌ Error sending connection request:', error);
      alert('Failed to send connection request. Please try again.');
    }
  };

  const handleSendReply = async () => {
    if (!replyText.trim() || !selectedConversation || !selectedConnection) return;

    setSendingReply(true);
    try {
      // Send real message through DuxWrap API
      const response = await axios.post('http://localhost:8000/api/duxwrap-test/message', {
        profile_url: selectedConnection.linkedin_url,
        message: replyText
      });

      if (response.data.success) {
        // Store message in database if it's to Sergio (real target)
        if (selectedConnection.isRealTarget && selectedConnection.name === 'Sergio Campos') {
          try {
            await axios.post('http://localhost:8000/api/real-conversation/add-message', null, {
              params: {
                message_text: replyText,
                direction: 'sent'
              }
            });
            console.log('✅ Message stored in database');
            
            // Reload real conversation to show the new message
            await loadRealConversation(selectedConnection);
          } catch (dbError) {
            console.error('⚠️ Failed to store message in database:', dbError);
            // Still show the message in UI even if database storage fails
            const newMessage = {
              id: Date.now(),
              sender: 'user',
              sender_name: selectedUser.name,
              content: replyText,
              timestamp: new Date().toISOString(),
              sequence_step: 'real_user_message',
              dux_message_id: response.data.data.message_id,
              status: 'queued'
            };
            setMessages(prev => [...prev, newMessage]);
          }
        } else {
          // Add message to UI for non-real targets
          const newMessage = {
            id: Date.now(),
            sender: 'user',
            sender_name: selectedUser.name,
            content: replyText,
            timestamp: new Date().toISOString(),
            sequence_step: 'manual_reply',
            dux_message_id: response.data.data.message_id,
            status: 'queued'
          };
          setMessages(prev => [...prev, newMessage]);
        }
        
        setReplyText('');
        
        // Show success notification
        if (selectedConnection.isRealTarget) {
          console.log('🚀 REAL MESSAGE queued successfully from', selectedUser.name, 'to', selectedConnection.name, ':', response.data.data);
          alert(`🚀 REAL message sent from ${selectedUser.name} to ${selectedConnection.name}!\n\nFrom: ${selectedUser.email}\nTo LinkedIn: ${selectedConnection.linkedin_url}\nMessage: "${replyText}"\nDuxSoup Message ID: ${response.data.data.message_id}\n\n✅ Stored in database for conversation history!`);
        } else {
          console.log('✅ Message queued successfully:', response.data.data);
        }
      } else {
        throw new Error('Failed to queue message');
      }
    } catch (error) {
      console.error('❌ Error sending message:', error);
      // Show error notification
      alert('Failed to send message. Please try again.');
    } finally {
      setSendingReply(false);
    }
  };

  const handleBookMeeting = async () => {
    if (!selectedConnection || !meetingData.scheduled_date) return;

    try {
      const response = await axios.post('http://localhost:8000/api/meetings/book', {
        contact_linkedin_url: selectedConnection.linkedin_url,
        meeting_type: meetingData.meeting_type,
        scheduled_date: meetingData.scheduled_date,
        duration_minutes: meetingData.duration_minutes,
        agenda: meetingData.agenda,
        booking_notes: `Meeting booked from conversation with ${selectedConnection.name}`,
        booking_message_id: null // Could link to specific message later
      });

      if (response.data.success) {
        alert(`✅ Meeting booked with ${selectedConnection.name}!\n\nType: ${meetingData.meeting_type}\nDate: ${new Date(meetingData.scheduled_date).toLocaleString()}\nDuration: ${meetingData.duration_minutes} minutes`);
        setShowBookMeeting(false);
        setMeetingData({
          meeting_type: 'call',
          scheduled_date: '',
          duration_minutes: 30,
          agenda: ''
        });
      } else {
        alert('Failed to book meeting. Please try again.');
      }
    } catch (error) {
      console.error('Error booking meeting:', error);
      alert('Failed to book meeting. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
          <p className="mt-1 text-sm text-gray-500">
            View and manage your LinkedIn messages
          </p>
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

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
          <p className="mt-1 text-sm text-gray-500">
            View and manage your LinkedIn messages
          </p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-center text-red-600">
            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          {isAgency && currentClient ? `${currentClient.name} Messages` : 'Messages'}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {isAgency && currentClient 
            ? `Manage ${currentClient.name}'s LinkedIn conversations`
            : 'View and manage your LinkedIn conversations'
          }
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* User Selection */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Select User
              </h3>
              {users.length === 0 ? (
                <div className="text-center py-8">
                  <User className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No users available</h3>
                </div>
              ) : (
                <div className="space-y-2">
                  {users.map((user) => (
                    <div
                      key={user.id}
                      onClick={() => handleUserSelect(user)}
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        selectedUser?.id === user.id
                          ? 'bg-blue-50 border border-blue-200'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                    <div className="flex items-center space-x-3">
                      <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
                        <User className="h-4 w-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {user.name}
                          </p>
                          {user.isRealUser && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              🎯 Real User
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 truncate">
                          {user.role}
                        </p>
                        {user.isRealUser && user.email && (
                          <p className="text-xs text-blue-600 truncate">
                            {user.email}
                          </p>
                        )}
                      </div>
                    </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Connections List */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                {selectedUser ? `${selectedUser.name}'s Connections` : 'Connections'}
              </h3>
              {!selectedUser ? (
                <div className="text-center py-8">
                  <User className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Select a user first</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Choose a user to see their connections.
                  </p>
                </div>
              ) : connections.length === 0 ? (
                <div className="text-center py-8">
                  <User className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No connections</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    This user has no LinkedIn connections.
                  </p>
                </div>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {connections.map((connection) => (
                    <div
                      key={connection.id}
                      onClick={() => handleConnectionSelect(connection)}
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        selectedConnection?.id === connection.id
                          ? 'bg-blue-50 border border-blue-200'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <img
                          src={connection.profile_image}
                          alt={connection.name}
                          className="h-8 w-8 rounded-full"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {connection.name}
                            </p>
                            {connection.isRealTarget && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                                🎯 Real Target
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-500 truncate">
                            {connection.title} at {connection.company}
                          </p>
                          {connection.isRealTarget && connection.email && (
                            <p className="text-xs text-blue-600 truncate">
                              {connection.email}
                            </p>
                          )}
                          {connection.has_conversation ? (
                            <div className="flex items-center mt-1">
                              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                              <span className="text-xs text-green-600">Active conversation</span>
                              {connection.sequence_name && (
                                <span className="text-xs text-blue-600 ml-2">
                                  • {connection.sequence_name}
                                </span>
                              )}
                            </div>
                          ) : (
                            <div className="flex items-center justify-between mt-1">
                              <span className="text-xs text-gray-500">No conversation</span>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleSendConnectionRequest(connection);
                                }}
                                className="flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                              >
                                <UserPlus className="h-3 w-3 mr-1" />
                                Connect
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Messages View */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg">
            {selectedConversation ? (
              <div className="flex flex-col h-96">
                {/* Conversation Header */}
                <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <img
                        src={selectedConnection?.profile_image}
                        alt={selectedConversation.contact_name}
                        className="h-8 w-8 rounded-full"
                      />
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          {selectedConversation.contact_name}
                        </h4>
                        <p className="text-xs text-gray-500">
                          {selectedConversation.contact_company} • {selectedConversation.contact_title}
                        </p>
                        {selectedConversation.sequence_name && (
                          <p className="text-xs text-blue-600">
                            Sequence: {selectedConversation.sequence_name}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {selectedConnection?.isRealTarget && (
                        <button
                          onClick={() => setShowBookMeeting(true)}
                          className="flex items-center px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
                        >
                          <Calendar className="h-3 w-3 mr-1" />
                          Book Meeting
                        </button>
                      )}
                      <button className="text-gray-400 hover:text-gray-600">
                        <Archive className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.sender === 'user'
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <div className="flex items-center justify-between mt-1">
                          <p className={`text-xs ${
                            message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                          }`}>
                            {formatTime(message.timestamp)}
                          </p>
                          {message.sequence_step && (
                            <span className={`text-xs px-2 py-1 rounded ${
                              message.sender === 'user' ? 'bg-blue-400 text-white' : 'bg-gray-200 text-gray-600'
                            }`}>
                              {message.sequence_step}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Reply Input */}
                <div className="px-4 py-3 border-t border-gray-200">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      placeholder="Type your message..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      onKeyPress={(e) => e.key === 'Enter' && handleSendReply()}
                    />
                    <button
                      onClick={handleSendReply}
                      disabled={!replyText.trim() || sendingReply}
                      className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      <Send className="h-4 w-4" />
                      <span>Send</span>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-96">
                <div className="text-center">
                  <MessageSquare className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">
                    {!selectedUser ? 'Select a user first' : 'Select a connection'}
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    {!selectedUser 
                      ? 'Choose a user to see their connections and start conversations.'
                      : 'Choose a connection from the list to view messages.'
                    }
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Book Meeting Modal */}
      {showBookMeeting && selectedConnection && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Book Meeting with {selectedConnection.name}
                </h3>
                <button
                  onClick={() => setShowBookMeeting(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-5 w-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Meeting Type
                  </label>
                  <select
                    value={meetingData.meeting_type}
                    onChange={(e) => setMeetingData({...meetingData, meeting_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="call">Phone Call</option>
                    <option value="video_call">Video Call</option>
                    <option value="demo">Product Demo</option>
                    <option value="discovery">Discovery Call</option>
                    <option value="presentation">Presentation</option>
                    <option value="due_event">Due Event</option>
                    <option value="field_event">Field Event</option>
                    <option value="webinar">Webinar</option>
                    <option value="meeting">In-Person Meeting</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Scheduled Date & Time
                  </label>
                  <input
                    type="datetime-local"
                    value={meetingData.scheduled_date}
                    onChange={(e) => setMeetingData({...meetingData, scheduled_date: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duration (minutes)
                  </label>
                  <select
                    value={meetingData.duration_minutes}
                    onChange={(e) => setMeetingData({...meetingData, duration_minutes: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={15}>15 minutes</option>
                    <option value={30}>30 minutes</option>
                    <option value={45}>45 minutes</option>
                    <option value={60}>1 hour</option>
                    <option value={90}>1.5 hours</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Agenda / Notes
                  </label>
                  <textarea
                    value={meetingData.agenda}
                    onChange={(e) => setMeetingData({...meetingData, agenda: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="What will you discuss in this meeting?"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowBookMeeting(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  onClick={handleBookMeeting}
                  disabled={!meetingData.scheduled_date}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  <Calendar className="h-4 w-4 mr-2" />
                  Book Meeting
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Messages;