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
  Building, 
  Shield, 
  Calculator, 
  ArrowLeft, 
  ArrowRight,
  Loader2,
  CheckCircle,
  AlertTriangle,
  Info,
  Plus,
  FileText,
  Users,
  Calendar,
  MapPin,
  Zap,
  Target,
  Sparkles
} from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface ProjectData {
  name: string
  description: string
  client_name: string
  client_contact: string
  location: string
  start_date: string
  end_date: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  tags: string
}

interface VesselData {
  tag_number: string
  name: string
  vessel_type: string
  design_pressure: string
  design_temperature: string
  inside_diameter: string
  wall_thickness: string
  material_specification: string
  design_code: string
  description: string
}

interface CalculationData {
  name: string
  description: string
  calculation_type: string
  input_parameters: Record<string, any>
}

interface WorkflowStep {
  id: number
  title: string
  description: string
  icon: any
  completed: boolean
}

export default function NewWorkflowPage() {
  const { token } = useAuth()
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  // Workflow data
  const [projectData, setProjectData] = useState<ProjectData>({
    name: '',
    description: '',
    client_name: '',
    client_contact: '',
    location: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    priority: 'medium',
    tags: ''
  })

  const [vesselData, setVesselData] = useState<VesselData>({
    tag_number: '',
    name: '',
    vessel_type: 'pressure_vessel',
    design_pressure: '',
    design_temperature: '',
    inside_diameter: '',
    wall_thickness: '',
    material_specification: 'SA-516 Grade 70',
    design_code: 'ASME VIII Div 1',
    description: ''
  })

  const [calculationData, setCalculationData] = useState<CalculationData>({
    name: '',
    description: '',
    calculation_type: 'ASME_VIII_DIV_1',
    input_parameters: {}
  })

  // Workflow state
  const [createdProjectId, setCreatedProjectId] = useState<number | null>(null)
  const [createdVesselId, setCreatedVesselId] = useState<number | null>(null)
  const [createdCalculationId, setCreatedCalculationId] = useState<number | null>(null)

  const workflowSteps: WorkflowStep[] = [
    {
      id: 1,
      title: 'Project Setup',
      description: 'Create a new engineering project',
      icon: Building,
      completed: !!createdProjectId
    },
    {
      id: 2,
      title: 'Vessel Registration',
      description: 'Add vessel or component details',
      icon: Shield,
      completed: !!createdVesselId
    },
    {
      id: 3,
      title: 'Calculation Setup',
      description: 'Configure engineering calculations',
      icon: Calculator,
      completed: !!createdCalculationId
    }
  ]

  const handleProjectDataChange = (field: keyof ProjectData, value: string) => {
    setProjectData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleVesselDataChange = (field: keyof VesselData, value: string) => {
    setVesselData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleCalculationDataChange = (field: keyof CalculationData, value: string) => {
    setCalculationData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const validateProjectData = () => {
    if (!projectData.name.trim()) {
      setError('Project name is required')
      return false
    }
    if (!projectData.description.trim()) {
      setError('Project description is required')
      return false
    }
    if (!projectData.client_name.trim()) {
      setError('Client name is required')
      return false
    }
    if (!projectData.start_date) {
      setError('Start date is required')
      return false
    }
    if (projectData.end_date && new Date(projectData.end_date) <= new Date(projectData.start_date)) {
      setError('End date must be after start date')
      return false
    }
    setError('')
    return true
  }

  const validateVesselData = () => {
    if (!vesselData.tag_number.trim()) {
      setError('Vessel tag number is required')
      return false
    }
    if (!vesselData.name.trim()) {
      setError('Vessel name is required')
      return false
    }
    if (!vesselData.design_pressure || parseFloat(vesselData.design_pressure) <= 0) {
      setError('Design pressure must be a positive number')
      return false
    }
    if (!vesselData.design_temperature || parseFloat(vesselData.design_temperature) <= 0) {
      setError('Design temperature must be a positive number')
      return false
    }
    if (!vesselData.inside_diameter || parseFloat(vesselData.inside_diameter) <= 0) {
      setError('Inside diameter must be a positive number')
      return false
    }
    setError('')
    return true
  }

  const validateCalculationData = () => {
    if (!calculationData.name.trim()) {
      setError('Calculation name is required')
      return false
    }
    if (!calculationData.calculation_type) {
      setError('Calculation type is required')
      return false
    }
    setError('')
    return true
  }

  const handleNext = async () => {
    if (currentStep === 1 && !validateProjectData()) return
    if (currentStep === 2 && !validateVesselData()) return
    if (currentStep === 3 && !validateCalculationData()) return

    if (currentStep === 1) {
      await createProject()
    } else if (currentStep === 2) {
      await createVessel()
    } else if (currentStep === 3) {
      await createCalculation()
    }
  }

  const createProject = async () => {
    setIsLoading(true)
    setError('')

    try {
      // Prepare the project payload with only fields expected by backend schema
      const projectPayload = {
        name: projectData.name.trim(),
        description: projectData.description.trim(),
        client_name: projectData.client_name.trim(),
        location: projectData.location.trim(),
        status: 'planning', // Use the correct status value
        start_date: projectData.start_date ? `${projectData.start_date}T00:00:00` : null,
        end_date: projectData.end_date ? `${projectData.end_date}T00:00:00` : null
      }

              // Sending project creation request

      const project = await apiService.createProject(projectPayload, token!) as { id: number }
      setCreatedProjectId(project.id)
      setSuccess('Project created successfully!')
      setCurrentStep(2)
    } catch (error) {
              // Handle project creation error
      setError(error instanceof Error ? error.message : 'Failed to create project')
    } finally {
      setIsLoading(false)
    }
  }

  const createVessel = async () => {
    if (!createdProjectId) {
      setError('Project must be created first')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const vesselPayload = {
        tag_number: vesselData.tag_number,
        name: vesselData.name,
        vessel_type: vesselData.vessel_type,
        design_code: vesselData.design_code,
        material_specification: vesselData.material_specification,
        description: vesselData.description,
        project_id: createdProjectId,
        design_pressure: parseFloat(vesselData.design_pressure),
        design_temperature: parseFloat(vesselData.design_temperature),
        diameter: parseFloat(vesselData.inside_diameter),
        wall_thickness: vesselData.wall_thickness ? parseFloat(vesselData.wall_thickness) : null
      }

      const vessel = await apiService.createVessel(vesselPayload, token!, createdProjectId!) as { id: number }
      setCreatedVesselId(vessel.id)
      setSuccess('Vessel created successfully!')
      setCurrentStep(3)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to create vessel')
    } finally {
      setIsLoading(false)
    }
  }

  const createCalculation = async () => {
    if (!createdProjectId || !createdVesselId) {
      setError('Project and vessel must be created first')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      // Prepare calculation parameters based on vessel data
      const inputParameters = {
        design_pressure: parseFloat(vesselData.design_pressure),
        design_temperature: parseFloat(vesselData.design_temperature),
        inside_diameter: parseFloat(vesselData.inside_diameter),
        wall_thickness: vesselData.wall_thickness ? parseFloat(vesselData.wall_thickness) : null,
        material_specification: vesselData.material_specification,
        design_code: vesselData.design_code,
        joint_efficiency: 1.0,
        corrosion_allowance: 0.125
      }

      const calculationPayload = {
        ...calculationData,
        project_id: createdProjectId,
        vessel_id: createdVesselId,
        input_parameters: inputParameters
      }

      const calculation = await apiService.createCalculation(calculationPayload, token!) as { id: number }
      setCreatedCalculationId(calculation.id)
      setSuccess('Calculation created successfully!')
      
      // Redirect to the created calculation
      router.push(`/dashboard/calculations/${calculation.id}`)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to create calculation')
    } finally {
      setIsLoading(false)
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const renderStepIndicator = () => (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {workflowSteps.map((step, index) => (
          <div key={step.id} className="flex items-center flex-1">
            <div className={`flex items-center justify-center w-14 h-14 rounded-xl border-2 transition-all duration-300 ${
              step.completed 
                ? 'bg-gradient-to-br from-emerald-500 to-green-600 border-emerald-400 text-white shadow-lg shadow-emerald-500/25' 
                : currentStep === step.id 
                ? 'bg-gradient-to-br from-cyan-500 to-blue-600 border-cyan-400 text-white shadow-lg shadow-cyan-500/25'
                : 'bg-slate-800/50 border-slate-600/50 text-slate-400'
            }`}>
              {step.completed ? (
                <CheckCircle className="w-7 h-7" />
              ) : (
                <step.icon className="w-7 h-7" />
              )}
            </div>
            <div className="ml-4 flex-1">
              <div className={`text-sm font-semibold ${step.completed || currentStep === step.id ? 'text-slate-100' : 'text-slate-400'}`}>
                {step.title}
              </div>
              <div className="text-xs text-slate-500">{step.description}</div>
            </div>
            {index < workflowSteps.length - 1 && (
              <div className={`flex-1 h-1 mx-6 rounded-full transition-all duration-300 ${
                step.completed ? 'bg-gradient-to-r from-emerald-500 to-green-500' : 'bg-slate-700/50'
              }`} />
            )}
          </div>
        ))}
      </div>
    </div>
  )

  const renderProjectStep = () => (
    <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-indigo-500/5"></div>
      <CardHeader className="relative border-b border-slate-700/50">
        <CardTitle className="flex items-center text-xl text-slate-100">
          <Building className="w-6 h-6 mr-3 text-blue-400" />
          Project Setup
        </CardTitle>
        <p className="text-slate-300 mt-2">Create a new engineering project to get started</p>
      </CardHeader>
      <CardContent className="p-6 space-y-6 relative">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="project_name" className="text-sm font-medium text-slate-200">Project Name *</Label>
            <Input
              id="project_name"
              value={projectData.name}
              onChange={(e) => handleProjectDataChange('name', e.target.value)}
              placeholder="Enter project name"
              className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/25"
            />
          </div>
          <div>
            <Label htmlFor="client_name" className="text-sm font-medium text-slate-200">Client Name *</Label>
            <Input
              id="client_name"
              value={projectData.client_name}
              onChange={(e) => handleProjectDataChange('client_name', e.target.value)}
              placeholder="Enter client name"
              className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/25"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="project_description" className="text-sm font-medium text-slate-200">Project Description *</Label>
          <Textarea
            id="project_description"
            value={projectData.description}
            onChange={(e) => handleProjectDataChange('description', e.target.value)}
            placeholder="Describe the project scope and objectives"
            rows={3}
            className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/25"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="start_date" className="text-sm font-medium text-slate-200">Start Date *</Label>
            <Input
              id="start_date"
              type="date"
              value={projectData.start_date}
              onChange={(e) => handleProjectDataChange('start_date', e.target.value)}
              className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-blue-500/50 focus:ring-blue-500/25"
            />
          </div>
          <div>
            <Label htmlFor="end_date" className="text-sm font-medium text-slate-200">End Date</Label>
            <Input
              id="end_date"
              type="date"
              value={projectData.end_date}
              onChange={(e) => handleProjectDataChange('end_date', e.target.value)}
              className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-blue-500/50 focus:ring-blue-500/25"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="location" className="text-sm font-medium text-slate-200">Location</Label>
            <Input
              id="location"
              value={projectData.location}
              onChange={(e) => handleProjectDataChange('location', e.target.value)}
              placeholder="Project location"
              className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/25"
            />
          </div>
          <div>
            <Label htmlFor="priority" className="text-sm font-medium text-slate-200">Priority</Label>
            <Select value={projectData.priority} onValueChange={(value) => handleProjectDataChange('priority', value)}>
              <SelectTrigger className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-blue-500/50 focus:ring-blue-500/25">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem value="low" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">Low</SelectItem>
                <SelectItem value="medium" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">Medium</SelectItem>
                <SelectItem value="high" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">High</SelectItem>
                <SelectItem value="critical" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">Critical</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div>
          <Label htmlFor="client_contact" className="text-sm font-medium text-slate-200">Client Contact</Label>
          <Input
            id="client_contact"
            value={projectData.client_contact}
            onChange={(e) => handleProjectDataChange('client_contact', e.target.value)}
            placeholder="Client contact information"
            className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/25"
          />
        </div>

        <div>
          <Label htmlFor="tags" className="text-sm font-medium text-slate-200">Tags</Label>
          <Input
            id="tags"
            value={projectData.tags}
            onChange={(e) => handleProjectDataChange('tags', e.target.value)}
            placeholder="Enter tags separated by commas"
            className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/25"
          />
        </div>
      </CardContent>
    </Card>
  )

  const renderVesselStep = () => (
    <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-teal-500/5"></div>
      <CardHeader className="relative border-b border-slate-700/50">
        <CardTitle className="flex items-center text-xl text-slate-100">
          <Shield className="w-6 h-6 mr-3 text-cyan-400" />
          Vessel Registration
        </CardTitle>
        <p className="text-slate-300 mt-2">Add vessel or component details for analysis</p>
      </CardHeader>
      <CardContent className="p-6 space-y-6 relative">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="tag_number" className="text-sm font-medium text-slate-200">Tag Number *</Label>
            <Input
              id="tag_number"
              value={vesselData.tag_number}
              onChange={(e) => handleVesselDataChange('tag_number', e.target.value)}
              placeholder="e.g., V-101"
              className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
            />
          </div>
          <div>
            <Label htmlFor="vessel_name" className="text-sm font-medium text-slate-200">Vessel Name *</Label>
            <Input
              id="vessel_name"
              value={vesselData.name}
              onChange={(e) => handleVesselDataChange('name', e.target.value)}
              placeholder="Enter vessel name"
              className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-cyan-500/50 focus:ring-cyan-500/25"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="vessel_type" className="text-sm font-medium text-slate-200">Vessel Type</Label>
            <Select value={vesselData.vessel_type} onValueChange={(value) => handleVesselDataChange('vessel_type', value)}>
              <SelectTrigger className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-cyan-500/50 focus:ring-cyan-500/25">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem value="pressure_vessel" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">Pressure Vessel</SelectItem>
                <SelectItem value="storage_tank" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">Storage Tank</SelectItem>
                <SelectItem value="heat_exchanger" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">Heat Exchanger</SelectItem>
                <SelectItem value="reactor" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">Reactor</SelectItem>
                <SelectItem value="separator" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">Separator</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="design_code" className="text-sm font-medium text-slate-200">Design Code</Label>
            <Select value={vesselData.design_code} onValueChange={(value) => handleVesselDataChange('design_code', value)}>
              <SelectTrigger className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-cyan-500/50 focus:ring-cyan-500/25">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem value="ASME VIII Div 1" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">ASME VIII Div 1</SelectItem>
                <SelectItem value="ASME VIII Div 2" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">ASME VIII Div 2</SelectItem>
                <SelectItem value="EN 13445" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">EN 13445</SelectItem>
                <SelectItem value="API 650" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">API 650</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="design_pressure" className="text-sm font-medium">Design Pressure (psi) *</Label>
            <Input
              id="design_pressure"
              type="number"
              value={vesselData.design_pressure}
              onChange={(e) => handleVesselDataChange('design_pressure', e.target.value)}
              placeholder="150"
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="design_temperature" className="text-sm font-medium">Design Temperature (°F) *</Label>
            <Input
              id="design_temperature"
              type="number"
              value={vesselData.design_temperature}
              onChange={(e) => handleVesselDataChange('design_temperature', e.target.value)}
              placeholder="350"
              className="mt-1"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="inside_diameter" className="text-sm font-medium">Inside Diameter (inches) *</Label>
            <Input
              id="inside_diameter"
              type="number"
              value={vesselData.inside_diameter}
              onChange={(e) => handleVesselDataChange('inside_diameter', e.target.value)}
              placeholder="48"
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="wall_thickness" className="text-sm font-medium">Wall Thickness (inches)</Label>
            <Input
              id="wall_thickness"
              type="number"
              value={vesselData.wall_thickness}
              onChange={(e) => handleVesselDataChange('wall_thickness', e.target.value)}
              placeholder="0.25"
              className="mt-1"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="material_specification" className="text-sm font-medium">Material Specification</Label>
          <Select value={vesselData.material_specification} onValueChange={(value) => handleVesselDataChange('material_specification', value)}>
            <SelectTrigger className="mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="SA-516 Grade 70">SA-516 Grade 70</SelectItem>
              <SelectItem value="SA-106 Grade B">SA-106 Grade B</SelectItem>
              <SelectItem value="SA-335 P11">SA-335 P11</SelectItem>
              <SelectItem value="SA-213 T22">SA-213 T22</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="vessel_description" className="text-sm font-medium">Description</Label>
          <Textarea
            id="vessel_description"
            value={vesselData.description}
            onChange={(e) => handleVesselDataChange('description', e.target.value)}
            placeholder="Additional vessel details"
            rows={3}
            className="mt-1"
          />
        </div>
      </CardContent>
    </Card>
  )

  const renderCalculationStep = () => (
    <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-indigo-500/5"></div>
      <CardHeader className="relative border-b border-slate-700/50">
        <CardTitle className="flex items-center text-xl text-slate-100">
          <Calculator className="w-6 h-6 mr-3 text-purple-400" />
          Calculation Setup
        </CardTitle>
        <p className="text-slate-300 mt-2">Configure engineering calculations with auto-filled parameters</p>
      </CardHeader>
      <CardContent className="p-6 space-y-6 relative">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="calculation_name" className="text-sm font-medium text-slate-200">Calculation Name *</Label>
            <Input
              id="calculation_name"
              value={calculationData.name}
              onChange={(e) => handleCalculationDataChange('name', e.target.value)}
              placeholder="e.g., V-101 Thickness Calculation"
              className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-purple-500/50 focus:ring-purple-500/25"
            />
          </div>
          <div>
            <Label htmlFor="calculation_type" className="text-sm font-medium text-slate-200">Calculation Type *</Label>
            <Select value={calculationData.calculation_type} onValueChange={(value) => handleCalculationDataChange('calculation_type', value)}>
              <SelectTrigger className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-purple-500/50 focus:ring-purple-500/25">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem value="ASME_VIII_DIV_1" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">ASME VIII Div 1 - Pressure Vessels</SelectItem>
                <SelectItem value="ASME_VIII_DIV_2" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">ASME VIII Div 2 - Alternative Rules</SelectItem>
                <SelectItem value="EN_13445" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">EN 13445 - European Standard</SelectItem>
                <SelectItem value="API_579" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">API 579 - Fitness for Service</SelectItem>
                <SelectItem value="ASME_B31_3" className="text-slate-100 focus:bg-slate-700 focus:text-slate-100">ASME B31.3 - Process Piping</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div>
          <Label htmlFor="calculation_description" className="text-sm font-medium text-slate-200">Calculation Description</Label>
          <Textarea
            id="calculation_description"
            value={calculationData.description}
            onChange={(e) => handleCalculationDataChange('description', e.target.value)}
            placeholder="Describe the calculation purpose and scope"
            rows={3}
            className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-purple-500/50 focus:ring-purple-500/25"
          />
        </div>

        <div className="bg-gradient-to-r from-purple-500/10 to-indigo-500/10 p-6 rounded-xl border border-purple-500/20">
          <div className="flex items-center mb-4">
            <Sparkles className="w-5 h-5 mr-2 text-purple-400" />
            <span className="text-sm font-semibold text-purple-300">Auto-filled Parameters</span>
          </div>
          <div className="text-sm text-slate-300">
            <p className="mb-3">Calculation parameters will be automatically filled from vessel data:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-purple-400" />
                <span>Design Pressure: <strong className="text-slate-100">{vesselData.design_pressure} psi</strong></span>
              </div>
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-purple-400" />
                <span>Design Temperature: <strong className="text-slate-100">{vesselData.design_temperature} °F</strong></span>
              </div>
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-purple-400" />
                <span>Inside Diameter: <strong className="text-slate-100">{vesselData.inside_diameter} inches</strong></span>
              </div>
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-purple-400" />
                <span>Material: <strong className="text-slate-100">{vesselData.material_specification}</strong></span>
              </div>
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-purple-400" />
                <span>Design Code: <strong className="text-slate-100">{vesselData.design_code}</strong></span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="min-h-full w-full">
      {/* Page Header */}
      <div className="mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm p-8">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-teal-500/5"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
        <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Zap className="h-8 w-8 text-emerald-400" />
                  <h1 className="text-4xl font-bold text-slate-100">Quick Workflow</h1>
                  <Sparkles className="h-6 w-6 text-amber-400" />
                </div>
                <p className="text-lg text-slate-300">
                  Create project, vessel, and calculation in one streamlined process
                  <span className="text-emerald-400 font-medium"> - Smart automation</span>
                </p>
        </div>
              <Button 
                variant="ghost" 
                asChild
                className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50 border border-slate-700/50"
              >
          <Link href="/dashboard">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Link>
        </Button>
      </div>
          </div>
        </div>
      </div>

      <div className="space-y-8">

      {/* Step Indicator */}
      {renderStepIndicator()}

      {/* Error/Success Messages */}
      {error && (
        <Alert variant="destructive" className="bg-red-500/10 border-red-500/20 text-red-400">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-emerald-500/10 border-emerald-500/20 text-emerald-400">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Step Content */}
      {currentStep === 1 && renderProjectStep()}
      {currentStep === 2 && renderVesselStep()}
      {currentStep === 3 && renderCalculationStep()}

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={handleBack}
          disabled={currentStep === 1 || isLoading}
          className="bg-slate-800/50 border-slate-600/50 text-slate-300 hover:text-slate-100 hover:bg-slate-700/50"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>

        <Button
          onClick={handleNext}
          disabled={isLoading}
          className="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Processing...
            </>
          ) : currentStep === 3 ? (
            <>
              Create & Run Calculation
              <ArrowRight className="w-4 h-4 ml-2" />
            </>
          ) : (
            <>
              Next Step
              <ArrowRight className="w-4 h-4 ml-2" />
            </>
          )}
        </Button>
      </div>
      </div>
    </div>
  )
} 