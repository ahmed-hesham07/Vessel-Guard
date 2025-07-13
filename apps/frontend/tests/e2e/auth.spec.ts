import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display landing page correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/Vessel Guard/)
    await expect(page.locator('h1')).toContainText('Vessel Guard')
  })

  test('should navigate to login page', async ({ page }) => {
    await page.click('text=Sign in')
    await expect(page).toHaveURL(/.*\/auth\/login/)
    await expect(page.locator('h1')).toContainText('Sign in')
  })

  test('should navigate to register page', async ({ page }) => {
    await page.click('text=Get Started')
    await expect(page).toHaveURL(/.*\/auth\/register/)
    await expect(page.locator('h1')).toContainText('Create account')
  })

  test('should show validation errors on invalid login', async ({ page }) => {
    await page.goto('/auth/login')
    
    // Try to submit empty form
    await page.click('button[type="submit"]')
    
    // Check for validation errors
    await expect(page.locator('text=Email is required')).toBeVisible()
    await expect(page.locator('text=Password is required')).toBeVisible()
  })

  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/auth/login')
    
    // Fill in test credentials
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    
    // Submit form
    await page.click('button[type="submit"]')
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/)
  })
})

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/auth/login')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')
  })

  test('should display dashboard correctly', async ({ page }) => {
    await expect(page.locator('text=Welcome back')).toBeVisible()
    await expect(page.locator('[data-testid="sidebar"]')).toBeVisible()
  })

  test('should navigate to projects page', async ({ page }) => {
    await page.click('text=Projects')
    await expect(page).toHaveURL(/.*\/dashboard\/projects/)
  })

  test('should navigate to vessels page', async ({ page }) => {
    await page.click('text=Vessels')
    await expect(page).toHaveURL(/.*\/dashboard\/vessels/)
  })

  test('should navigate to calculations page', async ({ page }) => {
    await page.click('text=Calculations')
    await expect(page).toHaveURL(/.*\/calculations/)
  })
})

test.describe('Responsive Design', () => {
  test('should work on mobile devices', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')
    
    // Check mobile menu
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible()
    
    // Test mobile navigation
    await page.click('[data-testid="mobile-menu-button"]')
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible()
  })

  test('should work on tablet devices', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.goto('/')
    
    // Verify layout adapts properly
    await expect(page.locator('main')).toBeVisible()
  })
})
