'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowLeft, Save, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface Project {
  id: number
  name: string
  description: string
  status: string
  priority: string
  start_date: string
  end_date?: string
  created_at: string
  updated_at: string
  owner: {
    id: number
    first_name: string
    last_name: string
    email: string
  }
  organization: {
    id: number
    name: string
  }
  vessels_count: number
  calculations_count: number
}

interface AssetFormData {
  tag_number: string
  name: string
  description: string
  asset_type: string
  service: string
  location: string
  design_pressure: string
  design_temperature: string
  operating_pressure: string
  operating_temperature: string
  material_grade: string
  corrosion_allowance: string
  joint_efficiency: string
  safety_factor: string
  diameter: string
  length: string
  wall_thickness: string
  project_id: string
}

export default function NewAssetPage() {
  const { token } = useAuth()
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoadingProjects, setIsLoadingProjects] = useState(true)
  const [formData, setFormData] = useState<AssetFormData>({
    tag_number: '',
    name: '',
    description: '',
    asset_type: 'pressure_vessel',
    service: '',
    location: '',
    design_pressure: '',
    design_temperature: '',
    operating_pressure: '',
    operating_temperature: '',
    material_grade: '',
    corrosion_allowance: '',
    joint_efficiency: '',
    safety_factor: '',
    diameter: '',
    length: '',
    wall_thickness: '',
    project_id: ''
  })

  // Load projects on component mount
  useEffect(() => {
    const fetchProjects = async () => {
      if (!token) {
        setIsLoadingProjects(false)
        return
      }
      
      try {
        setIsLoadingProjects(true)
        const response = await apiService.getProjects(token)
        setProjects(response)
      } catch (error) {
        console.error('Error fetching projects:', error)
        setProjects([])
      } finally {
        setIsLoadingProjects(false)
      }
    }
    
    fetchProjects()
  }, [token])

  const handleInputChange = (field: keyof AssetFormData, value: string) => {
    setFormData(prev => ({
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
      // Convert string values to appropriate types
      const submitData = {
        tag_number: formData.tag_number,
        name: formData.name,
        description: formData.description,
        vessel_type: formData.asset_type,
        service: formData.service,
        location: formData.location,
        design_code: "ASME VIII Div 1", // Default value
        design_pressure: parseFloat(formData.design_pressure) || 0,
        design_temperature: parseFloat(formData.design_temperature) || 0,
        operating_pressure: parseFloat(formData.operating_pressure) || 0,
        operating_temperature: parseFloat(formData.operating_temperature) || 0,
        material_grade: formData.material_grade,
        inside_diameter: parseFloat(formData.diameter) || 0,
        overall_length: parseFloat(formData.length) || 0,
        wall_thickness: parseFloat(formData.wall_thickness) || 0,
        corrosion_allowance: parseFloat(formData.corrosion_allowance) || 0,
        joint_efficiency: parseFloat(formData.joint_efficiency) || 1.0,
      }

      await apiService.createVessel(submitData, token, parseInt(formData.project_id))
      router.push('/dashboard/vessels')
    } catch (error: any) {
      console.error('Error creating asset:', error)
      setError(error.message || 'Failed to create asset')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/dashboard/vessels">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Add New Asset</h1>
            <p className="text-gray-600">
              Register a new asset or component in the system
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
          <CardTitle>Asset Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <Label htmlFor="tag_number">Tag Number *</Label>
                <Input
                  id="tag_number"
                  type="text"
                  value={formData.tag_number}
                  onChange={(e) => handleInputChange('tag_number', e.target.value)}
                  placeholder="V-101"
                  required
                  className="mt-1"
                />
              </div>

              <div className="md:col-span-2">
                <Label htmlFor="name">Asset Name *</Label>
                <Input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Enter asset name"
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
                  placeholder="Describe the asset purpose and specifications"
                  rows={3}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>

              <div>
                <Label htmlFor="asset_type">Asset Type *</Label>
                <select
                  id="asset_type"
                  value={formData.asset_type}
                  onChange={(e) => handleInputChange('asset_type', e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="pressure_vessel">Pressure Vessel</option>
                  <option value="storage_tank">Storage Tank</option>
                  <option value="heat_exchanger">Heat Exchanger</option>
                  <option value="reactor">Reactor</option>
                  <option value="column">Column</option>
                  <option value="separator">Separator</option>
                  <option value="filter">Filter</option>
                  <option value="piping">Piping</option>
                  <option value="air_cooling">Air Cooling</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <Label htmlFor="project_id">Project *</Label>
                <select
                  id="project_id"
                  value={formData.project_id}
                  onChange={(e) => handleInputChange('project_id', e.target.value)}
                  required
                  disabled={isLoadingProjects}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">
                    {isLoadingProjects ? 'Loading projects...' : 'Select a project'}
                  </option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="service">Service</Label>
                <Input
                  id="service"
                  type="text"
                  value={formData.service}
                  onChange={(e) => handleInputChange('service', e.target.value)}
                  placeholder="e.g., Water storage, Steam generation"
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  type="text"
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  placeholder="e.g., Plant A, Unit 1"
                  className="mt-1"
                />
              </div>
            </div>

            {/* Design Parameters */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Design Parameters</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="design_pressure">Design Pressure (psi)</Label>
                  <Input
                    id="design_pressure"
                    type="number"
                    value={formData.design_pressure}
                    onChange={(e) => handleInputChange('design_pressure', e.target.value)}
                    placeholder="150"
                    min="0"
                    step="0.1"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="design_temperature">Design Temperature (°F)</Label>
                  <Input
                    id="design_temperature"
                    type="number"
                    value={formData.design_temperature}
                    onChange={(e) => handleInputChange('design_temperature', e.target.value)}
                    placeholder="200"
                    step="0.1"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="operating_pressure">Operating Pressure (psi)</Label>
                  <Input
                    id="operating_pressure"
                    type="number"
                    value={formData.operating_pressure}
                    onChange={(e) => handleInputChange('operating_pressure', e.target.value)}
                    placeholder="100"
                    min="0"
                    step="0.1"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="operating_temperature">Operating Temperature (°F)</Label>
                  <Input
                    id="operating_temperature"
                    type="number"
                    value={formData.operating_temperature}
                    onChange={(e) => handleInputChange('operating_temperature', e.target.value)}
                    placeholder="150"
                    step="0.1"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="material_grade">Material Grade</Label>
                  <Input
                    id="material_grade"
                    type="text"
                    value={formData.material_grade}
                    onChange={(e) => handleInputChange('material_grade', e.target.value)}
                    placeholder="SA-516 Gr. 70"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="corrosion_allowance">Corrosion Allowance (in)</Label>
                  <Input
                    id="corrosion_allowance"
                    type="number"
                    value={formData.corrosion_allowance}
                    onChange={(e) => handleInputChange('corrosion_allowance', e.target.value)}
                    placeholder="0.125"
                    min="0"
                    step="0.001"
                    className="mt-1"
                  />
                </div>
              </div>
            </div>

            {/* Dimensional Parameters */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Dimensional Parameters</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="diameter">Diameter (in)</Label>
                  <Input
                    id="diameter"
                    type="number"
                    value={formData.diameter}
                    onChange={(e) => handleInputChange('diameter', e.target.value)}
                    placeholder="36"
                    min="0"
                    step="0.1"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="length">Length (in)</Label>
                  <Input
                    id="length"
                    type="number"
                    value={formData.length}
                    onChange={(e) => handleInputChange('length', e.target.value)}
                    placeholder="120"
                    min="0"
                    step="0.1"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="wall_thickness">Wall Thickness (in)</Label>
                  <Input
                    id="wall_thickness"
                    type="number"
                    value={formData.wall_thickness}
                    onChange={(e) => handleInputChange('wall_thickness', e.target.value)}
                    placeholder="0.5"
                    min="0"
                    step="0.001"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="joint_efficiency">Joint Efficiency</Label>
                  <Input
                    id="joint_efficiency"
                    type="number"
                    value={formData.joint_efficiency}
                    onChange={(e) => handleInputChange('joint_efficiency', e.target.value)}
                    placeholder="1.0"
                    min="0"
                    max="1"
                    step="0.01"
                    className="mt-1"
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3">
              <Button variant="outline" type="button" asChild>
                <Link href="/dashboard/vessels">Cancel</Link>
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Create Asset
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
