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
import { 
  Calculator, 
  ArrowLeft, 
  Loader2,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface Project {
  id: number
  name: string
}

interface Vessel {
  id: number
  name: string
  tag_number: string
}

interface Material {
  id: number
  name: string
  specification: string
  grade: string
}

const CALCULATION_TYPES = [
  {
    id: 'ASME_B31_3',
    name: 'ASME B31.3 - Process Piping',
    description: 'Calculate pipe wall thickness and pressure ratings for process piping systems',
    icon: Calculator
  },
  {
    id: 'ASME_VIII_DIV_1',
    name: 'ASME VIII Div 1 - Pressure Vessels',
    description: 'Calculate pressure vessel thickness and design requirements',
    icon: Calculator
  },
  {
    id: 'API_579',
    name: 'API 579 - Fitness for Service',
    description: 'Assess remaining life and fitness for service of equipment',
    icon: Calculator
  }
]

export default function NewCalculationPage() {
  const { token } = useAuth()
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [selectedType, setSelectedType] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Form data
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    project_id: '',
    vessel_id: '',
    calculation_type: '',
    input_parameters: {}
  })

  // ASME B31.3 specific parameters
  const [b31_3_params, setB31_3Params] = useState({
    design_pressure: '',
    design_temperature: '',
    pipe_outside_diameter: '',
    wall_thickness: '',
    material_id: '',
    joint_efficiency: '1.0',
    corrosion_allowance: '0.0625',
    temperature_derating_factor: '1.0'
  })

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleB31_3ParamChange = (field: string, value: string) => {
    setB31_3Params(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const validateStep1 = () => {
    if (!formData.name.trim()) {
      setError('Calculation name is required')
      return false
    }
    if (!selectedType) {
      setError('Please select a calculation type')
      return false
    }
    if (!formData.project_id) {
      setError('Please select a project')
      return false
    }
    setError('')
    return true
  }

  const validateStep2 = () => {
    const params = b31_3_params
    const requiredFields = ['design_pressure', 'design_temperature', 'pipe_outside_diameter', 'wall_thickness']
    
    for (const field of requiredFields) {
      if (!params[field as keyof typeof params] || parseFloat(params[field as keyof typeof params]) <= 0) {
        setError(`${field.replace(/_/g, ' ')} must be a positive number`)
        return false
      }
    }
    setError('')
    return true
  }

  const handleNext = () => {
    if (step === 1 && !validateStep1()) return
    if (step === 2 && !validateStep2()) return
    setStep(step + 1)
  }

  const handleSubmit = async () => {
    if (!validateStep2()) return

    setIsLoading(true)
    setError('')

    try {
      const calculationData = {
        name: formData.name,
        description: formData.description,
        project_id: parseInt(formData.project_id),
        vessel_id: formData.vessel_id ? parseInt(formData.vessel_id) : null,
        calculation_type: selectedType, // Use design code directly
        input_parameters: selectedType === 'ASME_B31_3' ? {
          design_pressure: parseFloat(b31_3_params.design_pressure),
          design_temperature: parseFloat(b31_3_params.design_temperature),
          nominal_diameter: parseFloat(b31_3_params.pipe_outside_diameter), // Map to expected parameter name
          schedule: b31_3_params.wall_thickness, // Map wall thickness to schedule
          material_specification: b31_3_params.material_specification || 'SA-106 Grade B'
        } : selectedType === 'ASME_VIII_DIV_1' ? {
          design_pressure: parseFloat(b31_3_params.design_pressure),
          design_temperature: parseFloat(b31_3_params.design_temperature),
          inside_diameter: parseFloat(b31_3_params.pipe_outside_diameter), // Use as inside diameter for pressure vessels
          wall_thickness: parseFloat(b31_3_params.wall_thickness),
          material_specification: b31_3_params.material_specification || 'SA-516 Grade 70',
          joint_efficiency: parseFloat(b31_3_params.joint_efficiency || '1.0')
        } : selectedType === 'API_579' ? {
          design_pressure: parseFloat(b31_3_params.design_pressure),
          design_temperature: parseFloat(b31_3_params.design_temperature),
          current_thickness: parseFloat(b31_3_params.wall_thickness),
          original_thickness: parseFloat(b31_3_params.wall_thickness) * 1.1, // Assume 10% loss
          material_specification: b31_3_params.material_specification || 'SA-516 Grade 70'
        } : {}
      }

      const result = await apiService.createCalculation(calculationData, token!) as { id: number }
      router.push(`/dashboard/calculations/${result.id}`)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to create calculation')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Link href="/dashboard/calculations">
          <Button variant="outline" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">New Calculation</h1>
          <p className="text-gray-600">Create a new engineering calculation</p>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center space-x-4">
        <div className={`flex items-center ${step >= 1 ? 'text-primary' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
            step >= 1 ? 'border-primary bg-primary text-white' : 'border-gray-300'
          }`}>
            {step > 1 ? <CheckCircle className="h-4 w-4" /> : '1'}
          </div>
          <span className="ml-2 text-sm font-medium">Basic Information</span>
        </div>
        <div className="flex-1 h-px bg-gray-300" />
        <div className={`flex items-center ${step >= 2 ? 'text-primary' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
            step >= 2 ? 'border-primary bg-primary text-white' : 'border-gray-300'
          }`}>
            {step > 2 ? <CheckCircle className="h-4 w-4" /> : '2'}
          </div>
          <span className="ml-2 text-sm font-medium">Parameters</span>
        </div>
        <div className="flex-1 h-px bg-gray-300" />
        <div className={`flex items-center ${step >= 3 ? 'text-primary' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
            step >= 3 ? 'border-primary bg-primary text-white' : 'border-gray-300'
          }`}>
            3
          </div>
          <span className="ml-2 text-sm font-medium">Review & Submit</span>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Step 1: Basic Information */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="name">Calculation Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="e.g., Main Steam Line Analysis"
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Brief description of the calculation"
                  className="mt-1"
                  rows={3}
                />
              </div>
            </div>

            <div>
              <Label>Calculation Type *</Label>
              <div className="mt-2 grid grid-cols-1 gap-3">
                {CALCULATION_TYPES.map((type) => (
                  <div
                    key={type.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedType === type.id
                        ? 'border-primary bg-primary/5'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedType(type.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <type.icon className="h-5 w-5 text-primary mt-0.5" />
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{type.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{type.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="project">Project *</Label>
                <Select value={formData.project_id} onValueChange={(value) => handleInputChange('project_id', value)}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select a project" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Project Alpha</SelectItem>
                    <SelectItem value="2">Project Beta</SelectItem>
                    <SelectItem value="3">Project Gamma</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="vessel">Vessel (Optional)</Label>
                <Select value={formData.vessel_id} onValueChange={(value) => handleInputChange('vessel_id', value)}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select a vessel" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Vessel A-101</SelectItem>
                    <SelectItem value="2">Vessel B-202</SelectItem>
                    <SelectItem value="3">Vessel C-303</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: ASME B31.3 Parameters */}
      {step === 2 && selectedType === 'ASME_B31_3' && (
        <Card>
          <CardHeader>
            <CardTitle>ASME B31.3 - Process Piping Parameters</CardTitle>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Enter the design parameters for your piping calculation. All values should be in imperial units (psi, °F, inches).
              </AlertDescription>
            </Alert>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="design_pressure">Design Pressure (psi) *</Label>
                <Input
                  id="design_pressure"
                  type="number"
                  step="0.1"
                  value={b31_3_params.design_pressure}
                  onChange={(e) => handleB31_3ParamChange('design_pressure', e.target.value)}
                  placeholder="e.g., 600"
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="design_temperature">Design Temperature (°F) *</Label>
                <Input
                  id="design_temperature"
                  type="number"
                  step="1"
                  value={b31_3_params.design_temperature}
                  onChange={(e) => handleB31_3ParamChange('design_temperature', e.target.value)}
                  placeholder="e.g., 750"
                  className="mt-1"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="pipe_outside_diameter">Pipe Outside Diameter (inches) *</Label>
                <Input
                  id="pipe_outside_diameter"
                  type="number"
                  step="0.001"
                  value={b31_3_params.pipe_outside_diameter}
                  onChange={(e) => handleB31_3ParamChange('pipe_outside_diameter', e.target.value)}
                  placeholder="e.g., 6.625"
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="wall_thickness">Wall Thickness (inches) *</Label>
                <Input
                  id="wall_thickness"
                  type="number"
                  step="0.001"
                  value={b31_3_params.wall_thickness}
                  onChange={(e) => handleB31_3ParamChange('wall_thickness', e.target.value)}
                  placeholder="e.g., 0.280"
                  className="mt-1"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <Label htmlFor="joint_efficiency">Joint Efficiency</Label>
                <Select value={b31_3_params.joint_efficiency} onValueChange={(value) => handleB31_3ParamChange('joint_efficiency', value)}>
                  <SelectTrigger className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1.0">1.0 (Seamless)</SelectItem>
                    <SelectItem value="0.85">0.85 (Welded)</SelectItem>
                    <SelectItem value="0.70">0.70 (Lap Welded)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="corrosion_allowance">Corrosion Allowance (inches)</Label>
                <Input
                  id="corrosion_allowance"
                  type="number"
                  step="0.001"
                  value={b31_3_params.corrosion_allowance}
                  onChange={(e) => handleB31_3ParamChange('corrosion_allowance', e.target.value)}
                  placeholder="e.g., 0.0625"
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="temperature_derating_factor">Temperature Derating Factor</Label>
                <Input
                  id="temperature_derating_factor"
                  type="number"
                  step="0.01"
                  value={b31_3_params.temperature_derating_factor}
                  onChange={(e) => handleB31_3ParamChange('temperature_derating_factor', e.target.value)}
                  placeholder="e.g., 0.85"
                  className="mt-1"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="material">Material Specification</Label>
              <Select value={b31_3_params.material_id} onValueChange={(value) => handleB31_3ParamChange('material_id', value)}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select material" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">A106 Grade B</SelectItem>
                  <SelectItem value="2">A53 Grade B</SelectItem>
                  <SelectItem value="3">A312 TP304</SelectItem>
                  <SelectItem value="4">A312 TP316</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Review and Submit */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>Review Calculation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">Calculation Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Name:</span> {formData.name}
                </div>
                <div>
                  <span className="font-medium">Type:</span> {CALCULATION_TYPES.find(t => t.id === selectedType)?.name}
                </div>
                <div>
                  <span className="font-medium">Design Pressure:</span> {b31_3_params.design_pressure} psi
                </div>
                <div>
                  <span className="font-medium">Design Temperature:</span> {b31_3_params.design_temperature} °F
                </div>
                <div>
                  <span className="font-medium">Pipe Diameter:</span> {b31_3_params.pipe_outside_diameter} inches
                </div>
                <div>
                  <span className="font-medium">Wall Thickness:</span> {b31_3_params.wall_thickness} inches
                </div>
              </div>
            </div>

            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                This calculation will be performed according to ASME B31.3 standards. 
                The results will include allowable pressure, safety factors, and compliance assessment.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={() => setStep(step - 1)}
          disabled={step === 1}
        >
          Previous
        </Button>
        
        <div className="flex space-x-2">
          {step < 3 ? (
            <Button onClick={handleNext}>
              Next
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating Calculation...
                </>
              ) : (
                'Create Calculation'
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
