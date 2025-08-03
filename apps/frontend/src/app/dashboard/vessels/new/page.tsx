'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowLeft, Save, Loader2, Shield, Target, Calculator } from 'lucide-react'
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
  owner?: {
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
  service_fluid: string
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
    service_fluid: '',
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
        service_fluid: formData.service_fluid,
        location: formData.location,
        design_code: "ASME VIII Div 1", // Default value
        design_pressure: parseFloat(formData.design_pressure) || 0,
        design_temperature: parseFloat(formData.design_temperature) || 0,
        operating_pressure: parseFloat(formData.operating_pressure) || 0,
        operating_temperature: parseFloat(formData.operating_temperature) || 0,
        material_specification: formData.material_grade,
        diameter: parseFloat(formData.diameter) || 0,
        length: parseFloat(formData.length) || 0,
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
    <div className="min-h-full w-full">
      {/* Page Header */}
      <div className="mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm p-8">
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Shield className="h-8 w-8 text-cyan-400" />
                  <h1 className="text-4xl font-bold text-slate-100">Add New Vessel</h1>
                </div>
                <p className="text-lg text-slate-300">
                  Register a new asset or component in the system
                  <span className="text-cyan-400 font-medium"> - Professional registration</span>
                </p>
              </div>
              <Button 
                variant="ghost" 
                asChild
                className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50 border border-slate-700/50"
              >
                <Link href="/dashboard/vessels">
                  <ArrowLeft className="h-5 w-5 mr-2" />
                  Back to Vessels
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto space-y-6">

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="bg-red-500/10 border-red-500/20 text-red-400">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5"></div>
        <CardHeader className="relative border-b border-slate-700/50">
          <CardTitle className="text-slate-100 flex items-center space-x-2">
            <Shield className="w-5 h-5 text-cyan-400" />
            <span>Asset Information</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="relative">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <Label htmlFor="tag_number" className="text-slate-200">Tag Number *</Label>
                <Input
                  id="tag_number"
                  type="text"
                  value={formData.tag_number}
                  onChange={(e) => handleInputChange('tag_number', e.target.value)}
                  placeholder="V-101"
                  required
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                />
              </div>

              <div className="md:col-span-2">
                <Label htmlFor="name" className="text-slate-200">Asset Name *</Label>
                <Input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Enter asset name"
                  required
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                />
              </div>

              <div className="md:col-span-2">
                <Label htmlFor="description" className="text-slate-200">Description</Label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Describe the asset purpose and specifications"
                  rows={3}
                  className="mt-1 block w-full rounded-md bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                />
              </div>

              <div>
                <Label htmlFor="asset_type" className="text-slate-200">Asset Type *</Label>
                <select
                  id="asset_type"
                  value={formData.asset_type}
                  onChange={(e) => handleInputChange('asset_type', e.target.value)}
                  className="mt-1 block w-full rounded-md bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-cyan-500/50 focus:ring-cyan-500/25"
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
                <Label htmlFor="project_id" className="text-slate-200">Project *</Label>
                <select
                  id="project_id"
                  value={formData.project_id}
                  onChange={(e) => handleInputChange('project_id', e.target.value)}
                  required
                  disabled={isLoadingProjects}
                  className="mt-1 block w-full rounded-md bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-cyan-500/50 focus:ring-cyan-500/25"
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
                <Label htmlFor="service_fluid" className="text-slate-200">Service Fluid</Label>
                <Input
                  id="service_fluid"
                  type="text"
                  value={formData.service_fluid}
                  onChange={(e) => handleInputChange('service_fluid', e.target.value)}
                  placeholder="e.g., Water, Steam, Natural Gas, Crude Oil"
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                />
              </div>

              <div>
                <Label htmlFor="location" className="text-slate-200">Location</Label>
                <Input
                  id="location"
                  type="text"
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  placeholder="e.g., Plant A, Unit 1"
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                />
              </div>
            </div>

            {/* Design Parameters */}
            <div className="border-t border-slate-700/50 pt-6">
              <h3 className="text-lg font-medium text-slate-100 mb-4 flex items-center space-x-2">
                <Target className="w-5 h-5 text-cyan-400" />
                <span>Design Parameters</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="design_pressure" className="text-slate-200">Design Pressure (psi)</Label>
                  <Input
                    id="design_pressure"
                    type="number"
                    value={formData.design_pressure}
                    onChange={(e) => handleInputChange('design_pressure', e.target.value)}
                    placeholder="150"
                    min="0"
                    step="0.1"
                    className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                  />
                </div>

                <div>
                  <Label htmlFor="design_temperature" className="text-slate-200">Design Temperature (°F)</Label>
                  <Input
                    id="design_temperature"
                    type="number"
                    value={formData.design_temperature}
                    onChange={(e) => handleInputChange('design_temperature', e.target.value)}
                    placeholder="200"
                    step="0.1"
                    className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                  />
                </div>

                <div>
                  <Label htmlFor="operating_pressure" className="text-slate-200">Operating Pressure (psi)</Label>
                  <Input
                    id="operating_pressure"
                    type="number"
                    value={formData.operating_pressure}
                    onChange={(e) => handleInputChange('operating_pressure', e.target.value)}
                    placeholder="100"
                    min="0"
                    step="0.1"
                    className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                  />
                </div>

                <div>
                  <Label htmlFor="operating_temperature" className="text-slate-200">Operating Temperature (°F)</Label>
                  <Input
                    id="operating_temperature"
                    type="number"
                    value={formData.operating_temperature}
                    onChange={(e) => handleInputChange('operating_temperature', e.target.value)}
                    placeholder="150"
                    step="0.1"
                    className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                  />
                </div>

                <div>
                  <Label htmlFor="material_grade" className="text-slate-200">Material Grade</Label>
                  <Input
                    id="material_grade"
                    type="text"
                    value={formData.material_grade}
                    onChange={(e) => handleInputChange('material_grade', e.target.value)}
                    placeholder="SA-516 Gr. 70"
                    className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                  />
                </div>

                <div>
                  <Label htmlFor="corrosion_allowance" className="text-slate-200">Corrosion Allowance (in)</Label>
                  <Input
                    id="corrosion_allowance"
                    type="number"
                    value={formData.corrosion_allowance}
                    onChange={(e) => handleInputChange('corrosion_allowance', e.target.value)}
                    placeholder="0.125"
                    min="0"
                    step="0.001"
                    className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
                  />
                </div>
              </div>
            </div>

            {/* Dimensional Parameters */}
            <div className="border-t border-slate-700/50 pt-6">
              <h3 className="text-lg font-medium text-slate-100 mb-4 flex items-center space-x-2">
                <Calculator className="w-5 h-5 text-blue-400" />
                <span>Dimensional Parameters</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="diameter" className="text-slate-200">Diameter (in)</Label>
                  <Input
                    id="diameter"
                    type="number"
                    value={formData.diameter}
                    onChange={(e) => handleInputChange('diameter', e.target.value)}
                    placeholder="36"
                    min="0"
                    step="0.1"
                    className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/25"
                  />
                </div>

                <div>
                  <Label htmlFor="length" className="text-slate-200">Length (in)</Label>
                  <Input
                    id="length"
                    type="number"
                    value={formData.length}
                    onChange={(e) => handleInputChange('length', e.target.value)}
                    placeholder="120"
                    min="0"
                    step="0.1"
                    className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/25"
                  />
                </div>

                <div>
                  <Label htmlFor="wall_thickness" className="text-slate-200">Wall Thickness (in)</Label>
                  <Input
                    id="wall_thickness"
                    type="number"
                    value={formData.wall_thickness}
                    onChange={(e) => handleInputChange('wall_thickness', e.target.value)}
                    placeholder="0.5"
                    min="0"
                    step="0.001"
                    className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/25"
                  />
                </div>

                <div>
                  <Label htmlFor="joint_efficiency" className="text-slate-200">Joint Efficiency</Label>
                  <Input
                    id="joint_efficiency"
                    type="number"
                    value={formData.joint_efficiency}
                    onChange={(e) => handleInputChange('joint_efficiency', e.target.value)}
                    placeholder="1.0"
                    min="0"
                    max="1"
                    step="0.01"
                    className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/25"
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3">
              <Button 
                variant="outline" 
                type="button" 
                asChild
                className="bg-slate-800/50 border-slate-600/50 text-slate-300 hover:text-slate-100 hover:bg-slate-700/50"
              >
                <Link href="/dashboard/vessels">Cancel</Link>
              </Button>
              <Button 
                type="submit" 
                disabled={isSubmitting}
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
              >
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
    </div>
  )
}
