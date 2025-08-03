import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProfilePage from '../../../src/app/profile/page';

// Mock Next.js components
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    back: jest.fn(),
  }),
}));

jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: { children: React.ReactNode; href: string }) {
    return <a href={href} {...props}>{children}</a>;
  };
});

describe('ProfilePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial Page Render', () => {
    it('should render the profile page correctly', () => {
      render(<ProfilePage />);

      // Check main page title
      expect(screen.getByText('Profile')).toBeInTheDocument();
      expect(screen.getByText('Manage your personal information and account settings')).toBeInTheDocument();

      // Check navigation tabs are present
      expect(screen.getByRole('button', { name: /profile/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /security/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /preferences/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /activity/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /certifications/i })).toBeInTheDocument();

      // Check profile tab content is visible by default
      expect(screen.getByText('Profile Information')).toBeInTheDocument();
    });

    it('should display user profile information', () => {
      render(<ProfilePage />);

      // Check user information is displayed
      expect(screen.getByDisplayValue('John Smith')).toBeInTheDocument();
      expect(screen.getByDisplayValue('john@atlanticmaritime.com')).toBeInTheDocument();
      expect(screen.getByDisplayValue('+1-555-0123')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Senior Vessel Inspector')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Inspection Services')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Boston, MA')).toBeInTheDocument();
    });

    it('should show user status information', () => {
      render(<ProfilePage />);

      // Check status badge (note: it's lowercase "active")
      expect(screen.getByText('active')).toBeInTheDocument();
      expect(screen.getByText('Joined')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should switch between tabs correctly', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      // Initially profile tab should be active (showing Profile Information)
      expect(screen.getByText('Profile Information')).toBeInTheDocument();

      // Click Security tab
      await user.click(screen.getByRole('button', { name: /security/i }));
      expect(screen.getByText('Security Settings')).toBeInTheDocument();

      // Click Preferences tab
      await user.click(screen.getByRole('button', { name: /preferences/i }));
      expect(screen.getByText('Preferences settings coming soon')).toBeInTheDocument();

      // Click Activity tab
      await user.click(screen.getByRole('button', { name: /activity/i }));
      expect(screen.getByText('Activity log coming soon')).toBeInTheDocument();

      // Click Certifications tab
      await user.click(screen.getByRole('button', { name: /certifications/i }));
      expect(screen.getByText('Professional Certifications')).toBeInTheDocument();

      // Go back to Profile tab
      await user.click(screen.getByRole('button', { name: /profile/i }));
      expect(screen.getByText('Profile Information')).toBeInTheDocument();
    });
  });

  describe('Profile Editing', () => {
    it('should enter edit mode when edit button is clicked', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      // Initially inputs should be read-only
      const nameInput = screen.getByDisplayValue('John Smith') as HTMLInputElement;
      expect(nameInput).toHaveAttribute('readonly');

      // Click edit button
      const editButton = screen.getByText('Edit Profile');
      await user.click(editButton);

      // Now inputs should be editable
      await waitFor(() => {
        expect(nameInput).not.toHaveAttribute('readonly');
      });

      // Button text should change
      expect(screen.getByText('Save Changes')).toBeInTheDocument();
    });

    it('should allow editing profile information', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      // Enter edit mode
      await user.click(screen.getByText('Edit Profile'));

      // Edit the name field
      const nameInput = screen.getByDisplayValue('John Smith') as HTMLInputElement;
      await user.clear(nameInput);
      await user.type(nameInput, 'John Doe');

      expect(nameInput.value).toBe('John Doe');

      // Edit the phone field
      const phoneInput = screen.getByDisplayValue('+1-555-0123') as HTMLInputElement;
      await user.clear(phoneInput);
      await user.type(phoneInput, '+1-555-9999');

      expect(phoneInput.value).toBe('+1-555-9999');
    });

    it('should save changes and show success message', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      // Enter edit mode
      await user.click(screen.getByText('Edit Profile'));

      // Make some changes
      const nameInput = screen.getByDisplayValue('John Smith');
      await user.clear(nameInput);
      await user.type(nameInput, 'Jane Smith');

      // Save changes
      await user.click(screen.getByText('Save Changes'));

      // Should show loading state
      expect(screen.getByText('Saving...')).toBeInTheDocument();

      // Wait for save to complete
      await waitFor(() => {
        expect(screen.getByText('Profile updated successfully!')).toBeInTheDocument();
      });

      // Should exit edit mode
      await waitFor(() => {
        expect(screen.getByText('Edit Profile')).toBeInTheDocument();
      });

      // Inputs should be read-only again
      const updatedNameInput = screen.getByDisplayValue('Jane Smith') as HTMLInputElement;
      expect(updatedNameInput).toHaveAttribute('readonly');
    });

    it('should show loading state during save', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      // Enter edit mode and save
      await user.click(screen.getByText('Edit Profile'));
      await user.click(screen.getByText('Save Changes'));

      // Check loading state
      expect(screen.getByText('Saving...')).toBeInTheDocument();

      // Button should be disabled during loading
      const saveButton = screen.getByText('Saving...');
      expect(saveButton).toBeDisabled();
    });
  });

  describe('Security Tab', () => {
    it('should display security settings correctly', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await user.click(screen.getByRole('button', { name: /security/i }));

      // Check security elements are present
      expect(screen.getByText('Two-Factor Authentication')).toBeInTheDocument();
      expect(screen.getByText('Password')).toBeInTheDocument();
      expect(screen.getByText('Active Sessions')).toBeInTheDocument();
      expect(screen.getByText('Login History')).toBeInTheDocument();
    });

    it('should show security status information', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await user.click(screen.getByRole('button', { name: /security/i }));

      // Check security status indicators
      expect(screen.getByText('Enabled')).toBeInTheDocument(); // 2FA status
      expect(screen.getByText('Change Password')).toBeInTheDocument();
    });
  });

  describe('Certifications Tab', () => {
    it('should display certifications information', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await user.click(screen.getByRole('button', { name: /certifications/i }));

      // Check certifications content
      expect(screen.getByText('Professional Certifications')).toBeInTheDocument();
      expect(screen.getByText('API 510 Pressure Vessel Inspector')).toBeInTheDocument();
      expect(screen.getByText('ASME Section VIII Inspector')).toBeInTheDocument();
      expect(screen.getByText('American Petroleum Institute')).toBeInTheDocument();
    });

    it('should show certification status badges', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await user.click(screen.getByRole('button', { name: /certifications/i }));

      // Check for active certification badges
      const activeBadges = screen.getAllByText('Active');
      expect(activeBadges.length).toBeGreaterThan(0);
    });
  });

  describe('Placeholder Tabs', () => {
    it('should show placeholder content for Preferences tab', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await user.click(screen.getByRole('button', { name: /preferences/i }));

      expect(screen.getByText('Preferences settings coming soon')).toBeInTheDocument();
    });

    it('should show placeholder content for Activity tab', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      await user.click(screen.getByRole('button', { name: /activity/i }));

      expect(screen.getByText('Activity log coming soon')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', () => {
      render(<ProfilePage />);

      // Check for proper heading hierarchy
      expect(screen.getByRole('heading', { level: 1, name: 'Profile' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 3, name: 'Profile Information' })).toBeInTheDocument();
    });

    it('should have proper form labels', () => {
      render(<ProfilePage />);

      // Check for proper labels
      expect(screen.getByText('Full Name')).toBeInTheDocument();
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('Phone')).toBeInTheDocument();
      expect(screen.getByText('Job Title')).toBeInTheDocument();
      expect(screen.getByText('Department')).toBeInTheDocument();
      expect(screen.getByText('Location')).toBeInTheDocument();
    });

    it('should announce status changes to screen readers', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      // Enter edit mode and save
      await user.click(screen.getByText('Edit Profile'));
      await user.click(screen.getByText('Save Changes'));

      // Success message should be announced
      await waitFor(() => {
        const successAlert = screen.getByRole('alert');
        expect(successAlert).toBeInTheDocument();
        expect(successAlert).toHaveTextContent('Profile updated successfully!');
      });
    });
  });

  describe('Form State Management', () => {
    it('should maintain form state during edit mode', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      // Enter edit mode
      await user.click(screen.getByText('Edit Profile'));

      // Verify all fields are editable
      const inputs = [
        screen.getByDisplayValue('John Smith'),
        screen.getByDisplayValue('john@atlanticmaritime.com'),
        screen.getByDisplayValue('+1-555-0123'),
        screen.getByDisplayValue('Senior Vessel Inspector'),
        screen.getByDisplayValue('Inspection Services'),
        screen.getByDisplayValue('Boston, MA'),
      ];

      inputs.forEach(input => {
        expect(input).not.toHaveAttribute('readonly');
      });
    });

    it('should revert to read-only after save', async () => {
      const user = userEvent.setup();
      render(<ProfilePage />);

      // Enter edit mode, make changes, and save
      await user.click(screen.getByText('Edit Profile'));
      const nameInput = screen.getByDisplayValue('John Smith');
      await user.clear(nameInput);
      await user.type(nameInput, 'Updated Name');
      await user.click(screen.getByText('Save Changes'));

      // Wait for save to complete and verify read-only state
      await waitFor(() => {
        expect(screen.getByText('Edit Profile')).toBeInTheDocument();
      });

      const updatedInput = screen.getByDisplayValue('Updated Name') as HTMLInputElement;
      expect(updatedInput).toHaveAttribute('readonly');
    });
  });
});
