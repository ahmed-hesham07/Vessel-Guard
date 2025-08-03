'use client'

import { useState } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { 
  Calculator, 
  ArrowLeft, 
  Loader2,
  CheckCircle,
  AlertTriangle,
  Info,
  Plus,
  Trash2,
  Copy,
  FileText
} from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface BatchCalculation {
  id: string
  name: string
  description: string
  calculation_type: string
  vessel_tag: string
  vessel_name: string
  design_pressure: string
  design_temperature: string
  inside_diameter: string
  material_specification: string
  design_code: string
  enabled: boolean
}

interface Project {
  id: number
  name: string
}

export default function BatchCalculationPage() {
  const { token } = useAuth()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<string>('')
  
  const [calculations, setCalculations] = useState<BatchCalculation[]>([
    {
      id: '1',
      name: 'V-101 Thickness Calculation',
      description: 'Cylindrical shell thickness calculation',
      calculation_type: 'ASME_VIII_DIV_1',
      vessel_tag: 'V-101',
      vessel_name: 'Pressure Vessel 101',
      design_pressure: '150',
      design_temperature: '350',
      inside_diameter: '48',
      material_specification: 'SA-516 Grade 70',
      design_code: 'ASME VIII Div 1',
      enabled: true
    }
  ])

  const calculationTypes = [
    { value: 'ASME_VIII_DIV_1', label: 'ASME VIII Div 1 - Pressure Vessels' },
    { value: 'ASME_B31_3', label: 'ASME B31.3 - Process Piping' },
    { value: 'API_579', label: 'API 579 - Fitness for Service' }
  ]

  const materialSpecifications = [
    'SA-516 Grade 70',
    'SA-106 Grade B',
    'SA-335 P11',
    'SA-213 T22',
    'SA-240 304',
    'SA-240 316'
  ]

  const designCodes = [
    'ASME VIII Div 1',
    'ASME VIII Div 2',
    'EN 13445',
    'API 650',
    'ASME B31.3'
  ]

  const handleCalculationChange = (id: string, field: keyof BatchCalculation, value: string | boolean) => {
    setCalculations(prev => prev.map(calc => 
      calc.id === id ? { ...calc, [field]: value } : calc
    ))
  }

  const addCalculation = () => {
    const newId = (calculations.length + 1).toString()
    const newCalculation: BatchCalculation = {
      id: newId,
      name: `V-${newId.padStart(3, '0')} Calculation`,
      description: 'Engineering calculation',
      calculation_type: 'ASME_VIII_DIV_1',
      vessel_tag: `V-${newId.padStart(3, '0')}`,
      vessel_name: `Vessel ${newId.padStart(3, '0')}`,
      design_pressure: '150',
      design_temperature: '350',
      inside_diameter: '48',
      material_specification: 'SA-516 Grade 70',
      design_code: 'ASME VIII Div 1',
      enabled: true
    }
    setCalculations(prev => [...prev, newCalculation])
  }

  const removeCalculation = (id: string) => {
    setCalculations(prev => prev.filter(calc => calc.id !== id))
  }

  const duplicateCalculation = (id: string) => {
    const calcToDuplicate = calculations.find(calc => calc.id === id)
    if (!calcToDuplicate) return

    const newId = (calculations.length + 1).toString()
    const duplicatedCalculation: BatchCalculation = {
      ...calcToDuplicate,
      id: newId,
      name: `${calcToDuplicate.name} (Copy)`,
      vessel_tag: `${calcToDuplicate.vessel_tag}-COPY`,
      vessel_name: `${calcToDuplicate.vessel_name} (Copy)`,
      enabled: true
    }
    setCalculations(prev => [...prev, duplicatedCalculation])
  }

  const validateCalculations = () => {
    if (!selectedProjectId) {
      setError('Please select a project')
      return false
    }

    const enabledCalculations = calculations.filter(calc => calc.enabled)
    if (enabledCalculations.length === 0) {
      setError('At least one calculation must be enabled')
      return false
    }

    for (const calc of enabledCalculations) {
      if (!calc.name.trim()) {
        setError(`Calculation ${calc.id}: Name is required`)
        return false
      }
      if (!calc.vessel_tag.trim()) {
        setError(`Calculation ${calc.id}: Vessel tag is required`)
        return false
      }
      if (!calc.design_pressure || parseFloat(calc.design_pressure) <= 0) {
        setError(`Calculation ${calc.id}: Design pressure must be positive`)
        return false
      }
      if (!calc.design_temperature || parseFloat(calc.design_temperature) <= 0) {
        setError(`Calculation ${calc.id}: Design temperature must be positive`)
        return false
      }
      if (!calc.inside_diameter || parseFloat(calc.inside_diameter) <= 0) {
        setError(`Calculation ${calc.id}: Inside diameter must be positive`)
        return false
      }
    }

    setError('')
    return true
  }

  const handleSubmit = async () => {
    if (!validateCalculations()) return

    setIsLoading(true)
    setError('')

    try {
      const enabledCalculations = calculations.filter(calc => calc.enabled)
      const results = []

      for (const calc of enabledCalculations) {
        try {
          // Create vessel first
          const vesselPayload = {
            tag_number: calc.vessel_tag,
            name: calc.vessel_name,
            vessel_type: 'pressure_vessel',
            design_pressure: parseFloat(calc.design_pressure),
            design_temperature: parseFloat(calc.design_temperature),
            diameter: parseFloat(calc.inside_diameter),
            material_specification: calc.material_specification,
            design_code: calc.design_code,
            description: calc.description
          }

          const vessel = await apiService.createVessel(vesselPayload, token!) as { id: number }

          // Create calculation
          const calculationPayload = {
            name: calc.name,
            description: calc.description,
            project_id: parseInt(selectedProjectId),
            vessel_id: vessel.id,
            calculation_type: calc.calculation_type, // Use design code directly
            input_parameters: calc.calculation_type === 'ASME_VIII_DIV_1' ? {
              design_pressure: parseFloat(calc.design_pressure),
              design_temperature: parseFloat(calc.design_temperature),
              inside_diameter: parseFloat(calc.inside_diameter),
              wall_thickness: 0.25, // Default value
              material_specification: calc.material_specification,
              joint_efficiency: 1.0
            } : calc.calculation_type === 'ASME_B31_3' ? {
              design_pressure: parseFloat(calc.design_pressure),
              design_temperature: parseFloat(calc.design_temperature),
              nominal_diameter: parseFloat(calc.inside_diameter),
              schedule: '40S', // Default schedule
              material_specification: calc.material_specification
            } : calc.calculation_type === 'API_579' ? {
              design_pressure: parseFloat(calc.design_pressure),
              design_temperature: parseFloat(calc.design_temperature),
              current_thickness: 0.2, // Default current thickness
              original_thickness: 0.25, // Default original thickness
              material_specification: calc.material_specification
            } : {}
          }

          const calculation = await apiService.createCalculation(calculationPayload, token!) as { id: number }
          results.push({ vessel, calculation, name: calc.name })
        } catch (error) {
          console.error(`Failed to create calculation ${calc.name}:`, error)
          results.push({ error: true, name: calc.name, message: error instanceof Error ? error.message : 'Unknown error' })
        }
      }

      const successCount = results.filter(r => !r.error).length
      const errorCount = results.filter(r => r.error).length

      if (errorCount === 0) {
        setSuccess(`Successfully created ${successCount} calculations!`)
        router.push('/dashboard/calculations')
      } else {
        setError(`Created ${successCount} calculations, ${errorCount} failed. Check console for details.`)
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to create calculations')
    } finally {
      setIsLoading(false)
    }
  }

  const renderCalculationCard = (calculation: BatchCalculation) => (
    <Card key={calculation.id} className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center">
            <Calculator className="w-5 h-5 mr-2" />
            {calculation.name}
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => duplicateCalculation(calculation.id)}
            >
              <Copy className="w-4 h-4 mr-1" />
              Duplicate
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => removeCalculation(calculation.id)}
              disabled={calculations.length === 1}
            >
              <Trash2 className="w-4 h-4 mr-1" />
              Remove
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id={`enabled-${calculation.id}`}
            checked={calculation.enabled}
            onChange={(e) => handleCalculationChange(calculation.id, 'enabled', e.target.checked)}
            className="rounded"
          />
          <Label htmlFor={`enabled-${calculation.id}`}>Enable this calculation</Label>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor={`name-${calculation.id}`}>Calculation Name</Label>
            <Input
              id={`name-${calculation.id}`}
              value={calculation.name}
              onChange={(e) => handleCalculationChange(calculation.id, 'name', e.target.value)}
              placeholder="Calculation name"
            />
          </div>
          <div>
            <Label htmlFor={`type-${calculation.id}`}>Calculation Type</Label>
            <Select 
              value={calculation.calculation_type} 
              onValueChange={(value) => handleCalculationChange(calculation.id, 'calculation_type', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {calculationTypes.map(type => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div>
          <Label htmlFor={`description-${calculation.id}`}>Description</Label>
          <Textarea
            id={`description-${calculation.id}`}
            value={calculation.description}
            onChange={(e) => handleCalculationChange(calculation.id, 'description', e.target.value)}
            placeholder="Calculation description"
            rows={2}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor={`vessel-tag-${calculation.id}`}>Vessel Tag</Label>
            <Input
              id={`vessel-tag-${calculation.id}`}
              value={calculation.vessel_tag}
              onChange={(e) => handleCalculationChange(calculation.id, 'vessel_tag', e.target.value)}
              placeholder="e.g., V-101"
            />
          </div>
          <div>
            <Label htmlFor={`vessel-name-${calculation.id}`}>Vessel Name</Label>
            <Input
              id={`vessel-name-${calculation.id}`}
              value={calculation.vessel_name}
              onChange={(e) => handleCalculationChange(calculation.id, 'vessel_name', e.target.value)}
              placeholder="Vessel name"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor={`pressure-${calculation.id}`}>Design Pressure (psi)</Label>
            <Input
              id={`pressure-${calculation.id}`}
              type="number"
              value={calculation.design_pressure}
              onChange={(e) => handleCalculationChange(calculation.id, 'design_pressure', e.target.value)}
              placeholder="150"
            />
          </div>
          <div>
            <Label htmlFor={`temperature-${calculation.id}`}>Design Temperature (°F)</Label>
            <Input
              id={`temperature-${calculation.id}`}
              type="number"
              value={calculation.design_temperature}
              onChange={(e) => handleCalculationChange(calculation.id, 'design_temperature', e.target.value)}
              placeholder="350"
            />
          </div>
          <div>
            <Label htmlFor={`diameter-${calculation.id}`}>Inside Diameter (inches)</Label>
            <Input
              id={`diameter-${calculation.id}`}
              type="number"
              value={calculation.inside_diameter}
              onChange={(e) => handleCalculationChange(calculation.id, 'inside_diameter', e.target.value)}
              placeholder="48"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor={`material-${calculation.id}`}>Material Specification</Label>
            <Select 
              value={calculation.material_specification} 
              onValueChange={(value) => handleCalculationChange(calculation.id, 'material_specification', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {materialSpecifications.map(material => (
                  <SelectItem key={material} value={material}>
                    {material}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor={`design-code-${calculation.id}`}>Design Code</Label>
            <Select 
              value={calculation.design_code} 
              onValueChange={(value) => handleCalculationChange(calculation.id, 'design_code', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {designCodes.map(code => (
                  <SelectItem key={code} value={code}>
                    {code}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Batch Calculations</h1>
          <p className="text-gray-600">Create multiple calculations quickly with similar parameters</p>
        </div>
        <Button variant="outline" asChild>
          <Link href="/dashboard/calculations">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Calculations
          </Link>
        </Button>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Project Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Project Selection</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="project">Select Project *</Label>
              <Select value={selectedProjectId} onValueChange={setSelectedProjectId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a project" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Sample Project 1</SelectItem>
                  <SelectItem value="2">Sample Project 2</SelectItem>
                  <SelectItem value="3">Sample Project 3</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button variant="outline" onClick={() => router.push('/dashboard/projects/new')}>
                <Plus className="w-4 h-4 mr-2" />
                Create New Project
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Calculations */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Calculations ({calculations.filter(c => c.enabled).length} enabled)</h2>
          <Button onClick={addCalculation}>
            <Plus className="w-4 h-4 mr-2" />
            Add Calculation
          </Button>
        </div>

        {calculations.map(renderCalculationCard)}
      </div>

      {/* Submit */}
      <div className="flex justify-end space-x-4">
        <Button variant="outline" asChild>
          <Link href="/dashboard/calculations">
            Cancel
          </Link>
        </Button>
        <Button onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Creating Calculations...
            </>
          ) : (
            <>
              <Calculator className="w-4 h-4 mr-2" />
              Create {calculations.filter(c => c.enabled).length} Calculations
            </>
          )}
        </Button>
      </div>
    </div>
  )
} 