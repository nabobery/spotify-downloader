import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => {
    // Initialize token from localStorage if it exists
    const savedToken = localStorage.getItem('spotify_token');
    return savedToken ? JSON.parse(savedToken) : null;
  });

  const login = (tokenInfo) => {
    setToken(tokenInfo);
    localStorage.setItem('spotify_token', JSON.stringify(tokenInfo));
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('spotify_token');
  };

  const refreshToken = async () => {
    if (!token?.refresh_token) return;

    try {
      const response = await api.post('/refresh_token', {
        refresh_token: token.refresh_token
      });

      const newTokenInfo = response.data;
      login(newTokenInfo);
      return newTokenInfo;
    } catch (error) {
      console.error('Error refreshing token:', error);
      logout();
      return null;
    }
  };

  // Check token expiration periodically
  useEffect(() => {
    if (!token) return;

    const checkTokenExpiration = async () => {
      const expiresIn = token.expires_at - Math.floor(Date.now() / 1000);

      // Refresh token if it expires in less than 5 minutes
      if (expiresIn < 300) {
        await refreshToken();
      }
    };

    const interval = setInterval(checkTokenExpiration, 60000); // Check every minute

    // Initial check
    checkTokenExpiration();

    return () => clearInterval(interval);
  }, [token]);

  return (
    <AuthContext.Provider value={{
      token,
      login,
      logout,
      refreshToken,
      isAuthenticated: !!token
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
