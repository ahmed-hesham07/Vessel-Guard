'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  Calculator, 
  Plus, 
  Search, 
  Filter, 
  Calendar, 
  FileText,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  Clock
} from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface Calculation {
  id: number
  name: string
  calculation_type: 'pressure_analysis' | 'stress_analysis' | 'fatigue_analysis' | 'corrosion_analysis' | 'thermal_analysis' | 'vibration_analysis' | 'custom'
  standard: 'ASME_VIII_DIV_1' | 'ASME_VIII_DIV_2' | 'ASME_B31_3' | 'API_579' | 'EN_13445' | 'other'
  status: 'draft' | 'in_progress' | 'completed' | 'reviewed' | 'approved' | 'rejected'
  description: string
  created_at: string
  updated_at: string
  vessel: {
    id: number
    name: string
    tag_number: string
  }
  project: {
    id: number
    name: string
  }
  engineer: {
    id: number
    first_name: string
    last_name: string
  }
  results: {
    is_valid: boolean
    safety_factor: number
    max_allowable_stress: number
    calculated_stress: number
    notes: string
  }
}

const calculationTypeLabels = {
  pressure_analysis: 'Pressure Analysis',
  stress_analysis: 'Stress Analysis',
  fatigue_analysis: 'Fatigue Analysis',
  corrosion_analysis: 'Corrosion Analysis',
  thermal_analysis: 'Thermal Analysis',
  vibration_analysis: 'Vibration Analysis',
  custom: 'Custom Analysis'
}

const standardLabels = {
  ASME_VIII_DIV_1: 'ASME VIII Div 1',
  ASME_VIII_DIV_2: 'ASME VIII Div 2',
  ASME_B31_3: 'ASME B31.3',
  API_579: 'API 579',
  EN_13445: 'EN 13445',
  other: 'Other'
}

const statusColors = {
  draft: 'bg-gray-100 text-gray-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  reviewed: 'bg-purple-100 text-purple-800',
  approved: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800'
}

export default function CalculationsPage() {
  const { token } = useAuth()
  const [calculations, setCalculations] = useState<Calculation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [standardFilter, setStandardFilter] = useState<string>('all')

  useEffect(() => {
    const fetchCalculations = async () => {
      if (!token) return

      try {
        const data = await apiService.getCalculations(token)
        setCalculations(data as Calculation[])
      } catch (error) {
        console.error('Error fetching calculations:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchCalculations()
  }, [token])

  const filteredCalculations = calculations.filter(calc => {
    const matchesSearch = calc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         calc.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         calc.vessel.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = typeFilter === 'all' || calc.calculation_type === typeFilter
    const matchesStatus = statusFilter === 'all' || calc.status === statusFilter
    const matchesStandard = standardFilter === 'all' || calc.standard === standardFilter
    
    return matchesSearch && matchesType && matchesStatus && matchesStandard
  })

  const handleDeleteCalculation = async (calcId: number) => {
    if (!token) return
    
    if (window.confirm('Are you sure you want to delete this calculation?')) {
      try {
        await apiService.deleteCalculation(calcId, token)
        setCalculations(calculations.filter(c => c.id !== calcId))
      } catch (error) {
        console.error('Error deleting calculation:', error)
      }
    }
  }

  const getResultsIcon = (calc: Calculation) => {
    if (!calc.results) return <Clock className="h-4 w-4 text-gray-400" />
    
    if (calc.results.is_valid) {
      return <CheckCircle2 className="h-4 w-4 text-green-500" />
    } else {
      return <AlertTriangle className="h-4 w-4 text-red-500" />
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
          <h1 className="text-2xl font-bold text-gray-900">Calculations</h1>
          <p className="text-gray-600">
            Engineering calculations and analysis results
          </p>
        </div>
        <Button asChild>
          <Link href="/calculations/new">
            <Plus className="h-4 w-4 mr-2" />
            New Calculation
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search calculations..."
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
            <option value="pressure_analysis">Pressure Analysis</option>
            <option value="stress_analysis">Stress Analysis</option>
            <option value="fatigue_analysis">Fatigue Analysis</option>
            <option value="corrosion_analysis">Corrosion Analysis</option>
            <option value="thermal_analysis">Thermal Analysis</option>
            <option value="vibration_analysis">Vibration Analysis</option>
            <option value="custom">Custom Analysis</option>
          </select>
          <select
            value={standardFilter}
            onChange={(e) => setStandardFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Standards</option>
            <option value="ASME_VIII_DIV_1">ASME VIII Div 1</option>
            <option value="ASME_VIII_DIV_2">ASME VIII Div 2</option>
            <option value="ASME_B31_3">ASME B31.3</option>
            <option value="API_579">API 579</option>
            <option value="EN_13445">EN 13445</option>
            <option value="other">Other</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="reviewed">Reviewed</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Calculations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCalculations.map((calc) => (
          <Card key={calc.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <CardTitle className="text-lg font-semibold text-gray-900">
                    {calc.name}
                  </CardTitle>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline">
                      {calculationTypeLabels[calc.calculation_type]}
                    </Badge>
                    <Badge className={statusColors[calc.status]}>
                      {calc.status.replace('_', ' ')}
                    </Badge>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getResultsIcon(calc)}
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-sm text-gray-600 line-clamp-2">
                  {calc.description}
                </p>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Standard:</span>
                  <span className="font-medium">{standardLabels[calc.standard]}</span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Vessel:</span>
                  <Link 
                    href={`/dashboard/vessels/${calc.vessel.id}`}
                    className="text-primary-600 hover:text-primary-700 font-medium"
                  >
                    {calc.vessel.tag_number}
                  </Link>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Project:</span>
                  <Link 
                    href={`/dashboard/projects/${calc.project.id}`}
                    className="text-primary-600 hover:text-primary-700 font-medium"
                  >
                    {calc.project.name}
                  </Link>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Engineer:</span>
                  <span className="font-medium">
                    {calc.engineer.first_name} {calc.engineer.last_name}
                  </span>
                </div>

                {calc.results && (
                  <div className="pt-2 border-t">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Safety Factor:</span>
                      <span className="font-medium">{calc.results.safety_factor}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Status:</span>
                      <span className={`font-medium ${calc.results.is_valid ? 'text-green-600' : 'text-red-600'}`}>
                        {calc.results.is_valid ? 'Valid' : 'Invalid'}
                      </span>
                    </div>
                  </div>
                )}
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Created: {new Date(calc.created_at).toLocaleDateString()}</span>
                  <span>Updated: {new Date(calc.updated_at).toLocaleDateString()}</span>
                </div>

                <div className="flex gap-2 mt-4">
                  <Button variant="outline" size="sm" asChild className="flex-1">
                    <Link href={`/calculations/${calc.id}`}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Link>
                  </Button>
                  <Button variant="outline" size="sm" asChild className="flex-1">
                    <Link href={`/calculations/${calc.id}/edit`}>
                      <Edit className="h-4 w-4 mr-1" />
                      Edit
                    </Link>
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleDeleteCalculation(calc.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredCalculations.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <Calculator className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No calculations found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || typeFilter !== 'all' || statusFilter !== 'all' || standardFilter !== 'all'
              ? 'No calculations match your current filters.' 
              : 'Get started by creating your first calculation.'}
          </p>
          <Button asChild>
            <Link href="/calculations/new">
              <Plus className="h-4 w-4 mr-2" />
              New Calculation
            </Link>
          </Button>
        </div>
      )}
    </div>
  )
}
