'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Plus, Search, Filter, Calendar, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface Inspection {
  id: number
  vessel_id: number
  inspection_type: string
  inspection_date: string
  inspector_name: string
  result: string
  next_inspection_date: string | null
  created_at: string
  vessel_tag_number?: string
  vessel_name?: string
}

export default function InspectionsPage() {
  const { token } = useAuth()
  const [inspections, setInspections] = useState<Inspection[]>([])
  const [filteredInspections, setFilteredInspections] = useState<Inspection[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [resultFilter, setResultFilter] = useState('all')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchInspections = async () => {
      if (!token) return
      
      try {
        const response = await apiService.getInspections(token)
        const inspectionsData = (response as any).items || response
        setInspections(inspectionsData)
        setFilteredInspections(inspectionsData)
      } catch (error) {
        console.error('Error fetching inspections:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchInspections()
  }, [token])

  useEffect(() => {
    let filtered = inspections

    if (searchQuery) {
      filtered = filtered.filter(inspection =>
        inspection.inspection_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        inspection.inspector_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        inspection.vessel_tag_number?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (resultFilter !== 'all') {
      filtered = filtered.filter(inspection => inspection.result === resultFilter)
    }

    setFilteredInspections(filtered)
  }, [inspections, searchQuery, resultFilter])

  const getResultColor = (result: string) => {
    switch (result) {
      case 'pass': return 'bg-green-100 text-green-800'
      case 'fail': return 'bg-red-100 text-red-800'
      case 'conditional': return 'bg-yellow-100 text-yellow-800'
      case 'not_applicable': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getResultIcon = (result: string) => {
    switch (result) {
      case 'pass': return CheckCircle
      case 'fail': return XCircle
      case 'conditional': return AlertTriangle
      case 'not_applicable': return Clock
      default: return Clock
    }
  }

  const formatInspectionType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const isOverdue = (nextInspectionDate: string | null) => {
    if (!nextInspectionDate) return false
    return new Date(nextInspectionDate) < new Date()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inspections</h1>
          <p className="text-gray-600">Manage vessel inspections and compliance</p>
        </div>
        <Button asChild>
          <Link href="/dashboard/inspections/new">
            <Plus className="w-4 h-4 mr-2" />
            Schedule Inspection
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search inspections..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={resultFilter}
                onChange={(e) => setResultFilter(e.target.value)}
                className="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value="all">All Results</option>
                <option value="pass">Pass</option>
                <option value="fail">Fail</option>
                <option value="conditional">Conditional</option>
                <option value="not_applicable">Not Applicable</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Inspections List */}
      <div className="grid gap-4">
        {filteredInspections.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-8">
                <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No inspections found</h3>
                <p className="text-gray-500 mb-4">
                  {searchQuery || resultFilter !== 'all' 
                    ? "No inspections match your current filters."
                    : "Get started by scheduling your first inspection."
                  }
                </p>
                <Button asChild>
                  <Link href="/dashboard/inspections/new">
                    <Plus className="w-4 h-4 mr-2" />
                    Schedule Inspection
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredInspections.map((inspection) => {
            const ResultIcon = getResultIcon(inspection.result)
            const nextInspectionOverdue = isOverdue(inspection.next_inspection_date)
            
            return (
              <Card key={inspection.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-1">
                        {formatInspectionType(inspection.inspection_type)} Inspection
                      </CardTitle>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <span>Inspector: {inspection.inspector_name}</span>
                        {inspection.vessel_tag_number && (
                          <>
                            <span>•</span>
                            <span>{inspection.vessel_tag_number}</span>
                          </>
                        )}
                        {inspection.vessel_name && (
                          <>
                            <span>•</span>
                            <span>{inspection.vessel_name}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getResultColor(inspection.result)}>
                        <ResultIcon className="w-3 h-3 mr-1" />
                        {inspection.result}
                      </Badge>
                      {nextInspectionOverdue && (
                        <Badge className="bg-red-100 text-red-800">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          Overdue
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Inspection Date: {formatDate(inspection.inspection_date)}</span>
                    {inspection.next_inspection_date && (
                      <span className={nextInspectionOverdue ? 'text-red-600' : ''}>
                        Next Due: {formatDate(inspection.next_inspection_date)}
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            )
          })
        )}
      </div>
    </div>
  )
}
