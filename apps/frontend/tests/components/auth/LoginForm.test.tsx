/**
 * Comprehensive authentication component tests
 * 
 * Tests login functionality, user authentication state,
 * error handling, and form validation.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/lib/node';
import '@testing-library/jest-dom';

import LoginForm from '@/components/auth/LoginForm';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock server setup
const server = setupServer(
  http.post('/api/v1/auth/login', async ({ request }) => {
    const formData = await request.formData();
    const email = formData.get('username') as string;
    const password = formData.get('password') as string;
    
    if (email === 'admin@vesselguard.com' && password === 'correct-password') {
      return HttpResponse.json({
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'admin@vesselguard.com',
          first_name: 'Admin',
          last_name: 'User',
          role: 'admin',
          organization_id: 1
        }
      });
    }
    
    return HttpResponse.json(
      { detail: 'Invalid credentials' },
      { status: 401 }
    );
  }),
  
  http.post('/api/v1/auth/refresh', () => {
    return HttpResponse.json({
      access_token: 'new-access-token',
      refresh_token: 'new-refresh-token',
      token_type: 'bearer'
    });
  }),
  
  http.get('/api/v1/users/me', ({ request }) => {
    const authHeader = request.headers.get('authorization');
    
    if (authHeader && authHeader.includes('mock-access-token')) {
      return HttpResponse.json({
        id: 1,
        email: 'admin@vesselguard.com',
        first_name: 'Admin',
        last_name: 'User',
        role: 'admin',
        organization_id: 1,
        is_active: true
      });
    }
    
    return HttpResponse.json(
      { detail: 'Unauthorized' },
      { status: 401 }
    );
  })
);

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });
  
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {children}
      </AuthProvider>
    </QueryClientProvider>
  );
};

// Test setup and teardown
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('LoginForm Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });
  
  test('renders login form with all required fields', () => {
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/vessel guard/i)).toBeInTheDocument();
  });
  
  test('displays validation errors for empty fields', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });
  
  test('displays validation error for invalid email format', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await user.type(emailInput, 'invalid-email');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument();
    });
  });
  
  test('displays validation error for short password', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, '123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument();
    });
  });
  
  test('submits form with valid credentials and shows success', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await user.type(emailInput, 'admin@vesselguard.com');
    await user.type(passwordInput, 'correct-password');
    await user.click(submitButton);
    
    // Should show loading state
    expect(screen.getByRole('button', { name: /signing in/i })).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText(/login successful/i)).toBeInTheDocument();
    });
    
    // Should store tokens in localStorage
    expect(localStorage.getItem('token')).toBe('mock-access-token');
    expect(localStorage.getItem('refresh_token')).toBe('mock-refresh-token');
  });
  
  test('displays error message for invalid credentials', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await user.type(emailInput, 'wrong@example.com');
    await user.type(passwordInput, 'wrong-password');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
    
    // Should not store tokens on error
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
  });
  
  test('handles network errors gracefully', async () => {
    const user = userEvent.setup();
    
    // Override server to simulate network error
    server.use(
      http.post('/api/v1/auth/login', () => {
        return HttpResponse.error();
      })
    );
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/network error.*try again/i)).toBeInTheDocument();
    });
  });
  
  test('disables form during submission', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await user.type(emailInput, 'admin@vesselguard.com');
    await user.type(passwordInput, 'correct-password');
    await user.click(submitButton);
    
    // Form fields should be disabled during submission
    expect(emailInput).toBeDisabled();
    expect(passwordInput).toBeDisabled();
    expect(submitButton).toBeDisabled();
    
    await waitFor(() => {
      expect(screen.getByText(/login successful/i)).toBeInTheDocument();
    });
  });
  
  test('remembers email when "Remember me" is checked', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const emailInput = screen.getByLabelText(/email/i);
    const rememberCheckbox = screen.getByLabelText(/remember me/i);
    
    await user.type(emailInput, 'test@example.com');
    await user.click(rememberCheckbox);
    
    // Should store email in localStorage
    await waitFor(() => {
      expect(localStorage.getItem('remembered_email')).toBe('test@example.com');
    });
    
    // Clear form and re-render to test restoration
    await user.clear(emailInput);
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    // Email should be restored from localStorage
    expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument();
  });
  
  test('clears error message when user starts typing', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    // First trigger an error
    await user.type(emailInput, 'wrong@example.com');
    await user.type(passwordInput, 'wrong-password');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
    
    // Start typing again - error should clear
    await user.type(emailInput, 'a');
    
    await waitFor(() => {
      expect(screen.queryByText(/invalid credentials/i)).not.toBeInTheDocument();
    });
  });
  
  test('shows password visibility toggle', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const passwordInput = screen.getByLabelText(/password/i);
    const toggleButton = screen.getByRole('button', { name: /show password/i });
    
    // Password should be hidden by default
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click toggle to show password
    await user.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');
    expect(screen.getByRole('button', { name: /hide password/i })).toBeInTheDocument();
    
    // Click toggle to hide password again
    await user.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });
});

describe('AuthContext Integration', () => {
  test('provides authentication state to components', async () => {
    const TestComponent = () => {
      const { user, isAuthenticated, login } = useAuth();
      
      return (
        <div>
          <div data-testid="auth-status">
            {isAuthenticated ? 'Authenticated' : 'Not authenticated'}
          </div>
          {user && <div data-testid="user-name">{user.first_name}</div>}
          <button onClick={() => login('admin@vesselguard.com', 'correct-password')}>
            Login
          </button>
        </div>
      );
    };
    
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );
    
    expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
    
    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(screen.getByTestId('user-name')).toHaveTextContent('Admin');
    });
  });
  
  test('automatically refreshes expired tokens', async () => {
    // Mock an expired token scenario
    localStorage.setItem('token', 'expired-token');
    localStorage.setItem('refresh_token', 'valid-refresh-token');
    
    server.use(
      http.get('/api/v1/users/me', ({ request }) => {
        const authHeader = request.headers.get('authorization');
        
        if (authHeader && authHeader.includes('expired-token')) {
          return HttpResponse.json({ detail: 'Token expired' }, { status: 401 });
        }
        
        if (authHeader && authHeader.includes('new-access-token')) {
          return HttpResponse.json({
            id: 1,
            email: 'admin@vesselguard.com',
            first_name: 'Admin',
            last_name: 'User',
            role: 'admin'
          });
        }
        
        return HttpResponse.json({ detail: 'Unauthorized' }, { status: 401 });
      })
    );
    
    const TestComponent = () => {
      const { user, checkAuth } = useAuth();
      
      return (
        <div>
          <button onClick={checkAuth}>Check Auth</button>
          {user && <div data-testid="user-email">{user.email}</div>}
        </div>
      );
    };
    
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );
    
    const checkButton = screen.getByRole('button', { name: /check auth/i });
    fireEvent.click(checkButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toHaveTextContent('admin@vesselguard.com');
    });
    
    // Should have refreshed the token
    expect(localStorage.getItem('token')).toBe('new-access-token');
  });
  
  test('logs out user when refresh token is invalid', async () => {
    localStorage.setItem('token', 'expired-token');
    localStorage.setItem('refresh_token', 'invalid-refresh-token');
    
    server.use(
      http.post('/api/v1/auth/refresh', () => {
        return HttpResponse.json({ detail: 'Invalid refresh token' }, { status: 401 });
      })
    );
    
    const TestComponent = () => {
      const { isAuthenticated, checkAuth } = useAuth();
      
      return (
        <div>
          <div data-testid="auth-status">
            {isAuthenticated ? 'Authenticated' : 'Not authenticated'}
          </div>
          <button onClick={checkAuth}>Check Auth</button>
        </div>
      );
    };
    
    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );
    
    const checkButton = screen.getByRole('button', { name: /check auth/i });
    fireEvent.click(checkButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
    });
    
    // Should have cleared tokens
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
  });
});

describe('Accessibility Tests', () => {
  test('login form is accessible via keyboard navigation', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    // Tab through form elements
    await user.tab();
    expect(screen.getByLabelText(/email/i)).toHaveFocus();
    
    await user.tab();
    expect(screen.getByLabelText(/password/i)).toHaveFocus();
    
    await user.tab();
    expect(screen.getByLabelText(/remember me/i)).toHaveFocus();
    
    await user.tab();
    expect(screen.getByRole('button', { name: /sign in/i })).toHaveFocus();
  });
  
  test('form has proper ARIA labels and descriptions', () => {
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    
    expect(emailInput).toHaveAttribute('aria-required', 'true');
    expect(passwordInput).toHaveAttribute('aria-required', 'true');
    expect(emailInput).toHaveAttribute('type', 'email');
    expect(passwordInput).toHaveAttribute('type', 'password');
  });
  
  test('error messages are associated with form fields', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    );
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      const emailInput = screen.getByLabelText(/email/i);
      const emailError = screen.getByText(/email is required/i);
      
      expect(emailInput).toHaveAttribute('aria-describedby');
      expect(emailError).toHaveAttribute('id', emailInput.getAttribute('aria-describedby'));
    });
  });
});

export default {};
