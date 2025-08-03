import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProfilePage from '@/app/profile/page';

// Mock fetch API
global.fetch = jest.fn();

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('ProfilePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock the API call
    mockFetch.mockResolvedValueOnce(
      new Response(JSON.stringify({
        id: 1,
        name: 'John Smith',
        email: 'john.smith@vesselguard.com',
        phone: '+1-555-0123',
        title: 'Senior Inspector',
        department: 'VesselGuard Marine Solutions',
        location: 'Boston, MA',
        status: 'active',
        joined_at: '2023-06-01T00:00:00Z',
        security: {
          two_factor_enabled: true,
          last_password_change: '2023-12-01T00:00:00Z',
          last_login: '2024-01-15T12:30:00Z',
          active_sessions: 2,
          failed_login_attempts: 0
        }
      }), { status: 200, headers: { 'Content-Type': 'application/json' } })
    );
  });

  describe('Basic Rendering', () => {
    it('should render profile page with basic elements', async () => {
      render(<ProfilePage />);

      // Check main heading using role
      expect(screen.getByRole('heading', { name: 'Profile' })).toBeInTheDocument();
      
      // Check descriptive text
      expect(screen.getByText('Manage your personal information and account settings')).toBeInTheDocument();

      // Check tab navigation buttons
      expect(screen.getByRole('button', { name: /profile/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /security/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /preferences/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /activity/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /certifications/i })).toBeInTheDocument();
    });

    it('should display user status badges', async () => {
      render(<ProfilePage />);

      await waitFor(() => {
        expect(screen.getByText('active')).toBeInTheDocument();
        expect(screen.getByText(/Joined/)).toBeInTheDocument();
      });
    });

    it('should load and display profile data', async () => {
      render(<ProfilePage />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('John Smith')).toBeInTheDocument();
        expect(screen.getByDisplayValue('john.smith@vesselguard.com')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Senior Inspector')).toBeInTheDocument();
      });
    });
  });

  describe('Profile Tab Functionality', () => {
    it('should show profile information by default', async () => {
      render(<ProfilePage />);

      await waitFor(() => {
        expect(screen.getByText('Profile Information')).toBeInTheDocument();
        expect(screen.getByDisplayValue('John Smith')).toBeInTheDocument();
      });
    });

    it('should enter edit mode when edit button is clicked', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('John Smith')).toBeInTheDocument();
      });

      // Click edit button
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      await user.click(editButton);

      // Check for Save Changes button (indicates edit mode)
      expect(screen.getByRole('button', { name: /save changes/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });

    it('should allow editing form fields', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('John Smith')).toBeInTheDocument();
      });

      // Enter edit mode
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      await user.click(editButton);

      // Edit name field
      const nameInput = screen.getByDisplayValue('John Smith');
      await user.clear(nameInput);
      await user.type(nameInput, 'Updated Name');
      
      expect(nameInput).toHaveValue('Updated Name');
    });

    it('should show loading state during save', async () => {
      const user = userEvent.setup();
      
      // Mock delayed response for save
      mockFetch.mockResolvedValueOnce(
        new Response(JSON.stringify({}), { 
          status: 200, 
          headers: { 'Content-Type': 'application/json' } 
        })
      );

      render(<ProfilePage />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('John Smith')).toBeInTheDocument();
      });

      // Enter edit mode and save
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      await user.click(editButton);

      const saveButton = screen.getByRole('button', { name: /save changes/i });
      await user.click(saveButton);

      // Check for loading state
      expect(screen.getByRole('button', { name: /saving/i })).toBeInTheDocument();
    });
  });

  describe('Security Tab', () => {
    it('should switch to security tab and show security settings', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      // Click Security tab
      await user.click(screen.getByRole('button', { name: /security/i }));

      await waitFor(() => {
        expect(screen.getByText('Security Settings')).toBeInTheDocument();
        expect(screen.getByText('Authentication')).toBeInTheDocument();
        expect(screen.getByText('Two-Factor Authentication')).toBeInTheDocument();
        expect(screen.getByText('Password')).toBeInTheDocument();
        expect(screen.getByText('Active Sessions')).toBeInTheDocument();
        expect(screen.getByText('Last Login')).toBeInTheDocument();
      });
    });

    it('should show security status information', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await user.click(screen.getByRole('button', { name: /security/i }));

      await waitFor(() => {
        expect(screen.getByText('Enabled')).toBeInTheDocument(); // 2FA status
        expect(screen.getByText('Change')).toBeInTheDocument(); // Change password button
      });
    });
  });

  describe('Placeholder Tabs', () => {
    it('should show placeholder content for Preferences tab', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await user.click(screen.getByRole('button', { name: /preferences/i }));

      await waitFor(() => {
        expect(screen.getByText(/preferences settings coming soon/i)).toBeInTheDocument();
      });
    });

    it('should show placeholder content for Activity tab', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await user.click(screen.getByRole('button', { name: /activity/i }));

      await waitFor(() => {
        expect(screen.getByText(/activity log coming soon/i)).toBeInTheDocument();
      });
    });

    it('should show placeholder content for Certifications tab', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await user.click(screen.getByRole('button', { name: /certifications/i }));

      await waitFor(() => {
        expect(screen.getByText(/certifications management coming soon/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', async () => {
      render(<ProfilePage />);

      expect(screen.getByRole('heading', { level: 1, name: 'Profile' })).toBeInTheDocument();
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { level: 3, name: 'Profile Information' })).toBeInTheDocument();
      });
    });

    it('should have proper form labels', async () => {
      render(<ProfilePage />);

      await waitFor(() => {
        expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/phone number/i)).toBeInTheDocument();
      });
    });
  });
});
