import React, { useState, useEffect } from 'react';
import { Clock, Calendar, Play, Pause, Save } from 'lucide-react';

export const SchedulePlannerTab = ({ config, updateSetting, validationErrors = {} }) => {
  const [schedule, setSchedule] = useState({});
  const [hasChanges, setHasChanges] = useState(false);

  const dayNames = [
    'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
  ];

  useEffect(() => {
    if (config?.settings?.robotscheduleplan) {
      setSchedule(config.settings.robotscheduleplan);
    } else {
      // Default schedule - weekdays 9am to 11pm
      setSchedule({
        "0": [["09:00", "23:00"]], // Sunday
        "1": [["09:00", "23:00"]], // Monday
        "2": [["09:00", "23:00"]], // Tuesday
        "3": [["09:00", "23:00"]], // Wednesday
        "4": [["09:00", "23:00"]], // Thursday
        "5": [["09:00", "23:00"]], // Friday
        "6": []                    // Saturday (off)
      });
    }
  }, [config]);

  const updateDaySchedule = (dayIndex, timeSlots) => {
    const newSchedule = {
      ...schedule,
      [dayIndex]: timeSlots
    };
    setSchedule(newSchedule);
    setHasChanges(true);
  };

  const addTimeSlot = (dayIndex) => {
    const currentSlots = schedule[dayIndex] || [];
    const newSlots = [...currentSlots, ["09:00", "17:00"]];
    updateDaySchedule(dayIndex, newSlots);
  };

  const removeTimeSlot = (dayIndex, slotIndex) => {
    const currentSlots = schedule[dayIndex] || [];
    const newSlots = currentSlots.filter((_, index) => index !== slotIndex);
    updateDaySchedule(dayIndex, newSlots);
  };

  const updateTimeSlot = (dayIndex, slotIndex, timeIndex, value) => {
    const currentSlots = [...(schedule[dayIndex] || [])];
    if (!currentSlots[slotIndex]) {
      currentSlots[slotIndex] = ["09:00", "17:00"];
    }
    currentSlots[slotIndex][timeIndex] = value;
    updateDaySchedule(dayIndex, currentSlots);
  };

  const toggleDayActive = (dayIndex) => {
    const isActive = schedule[dayIndex] && schedule[dayIndex].length > 0;
    if (isActive) {
      updateDaySchedule(dayIndex, []);
    } else {
      updateDaySchedule(dayIndex, [["09:00", "17:00"]]);
    }
  };

  const saveSchedule = () => {
    updateSetting('robotscheduleplan', schedule);
    setHasChanges(false);
  };

  const setPresetSchedule = (preset) => {
    let newSchedule = {};
    
    switch (preset) {
      case 'business_hours':
        // Monday-Friday 9am-5pm
        newSchedule = {
          "0": [], // Sunday off
          "1": [["09:00", "17:00"]], // Monday
          "2": [["09:00", "17:00"]], // Tuesday
          "3": [["09:00", "17:00"]], // Wednesday
          "4": [["09:00", "17:00"]], // Thursday
          "5": [["09:00", "17:00"]], // Friday
          "6": []  // Saturday off
        };
        break;
      case 'extended_hours':
        // Monday-Friday 8am-8pm
        newSchedule = {
          "0": [],
          "1": [["08:00", "20:00"]],
          "2": [["08:00", "20:00"]],
          "3": [["08:00", "20:00"]],
          "4": [["08:00", "20:00"]],
          "5": [["08:00", "20:00"]],
          "6": []
        };
        break;
      case 'always_on':
        // Every day 9am-11pm
        newSchedule = {
          "0": [["09:00", "23:00"]],
          "1": [["09:00", "23:00"]],
          "2": [["09:00", "23:00"]],
          "3": [["09:00", "23:00"]],
          "4": [["09:00", "23:00"]],
          "5": [["09:00", "23:00"]],
          "6": [["09:00", "23:00"]]
        };
        break;
      case 'off':
        // All days off
        newSchedule = {
          "0": [], "1": [], "2": [], "3": [], "4": [], "5": [], "6": []
        };
        break;
    }
    
    setSchedule(newSchedule);
    setHasChanges(true);
  };

  const getTotalHours = () => {
    let totalMinutes = 0;
    Object.values(schedule).forEach(daySlots => {
      daySlots.forEach(([start, end]) => {
        const startMinutes = parseInt(start.split(':')[0]) * 60 + parseInt(start.split(':')[1]);
        const endMinutes = parseInt(end.split(':')[0]) * 60 + parseInt(end.split(':')[1]);
        totalMinutes += endMinutes - startMinutes;
      });
    });
    return (totalMinutes / 60).toFixed(1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h4 className="text-lg font-medium text-gray-900 mb-2">Automation Schedule Planner</h4>
        <p className="text-sm text-gray-600">
          Configure when DuxSoup automation should run throughout the week
        </p>
      </div>

      {/* Schedule Overview */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h5 className="text-sm font-medium text-blue-900">Schedule Overview</h5>
            <p className="text-sm text-blue-700">
              Total automation time: <span className="font-medium">{getTotalHours()} hours/week</span>
            </p>
          </div>
          {hasChanges && (
            <button
              onClick={saveSchedule}
              className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              <Save className="h-4 w-4 mr-2" />
              Save Schedule
            </button>
          )}
        </div>
      </div>

      {/* Preset Schedules */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h5 className="text-sm font-medium text-gray-900 mb-3">Quick Presets</h5>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button
            onClick={() => setPresetSchedule('business_hours')}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Business Hours
            <div className="text-xs text-gray-500">Mon-Fri 9am-5pm</div>
          </button>
          
          <button
            onClick={() => setPresetSchedule('extended_hours')}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Extended Hours
            <div className="text-xs text-gray-500">Mon-Fri 8am-8pm</div>
          </button>
          
          <button
            onClick={() => setPresetSchedule('always_on')}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Always On
            <div className="text-xs text-gray-500">Daily 9am-11pm</div>
          </button>
          
          <button
            onClick={() => setPresetSchedule('off')}
            className="px-3 py-2 text-sm border border-red-300 text-red-700 rounded-md hover:bg-red-50"
          >
            All Off
            <div className="text-xs text-red-500">No automation</div>
          </button>
        </div>
      </div>

      {/* Weekly Schedule Grid */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h5 className="text-sm font-medium text-gray-900 mb-4">Weekly Schedule</h5>
        
        <div className="space-y-4">
          {dayNames.map((dayName, dayIndex) => {
            const daySlots = schedule[dayIndex] || [];
            const isActive = daySlots.length > 0;
            
            return (
              <div key={dayIndex} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => toggleDayActive(dayIndex)}
                      className={`w-6 h-6 rounded-full flex items-center justify-center ${
                        isActive ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-400'
                      }`}
                    >
                      {isActive ? <Play className="h-3 w-3" /> : <Pause className="h-3 w-3" />}
                    </button>
                    <h6 className="text-sm font-medium text-gray-900">{dayName}</h6>
                    <span className="text-xs text-gray-500">
                      {isActive ? `${daySlots.length} time slot${daySlots.length > 1 ? 's' : ''}` : 'Off'}
                    </span>
                  </div>
                  
                  {isActive && (
                    <button
                      onClick={() => addTimeSlot(dayIndex)}
                      className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    >
                      + Add Slot
                    </button>
                  )}
                </div>

                {isActive && (
                  <div className="space-y-2">
                    {daySlots.map((slot, slotIndex) => (
                      <div key={slotIndex} className="flex items-center space-x-2">
                        <Clock className="h-4 w-4 text-gray-400" />
                        <input
                          type="time"
                          value={slot[0]}
                          onChange={(e) => updateTimeSlot(dayIndex, slotIndex, 0, e.target.value)}
                          className="px-2 py-1 border border-gray-300 rounded text-sm"
                        />
                        <span className="text-gray-500">to</span>
                        <input
                          type="time"
                          value={slot[1]}
                          onChange={(e) => updateTimeSlot(dayIndex, slotIndex, 1, e.target.value)}
                          className="px-2 py-1 border border-gray-300 rounded text-sm"
                        />
                        {daySlots.length > 1 && (
                          <button
                            onClick={() => removeTimeSlot(dayIndex, slotIndex)}
                            className="px-2 py-1 text-xs text-red-600 hover:text-red-800"
                          >
                            Remove
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Schedule Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h5 className="text-sm font-medium text-gray-900 mb-3">Current Schedule Summary</h5>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h6 className="font-medium text-gray-700 mb-2">Active Days:</h6>
            <ul className="space-y-1">
              {dayNames.map((dayName, dayIndex) => {
                const daySlots = schedule[dayIndex] || [];
                if (daySlots.length === 0) return null;
                
                return (
                  <li key={dayIndex} className="flex items-center space-x-2">
                    <span className="w-20 text-gray-600">{dayName}:</span>
                    <span className="text-gray-900">
                      {daySlots.map(slot => `${slot[0]}-${slot[1]}`).join(', ')}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>
          
          <div>
            <h6 className="font-medium text-gray-700 mb-2">Statistics:</h6>
            <ul className="space-y-1 text-gray-600">
              <li>Active days: {Object.values(schedule).filter(slots => slots.length > 0).length}/7</li>
              <li>Total time slots: {Object.values(schedule).reduce((sum, slots) => sum + slots.length, 0)}</li>
              <li>Weekly hours: {getTotalHours()}</li>
              <li>Avg hours/day: {(parseFloat(getTotalHours()) / 7).toFixed(1)}</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Additional Schedule Settings */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h5 className="text-sm font-medium text-gray-900 mb-3">Schedule Settings</h5>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Wait Between Actions (minutes)
            </label>
            <input
              type="number"
              min="1"
              max="60"
              value={config?.settings?.waitminutes || 2}
              onChange={(e) => updateSetting('waitminutes', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Time to wait between automation actions</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Wait Between Visits (count)
            </label>
            <input
              type="number"
              min="1"
              max="100"
              value={config?.settings?.waitvisits || 31}
              onChange={(e) => updateSetting('waitvisits', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Number of visits between wait periods</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Page Load Timeout (ms)
            </label>
            <input
              type="number"
              min="5000"
              max="60000"
              step="1000"
              value={config?.settings?.maxpageloadtime || 20000}
              onChange={(e) => updateSetting('maxpageloadtime', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Maximum time to wait for pages to load</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Page Init Delay (ms)
            </label>
            <input
              type="number"
              min="1000"
              max="30000"
              step="1000"
              value={config?.settings?.pageinitdelay || 5000}
              onChange={(e) => updateSetting('pageinitdelay', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Delay before starting page automation</p>
          </div>
        </div>

        <div className="mt-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={config?.settings?.pauserobot || false}
              onChange={(e) => updateSetting('pauserobot', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">Pause robot (override schedule)</span>
          </label>
        </div>
      </div>

      {/* Save Changes Notice */}
      {hasChanges && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <Calendar className="h-5 w-5 text-yellow-400" />
            <div className="ml-3">
              <h6 className="text-sm font-medium text-yellow-800">Schedule Changes Pending</h6>
              <p className="text-sm text-yellow-700">
                Click "Save Schedule" to apply your schedule changes, then use "Push to DuxSoup" to sync with DuxSoup.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
