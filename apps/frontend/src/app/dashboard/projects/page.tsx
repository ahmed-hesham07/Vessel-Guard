'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  Building, 
  Plus, 
  Search, 
  Filter,
  FileText,
  Users,
  Calculator,
  Shield,
  Calendar,
  TrendingUp
} from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface Project {
  id: number
  name: string
  description: string
  status: 'active' | 'completed' | 'on_hold' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'critical'
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
  inspections_count: number
}

export default function ProjectsPage() {
  const { token } = useAuth()
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')

  useEffect(() => {
    fetchProjects()
  }, [token])

  const fetchProjects = async () => {
    if (!token) return

    try {
      const data = await apiService.getProjects(token)
      setProjects(data as Project[])
    } catch (error) {
      console.error('Error fetching projects:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      active: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      completed: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      on_hold: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      cancelled: 'bg-red-500/20 text-red-400 border-red-500/30'
    }
    return variants[status as keyof typeof variants] || 'bg-slate-500/20 text-slate-400 border-slate-500/30'
  }

  const getPriorityBadge = (priority: string) => {
    const variants = {
      low: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
      medium: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      critical: 'bg-red-500/20 text-red-400 border-red-500/30'
    }
    return variants[priority as keyof typeof variants] || 'bg-slate-500/20 text-slate-400 border-slate-500/30'
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
        return <TrendingUp className="h-4 w-4 text-red-500" />
      case 'high':
        return <TrendingUp className="h-4 w-4 text-orange-500" />
      case 'medium':
        return <TrendingUp className="h-4 w-4 text-blue-500" />
      case 'low':
        return <TrendingUp className="h-4 w-4 text-gray-500" />
      default:
        return <TrendingUp className="h-4 w-4 text-gray-500" />
    }
  }

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter
    const matchesPriority = priorityFilter === 'all' || project.priority === priorityFilter
    
    return matchesSearch && matchesStatus && matchesPriority
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-full w-full">
      {/* Page Header */}
      <div className="mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm p-8">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Building className="h-8 w-8 text-blue-400" />
                  <h1 className="text-4xl font-bold text-slate-100">Projects</h1>
                </div>
                <p className="text-lg text-slate-300">
                  Manage engineering projects and compliance workflows
                  <span className="text-blue-400 font-medium"> - Professional grade</span>
                </p>
              </div>
              <div className="hidden lg:block">
                <div className="text-right">
                  <div className="text-3xl font-bold text-blue-400">{projects.length}</div>
                  <div className="text-sm text-slate-400">Active Projects</div>
                </div>
              </div>
            </div>
            
            {/* Quick Stats */}
            <div className="flex items-center space-x-6 p-4 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4 text-cyan-400" />
                <span className="text-slate-300 text-sm">Compliance Tracking</span>
              </div>
              <div className="flex items-center space-x-2">
                <Users className="h-4 w-4 text-purple-400" />
                <span className="text-slate-300 text-sm">Team Collaboration</span>
              </div>
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4 text-emerald-400" />
                <span className="text-slate-300 text-sm">Progress Monitoring</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Actions Bar */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all duration-200"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="on_hold">On Hold</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all duration-200"
          >
            <option value="all">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        
        {/* New Project Button */}
        <Link href="/dashboard/projects/new">
          <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 group">
            <Plus className="h-5 w-5 mr-2 group-hover:rotate-90 transition-transform duration-300" />
            New Project
          </Button>
        </Link>
      </div>

      {/* Projects List */}
      <div className="grid gap-6">
        {filteredProjects.length === 0 ? (
          <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5"></div>
            <CardContent className="pt-6 relative">
              <div className="text-center py-8">
                <Building className="mx-auto h-12 w-12 text-slate-400" />
                <h3 className="mt-2 text-sm font-medium text-slate-100">No projects found</h3>
                <p className="mt-1 text-sm text-slate-400">
                  {searchTerm || statusFilter !== 'all' || priorityFilter !== 'all' 
                    ? 'Try adjusting your filters.' 
                    : 'Get started by creating your first project.'}
                </p>
                {!searchTerm && statusFilter === 'all' && priorityFilter === 'all' && (
                  <div className="mt-6">
                    <Link href="/dashboard/projects/new">
                      <Button className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white">
                        <Plus className="mr-2 h-4 w-4" />
                        New Project
                      </Button>
                    </Link>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredProjects.map((project) => (
            <Card key={project.id} className="group relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm hover:border-blue-500/50 transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <CardContent className="pt-6 relative">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start space-x-4 mb-4">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 text-blue-400 group-hover:scale-110 transition-transform duration-300">
                        {getPriorityIcon(project.priority)}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-slate-100 mb-1">
                          <Link 
                            href={`/dashboard/projects/${project.id}`}
                            className="hover:text-blue-400 transition-colors duration-200"
                          >
                            {project.name}
                          </Link>
                        </h3>
                        <p className="text-sm text-slate-300 mb-3">
                          {project.description}
                        </p>
                        
                        <div className="flex flex-wrap gap-2">
                          <Badge className={getStatusBadge(project.status)}>
                            {project.status.replace('_', ' ')}
                          </Badge>
                          <Badge className={getPriorityBadge(project.priority)}>
                            {project.priority}
                          </Badge>
                          <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/30">
                            {project.owner?.first_name && project.owner?.last_name 
                              ? `${project.owner.first_name} ${project.owner.last_name}`
                              : 'Unknown Owner'}
                          </Badge>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center space-x-2 text-slate-400">
                        <Shield className="h-4 w-4 text-cyan-400" />
                        <span>{project.vessels_count} Vessels</span>
                      </div>
                      <div className="flex items-center space-x-2 text-slate-400">
                        <Calculator className="h-4 w-4 text-emerald-400" />
                        <span>{project.calculations_count} Calculations</span>
                      </div>
                      <div className="flex items-center space-x-2 text-slate-400">
                        <FileText className="h-4 w-4 text-purple-400" />
                        <span>{project.inspections_count} Inspections</span>
                      </div>
                      <div className="flex items-center space-x-2 text-slate-400">
                        <Calendar className="h-4 w-4 text-amber-400" />
                        <span className="text-xs">
                          {new Date(project.start_date).toLocaleDateString()}
                          {project.end_date && ` - ${new Date(project.end_date).toLocaleDateString()}`}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <Link href={`/dashboard/projects/${project.id}`}>
                      <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50">
                        <FileText className="mr-2 h-4 w-4" />
                        View
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
