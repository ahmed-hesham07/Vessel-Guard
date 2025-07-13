import { test, expect } from '@playwright/test'

test.describe('Calculation Workflows', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/auth/login')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')
  })

  test('should create ASME B31.3 calculation', async ({ page }) => {
    await page.goto('/calculations/asme-b31-3')
    
    // Fill calculation form
    await page.fill('input[name="pipe_diameter"]', '10')
    await page.fill('input[name="wall_thickness"]', '0.5')
    await page.fill('input[name="design_pressure"]', '150')
    await page.fill('input[name="design_temperature"]', '200')
    
    // Submit calculation
    await page.click('button[type="submit"]')
    
    // Check results
    await expect(page.locator('[data-testid="calculation-results"]')).toBeVisible()
    await expect(page.locator('text=Allowable Pressure')).toBeVisible()
  })

  test('should save calculation results', async ({ page }) => {
    await page.goto('/calculations/asme-b31-3')
    
    // Fill and submit calculation
    await page.fill('input[name="pipe_diameter"]', '12')
    await page.fill('input[name="wall_thickness"]', '0.375')
    await page.fill('input[name="design_pressure"]', '100')
    await page.fill('input[name="design_temperature"]', '150')
    await page.click('button[type="submit"]')
    
    // Save results
    await page.click('button:has-text("Save Calculation")')
    await page.fill('input[name="calculation_name"]', 'Test Piping Calculation')
    await page.click('button:has-text("Save")')
    
    // Verify save success
    await expect(page.locator('text=Calculation saved successfully')).toBeVisible()
  })

  test('should validate calculation inputs', async ({ page }) => {
    await page.goto('/calculations/asme-b31-3')
    
    // Try to submit with invalid inputs
    await page.fill('input[name="pipe_diameter"]', '-5')
    await page.fill('input[name="wall_thickness"]', '0')
    await page.click('button[type="submit"]')
    
    // Check for validation errors
    await expect(page.locator('text=Diameter must be positive')).toBeVisible()
    await expect(page.locator('text=Wall thickness must be greater than 0')).toBeVisible()
  })
})

test.describe('Project Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')
  })

  test('should create new project', async ({ page }) => {
    await page.goto('/dashboard/projects')
    
    await page.click('button:has-text("New Project")')
    await page.fill('input[name="name"]', 'Test Refinery Project')
    await page.fill('textarea[name="description"]', 'A test project for E2E testing')
    await page.selectOption('select[name="type"]', 'refinery')
    await page.click('button[type="submit"]')
    
    // Verify project creation
    await expect(page.locator('text=Test Refinery Project')).toBeVisible()
  })

  test('should edit project details', async ({ page }) => {
    await page.goto('/dashboard/projects')
    
    // Click on existing project
    await page.click('[data-testid="project-card"]:first-child')
    await page.click('button:has-text("Edit Project")')
    
    // Update project details
    await page.fill('input[name="name"]', 'Updated Project Name')
    await page.click('button[type="submit"]')
    
    // Verify update
    await expect(page.locator('text=Updated Project Name')).toBeVisible()
  })
})

test.describe('Vessel Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')
  })

  test('should add new vessel', async ({ page }) => {
    await page.goto('/dashboard/vessels')
    
    await page.click('button:has-text("Add Vessel")')
    await page.fill('input[name="tag_number"]', 'V-101')
    await page.fill('input[name="description"]', 'Test Pressure Vessel')
    await page.selectOption('select[name="vessel_type"]', 'pressure_vessel')
    await page.fill('input[name="design_pressure"]', '150')
    await page.fill('input[name="design_temperature"]', '200')
    await page.click('button[type="submit"]')
    
    // Verify vessel creation
    await expect(page.locator('text=V-101')).toBeVisible()
    await expect(page.locator('text=Test Pressure Vessel')).toBeVisible()
  })

  test('should filter vessels by type', async ({ page }) => {
    await page.goto('/dashboard/vessels')
    
    // Apply filter
    await page.selectOption('select[name="vessel_type_filter"]', 'pressure_vessel')
    
    // Verify filter works
    await expect(page.locator('[data-testid="vessel-card"]')).toHaveCount(1)
  })
})
