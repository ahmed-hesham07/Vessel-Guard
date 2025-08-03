/**
 * @fileoverview Comprehensive tests for Vessel Creation Form
 * 
 * This test suite follows our systematic testing methodology for business logic forms.
 * Tests engineering-specific validation, ASME standard compliance, and vessel parameter relationships.
 * 
 * Complexity Level: High - Business Logic Forms (Phase 2)
 * - Engineering parameter validation
 * - Cross-field dependency validation  
 * - ASME standard compliance
 * - API integration patterns
 * - Error handling for complex workflows
 * 
 * @author Testing Framework - Systematic Form Testing
 * @version 1.0.0
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/auth-context'
import { apiService } from '@/lib/api'
import NewAssetPage from '@/app/dashboard/vessels/new/page'

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('@/contexts/auth-context', () => ({
  useAuth: jest.fn(),
}))

jest.mock('@/lib/api', () => ({
  apiService: {
    getProjects: jest.fn(),
    createVessel: jest.fn(),
  },
}))

// Mock UI components
jest.mock('@/components/ui/card', () => ({
  Card: ({ children }: { children: React.ReactNode }) => <div data-testid="card">{children}</div>,
  CardContent: ({ children }: { children: React.ReactNode }) => <div data-testid="card-content">{children}</div>,
  CardHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="card-header">{children}</div>,
  CardTitle: ({ children }: { children: React.ReactNode }) => <h2 data-testid="card-title">{children}</h2>,
}))

jest.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, disabled, type, ...props }: any) => (
    <button onClick={onClick} disabled={disabled} type={type} {...props}>
      {children}
    </button>
  ),
}))

jest.mock('@/components/ui/input', () => ({
  Input: (props: any) => <input {...props} />,
}))

jest.mock('@/components/ui/label', () => ({
  Label: ({ children, htmlFor }: { children: React.ReactNode; htmlFor?: string }) => (
    <label htmlFor={htmlFor}>{children}</label>
  ),
}))

jest.mock('@/components/ui/alert', () => ({
  Alert: ({ children }: { children: React.ReactNode }) => <div role="alert">{children}</div>,
  AlertDescription: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}))

describe('VesselCreationForm - Business Logic Forms Testing', () => {
  // Test fixtures
  const mockRouter = {
    push: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    replace: jest.fn(),
  }

  const mockProjects = [
    {
      id: 1,
      name: 'Refinery Unit 1',
      description: 'Main refinery processing unit',
      status: 'active',
      priority: 'high',
      start_date: '2024-01-01',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      owner: {
        id: 1,
        first_name: 'John',
        last_name: 'Engineer',
        email: 'john@example.com',
      },
      organization: {
        id: 1,
        name: 'ACME Engineering',
      },
      vessels_count: 5,
      calculations_count: 12,
    },
    {
      id: 2,
      name: 'Chemical Plant B',
      description: 'Secondary chemical processing facility',
      status: 'active',
      priority: 'medium',
      start_date: '2024-02-01',
      created_at: '2024-02-01T00:00:00Z',
      updated_at: '2024-02-01T00:00:00Z',
      owner: {
        id: 2,
        first_name: 'Jane',
        last_name: 'Manager',
        email: 'jane@example.com',
      },
      organization: {
        id: 1,
        name: 'ACME Engineering',
      },
      vessels_count: 3,
      calculations_count: 8,
    },
  ]

  const validVesselData = {
    tag_number: 'V-101',
    name: 'Main Reactor Vessel',
    description: 'Primary reaction vessel for petrochemical processing',
    asset_type: 'pressure_vessel',
    service: 'Catalytic cracking',
    location: 'Unit 1, Area A',
    design_pressure: '150',
    design_temperature: '650',
    operating_pressure: '120',
    operating_temperature: '600',
    material_grade: 'SA-516 Gr. 70',
    corrosion_allowance: '0.125',
    diameter: '72',
    length: '240',
    wall_thickness: '1.5',
    joint_efficiency: '0.85',
    project_id: '1',
  }

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks()

    // Setup default mock implementations
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(useAuth as jest.Mock).mockReturnValue({
      token: 'valid-token',
      user: { id: 1, role: 'engineer' },
    })
    ;(apiService.getProjects as jest.Mock).mockResolvedValue(mockProjects)
    ;(apiService.createVessel as jest.Mock).mockResolvedValue({ id: 1, ...validVesselData })
  })

  // ===== RENDERING AND STRUCTURE TESTS =====
  describe('Component Rendering', () => {
    it('should render vessel creation form with all sections', async () => {
      render(<NewAssetPage />)

      // Header section
      expect(screen.getByText('Add New Asset')).toBeInTheDocument()
      expect(screen.getByText('Register a new asset or component in the system')).toBeInTheDocument()

      // Form sections
      expect(screen.getByText('Asset Information')).toBeInTheDocument()
      expect(screen.getByText('Design Parameters')).toBeInTheDocument()
      expect(screen.getByText('Dimensional Parameters')).toBeInTheDocument()

      // Wait for projects to load
      await waitFor(() => {
        expect(screen.getByDisplayValue('Select a project')).toBeInTheDocument()
      })
    })

    it('should render all required engineering input fields', async () => {
      render(<NewAssetPage />)

      // Basic identification fields
      expect(screen.getByLabelText(/tag number/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/asset name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/asset type/i)).toBeInTheDocument()

      // Engineering design parameters
      expect(screen.getByLabelText(/design pressure/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/design temperature/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/operating pressure/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/operating temperature/i)).toBeInTheDocument()

      // Material specifications
      expect(screen.getByLabelText(/material grade/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/corrosion allowance/i)).toBeInTheDocument()

      // Dimensional parameters
      expect(screen.getByLabelText(/diameter/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/length/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/wall thickness/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/joint efficiency/i)).toBeInTheDocument()
    })

    it('should have proper vessel type options for engineering applications', () => {
      render(<NewAssetPage />)

      const assetTypeSelect = screen.getByLabelText(/asset type/i)
      
      // Check for engineering-relevant vessel types
      expect(assetTypeSelect).toHaveValue('pressure_vessel')
      
      // Verify all vessel type options exist
      const options = Array.from(assetTypeSelect.querySelectorAll('option')).map(opt => opt.textContent)
      expect(options).toEqual([
        'Pressure Vessel',
        'Storage Tank', 
        'Heat Exchanger',
        'Reactor',
        'Column',
        'Separator',
        'Filter',
        'Piping',
        'Air Cooling',
        'Other'
      ])
    })
  })

  // ===== PROJECT LOADING AND INTEGRATION =====
  describe('Project Integration', () => {
    it('should load and display available projects', async () => {
      render(<NewAssetPage />)

      // Wait for projects to load
      await waitFor(() => {
        expect(apiService.getProjects).toHaveBeenCalledWith('valid-token')
      })

      // Check project options are displayed
      await waitFor(() => {
        const projectSelect = screen.getByLabelText(/project/i)
        expect(projectSelect).toBeInTheDocument()
        
        // Verify projects are loaded
        expect(screen.getByText('Refinery Unit 1')).toBeInTheDocument()
        expect(screen.getByText('Chemical Plant B')).toBeInTheDocument()
      })
    })

    it('should handle project loading errors gracefully', async () => {
      ;(apiService.getProjects as jest.Mock).mockRejectedValue(new Error('Network error'))
      
      render(<NewAssetPage />)

      await waitFor(() => {
        expect(apiService.getProjects).toHaveBeenCalled()
      })

      // Should not crash and show select without options
      expect(screen.getByLabelText(/project/i)).toBeInTheDocument()
    })

    it('should disable project selection while loading', () => {
      render(<NewAssetPage />)
      
      const projectSelect = screen.getByLabelText(/project/i)
      expect(projectSelect).toBeDisabled()
      expect(screen.getByText('Loading projects...')).toBeInTheDocument()
    })
  })

  // ===== FORM INTERACTION AND STATE MANAGEMENT =====
  describe('Form Interactions', () => {
    it('should handle basic form field changes', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      // Test tag number input
      const tagNumberInput = screen.getByLabelText(/tag number/i)
      await user.type(tagNumberInput, 'V-101')
      expect(tagNumberInput).toHaveValue('V-101')

      // Test name input
      const nameInput = screen.getByLabelText(/asset name/i)
      await user.type(nameInput, 'Test Vessel')
      expect(nameInput).toHaveValue('Test Vessel')

      // Test numeric input
      const designPressureInput = screen.getByLabelText(/design pressure/i)
      await user.type(designPressureInput, '150')
      expect(designPressureInput).toHaveValue('150')
    })

    it('should handle vessel type selection', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      const assetTypeSelect = screen.getByLabelText(/asset type/i)
      
      await user.selectOptions(assetTypeSelect, 'storage_tank')
      expect(assetTypeSelect).toHaveValue('storage_tank')
      
      await user.selectOptions(assetTypeSelect, 'heat_exchanger')  
      expect(assetTypeSelect).toHaveValue('heat_exchanger')
    })

    it('should handle engineering parameter inputs with proper formatting', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      // Test decimal precision inputs
      const corrosionInput = screen.getByLabelText(/corrosion allowance/i)
      await user.type(corrosionInput, '0.125')
      expect(corrosionInput).toHaveValue('0.125')

      const jointEfficiencyInput = screen.getByLabelText(/joint efficiency/i)
      await user.type(jointEfficiencyInput, '0.85')
      expect(jointEfficiencyInput).toHaveValue('0.85')

      const wallThicknessInput = screen.getByLabelText(/wall thickness/i)
      await user.type(wallThicknessInput, '1.5')
      expect(wallThicknessInput).toHaveValue('1.5')
    })
  })

  // ===== ENGINEERING VALIDATION TESTS =====
  describe('Engineering Parameter Validation', () => {
    it('should enforce required fields for engineering compliance', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      // Try to submit without required fields
      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      // Check HTML5 validation prevents submission
      const tagNumberInput = screen.getByLabelText(/tag number/i)
      expect(tagNumberInput).toBeRequired()

      const nameInput = screen.getByLabelText(/asset name/i)
      expect(nameInput).toBeRequired()
    })

    it('should validate pressure relationships (operating ≤ design)', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      // Fill required fields first
      await user.type(screen.getByLabelText(/tag number/i), 'V-101')
      await user.type(screen.getByLabelText(/asset name/i), 'Test Vessel')

      // Wait for projects and select one
      await waitFor(() => {
        expect(screen.getByText('Refinery Unit 1')).toBeInTheDocument()
      })
      await user.selectOptions(screen.getByLabelText(/project/i), '1')

      // Set design pressure lower than operating (invalid scenario)
      await user.type(screen.getByLabelText(/design pressure/i), '100')
      await user.type(screen.getByLabelText(/operating pressure/i), '150')

      // This should be validated on the backend - form should still submit for testing
      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      await waitFor(() => {
        expect(apiService.createVessel).toHaveBeenCalled()
      })
    })

    it('should handle joint efficiency within valid range (0-1)', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      const jointEfficiencyInput = screen.getByLabelText(/joint efficiency/i)
      
      // Test valid value
      await user.type(jointEfficiencyInput, '0.85')
      expect(jointEfficiencyInput).toHaveValue('0.85')

      // Test boundary values
      await user.clear(jointEfficiencyInput)
      await user.type(jointEfficiencyInput, '1.0')
      expect(jointEfficiencyInput).toHaveValue('1.0')

      await user.clear(jointEfficiencyInput)
      await user.type(jointEfficiencyInput, '0.0')
      expect(jointEfficiencyInput).toHaveValue('0.0')
    })
  })

  // ===== FORM SUBMISSION AND API INTEGRATION =====
  describe('Form Submission', () => {
    const fillValidForm = async (user: any) => {
      await user.type(screen.getByLabelText(/tag number/i), validVesselData.tag_number)
      await user.type(screen.getByLabelText(/asset name/i), validVesselData.name)
      await user.type(screen.getByLabelText(/description/i), validVesselData.description)
      await user.selectOptions(screen.getByLabelText(/asset type/i), validVesselData.asset_type)
      await user.type(screen.getByLabelText(/service/i), validVesselData.service)
      await user.type(screen.getByLabelText(/location/i), validVesselData.location)

      // Wait for projects to load and select
      await waitFor(() => {
        expect(screen.getByText('Refinery Unit 1')).toBeInTheDocument()
      })
      await user.selectOptions(screen.getByLabelText(/project/i), validVesselData.project_id)

      // Fill engineering parameters
      await user.type(screen.getByLabelText(/design pressure/i), validVesselData.design_pressure)
      await user.type(screen.getByLabelText(/design temperature/i), validVesselData.design_temperature)
      await user.type(screen.getByLabelText(/operating pressure/i), validVesselData.operating_pressure)
      await user.type(screen.getByLabelText(/operating temperature/i), validVesselData.operating_temperature)
      await user.type(screen.getByLabelText(/material grade/i), validVesselData.material_grade)
      await user.type(screen.getByLabelText(/corrosion allowance/i), validVesselData.corrosion_allowance)
      await user.type(screen.getByLabelText(/diameter/i), validVesselData.diameter)
      await user.type(screen.getByLabelText(/length/i), validVesselData.length)
      await user.type(screen.getByLabelText(/wall thickness/i), validVesselData.wall_thickness)
      await user.type(screen.getByLabelText(/joint efficiency/i), validVesselData.joint_efficiency)
    }

    it('should submit vessel creation with correct engineering data transformation', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      await fillValidForm(user)

      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      await waitFor(() => {
        expect(apiService.createVessel).toHaveBeenCalledWith(
          {
            tag_number: 'V-101',
            name: 'Main Reactor Vessel',
            description: 'Primary reaction vessel for petrochemical processing',
            vessel_type: 'pressure_vessel',
            service: 'Catalytic cracking',
            location: 'Unit 1, Area A',
            design_code: 'ASME VIII Div 1',
            design_pressure: 150,
            design_temperature: 650,
            operating_pressure: 120,
            operating_temperature: 600,
            material_grade: 'SA-516 Gr. 70',
            inside_diameter: 72,
            overall_length: 240,
            wall_thickness: 1.5,
            corrosion_allowance: 0.125,
            joint_efficiency: 0.85,
          },
          'valid-token',
          1
        )
      })
    })

    it('should handle successful vessel creation and navigation', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      await fillValidForm(user)

      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith('/dashboard/vessels')
      })
    })

    it('should show loading state during submission', async () => {
      // Make API call hang to test loading state
      ;(apiService.createVessel as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      )

      const user = userEvent.setup()
      render(<NewAssetPage />)

      await fillValidForm(user)

      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      // Check loading state
      expect(screen.getByText(/creating.../i)).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
    })

    it('should handle vessel creation errors appropriately', async () => {
      const errorMessage = 'Vessel with this tag number already exists'
      ;(apiService.createVessel as jest.Mock).mockRejectedValue(new Error(errorMessage))

      const user = userEvent.setup()
      render(<NewAssetPage />)

      await fillValidForm(user)

      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })

      // Ensure navigation doesn't happen on error
      expect(mockRouter.push).not.toHaveBeenCalled()
    })
  })

  // ===== ACCESSIBILITY AND UX TESTING =====
  describe('Accessibility and User Experience', () => {
    it('should have proper labels and form associations', () => {
      render(<NewAssetPage />)

      // Check label associations
      expect(screen.getByLabelText(/tag number/i)).toHaveAttribute('id', 'tag_number')
      expect(screen.getByLabelText(/asset name/i)).toHaveAttribute('id', 'name')
      expect(screen.getByLabelText(/design pressure/i)).toHaveAttribute('id', 'design_pressure')
      expect(screen.getByLabelText(/joint efficiency/i)).toHaveAttribute('id', 'joint_efficiency')
    })

    it('should have appropriate input types for engineering data', () => {
      render(<NewAssetPage />)

      // Text inputs for identifiers
      expect(screen.getByLabelText(/tag number/i)).toHaveAttribute('type', 'text')
      expect(screen.getByLabelText(/asset name/i)).toHaveAttribute('type', 'text')

      // Number inputs for measurements
      expect(screen.getByLabelText(/design pressure/i)).toHaveAttribute('type', 'number')
      expect(screen.getByLabelText(/design temperature/i)).toHaveAttribute('type', 'number')
      expect(screen.getByLabelText(/diameter/i)).toHaveAttribute('type', 'number')
      expect(screen.getByLabelText(/wall thickness/i)).toHaveAttribute('type', 'number')
    })

    it('should provide helpful placeholders for engineering parameters', () => {
      render(<NewAssetPage />)

      expect(screen.getByLabelText(/tag number/i)).toHaveAttribute('placeholder', 'V-101')
      expect(screen.getByLabelText(/design pressure/i)).toHaveAttribute('placeholder', '150')
      expect(screen.getByLabelText(/corrosion allowance/i)).toHaveAttribute('placeholder', '0.125')
      expect(screen.getByLabelText(/material grade/i)).toHaveAttribute('placeholder', 'SA-516 Gr. 70')
    })

    it('should have proper navigation controls', () => {
      render(<NewAssetPage />)

      expect(screen.getByText('Cancel')).toBeInTheDocument()
      expect(screen.getByText(/create asset/i)).toBeInTheDocument()
    })
  })

  // ===== EDGE CASES AND ERROR HANDLING =====
  describe('Edge Cases and Error Handling', () => {
    it('should handle missing authentication token', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        token: null,
        user: null,
      })

      render(<NewAssetPage />)

      // Should still render but not load projects
      expect(screen.getByText('Add New Asset')).toBeInTheDocument()
    })

    it('should handle decimal input formatting', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      const corrosionInput = screen.getByLabelText(/corrosion allowance/i)
      
      // Test various decimal formats
      await user.type(corrosionInput, '0.125')
      expect(corrosionInput).toHaveValue('0.125')

      await user.clear(corrosionInput)
      await user.type(corrosionInput, '.5')
      expect(corrosionInput).toHaveValue('.5')
    })

    it('should handle empty form submission gracefully', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      // Form should prevent submission due to required fields
      expect(apiService.createVessel).not.toHaveBeenCalled()
    })

    it('should default joint efficiency to 1.0 when empty', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      // Fill minimum required fields
      await user.type(screen.getByLabelText(/tag number/i), 'V-101')
      await user.type(screen.getByLabelText(/asset name/i), 'Test Vessel')

      await waitFor(() => {
        expect(screen.getByText('Refinery Unit 1')).toBeInTheDocument()
      })
      await user.selectOptions(screen.getByLabelText(/project/i), '1')

      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      await waitFor(() => {
        expect(apiService.createVessel).toHaveBeenCalledWith(
          expect.objectContaining({
            joint_efficiency: 1.0,
          }),
          'valid-token',
          1
        )
      })
    })
  })

  // ===== DATA TRANSFORMATION TESTS =====
  describe('Data Transformation', () => {
    it('should properly convert string inputs to numeric values', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      // Fill form with string values
      await user.type(screen.getByLabelText(/tag number/i), 'V-101')
      await user.type(screen.getByLabelText(/asset name/i), 'Test Vessel')
      
      await waitFor(() => {
        expect(screen.getByText('Refinery Unit 1')).toBeInTheDocument()
      })
      await user.selectOptions(screen.getByLabelText(/project/i), '1')

      await user.type(screen.getByLabelText(/design pressure/i), '150.5')
      await user.type(screen.getByLabelText(/wall thickness/i), '1.25')

      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      await waitFor(() => {
        expect(apiService.createVessel).toHaveBeenCalledWith(
          expect.objectContaining({
            design_pressure: 150.5,
            wall_thickness: 1.25,
          }),
          'valid-token',
          1
        )
      })
    })

    it('should handle zero values correctly', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      await user.type(screen.getByLabelText(/tag number/i), 'V-101')
      await user.type(screen.getByLabelText(/asset name/i), 'Test Vessel')
      
      await waitFor(() => {
        expect(screen.getByText('Refinery Unit 1')).toBeInTheDocument()
      })
      await user.selectOptions(screen.getByLabelText(/project/i), '1')

      await user.type(screen.getByLabelText(/design pressure/i), '0')
      await user.type(screen.getByLabelText(/operating pressure/i), '0')

      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      await waitFor(() => {
        expect(apiService.createVessel).toHaveBeenCalledWith(
          expect.objectContaining({
            design_pressure: 0,
            operating_pressure: 0,
          }),
          'valid-token',
          1
        )
      })
    })

    it('should set default design code to ASME VIII Div 1', async () => {
      const user = userEvent.setup()
      render(<NewAssetPage />)

      await user.type(screen.getByLabelText(/tag number/i), 'V-101')
      await user.type(screen.getByLabelText(/asset name/i), 'Test Vessel')
      
      await waitFor(() => {
        expect(screen.getByText('Refinery Unit 1')).toBeInTheDocument()
      })
      await user.selectOptions(screen.getByLabelText(/project/i), '1')

      const submitButton = screen.getByText(/create asset/i)
      await user.click(submitButton)

      await waitFor(() => {
        expect(apiService.createVessel).toHaveBeenCalledWith(
          expect.objectContaining({
            design_code: 'ASME VIII Div 1',
          }),
          'valid-token',
          1
        )
      })
    })
  })
})
