'use client'

import { useState } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowLeft, Save, Loader2, Building, Target } from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface ProjectFormData {
  name: string
  description: string
  status: 'active' | 'completed' | 'on_hold' | 'cancelled' | 'archived'
  priority: 'low' | 'medium' | 'high' | 'critical'
  start_date: string
  end_date: string
  location: string
  client_name: string
  client_contact: string
  budget: string
  tags: string
}

export default function NewProjectPage() {
  const { token } = useAuth()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState<ProjectFormData>({
    name: '',
    description: '',
    status: 'active',
    priority: 'medium',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    location: '',
    client_name: '',
    client_contact: '',
    budget: '',
    tags: ''
  })

  const handleInputChange = (field: keyof ProjectFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const validateForm = () => {
    if (!formData.name.trim()) {
      setError('Project name is required')
      return false
    }
    
    if (!formData.description.trim()) {
      setError('Project description is required')
      return false
    }
    
    if (!formData.start_date) {
      setError('Start date is required')
      return false
    }
    
    if (formData.end_date && new Date(formData.end_date) <= new Date(formData.start_date)) {
      setError('End date must be after start date')
      return false
    }
    
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (!validateForm()) {
      return
    }

    setIsLoading(true)

    try {
      const projectData = {
        ...formData,
        budget: formData.budget ? parseFloat(formData.budget) : null,
        tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()) : []
      }

      const project = await apiService.createProject(projectData, token!) as { id: string }
      router.push(`/dashboard/projects/${project.id}`)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to create project')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-full w-full">
      {/* Page Header */}
      <div className="mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm p-8">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-indigo-500/5"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Building className="h-8 w-8 text-purple-400" />
                  <h1 className="text-4xl font-bold text-slate-100">Create New Project</h1>
                </div>
                <p className="text-lg text-slate-300">
                  Set up a new engineering project with all the necessary details
                  <span className="text-purple-400 font-medium"> - Professional setup</span>
                </p>
              </div>
              <Button 
                variant="ghost" 
                asChild
                className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50 border border-slate-700/50"
              >
                <Link href="/dashboard/projects">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Projects
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto space-y-6">

      {/* Form */}
      <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-indigo-500/5"></div>
        <CardHeader className="relative border-b border-slate-700/50">
          <CardTitle className="text-slate-100 flex items-center space-x-2">
            <Target className="w-5 h-5 text-purple-400" />
            <span>Project Information</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="relative">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <Alert variant="destructive" className="bg-red-500/10 border-red-500/20 text-red-400">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <Label htmlFor="name" className="text-slate-200">Project Name *</Label>
                <Input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Enter project name"
                  required
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-purple-500/50 focus:ring-purple-500/25"
                />
              </div>

              <div className="md:col-span-2">
                <Label htmlFor="description" className="text-slate-200">Description *</Label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Describe the project scope and objectives"
                  required
                  rows={4}
                  className="mt-1 block w-full rounded-md bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-purple-500/50 focus:ring-purple-500/25"
                />
              </div>

              <div>
                <Label htmlFor="status" className="text-slate-200">Status</Label>
                <select
                  id="status"
                  value={formData.status}
                  onChange={(e) => handleInputChange('status', e.target.value)}
                  className="mt-1 block w-full rounded-md bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-purple-500/50 focus:ring-purple-500/25"
                >
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="on_hold">On Hold</option>
                  <option value="cancelled">Cancelled</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              <div>
                <Label htmlFor="priority" className="text-slate-200">Priority</Label>
                <select
                  id="priority"
                  value={formData.priority}
                  onChange={(e) => handleInputChange('priority', e.target.value)}
                  className="mt-1 block w-full rounded-md bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-purple-500/50 focus:ring-purple-500/25"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div>
                <Label htmlFor="start_date" className="text-slate-200">Start Date *</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => handleInputChange('start_date', e.target.value)}
                  required
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-purple-500/50 focus:ring-purple-500/25"
                />
              </div>

              <div>
                <Label htmlFor="end_date" className="text-slate-200">End Date</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => handleInputChange('end_date', e.target.value)}
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 focus:border-purple-500/50 focus:ring-purple-500/25"
                />
              </div>

              <div>
                <Label htmlFor="location" className="text-slate-200">Location</Label>
                <Input
                  id="location"
                  type="text"
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  placeholder="Project location"
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-purple-500/50 focus:ring-purple-500/25"
                />
              </div>

              <div>
                <Label htmlFor="budget" className="text-slate-200">Budget ($)</Label>
                <Input
                  id="budget"
                  type="number"
                  value={formData.budget}
                  onChange={(e) => handleInputChange('budget', e.target.value)}
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-purple-500/50 focus:ring-purple-500/25"
                />
              </div>

              <div>
                <Label htmlFor="client_name" className="text-slate-200">Client Name</Label>
                <Input
                  id="client_name"
                  type="text"
                  value={formData.client_name}
                  onChange={(e) => handleInputChange('client_name', e.target.value)}
                  placeholder="Client or company name"
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-purple-500/50 focus:ring-purple-500/25"
                />
              </div>

              <div>
                <Label htmlFor="client_contact" className="text-slate-200">Client Contact</Label>
                <Input
                  id="client_contact"
                  type="text"
                  value={formData.client_contact}
                  onChange={(e) => handleInputChange('client_contact', e.target.value)}
                  placeholder="Contact person and details"
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-purple-500/50 focus:ring-purple-500/25"
                />
              </div>

              <div className="md:col-span-2">
                <Label htmlFor="tags" className="text-slate-200">Tags</Label>
                <Input
                  id="tags"
                  type="text"
                  value={formData.tags}
                  onChange={(e) => handleInputChange('tags', e.target.value)}
                  placeholder="Comma-separated tags (e.g., ASME, pressure vessel, inspection)"
                  className="mt-1 bg-slate-800/50 border-slate-600/50 text-slate-100 placeholder:text-slate-400 focus:border-purple-500/50 focus:ring-purple-500/25"
                />
                <p className="text-sm text-slate-400 mt-1">
                  Enter tags separated by commas to help categorize and find this project
                </p>
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
                <Link href="/dashboard/projects">
                  Cancel
                </Link>
              </Button>
              <Button 
                type="submit" 
                disabled={isLoading}
                className="bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Create Project
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
