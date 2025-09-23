/**
 * Mock Data Logger
 * 
 * Utility to track and log when mock data is being used in the application.
 * This helps identify what needs to be replaced with real APIs for production.
 */

const MOCK_DATA_ENABLED = process.env.REACT_APP_USE_MOCK_DATA !== 'false';

/**
 * Log when mock data is being used
 * @param {string} component - Component name using mock data
 * @param {string} dataType - Type of data being mocked
 * @param {Object} details - Additional details about the mock data
 */
export const logMockData = (component, dataType, details = {}) => {
  if (MOCK_DATA_ENABLED) {
    console.warn('🎭 MOCK DATA ACTIVE:', {
      component,
      dataType,
      timestamp: new Date().toISOString(),
      production_ready: false,
      ...details
    });
    
    // Store mock data usage for audit
    if (typeof window !== 'undefined') {
      const mockDataLog = JSON.parse(localStorage.getItem('mockDataLog') || '[]');
      mockDataLog.push({
        component,
        dataType,
        timestamp: new Date().toISOString(),
        ...details
      });
      localStorage.setItem('mockDataLog', JSON.stringify(mockDataLog.slice(-100))); // Keep last 100 entries
    }
  }
};

/**
 * Check if mock data should be used
 * @returns {boolean}
 */
export const shouldUseMockData = () => {
  return MOCK_DATA_ENABLED;
};

/**
 * Get mock data usage log
 * @returns {Array}
 */
export const getMockDataLog = () => {
  if (typeof window !== 'undefined') {
    return JSON.parse(localStorage.getItem('mockDataLog') || '[]');
  }
  return [];
};

/**
 * Clear mock data log
 */
export const clearMockDataLog = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('mockDataLog');
  }
};

/**
 * Display mock data summary in console
 */
export const showMockDataSummary = () => {
  const log = getMockDataLog();
  const summary = log.reduce((acc, entry) => {
    const key = `${entry.component}:${entry.dataType}`;
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  
  console.group('🎭 Mock Data Usage Summary');
  Object.entries(summary).forEach(([key, count]) => {
    console.log(`${key}: ${count} times`);
  });
  console.groupEnd();
  
  return summary;
};

// Development helper: Show mock data summary every 5 minutes
if (MOCK_DATA_ENABLED && process.env.NODE_ENV === 'development') {
  setInterval(() => {
    const log = getMockDataLog();
    if (log.length > 0) {
      showMockDataSummary();
    }
  }, 5 * 60 * 1000); // 5 minutes
}
