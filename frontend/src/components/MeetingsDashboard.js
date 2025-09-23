import React, { useState, useEffect } from 'react';
import { Calendar, Clock, User, Building, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

function MeetingsDashboard({ currentClient, isAgency }) {
  const [meetingsData, setMeetingsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMeetingsData();
  }, [currentClient]);

  const loadMeetingsData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.get('http://localhost:8000/api/meetings/dashboard');
      
      if (response.data.success) {
        setMeetingsData(response.data.data);
      } else {
        setError('Failed to load meetings data');
      }
    } catch (err) {
      setError('Failed to load meetings data');
      console.error('Error loading meetings:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Not scheduled';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'cancelled':
      case 'no_show':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'scheduled':
      case 'confirmed':
        return <Clock className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
      case 'no_show':
        return 'bg-red-100 text-red-800';
      case 'scheduled':
      case 'confirmed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isAgency && currentClient ? `${currentClient.name} Meetings` : 'Meetings'}
          </h1>
          <p className="mt-1 text-sm text-gray-500">Loading meetings...</p>
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
          <h1 className="text-2xl font-bold text-gray-900">Meetings</h1>
          <p className="mt-1 text-sm text-gray-500">Manage your scheduled meetings</p>
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
          {isAgency && currentClient ? `${currentClient.name} Meetings` : 'Meetings'}
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {isAgency && currentClient 
            ? `Manage ${currentClient.name}'s scheduled meetings and outcomes`
            : 'Manage your scheduled meetings and outcomes'
          }
        </p>
      </div>

      {/* Stats Cards */}
      {meetingsData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Calendar className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Meetings (7d)</dt>
                    <dd className="text-lg font-medium text-gray-900">{meetingsData.stats.total_meetings_7d}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Completed</dt>
                    <dd className="text-lg font-medium text-gray-900">{meetingsData.stats.completed_meetings_7d}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Clock className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Scheduled</dt>
                    <dd className="text-lg font-medium text-gray-900">{meetingsData.stats.scheduled_meetings}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <User className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Conversion Rate</dt>
                    <dd className="text-lg font-medium text-gray-900">{meetingsData.stats.conversion_rate.toFixed(1)}%</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Meetings */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Upcoming Meetings
            </h3>
            
            {meetingsData && meetingsData.upcoming_meetings.length === 0 ? (
              <div className="text-center py-8">
                <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No upcoming meetings</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Book meetings through the Messages interface.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {meetingsData && meetingsData.upcoming_meetings.map((meeting) => (
                  <div
                    key={meeting.meeting_id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="text-sm font-medium text-gray-900">
                            {meeting.contact_name}
                          </h4>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(meeting.meeting_status)}`}>
                            {getStatusIcon(meeting.meeting_status)}
                            <span className="ml-1">{meeting.meeting_status}</span>
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {meeting.contact_company} • {meeting.meeting_type}
                        </p>
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                          <span>📅 {formatDateTime(meeting.scheduled_date)}</span>
                          <span>⏱️ {meeting.duration_minutes} min</span>
                        </div>
                        {meeting.agenda && (
                          <p className="text-xs text-gray-600 mt-2">
                            Agenda: {meeting.agenda}
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

        {/* Recent Meetings */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Recent Meetings
            </h3>
            
            {meetingsData && meetingsData.recent_meetings.length === 0 ? (
              <div className="text-center py-8">
                <CheckCircle className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No recent meetings</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Completed meetings will appear here.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {meetingsData && meetingsData.recent_meetings.map((meeting) => (
                  <div
                    key={meeting.meeting_id}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="text-sm font-medium text-gray-900">
                            {meeting.contact_name}
                          </h4>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(meeting.outcome || 'completed')}`}>
                            {meeting.outcome || 'completed'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {meeting.contact_company} • {meeting.meeting_type}
                        </p>
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                          <span>📅 {formatDateTime(meeting.actual_date)}</span>
                          <span>⏱️ {meeting.duration_minutes} min</span>
                        </div>
                        {meeting.outcome_notes && (
                          <p className="text-xs text-gray-600 mt-2">
                            Notes: {meeting.outcome_notes}
                          </p>
                        )}
                        {meeting.next_action && (
                          <p className="text-xs text-blue-600 mt-1">
                            Next: {meeting.next_action}
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

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Calendar className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              Meeting Management
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                Book meetings directly from conversations in the Messages interface. 
                When a contact agrees to a meeting, use the "Book Meeting" button to track it here.
              </p>
              <p className="mt-2">
                <strong>Workflow:</strong> Messages → Contact agrees → Book Meeting → Track outcome → Set follow-up
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MeetingsDashboard;
