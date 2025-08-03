/**
 * Test to verify validation error state management
 */

// Mock the auth context first
jest.mock('@/contexts/auth-context');

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import LoginForm from '@/components/auth/LoginForm';
import { mockLogin } from '../../../src/contexts/__mocks__/auth-context';

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

describe('LoginForm - Validation Error Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('shows validation errors after empty form submission', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    // Submit empty form
    await user.click(submitButton);
    
    // Wait for React to update state and re-render
    await waitFor(
      () => {
        // Look for the specific error messages we expect
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );

    await waitFor(
      () => {
        expect(screen.getByText('Password is required')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );

    // Verify login wasn't called due to validation failure
    expect(mockLogin).not.toHaveBeenCalled();
  });

  test('shows email validation error for invalid format', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    // Enter invalid email
    await user.type(emailInput, 'invalid-email');
    await user.click(submitButton);
    
    // Wait for validation error
    await waitFor(
      () => {
        expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );

    expect(mockLogin).not.toHaveBeenCalled();
  });

  test('mock login is called with valid credentials', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    // Enter valid credentials
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    // Wait for form submission to call login
    await waitFor(
      () => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
      },
      { timeout: 5000 }
    );
  });
});
