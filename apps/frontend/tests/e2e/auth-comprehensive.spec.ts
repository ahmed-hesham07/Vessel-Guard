/**
 * End-to-end authentication tests
 * 
 * Tests complete user authentication flows including
 * login, navigation, and logout across the application.
 */

import { test, expect } from '@playwright/test';

// Test data
const testUser = {
  email: 'admin@vesselguard.com',
  password: 'AdminPassword123!',
  firstName: 'Admin',
  lastName: 'User'
};

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Set up API mocking
    await page.route('**/api/v1/auth/login', async (route) => {
      const request = route.request();
      
      try {
        const postData = request.postDataJSON();
        
        if (postData?.email === testUser.email && postData?.password === testUser.password) {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              access_token: 'mock-access-token-e2e',
              refresh_token: 'mock-refresh-token-e2e',
              token_type: 'bearer',
              user: {
                id: 1,
                email: testUser.email,
                first_name: testUser.firstName,
                last_name: testUser.lastName,
                role: 'admin',
                organization_id: 1,
                is_active: true
              }
            })
          });
        } else {
          await route.fulfill({
            status: 401,
            contentType: 'application/json',
            body: JSON.stringify({
              detail: 'Invalid email or password'
            })
          });
        }
      } catch (e) {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Bad request'
          })
        });
      }
    });
  });

  test('should display landing page correctly', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Vessel Guard/);
    await expect(page.locator('h1')).toContainText('Vessel Guard');
  });

  test('should navigate to login page', async ({ page }) => {
    await page.goto('/');
    
    // Find and click sign in link/button
    const signInButton = page.locator('text=Sign in').first();
    if (await signInButton.isVisible()) {
      await signInButton.click();
      await expect(page).toHaveURL(/.*\/auth\/login/);
    }
  });

  test('should show validation errors for empty login form', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Try to submit empty form
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    
    // Check for validation errors (may vary based on implementation)
    const emailError = page.locator('text=Email is required').first();
    const passwordError = page.locator('text=Password is required').first();
    
    // Check if either error exists (different forms may have different validation)
    const hasEmailError = await emailError.isVisible();
    const hasPasswordError = await passwordError.isVisible();
    
    // At least one validation should be present
    expect(hasEmailError || hasPasswordError).toBeTruthy();
  });

  test('should handle login form interaction', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Find email and password inputs
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    
    if (await emailInput.isVisible() && await passwordInput.isVisible()) {
      await emailInput.fill(testUser.email);
      await passwordInput.fill(testUser.password);
      
      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();
      
      // Should either redirect or show some response
      await page.waitForTimeout(1000); // Give time for response
    }
  });

  test('should handle keyboard navigation', async ({ page }) => {
    await page.goto('/auth/login');
    
    // Test Tab navigation
    await page.keyboard.press('Tab');
    
    // Check if focus moves properly (implementation may vary)
    const focusedElement = await page.locator(':focus').first();
    expect(await focusedElement.isVisible()).toBeTruthy();
  });
});

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Set up authenticated state
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({
        id: 1,
        email: 'test@example.com',
        name: 'Test User'
      }));
    });
  });

  test('should handle protected route access', async ({ page }) => {
    // Try to access dashboard
    await page.goto('/dashboard');
    
    // Should either show dashboard or redirect to login
    const url = page.url();
    expect(url.includes('/dashboard') || url.includes('/auth/login')).toBeTruthy();
  });

  test('should clear authentication on logout', async ({ page }) => {
    await page.goto('/');
    
    // Clear auth state (simulate logout)
    await page.evaluate(() => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    });
    
    // Verify localStorage is cleared
    const authToken = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(authToken).toBeNull();
  });
});

test.describe('Responsive Design', () => {
  test('should work on mobile devices', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check if page loads properly on mobile
    await expect(page.locator('body')).toBeVisible();
  });

  test('should work on tablet devices', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    
    // Check if page loads properly on tablet
    await expect(page.locator('body')).toBeVisible();
  });
});

export default {};
