import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RegisterPage from '../../../src/app/register/page';
import { useAuth } from '../../../src/contexts/auth-context';

// Mock the auth context
const mockRegister = jest.fn();
const mockPush = jest.fn();

jest.mock('../../../src/contexts/auth-context', () => ({
  useAuth: jest.fn(() => ({
    register: mockRegister,
    isAuthenticated: false,
  })),
}));

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    back: jest.fn(),
  }),
}));

// Mock Next.js Link component
jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: { children: React.ReactNode; href: string }) {
    return <a href={href} {...props}>{children}</a>;
  };
});

describe('RegisterPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset mock to default state
    (useAuth as jest.Mock).mockReturnValue({
      register: mockRegister,
      isAuthenticated: false,
    });
  });

  describe('Initial Form Render', () => {
    it('should render the registration form correctly', () => {
      render(<RegisterPage />);

      // Check page title and description
      expect(screen.getByText('Create your account')).toBeInTheDocument();
      expect(screen.getByText('Join Vessel Guard to manage your engineering compliance')).toBeInTheDocument();

      // Check all form fields are present
      expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/phone number/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/job title/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/department/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/organization name/i)).toBeInTheDocument();
      expect(screen.getByLabelText('Password *')).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();

      // Check submit button
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();

      // Check terms and privacy links
      expect(screen.getByText('Terms of Service')).toBeInTheDocument();
      expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
    });

    it('should have proper form structure and required fields', () => {
      render(<RegisterPage />);

      const form = document.querySelector('form');
      expect(form).toBeInTheDocument();

      // Check required fields
      const requiredFields = [
        screen.getByLabelText(/first name/i),
        screen.getByLabelText(/last name/i),
        screen.getByLabelText(/email address/i),
        screen.getByLabelText('Password *'),
        screen.getByLabelText(/confirm password/i),
      ];

      requiredFields.forEach(field => {
        expect(field).toHaveAttribute('required');
      });

      // Check optional fields don't have required
      const optionalFields = [
        screen.getByLabelText(/phone number/i),
        screen.getByLabelText(/job title/i),
        screen.getByLabelText(/department/i),
        screen.getByLabelText(/organization name/i),
      ];

      optionalFields.forEach(field => {
        expect(field).not.toHaveAttribute('required');
      });
    });

    it('should redirect authenticated users to dashboard', () => {
      // Mock authenticated state
      (useAuth as jest.Mock).mockReturnValue({
        register: mockRegister,
        isAuthenticated: true,
      });

      render(<RegisterPage />);

      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  describe('Form Validation', () => {
    it('should validate required fields', async () => {
      render(<RegisterPage />);

      const form = document.querySelector('form') as HTMLFormElement;
      
      // Submit empty form
      fireEvent.submit(form);

      // Wait for validation error
      await waitFor(() => {
        expect(screen.getByText('Please fill in all required fields')).toBeInTheDocument();
      });

      // Ensure register was not called
      expect(mockRegister).not.toHaveBeenCalled();
    });

    it('should validate email format', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      // Fill required fields with invalid email
      await user.type(screen.getByLabelText(/first name/i), 'John');
      await user.type(screen.getByLabelText(/last name/i), 'Doe');
      await user.type(screen.getByLabelText(/email address/i), 'invalid-email');
      await user.type(screen.getByLabelText('Password *'), 'ValidPass123!');
      await user.type(screen.getByLabelText(/confirm password/i), 'ValidPass123!');
      
      const termsCheckbox = screen.getByLabelText(/i agree to the/i);
      await user.click(termsCheckbox);

      const form = document.querySelector('form') as HTMLFormElement;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
      });

      expect(mockRegister).not.toHaveBeenCalled();
    });

    it('should validate password requirements', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      // Fill required fields with weak password
      await user.type(screen.getByLabelText(/first name/i), 'John');
      await user.type(screen.getByLabelText(/last name/i), 'Doe');
      await user.type(screen.getByLabelText(/email address/i), 'john@example.com');
      await user.type(screen.getByLabelText('Password *'), 'weak');
      await user.type(screen.getByLabelText(/confirm password/i), 'weak');
      
      const termsCheckbox = screen.getByLabelText(/i agree to the/i);
      await user.click(termsCheckbox);

      const form = document.querySelector('form') as HTMLFormElement;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Password does not meet the requirements')).toBeInTheDocument();
      });

      expect(mockRegister).not.toHaveBeenCalled();
    });

    it('should validate password confirmation match', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      // Fill required fields with mismatched passwords
      await user.type(screen.getByLabelText(/first name/i), 'John');
      await user.type(screen.getByLabelText(/last name/i), 'Doe');
      await user.type(screen.getByLabelText(/email address/i), 'john@example.com');
      await user.type(screen.getByLabelText('Password *'), 'ValidPass123!');
      await user.type(screen.getByLabelText(/confirm password/i), 'DifferentPass123!');
      
      const termsCheckbox = screen.getByLabelText(/i agree to the/i);
      await user.click(termsCheckbox);

      const form = document.querySelector('form') as HTMLFormElement;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
      });

      expect(mockRegister).not.toHaveBeenCalled();
    });
  });

  describe('Password Requirements Display', () => {
    it('should show password requirements when typing password', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const passwordInput = screen.getByLabelText('Password *');
      
      // Start typing password
      await user.type(passwordInput, 'weak');

      // Password requirements should appear
      await waitFor(() => {
        expect(screen.getByText('Password Requirements:')).toBeInTheDocument();
      });

      // Check all requirement messages are visible
      expect(screen.getByText('At least 8 characters')).toBeInTheDocument();
      expect(screen.getByText('At least one uppercase letter (A-Z)')).toBeInTheDocument();
      expect(screen.getByText('At least one lowercase letter (a-z)')).toBeInTheDocument();
      expect(screen.getByText('At least one number (0-9)')).toBeInTheDocument();
      expect(screen.getByText('At least one special character (!@#$%^&*)')).toBeInTheDocument();
    });

    it('should update requirement indicators as password improves', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const passwordInput = screen.getByLabelText('Password *');
      
      // Type password that meets some requirements
      await user.type(passwordInput, 'Password123!');

      // Wait for requirements to update
      await waitFor(() => {
        expect(screen.getByText('Password Requirements:')).toBeInTheDocument();
      });

      // All requirements should be met (visual indicators would show green checkmarks)
      // Note: The exact visual representation would need to be tested based on the PasswordRequirement component
    });

    it('should not show requirements when password field is empty', () => {
      render(<RegisterPage />);

      // Password requirements should not be visible initially
      expect(screen.queryByText('Password Requirements:')).not.toBeInTheDocument();
    });
  });

  describe('Password Visibility Toggle', () => {
    it('should toggle password visibility', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const passwordInput = screen.getByLabelText('Password *') as HTMLInputElement;
      const toggleButtons = screen.getAllByRole('button', { name: '' }); // Eye icons don't have text
      const passwordToggle = toggleButtons[0]; // First toggle is for password

      // Initially password should be hidden
      expect(passwordInput).toHaveAttribute('type', 'password');

      // Click toggle to show password
      await user.click(passwordToggle);
      expect(passwordInput).toHaveAttribute('type', 'text');

      // Click toggle to hide password again
      await user.click(passwordToggle);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    it('should toggle confirm password visibility', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      const confirmPasswordInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement;
      const toggleButtons = screen.getAllByRole('button', { name: '' }); // Eye icons don't have text
      const confirmPasswordToggle = toggleButtons[1]; // Second toggle is for confirm password

      // Initially password should be hidden
      expect(confirmPasswordInput).toHaveAttribute('type', 'password');

      // Click toggle to show password
      await user.click(confirmPasswordToggle);
      expect(confirmPasswordInput).toHaveAttribute('type', 'text');

      // Click toggle to hide password again
      await user.click(confirmPasswordToggle);
      expect(confirmPasswordInput).toHaveAttribute('type', 'password');
    });
  });

  describe('Form Submission', () => {
    it('should submit form with valid data', async () => {
      const user = userEvent.setup();
      mockRegister.mockResolvedValueOnce(undefined);

      render(<RegisterPage />);

      // Fill all required fields with valid data
      await user.type(screen.getByLabelText(/first name/i), 'John');
      await user.type(screen.getByLabelText(/last name/i), 'Doe');
      await user.type(screen.getByLabelText(/email address/i), 'john@example.com');
      await user.type(screen.getByLabelText(/phone number/i), '+1234567890');
      await user.type(screen.getByLabelText(/job title/i), 'Engineer');
      await user.type(screen.getByLabelText(/department/i), 'Engineering');
      await user.type(screen.getByLabelText(/organization name/i), 'Acme Corp');
      await user.type(screen.getByLabelText('Password *'), 'ValidPass123!');
      await user.type(screen.getByLabelText(/confirm password/i), 'ValidPass123!');
      
      const termsCheckbox = screen.getByLabelText(/i agree to the/i);
      await user.click(termsCheckbox);

      const form = document.querySelector('form') as HTMLFormElement;
      fireEvent.submit(form);

      // Wait for submission
      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          phone: '+1234567890',
          job_title: 'Engineer',
          department: 'Engineering',
          organization_name: 'Acme Corp',
          password: 'ValidPass123!'
          // Note: confirmPassword should be excluded
        });
      });
    });

    it('should show loading state during submission', async () => {
      const user = userEvent.setup();
      
      // Mock slow registration
      let resolveRegister: (value: any) => void;
      const slowPromise = new Promise((resolve) => {
        resolveRegister = resolve;
      });
      mockRegister.mockReturnValueOnce(slowPromise);

      render(<RegisterPage />);

      // Fill form with valid data
      await user.type(screen.getByLabelText(/first name/i), 'John');
      await user.type(screen.getByLabelText(/last name/i), 'Doe');
      await user.type(screen.getByLabelText(/email address/i), 'john@example.com');
      await user.type(screen.getByLabelText('Password *'), 'ValidPass123!');
      await user.type(screen.getByLabelText(/confirm password/i), 'ValidPass123!');
      
      const termsCheckbox = screen.getByLabelText(/i agree to the/i);
      await user.click(termsCheckbox);

      const submitButton = screen.getByRole('button', { name: /create account/i });

      const form = document.querySelector('form') as HTMLFormElement;
      fireEvent.submit(form);

      // Check loading state
      await waitFor(() => {
        expect(screen.getByText('Creating account...')).toBeInTheDocument();
      });

      // Button should be disabled
      expect(submitButton).toBeDisabled();

      // Resolve the promise to clean up
      resolveRegister!(undefined);
    });

    it('should handle registration errors', async () => {
      const user = userEvent.setup();
      mockRegister.mockRejectedValueOnce(new Error('Email already exists'));

      render(<RegisterPage />);

      // Fill form with valid data
      await user.type(screen.getByLabelText(/first name/i), 'John');
      await user.type(screen.getByLabelText(/last name/i), 'Doe');
      await user.type(screen.getByLabelText(/email address/i), 'existing@example.com');
      await user.type(screen.getByLabelText('Password *'), 'ValidPass123!');
      await user.type(screen.getByLabelText(/confirm password/i), 'ValidPass123!');
      
      const termsCheckbox = screen.getByLabelText(/i agree to the/i);
      await user.click(termsCheckbox);

      const form = document.querySelector('form') as HTMLFormElement;
      fireEvent.submit(form);

      // Wait for error message
      await waitFor(() => {
        expect(screen.getByText('Email already exists')).toBeInTheDocument();
      });
    });

    it('should handle unknown errors with fallback message', async () => {
      const user = userEvent.setup();
      mockRegister.mockRejectedValueOnce('Unknown error');

      render(<RegisterPage />);

      // Fill form with valid data
      await user.type(screen.getByLabelText(/first name/i), 'John');
      await user.type(screen.getByLabelText(/last name/i), 'Doe');
      await user.type(screen.getByLabelText(/email address/i), 'john@example.com');
      await user.type(screen.getByLabelText('Password *'), 'ValidPass123!');
      await user.type(screen.getByLabelText(/confirm password/i), 'ValidPass123!');
      
      const termsCheckbox = screen.getByLabelText(/i agree to the/i);
      await user.click(termsCheckbox);

      const form = document.querySelector('form') as HTMLFormElement;
      fireEvent.submit(form);

      // Wait for fallback error message
      await waitFor(() => {
        expect(screen.getByText('Registration failed')).toBeInTheDocument();
      });
    });
  });

  describe('Navigation Links', () => {
    it('should have correct navigation links', () => {
      render(<RegisterPage />);

      const termsLink = screen.getByText('Terms of Service').closest('a');
      expect(termsLink).toHaveAttribute('href', '/terms');

      const privacyLink = screen.getByText('Privacy Policy').closest('a');
      expect(privacyLink).toHaveAttribute('href', '/privacy');
    });
  });

  describe('Form Field Interactions', () => {
    it('should maintain error message while typing until form is resubmitted', async () => {
      const user = userEvent.setup();
      render(<RegisterPage />);

      // Submit empty form to trigger error
      const form = document.querySelector('form') as HTMLFormElement;
      fireEvent.submit(form);

      // Wait for error message
      await waitFor(() => {
        expect(screen.getByText('Please fill in all required fields')).toBeInTheDocument();
      });

      // Start typing in first name - error should persist
      await user.type(screen.getByLabelText(/first name/i), 'John');
      
      // Error should still be visible
      expect(screen.getByText('Please fill in all required fields')).toBeInTheDocument();

      // Fill all required fields
      await user.type(screen.getByLabelText(/last name/i), 'Doe');
      await user.type(screen.getByLabelText(/email address/i), 'john@example.com');
      await user.type(screen.getByLabelText('Password *'), 'ValidPass123!');
      await user.type(screen.getByLabelText(/confirm password/i), 'ValidPass123!');
      
      const termsCheckbox = screen.getByLabelText(/i agree to the/i);
      await user.click(termsCheckbox);

      // Mock successful registration
      mockRegister.mockResolvedValueOnce(undefined);

      // Submit form again
      fireEvent.submit(form);

      // Error should be cleared after successful submission attempt
      await waitFor(() => {
        expect(screen.queryByText('Please fill in all required fields')).not.toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels and structure', () => {
      render(<RegisterPage />);

      // Check all inputs have proper labels
      const inputs = [
        { label: /first name/i, id: 'first_name' },
        { label: /last name/i, id: 'last_name' },
        { label: /email address/i, id: 'email' },
        { label: /phone number/i, id: 'phone' },
        { label: /job title/i, id: 'job_title' },
        { label: /department/i, id: 'department' },
        { label: /organization name/i, id: 'organization_name' },
        { label: 'Password *', id: 'password' },
        { label: /confirm password/i, id: 'confirmPassword' },
      ];

      inputs.forEach(({ label, id }) => {
        const input = screen.getByLabelText(label);
        expect(input).toHaveAttribute('id', id);
      });
    });

    it('should have proper heading hierarchy', () => {
      render(<RegisterPage />);

      const mainHeading = screen.getByRole('heading', { level: 2 });
      expect(mainHeading).toHaveTextContent('Create your account');
    });

    it('should show error messages in accessible way', async () => {
      render(<RegisterPage />);

      const form = document.querySelector('form') as HTMLFormElement;
      fireEvent.submit(form);

      // Wait for error message
      await waitFor(() => {
        const errorAlert = screen.getByRole('alert');
        expect(errorAlert).toBeInTheDocument();
        expect(errorAlert).toHaveTextContent('Please fill in all required fields');
      });
    });
  });
});
