'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  Plus, 
  Search, 
  Filter, 
  Calendar, 
  Gauge,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface Vessel {
  id: number
  name: string
  tag_number: string
  type: 'pressure_vessel' | 'storage_tank' | 'heat_exchanger' | 'reactor' | 'separator' | 'piping' | 'air_cooling' | 'fitting' | 'valve'
  geometry: 'cylindrical' | 'spherical' | 'conical' | 'rectangular' | 'custom'
  design_code: string
  status: 'active' | 'inactive' | 'maintenance' | 'decommissioned'
  design_pressure: number
  design_temperature: number
  operating_pressure: number
  operating_temperature: number
  material_grade: string
  diameter: number
  length: number
  wall_thickness: number
  location: string
  installation_date: string
  last_inspection_date?: string
  next_inspection_date?: string
  created_at: string
  updated_at: string
  project: {
    id: number
    name: string
  }
}

const vesselTypeLabels = {
  pressure_vessel: 'Pressure Vessel',
  storage_tank: 'Storage Tank',
  heat_exchanger: 'Heat Exchanger',
  reactor: 'Reactor',
  separator: 'Separator',
  piping: 'Piping',
  air_cooling: 'Air Cooling',
  fitting: 'Fitting',
  valve: 'Valve'
}

const statusColors = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  maintenance: 'bg-yellow-100 text-yellow-800',
  decommissioned: 'bg-red-100 text-red-800'
}

export default function VesselsPage() {
  const { token } = useAuth()
  const [vessels, setVessels] = useState<Vessel[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    const fetchVessels = async () => {
      if (!token) return

      try {
        const data = await apiService.getVessels(token)
        setVessels(data as Vessel[])
      } catch (error) {
        console.error('Error fetching vessels:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchVessels()
  }, [token])

  const filteredVessels = vessels.filter(vessel => {
    const matchesSearch = vessel.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vessel.tag_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vessel.location.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = typeFilter === 'all' || vessel.type === typeFilter
    const matchesStatus = statusFilter === 'all' || vessel.status === statusFilter
    
    return matchesSearch && matchesType && matchesStatus
  })

  const handleDeleteVessel = async (vesselId: number) => {
    if (!token) return
    
    if (window.confirm('Are you sure you want to delete this vessel?')) {
      try {
        await apiService.deleteVessel(vesselId, token)
        setVessels(vessels.filter(v => v.id !== vesselId))
      } catch (error) {
        console.error('Error deleting vessel:', error)
      }
    }
  }

  const getInspectionStatus = (vessel: Vessel) => {
    if (!vessel.next_inspection_date) return null
    
    const nextInspection = new Date(vessel.next_inspection_date)
    const today = new Date()
    const daysUntilInspection = Math.ceil((nextInspection.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
    
    if (daysUntilInspection < 0) {
      return { status: 'overdue', label: 'Overdue', color: 'text-red-600' }
    } else if (daysUntilInspection <= 30) {
      return { status: 'due-soon', label: 'Due Soon', color: 'text-yellow-600' }
    } else {
      return { status: 'up-to-date', label: 'Up to Date', color: 'text-green-600' }
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow h-32"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Vessels</h1>
          <p className="text-gray-600">
            Manage your pressure vessels, tanks, and piping components
          </p>
        </div>
        <Button asChild>
          <Link href="/dashboard/vessels/new">
            <Plus className="h-4 w-4 mr-2" />
            Add Vessel
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search vessels..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <div className="flex gap-2">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Types</option>
            <option value="pressure_vessel">Pressure Vessel</option>
            <option value="storage_tank">Storage Tank</option>
            <option value="heat_exchanger">Heat Exchanger</option>
            <option value="reactor">Reactor</option>
            <option value="separator">Separator</option>
            <option value="piping">Piping</option>
            <option value="air_cooling">Air Cooling</option>
            <option value="fitting">Fitting</option>
            <option value="valve">Valve</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="maintenance">Maintenance</option>
            <option value="decommissioned">Decommissioned</option>
          </select>
        </div>
      </div>

      {/* Vessels Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredVessels.map((vessel) => {
          const inspectionStatus = getInspectionStatus(vessel)
          
          return (
            <Card key={vessel.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg font-semibold text-gray-900">
                      {vessel.name}
                    </CardTitle>
                    <p className="text-sm text-gray-600">
                      {vessel.tag_number}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="outline">
                        {vesselTypeLabels[vessel.type]}
                      </Badge>
                      <Badge className={statusColors[vessel.status]}>
                        {vessel.status}
                      </Badge>
                    </div>
                  </div>
                  <div className="relative">
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Design Pressure:</span>
                    <span className="font-medium">{vessel.design_pressure} psi</span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Design Temp:</span>
                    <span className="font-medium">{vessel.design_temperature}°F</span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Material:</span>
                    <span className="font-medium">{vessel.material_grade}</span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Location:</span>
                    <span className="font-medium">{vessel.location}</span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Project:</span>
                    <Link 
                      href={`/dashboard/projects/${vessel.project.id}`}
                      className="text-primary-600 hover:text-primary-700 font-medium"
                    >
                      {vessel.project.name}
                    </Link>
                  </div>

                  {inspectionStatus && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Inspection:</span>
                      <div className="flex items-center gap-1">
                        {inspectionStatus.status === 'overdue' && (
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                        )}
                        {inspectionStatus.status === 'due-soon' && (
                          <Calendar className="h-4 w-4 text-yellow-500" />
                        )}
                        {inspectionStatus.status === 'up-to-date' && (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        )}
                        <span className={`font-medium ${inspectionStatus.color}`}>
                          {inspectionStatus.label}
                        </span>
                      </div>
                    </div>
                  )}

                  <div className="flex gap-2 mt-4">
                    <Button variant="outline" size="sm" asChild className="flex-1">
                      <Link href={`/dashboard/vessels/${vessel.id}`}>
                        <Eye className="h-4 w-4 mr-1" />
                        View
                      </Link>
                    </Button>
                    <Button variant="outline" size="sm" asChild className="flex-1">
                      <Link href={`/dashboard/vessels/${vessel.id}/edit`}>
                        <Edit className="h-4 w-4 mr-1" />
                        Edit
                      </Link>
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => handleDeleteVessel(vessel.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Empty State */}
      {filteredVessels.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No vessels found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || typeFilter !== 'all' || statusFilter !== 'all' 
              ? 'No vessels match your current filters.' 
              : 'Get started by adding your first vessel.'}
          </p>
          <Button asChild>
            <Link href="/dashboard/vessels/new">
              <Plus className="h-4 w-4 mr-2" />
              Add Vessel
            </Link>
          </Button>
        </div>
      )}
    </div>
  )
}
