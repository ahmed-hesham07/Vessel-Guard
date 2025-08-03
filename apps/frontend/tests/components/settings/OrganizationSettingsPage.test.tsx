import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import OrganizationSettingsPage from '@/app/settings/page';

describe('OrganizationSettingsPage', () => {
  describe('Basic Rendering', () => {
    it('should render settings page with main elements', () => {
      render(<OrganizationSettingsPage />);

      // Check main heading
      expect(screen.getByRole('heading', { name: 'Organization Settings' })).toBeInTheDocument();

      // Check description
      expect(screen.getByText('Manage your organization settings and preferences')).toBeInTheDocument();

      // Check all tab navigation buttons
      expect(screen.getByRole('button', { name: /organization profile/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /users & roles/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /subscription & billing/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /security settings/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /notifications/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /api settings/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /branding/i })).toBeInTheDocument();
    });

    it('should show organization profile by default', () => {
      render(<OrganizationSettingsPage />);

      // Check default tab content
      expect(screen.getByRole('heading', { name: 'Organization Profile', level: 3 })).toBeInTheDocument();
      expect(screen.getByDisplayValue('Atlantic Maritime Solutions')).toBeInTheDocument();
      expect(screen.getByDisplayValue('info@atlanticmaritime.com')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should switch to Users & Roles tab', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      await user.click(screen.getByRole('button', { name: /users & roles/i }));

      expect(screen.getByRole('heading', { name: 'Users & Roles', level: 3 })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /add user/i })).toBeInTheDocument();
      
      // Check user list
      expect(screen.getByText('John Smith')).toBeInTheDocument();
      expect(screen.getByText('Sarah Johnson')).toBeInTheDocument();
      expect(screen.getByText('Mike Wilson')).toBeInTheDocument();
      expect(screen.getByText('Emily Davis')).toBeInTheDocument();
    });

    it('should switch to Subscription & Billing tab', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      await user.click(screen.getByRole('button', { name: /subscription & billing/i }));

      expect(screen.getByRole('heading', { name: 'Subscription & Billing', level: 3 })).toBeInTheDocument();
      expect(screen.getByText('Enterprise')).toBeInTheDocument();
      expect(screen.getByText(/unlimited vessels/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /manage billing/i })).toBeInTheDocument();
    });

    it('should switch to Security Settings tab', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      await user.click(screen.getByRole('button', { name: /security settings/i }));

      expect(screen.getByRole('heading', { name: 'Security Settings', level: 3 })).toBeInTheDocument();
      expect(screen.getByText('Two-Factor Authentication')).toBeInTheDocument();
      expect(screen.getByText('Single Sign-On (SSO)')).toBeInTheDocument();
      expect(screen.getByText('Password Policy')).toBeInTheDocument();
    });

    it('should switch to Notifications tab', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      await user.click(screen.getByRole('button', { name: /notifications/i }));

      expect(screen.getByRole('heading', { name: 'Notification Settings', level: 3 })).toBeInTheDocument();
      expect(screen.getByText('Email Notifications')).toBeInTheDocument();
      expect(screen.getByText('SMS Notifications')).toBeInTheDocument();
      expect(screen.getByText('Slack Integration')).toBeInTheDocument();
    });

    it('should switch to API Settings tab', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      await user.click(screen.getByRole('button', { name: /api settings/i }));

      expect(screen.getByRole('heading', { name: 'API Configuration', level: 3 })).toBeInTheDocument();
      expect(screen.getByText('API Access')).toBeInTheDocument();
      expect(screen.getByText('Rate Limiting')).toBeInTheDocument();
      expect(screen.getByText('Webhooks')).toBeInTheDocument();
    });

    it('should switch to Branding tab', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      await user.click(screen.getByRole('button', { name: /branding/i }));

      expect(screen.getByRole('heading', { name: 'Brand Customization', level: 3 })).toBeInTheDocument();
      expect(screen.getByText('Logo')).toBeInTheDocument();
      expect(screen.getByText('Brand Colors')).toBeInTheDocument();
    });
  });

  describe('Organization Profile Editing', () => {
    it('should enter edit mode when edit button is clicked', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      // Click edit button
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      await user.click(editButton);

      // Check for Save and Cancel buttons (indicates edit mode)
      expect(screen.getByRole('button', { name: /save changes/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });

    it('should allow editing organization fields', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      // Enter edit mode
      await user.click(screen.getByRole('button', { name: /edit profile/i }));

      // Edit organization name
      const nameInput = screen.getByDisplayValue('Atlantic Maritime Solutions');
      await user.clear(nameInput);
      await user.type(nameInput, 'Updated Organization Name');
      
      expect(nameInput).toHaveValue('Updated Organization Name');
    });

    it('should show loading state during save', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      // Enter edit mode
      await user.click(screen.getByRole('button', { name: /edit profile/i }));

      // Click save button
      const saveButton = screen.getByRole('button', { name: /save changes/i });
      await user.click(saveButton);

      // Check for loading state
      expect(screen.getByRole('button', { name: /saving/i })).toBeInTheDocument();
    });

    it('should show success message after save', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      // Enter edit mode and save
      await user.click(screen.getByRole('button', { name: /edit profile/i }));
      await user.click(screen.getByRole('button', { name: /save changes/i }));

      // Wait for success message
      await waitFor(() => {
        expect(screen.getByText(/organization profile updated successfully/i)).toBeInTheDocument();
      });
    });
  });

  describe('User Management', () => {
    it('should display user list with correct information', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      await user.click(screen.getByRole('button', { name: /users & roles/i }));

      // Check user information
      expect(screen.getByText('John Smith')).toBeInTheDocument();
      expect(screen.getByText('john@atlanticmaritime.com')).toBeInTheDocument();
      expect(screen.getByText('Sarah Johnson')).toBeInTheDocument();
      expect(screen.getByText('sarah@atlanticmaritime.com')).toBeInTheDocument();

      // Check role badges
      expect(screen.getByText('admin')).toBeInTheDocument();
      expect(screen.getByText('manager')).toBeInTheDocument();
      expect(screen.getByText('inspector')).toBeInTheDocument();
      expect(screen.getByText('viewer')).toBeInTheDocument();

      // Check status badges
      const activeStatuses = screen.getAllByText('active');
      expect(activeStatuses.length).toBeGreaterThan(0);
      expect(screen.getByText('pending')).toBeInTheDocument();
    });
  });

  describe('Security Settings', () => {
    it('should show security configuration options', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      await user.click(screen.getByRole('button', { name: /security settings/i }));

      // Check security features
      expect(screen.getByText('Two-Factor Authentication')).toBeInTheDocument();
      expect(screen.getByText('Single Sign-On (SSO)')).toBeInTheDocument();
      expect(screen.getByText('Password Policy')).toBeInTheDocument();

      // Check toggles/settings exist
      const toggles = screen.getAllByRole('checkbox');
      expect(toggles.length).toBeGreaterThan(0);
    });
  });

  describe('Subscription & Billing', () => {
    it('should show subscription information', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      await user.click(screen.getByRole('button', { name: /subscription & billing/i }));

      // Check subscription details
      expect(screen.getByText('Enterprise')).toBeInTheDocument();
      expect(screen.getByText(/unlimited vessels/i)).toBeInTheDocument();
      expect(screen.getByText(/advanced reporting/i)).toBeInTheDocument();
      expect(screen.getByText(/api access/i)).toBeInTheDocument();
      expect(screen.getByText(/sso/i)).toBeInTheDocument();
      expect(screen.getByText(/custom branding/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', () => {
      render(<OrganizationSettingsPage />);

      expect(screen.getByRole('heading', { level: 1, name: 'Organization Settings' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 3, name: 'Organization Profile' })).toBeInTheDocument();
    });

    it('should have proper form labels in edit mode', async () => {
      const user = userEvent.setup();
      render(<OrganizationSettingsPage />);

      // Enter edit mode
      await user.click(screen.getByRole('button', { name: /edit profile/i }));

      // Check for labeled inputs
      expect(screen.getByLabelText(/organization name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/phone/i)).toBeInTheDocument();
    });

    it('should have proper button accessibility', () => {
      render(<OrganizationSettingsPage />);

      // Check tab buttons have accessible names
      const tabButtons = screen.getAllByRole('button');
      tabButtons.forEach(button => {
        expect(button).toHaveAccessibleName();
      });
    });
  });
});
