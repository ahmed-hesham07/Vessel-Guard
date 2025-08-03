import React from 'react';

// Create mock functions that return promises
const mockLogin = jest.fn().mockResolvedValue({ success: true });
const mockLogout = jest.fn().mockResolvedValue(undefined);
const mockCheckAuth = jest.fn().mockResolvedValue(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <div data-testid="mock-auth-provider">{children}</div>;
};

export const useAuth = () => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  login: mockLogin,
  logout: mockLogout,
  checkAuth: mockCheckAuth,
  clearError: jest.fn(),
  error: null,
});

// Export the mock functions for use in tests
export { mockLogin, mockLogout, mockCheckAuth };

export default {
  AuthProvider,
  useAuth,
};
