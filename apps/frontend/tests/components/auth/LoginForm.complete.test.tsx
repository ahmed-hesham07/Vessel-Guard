import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginForm from '../../../src/components/auth/LoginForm';
import { mockLogin, mockLogout, mockCheckAuth } from '../../../src/contexts/__mocks__/auth-context';

// Mock the auth context module
jest.mock('../../../src/contexts/auth-context');

describe('LoginForm - Complete Testing', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    
    // Clear localStorage
    localStorage.clear();
    
    // Reset mock implementations
    mockLogin.mockClear();
    mockLogout.mockClear();
    mockCheckAuth.mockClear();
  });

  describe('Validation Error Display', () => {
    it('should display validation errors for empty form submission', async () => {
      render(<LoginForm />);

      // Get form and submit it directly
      const form = document.querySelector('form') as HTMLFormElement;

      // Submit empty form using form submit (more reliable than button click)
      fireEvent.submit(form);

      // Check that validation errors appear
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      });
      
      await waitFor(() => {
        expect(screen.getByText('Password is required')).toBeInTheDocument();
      });

      // Ensure login was not called due to validation failure
      expect(mockLogin).not.toHaveBeenCalled();
    });

    it('should display email validation error for invalid email', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);

      const emailInput = screen.getByLabelText(/email address/i);
      const passwordInput = document.getElementById('password') as HTMLInputElement;
      const form = document.querySelector('form') as HTMLFormElement;

      // Enter invalid email and valid password
      await user.type(emailInput, 'invalid-email');
      await user.type(passwordInput, 'password123');
      
      // Submit form
      fireEvent.submit(form);

      // Check that email validation error appears
      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
      });

      // Ensure login was not called due to validation failure
      expect(mockLogin).not.toHaveBeenCalled();
    });

    it('should display password validation error for short password', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);

      const emailInput = screen.getByLabelText(/email address/i);
      const passwordInput = document.getElementById('password') as HTMLInputElement;
      const form = document.querySelector('form') as HTMLFormElement;

      // Enter valid email and short password
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, '123');
      
      // Submit form
      fireEvent.submit(form);

      // Check that password validation error appears
      await waitFor(() => {
        expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument();
      });

      // Ensure login was not called due to validation failure
      expect(mockLogin).not.toHaveBeenCalled();
    });
  });

  describe('Successful Form Submission', () => {
    it('should call login with correct credentials for valid form', async () => {
      const user = userEvent.setup();
      const mockOnSuccess = jest.fn();
      
      // Mock successful login
      mockLogin.mockResolvedValue(undefined);
      
      render(<LoginForm onSuccess={mockOnSuccess} />);

      const emailInput = screen.getByLabelText(/email address/i);
      const passwordInput = document.getElementById('password') as HTMLInputElement;
      const form = document.querySelector('form') as HTMLFormElement;

      // Fill form with valid data
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      
      // Submit form
      fireEvent.submit(form);

      // Check that login was called with correct parameters
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
      });

      // Check for success message
      await waitFor(() => {
        expect(screen.getByText('Login successful!')).toBeInTheDocument();
      });

      // Check that onSuccess callback was called
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should display error message when login fails', async () => {
      const user = userEvent.setup();
      
      // Mock failed login
      mockLogin.mockRejectedValue(new Error('Invalid credentials'));
      
      render(<LoginForm />);

      const emailInput = screen.getByLabelText(/email address/i);
      const passwordInput = document.getElementById('password') as HTMLInputElement;
      const form = document.querySelector('form') as HTMLFormElement;

      // Fill form with valid data
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'wrongpassword');
      
      // Submit form
      fireEvent.submit(form);

      // Wait for login to be called
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'wrongpassword');
      });

      // Check that error message appears
      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });
    });

    it('should handle network errors gracefully', async () => {
      const user = userEvent.setup();
      
      // Mock network error
      mockLogin.mockRejectedValue(new Error('Network error occurred'));
      
      render(<LoginForm />);

      const emailInput = screen.getByLabelText(/email address/i);
      const passwordInput = document.getElementById('password') as HTMLInputElement;
      const form = document.querySelector('form') as HTMLFormElement;

      // Fill form with valid data
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      
      // Submit form
      fireEvent.submit(form);

      // Wait for login to be called
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalled();
      });

      // Check that network error message appears
      await waitFor(() => {
        expect(screen.getByText('Network error. Please try again.')).toBeInTheDocument();
      });
    });
  });

  describe('Form Interaction', () => {
    it('should clear validation errors when user starts typing', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);

      const emailInput = screen.getByLabelText(/email address/i);
      const form = document.querySelector('form') as HTMLFormElement;

      // Submit empty form to trigger validation errors
      fireEvent.submit(form);

      // Wait for validation error to appear
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      });

      // Start typing in email field
      await user.type(emailInput, 't');

      // Wait for validation error to disappear
      await waitFor(() => {
        expect(screen.queryByText('Email is required')).not.toBeInTheDocument();
      });
    });

    it('should toggle password visibility', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);

      const passwordInput = document.getElementById('password') as HTMLInputElement;
      const toggleButton = screen.getByRole('button', { name: /show password/i });

      // Initially password should be hidden
      expect(passwordInput).toHaveAttribute('type', 'password');

      // Click toggle to show password
      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'text');

      // Click toggle to hide password again
      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });
  });

  describe('Remember Me Functionality', () => {
    it('should save email to localStorage when remember me is checked', async () => {
      const user = userEvent.setup();
      render(<LoginForm />);

      const emailInput = screen.getByLabelText(/email address/i);
      const rememberCheckbox = screen.getByLabelText(/remember me/i);

      // Enter email and check remember me
      await user.type(emailInput, 'test@example.com');
      await user.click(rememberCheckbox);

      // Check that email was saved to localStorage
      expect(localStorage.getItem('remembered_email')).toBe('test@example.com');
    });

    it('should load remembered email on component mount', () => {
      // Pre-populate localStorage
      localStorage.setItem('remembered_email', 'remembered@example.com');

      render(<LoginForm />);

      const emailInput = screen.getByLabelText(/email address/i);
      const rememberCheckbox = screen.getByLabelText(/remember me/i);

      // Check that email was loaded and remember me is checked
      expect(emailInput).toHaveValue('remembered@example.com');
      expect(rememberCheckbox).toBeChecked();
    });
  });
});
