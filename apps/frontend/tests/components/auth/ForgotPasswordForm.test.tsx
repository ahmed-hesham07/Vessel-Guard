import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ForgotPasswordPage from '../../../src/app/forgot-password/page';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    back: jest.fn(),
  }),
}));

// Mock Next.js Link component
jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: { children: React.ReactNode; href: string }) {
    return <a href={href} {...props}>{children}</a>;
  };
});

describe('ForgotPasswordPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Set up default environment variable
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Initial Form Render', () => {
    it('should render the forgot password form correctly', () => {
      render(<ForgotPasswordPage />);

      // Check page title and description
      expect(screen.getByText('Forgot your password?')).toBeInTheDocument();
      expect(screen.getByText('Enter your email address and we\'ll send you a link to reset your password')).toBeInTheDocument();

      // Check form elements
      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument();

      // Check navigation link
      expect(screen.getByText('Back to sign in')).toBeInTheDocument();
    });

    it('should have proper form structure', () => {
      render(<ForgotPasswordPage />);

      const form = document.querySelector('form');
      expect(form).toBeInTheDocument();

      const emailInput = screen.getByLabelText(/email address/i);
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('required');
      expect(emailInput).toHaveAttribute('placeholder', 'Enter your email');
    });
  });

  describe('Form Validation', () => {
    it('should require email field', async () => {
      render(<ForgotPasswordPage />);

      const form = document.querySelector('form') as HTMLFormElement;
      
      // Submit empty form
      fireEvent.submit(form);

      // HTML5 validation should prevent submission
      const emailInput = screen.getByLabelText(/email address/i);
      expect(emailInput).toBeInvalid();
    });

    it('should validate email format', async () => {
      const user = userEvent.setup();
      render(<ForgotPasswordPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const form = document.querySelector('form') as HTMLFormElement;

      // Enter invalid email
      await user.type(emailInput, 'invalid-email');
      fireEvent.submit(form);

      // HTML5 validation should prevent submission
      expect(emailInput).toBeInvalid();
    });
  });

  describe('Form Submission', () => {
    it('should submit form with valid email and show loading state', async () => {
      const user = userEvent.setup();
      
      // Mock successful API response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Reset email sent' }),
      });

      render(<ForgotPasswordPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });
      const form = document.querySelector('form') as HTMLFormElement;

      // Fill form with valid email
      await user.type(emailInput, 'test@example.com');

      // Submit form
      fireEvent.submit(form);

      // Check loading state
      await waitFor(() => {
        expect(screen.getByText('Sending...')).toBeInTheDocument();
      });

      // Verify API call
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/auth/forgot-password',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email: 'test@example.com' }),
        }
      );
    });

    it('should show success state after successful submission', async () => {
      const user = userEvent.setup();
      
      // Mock successful API response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Reset email sent' }),
      });

      render(<ForgotPasswordPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const form = document.querySelector('form') as HTMLFormElement;

      // Fill and submit form
      await user.type(emailInput, 'test@example.com');
      fireEvent.submit(form);

      // Wait for success state
      await waitFor(() => {
        expect(screen.getByText('Check your email')).toBeInTheDocument();
      });

      // Check success message content
      expect(screen.getByText('Email sent successfully')).toBeInTheDocument();
      expect(screen.getByText('Reset link sent to test@example.com')).toBeInTheDocument();
      expect(screen.getByText('Check your inbox and click the link to reset your password')).toBeInTheDocument();

      // Check help text
      expect(screen.getByText('Didn\'t receive the email?')).toBeInTheDocument();
      expect(screen.getByText('Check your spam/junk folder')).toBeInTheDocument();

      // Check action buttons
      expect(screen.getByRole('button', { name: /try different email/i })).toBeInTheDocument();
    });

    it('should handle API errors gracefully', async () => {
      const user = userEvent.setup();
      
      // Mock API error response
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'User not found' }),
      });

      render(<ForgotPasswordPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const form = document.querySelector('form') as HTMLFormElement;

      // Fill and submit form
      await user.type(emailInput, 'nonexistent@example.com');
      fireEvent.submit(form);

      // Wait for error message
      await waitFor(() => {
        expect(screen.getByText('User not found')).toBeInTheDocument();
      });

      // Verify form is still visible (not in success state)
      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument();
    });

    it('should handle network errors', async () => {
      const user = userEvent.setup();
      
      // Mock network error
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      render(<ForgotPasswordPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const form = document.querySelector('form') as HTMLFormElement;

      // Fill and submit form
      await user.type(emailInput, 'test@example.com');
      fireEvent.submit(form);

      // Wait for error message
      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });

    it('should handle unknown errors with fallback message', async () => {
      const user = userEvent.setup();
      
      // Mock API error with no detail
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      });

      render(<ForgotPasswordPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const form = document.querySelector('form') as HTMLFormElement;

      // Fill and submit form
      await user.type(emailInput, 'test@example.com');
      fireEvent.submit(form);

      // Wait for fallback error message
      await waitFor(() => {
        expect(screen.getByText('Failed to send reset email')).toBeInTheDocument();
      });
    });
  });

  describe('Success State Interactions', () => {
    it('should allow user to try different email from success state', async () => {
      const user = userEvent.setup();
      
      // Mock successful API response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Reset email sent' }),
      });

      render(<ForgotPasswordPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const form = document.querySelector('form') as HTMLFormElement;

      // Fill and submit form to reach success state
      await user.type(emailInput, 'test@example.com');
      fireEvent.submit(form);

      // Wait for success state
      await waitFor(() => {
        expect(screen.getByText('Check your email')).toBeInTheDocument();
      });

      // Click "Try different email" button
      const tryDifferentButton = screen.getByRole('button', { name: /try different email/i });
      await user.click(tryDifferentButton);

      // Should return to form state
      await waitFor(() => {
        expect(screen.getByText('Forgot your password?')).toBeInTheDocument();
      });

      // Form should be reset but previous email should still be there
      const newEmailInput = screen.getByLabelText(/email address/i);
      expect(newEmailInput).toHaveValue('test@example.com');
    });
  });

  describe('Navigation Links', () => {
    it('should have correct navigation links in form state', () => {
      render(<ForgotPasswordPage />);

      const backToSignInLink = screen.getByText('Back to sign in').closest('a');
      expect(backToSignInLink).toHaveAttribute('href', '/login');
    });

    it('should have correct navigation links in success state', async () => {
      const user = userEvent.setup();
      
      // Mock successful API response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Reset email sent' }),
      });

      render(<ForgotPasswordPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const form = document.querySelector('form') as HTMLFormElement;

      // Submit form to reach success state
      await user.type(emailInput, 'test@example.com');
      fireEvent.submit(form);

      // Wait for success state
      await waitFor(() => {
        expect(screen.getByText('Check your email')).toBeInTheDocument();
      });

      // Check navigation link in success state
      const backToSignInLink = screen.getByText('Back to sign in').closest('a');
      expect(backToSignInLink).toHaveAttribute('href', '/login');
    });
  });

  describe('Loading States', () => {
    it('should disable submit button during loading', async () => {
      const user = userEvent.setup();
      
      // Mock slow API response
      let resolvePromise: (value: any) => void;
      const slowPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });
      mockFetch.mockReturnValueOnce(slowPromise);

      render(<ForgotPasswordPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });
      const form = document.querySelector('form') as HTMLFormElement;

      // Fill and submit form
      await user.type(emailInput, 'test@example.com');
      fireEvent.submit(form);

      // Check loading state
      await waitFor(() => {
        expect(screen.getByText('Sending...')).toBeInTheDocument();
      });

      // Button should be disabled
      expect(submitButton).toBeDisabled();

      // Resolve the promise to clean up
      resolvePromise!({
        ok: true,
        json: async () => ({ message: 'Reset email sent' }),
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels and structure', () => {
      render(<ForgotPasswordPage />);

      // Check form accessibility
      const emailInput = screen.getByLabelText(/email address/i);
      expect(emailInput).toHaveAttribute('id', 'email');

      const emailLabel = screen.getByText('Email address');
      expect(emailLabel).toHaveAttribute('for', 'email');
    });

    it('should have proper heading hierarchy', () => {
      render(<ForgotPasswordPage />);

      const mainHeading = screen.getByRole('heading', { level: 2 });
      expect(mainHeading).toHaveTextContent('Forgot your password?');
    });

    it('should show error messages in accessible way', async () => {
      const user = userEvent.setup();
      
      // Mock API error
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'User not found' }),
      });

      render(<ForgotPasswordPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const form = document.querySelector('form') as HTMLFormElement;

      // Submit form with error
      await user.type(emailInput, 'test@example.com');
      fireEvent.submit(form);

      // Wait for error message
      await waitFor(() => {
        const errorAlert = screen.getByRole('alert');
        expect(errorAlert).toBeInTheDocument();
        expect(errorAlert).toHaveTextContent('User not found');
      });
    });
  });
});
