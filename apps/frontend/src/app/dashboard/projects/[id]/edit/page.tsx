'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { useRouter, useParams } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Building, 
  ArrowLeft, 
  Loader2,
  CheckCircle,
  AlertTriangle,
  Save
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
  status: string
}

export default function EditProjectPage() {
  const { token } = useAuth()
  const router = useRouter()
  const params = useParams()
  const projectId = params.id as string
  
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  const [projectData, setProjectData] = useState<ProjectData>({
    name: '',
    description: '',
    client_name: '',
    client_contact: '',
    location: '',
    start_date: '',
    end_date: '',
    priority: 'medium',
    tags: '',
    status: 'planning' // Changed from 'active' to 'planning'
  })

  useEffect(() => {
    const fetchProject = async () => {
      if (!token || !projectId) return

      try {
        const project = await apiService.getProject(parseInt(projectId), token) as any
        setProjectData({
          name: project.name || '',
          description: project.description || '',
          client_name: project.client_name || '',
          client_contact: project.client_contact || '',
          location: project.location || '',
          start_date: project.start_date ? new Date(project.start_date).toISOString().split('T')[0] : '',
          end_date: project.end_date ? new Date(project.end_date).toISOString().split('T')[0] : '',
          priority: project.priority || 'medium',
          tags: Array.isArray(project.tags) ? project.tags.join(', ') : project.tags || '',
          status: project.status || 'planning' // Changed from 'active' to 'planning'
        })
      } catch (error) {
        setError('Failed to load project data')
        console.error('Error fetching project:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchProject()
  }, [token, projectId])

  const handleProjectDataChange = (field: keyof ProjectData, value: string) => {
    setProjectData(prev => ({
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

  const handleSave = async () => {
    if (!validateProjectData()) return

    setIsSaving(true)
    setError('')

    try {
      // Prepare the project payload with only fields expected by backend schema
      const projectPayload = {
        name: projectData.name.trim(),
        description: projectData.description.trim(),
        client_name: projectData.client_name.trim(),
        location: projectData.location.trim(),
        status: projectData.status,
        start_date: projectData.start_date ? `${projectData.start_date}T00:00:00` : null,
        end_date: projectData.end_date ? `${projectData.end_date}T00:00:00` : null
      }

              // Sending project update request

      await apiService.updateProject(parseInt(projectId), projectPayload, token!)
      setSuccess('Project updated successfully!')
      
      // Redirect back to project details after a short delay
      setTimeout(() => {
        router.push(`/dashboard/projects/${projectId}`)
      }, 1500)
    } catch (error) {
              // Handle project update error
      setError(error instanceof Error ? error.message : 'Failed to update project')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Edit Project</h1>
          <p className="text-gray-600 mt-2">Update project details and information</p>
        </div>
        <Button variant="outline" asChild>
          <Link href={`/dashboard/projects/${projectId}`}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Project
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

      {/* Edit Form */}
      <Card className="border-0 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 border-b">
          <CardTitle className="flex items-center text-xl">
            <Building className="w-6 h-6 mr-3 text-blue-600" />
            Project Details
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="project_name" className="text-sm font-medium">Project Name *</Label>
              <Input
                id="project_name"
                value={projectData.name}
                onChange={(e) => handleProjectDataChange('name', e.target.value)}
                placeholder="Enter project name"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="client_name" className="text-sm font-medium">Client Name *</Label>
              <Input
                id="client_name"
                value={projectData.client_name}
                onChange={(e) => handleProjectDataChange('client_name', e.target.value)}
                placeholder="Enter client name"
                className="mt-1"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="project_description" className="text-sm font-medium">Project Description *</Label>
            <Textarea
              id="project_description"
              value={projectData.description}
              onChange={(e) => handleProjectDataChange('description', e.target.value)}
              placeholder="Describe the project scope and objectives"
              rows={3}
              className="mt-1"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="start_date" className="text-sm font-medium">Start Date *</Label>
              <Input
                id="start_date"
                type="date"
                value={projectData.start_date}
                onChange={(e) => handleProjectDataChange('start_date', e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="end_date" className="text-sm font-medium">End Date</Label>
              <Input
                id="end_date"
                type="date"
                value={projectData.end_date}
                onChange={(e) => handleProjectDataChange('end_date', e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="location" className="text-sm font-medium">Location</Label>
              <Input
                id="location"
                value={projectData.location}
                onChange={(e) => handleProjectDataChange('location', e.target.value)}
                placeholder="Project location"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="priority" className="text-sm font-medium">Priority</Label>
              <Select value={projectData.priority} onValueChange={(value) => handleProjectDataChange('priority', value)}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="client_contact" className="text-sm font-medium">Client Contact</Label>
              <Input
                id="client_contact"
                value={projectData.client_contact}
                onChange={(e) => handleProjectDataChange('client_contact', e.target.value)}
                placeholder="Client contact information"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="status" className="text-sm font-medium">Status</Label>
              <Select value={projectData.status} onValueChange={(value) => handleProjectDataChange('status', value)}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                              <SelectContent>
                <SelectItem value="planning">Planning</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="review">Review</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
                <SelectItem value="on_hold">On Hold</SelectItem>
              </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            <Label htmlFor="tags" className="text-sm font-medium">Tags</Label>
            <Input
              id="tags"
              value={projectData.tags}
              onChange={(e) => handleProjectDataChange('tags', e.target.value)}
              placeholder="Enter tags separated by commas"
              className="mt-1"
            />
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <Button variant="outline" asChild>
          <Link href={`/dashboard/projects/${projectId}`}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Cancel
          </Link>
        </Button>

        <Button
          onClick={handleSave}
          disabled={isSaving}
          className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
        >
          {isSaving ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </>
          )}
        </Button>
      </div>
    </div>
  )
} 