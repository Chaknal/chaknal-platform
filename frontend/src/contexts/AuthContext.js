import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is authenticated on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        // Set axios default header
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        // Verify token and get user context
        const response = await axios.get('/auth/me');
        setUser(response.data);
      }
    } catch (err) {
      // Token is invalid, clear it
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_context');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      const response = await axios.post('/auth/login', { email, password });
      const { access_token, user_context } = response.data;

      // Store token and user context
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user_context', JSON.stringify(user_context));

      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // Update user state
      setUser(user_context);

      return { success: true };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_context');
    
    // Clear axios header
    delete axios.defaults.headers.common['Authorization'];
    
    // Clear user state
    setUser(null);
    setError(null);
  };

  const refreshUserContext = async () => {
    try {
      const response = await axios.get('/auth/me');
      setUser(response.data);
      
      // Update stored user context
      localStorage.setItem('user_context', JSON.stringify(response.data));
    } catch (err) {
      console.error('Failed to refresh user context:', err);
      // If refresh fails, logout user
      logout();
    }
  };

  // Check if user has specific permission
  const hasPermission = (permission) => {
    if (!user || !user.permissions) return false;
    return user.permissions.includes(permission);
  };

  // Check if user is superuser
  const isSuperuser = () => {
    return user?.is_superuser || false;
  };

  // Get user's organization
  const getUserOrganization = () => {
    return user?.organization || null;
  };

  // Get user's company
  const getUserCompany = () => {
    return user?.company || null;
  };

  // Check if user belongs to specific organization
  const belongsToOrganization = (orgId) => {
    return user?.organization?.id === orgId;
  };

  // Check if user belongs to specific company
  const belongsToCompany = (companyId) => {
    return user?.company?.id === companyId;
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    refreshUserContext,
    hasPermission,
    isSuperuser,
    getUserOrganization,
    getUserCompany,
    belongsToOrganization,
    belongsToCompany,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
