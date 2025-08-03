/**
 * Minimal LoginForm component test to verify mocks work
 */

// Mock the auth context first
jest.mock('@/contexts/auth-context');

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import LoginForm from '@/components/auth/LoginForm';

// Test wrapper
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });
  
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('LoginForm - Smoke Test', () => {
  test('renders without crashing', () => {
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    // Just verify it renders
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });
});
