'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowLeft, Play, Loader2, Calculator } from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface CalculationFormData {
  vessel_id: string
  name: string
  description: string
  calculation_type: string
  input_parameters: {
    [key: string]: any
  }
}

interface PressureVesselParameters {
  design_pressure: string
  design_temperature: string
  internal_diameter: string
  wall_thickness: string
  material_grade: string
  allowable_stress: string
  joint_efficiency: string
  corrosion_allowance: string
  length: string
  operating_pressure: string
  operating_temperature: string
  safety_factor: string
  standard: string
}

export default function NewCalculationPage() {
  const { token } = useAuth()
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [vessels, setVessels] = useState<any[]>([])
  
  const [formData, setFormData] = useState<CalculationFormData>({
    vessel_id: '',
    name: '',
    description: '',
    calculation_type: 'pressure_vessel',
    input_parameters: {}
  })

  const [pressureVesselParams, setPressureVesselParams] = useState<PressureVesselParameters>({
    design_pressure: '',
    design_temperature: '',
    internal_diameter: '',
    wall_thickness: '',
    material_grade: '',
    allowable_stress: '',
    joint_efficiency: '1.0',
    corrosion_allowance: '0.0',
    length: '',
    operating_pressure: '',
    operating_temperature: '',
    safety_factor: '3.0',
    standard: 'ASME_VIII_DIV1'
  })

  // Load vessels on component mount
  useEffect(() => {
    const fetchVessels = async () => {
      if (!token) return
      
      try {
        const response = await apiService.getVessels(token)
        setVessels((response as any).items || response)
      } catch (error) {
        console.error('Error fetching vessels:', error)
      }
    }
    
    fetchVessels()
  }, [token])

  const handleInputChange = (field: keyof CalculationFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleParameterChange = (field: keyof PressureVesselParameters, value: string) => {
    setPressureVesselParams(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!token) return

    setIsSubmitting(true)
    setError(null)

    try {
      const submitData = {
        vessel_id: parseInt(formData.vessel_id),
        name: formData.name,
        description: formData.description,
        calculation_type: formData.calculation_type,
        input_parameters: formData.calculation_type === 'pressure_vessel' ? pressureVesselParams : formData.input_parameters,
      }

      await apiService.createCalculation(submitData, token)
      router.push('/dashboard/calculations')
    } catch (error: any) {
      console.error('Error creating calculation:', error)
      setError(error.message || 'Failed to create calculation')
    } finally {
      setIsSubmitting(false)
    }
  }

  const calculationTypes = [
    { value: 'pressure_vessel', label: 'Pressure Vessel Design' },
    { value: 'stress_analysis', label: 'Stress Analysis' },
    { value: 'fatigue_analysis', label: 'Fatigue Analysis' },
    { value: 'thermal_stress', label: 'Thermal Stress' },
    { value: 'nozzle_reinforcement', label: 'Nozzle Reinforcement' },
    { value: 'flange_design', label: 'Flange Design' },
    { value: 'support_design', label: 'Support Design' },
    { value: 'seismic_analysis', label: 'Seismic Analysis' },
    { value: 'wind_load', label: 'Wind Load Analysis' },
    { value: 'other', label: 'Other' }
  ]

  const standards = [
    { value: 'ASME_VIII_DIV1', label: 'ASME VIII Division 1' },
    { value: 'ASME_VIII_DIV2', label: 'ASME VIII Division 2' },
    { value: 'EN_13445', label: 'EN 13445' },
    { value: 'API_510', label: 'API 510' },
    { value: 'PD_5500', label: 'PD 5500' }
  ]

  const safetyFactors = [
    { value: '1.5', label: '1.5 (Testing)' },
    { value: '3.0', label: '3.0 (Normal Service)' },
    { value: '4.0', label: '4.0 (High Pressure)' },
    { value: '5.0', label: '5.0 (Critical Service)' }
  ]

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/dashboard/calculations">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Run Calculation</h1>
            <p className="text-gray-600">
              Create and execute engineering calculations for vessel analysis
            </p>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle>Calculation Setup</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="vessel_id">Vessel *</Label>
                <select
                  id="vessel_id"
                  value={formData.vessel_id}
                  onChange={(e) => handleInputChange('vessel_id', e.target.value)}
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">Select a vessel</option>
                  {vessels.map((vessel) => (
                    <option key={vessel.id} value={vessel.id}>
                      {vessel.tag_number} - {vessel.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="calculation_type">Calculation Type *</Label>
                <select
                  id="calculation_type"
                  value={formData.calculation_type}
                  onChange={(e) => handleInputChange('calculation_type', e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  {calculationTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-2">
                <Label htmlFor="name">Calculation Name *</Label>
                <Input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Enter calculation name"
                  required
                  className="mt-1"
                />
              </div>

              <div className="md:col-span-2">
                <Label htmlFor="description">Description</Label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Enter calculation description"
                  rows={3}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>

            {/* Pressure Vessel Parameters */}
            {formData.calculation_type === 'pressure_vessel' && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Pressure Vessel Parameters</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="design_pressure">Design Pressure (psi) *</Label>
                      <Input
                        id="design_pressure"
                        type="number"
                        step="0.01"
                        value={pressureVesselParams.design_pressure}
                        onChange={(e) => handleParameterChange('design_pressure', e.target.value)}
                        placeholder="150"
                        required
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="design_temperature">Design Temperature (°F) *</Label>
                      <Input
                        id="design_temperature"
                        type="number"
                        step="0.01"
                        value={pressureVesselParams.design_temperature}
                        onChange={(e) => handleParameterChange('design_temperature', e.target.value)}
                        placeholder="200"
                        required
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="internal_diameter">Internal Diameter (inches) *</Label>
                      <Input
                        id="internal_diameter"
                        type="number"
                        step="0.01"
                        value={pressureVesselParams.internal_diameter}
                        onChange={(e) => handleParameterChange('internal_diameter', e.target.value)}
                        placeholder="36"
                        required
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="wall_thickness">Wall Thickness (inches) *</Label>
                      <Input
                        id="wall_thickness"
                        type="number"
                        step="0.01"
                        value={pressureVesselParams.wall_thickness}
                        onChange={(e) => handleParameterChange('wall_thickness', e.target.value)}
                        placeholder="0.5"
                        required
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="material_grade">Material Grade</Label>
                      <Input
                        id="material_grade"
                        type="text"
                        value={pressureVesselParams.material_grade}
                        onChange={(e) => handleParameterChange('material_grade', e.target.value)}
                        placeholder="A516 Grade 70"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="allowable_stress">Allowable Stress (psi)</Label>
                      <Input
                        id="allowable_stress"
                        type="number"
                        step="0.01"
                        value={pressureVesselParams.allowable_stress}
                        onChange={(e) => handleParameterChange('allowable_stress', e.target.value)}
                        placeholder="20000"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="joint_efficiency">Joint Efficiency</Label>
                      <Input
                        id="joint_efficiency"
                        type="number"
                        step="0.01"
                        min="0.1"
                        max="1.0"
                        value={pressureVesselParams.joint_efficiency}
                        onChange={(e) => handleParameterChange('joint_efficiency', e.target.value)}
                        placeholder="1.0"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="corrosion_allowance">Corrosion Allowance (inches)</Label>
                      <Input
                        id="corrosion_allowance"
                        type="number"
                        step="0.01"
                        min="0"
                        value={pressureVesselParams.corrosion_allowance}
                        onChange={(e) => handleParameterChange('corrosion_allowance', e.target.value)}
                        placeholder="0.0"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="length">Length (inches)</Label>
                      <Input
                        id="length"
                        type="number"
                        step="0.01"
                        value={pressureVesselParams.length}
                        onChange={(e) => handleParameterChange('length', e.target.value)}
                        placeholder="120"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="operating_pressure">Operating Pressure (psi)</Label>
                      <Input
                        id="operating_pressure"
                        type="number"
                        step="0.01"
                        value={pressureVesselParams.operating_pressure}
                        onChange={(e) => handleParameterChange('operating_pressure', e.target.value)}
                        placeholder="120"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="operating_temperature">Operating Temperature (°F)</Label>
                      <Input
                        id="operating_temperature"
                        type="number"
                        step="0.01"
                        value={pressureVesselParams.operating_temperature}
                        onChange={(e) => handleParameterChange('operating_temperature', e.target.value)}
                        placeholder="180"
                        className="mt-1"
                      />
                    </div>

                    <div>
                      <Label htmlFor="safety_factor">Safety Factor</Label>
                      <select
                        id="safety_factor"
                        value={pressureVesselParams.safety_factor}
                        onChange={(e) => handleParameterChange('safety_factor', e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      >
                        {safetyFactors.map((factor) => (
                          <option key={factor.value} value={factor.value}>
                            {factor.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <Label htmlFor="standard">Design Standard</Label>
                      <select
                        id="standard"
                        value={pressureVesselParams.standard}
                        onChange={(e) => handleParameterChange('standard', e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                      >
                        {standards.map((standard) => (
                          <option key={standard.value} value={standard.value}>
                            {standard.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Other calculation types - placeholder for future expansion */}
            {formData.calculation_type !== 'pressure_vessel' && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Calculation Parameters</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-500">
                    <Calculator className="mx-auto h-12 w-12 mb-4" />
                    <p>Parameters for {calculationTypes.find(t => t.value === formData.calculation_type)?.label} calculations will be available in a future update.</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Actions */}
            <div className="flex justify-end space-x-3">
              <Button variant="outline" type="button" asChild>
                <Link href="/dashboard/calculations">Cancel</Link>
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Run Calculation
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
