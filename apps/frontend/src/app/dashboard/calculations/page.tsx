'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Plus, Search, Filter, Calculator, FileText, Clock, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface Calculation {
  id: number
  name: string
  calculation_type: string
  status: string
  vessel_id: number
  created_at: string
  completed_at: string | null
  vessel_tag_number?: string
  vessel_name?: string
}

export default function CalculationsPage() {
  const { token } = useAuth()
  const [calculations, setCalculations] = useState<Calculation[]>([])
  const [filteredCalculations, setFilteredCalculations] = useState<Calculation[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchCalculations = async () => {
      if (!token) return
      
      try {
        const response = await apiService.getCalculations(token)
        const calculationsData = (response as any).items || response
        setCalculations(calculationsData)
        setFilteredCalculations(calculationsData)
      } catch (error) {
        console.error('Error fetching calculations:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchCalculations()
  }, [token])

  useEffect(() => {
    let filtered = calculations

    if (searchQuery) {
      filtered = filtered.filter(calc =>
        calc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        calc.calculation_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        calc.vessel_tag_number?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(calc => calc.status === statusFilter)
    }

    setFilteredCalculations(filtered)
  }, [calculations, searchQuery, statusFilter])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'running': return 'bg-yellow-100 text-yellow-800'
      case 'pending': return 'bg-blue-100 text-blue-800'
      case 'failed': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return CheckCircle
      case 'running': return Clock
      case 'pending': return Clock
      case 'failed': return FileText
      default: return Calculator
    }
  }

  const formatCalculationType = (type: string) => {
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
          <h1 className="text-2xl font-bold text-gray-900">Calculations</h1>
          <p className="text-gray-600">Manage engineering calculations and analysis</p>
        </div>
        <Button asChild>
          <Link href="/dashboard/calculations/new">
            <Plus className="w-4 h-4 mr-2" />
            Run Calculation
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
                placeholder="Search calculations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Calculations List */}
      <div className="grid gap-4">
        {filteredCalculations.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-8">
                <Calculator className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No calculations found</h3>
                <p className="text-gray-500 mb-4">
                  {searchQuery || statusFilter !== 'all' 
                    ? "No calculations match your current filters."
                    : "Get started by running your first calculation."
                  }
                </p>
                <Button asChild>
                  <Link href="/dashboard/calculations/new">
                    <Plus className="w-4 h-4 mr-2" />
                    Run Calculation
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredCalculations.map((calculation) => {
            const StatusIcon = getStatusIcon(calculation.status)
            return (
              <Card key={calculation.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-1">{calculation.name}</CardTitle>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <span>{formatCalculationType(calculation.calculation_type)}</span>
                        {calculation.vessel_tag_number && (
                          <>
                            <span>•</span>
                            <span>{calculation.vessel_tag_number}</span>
                          </>
                        )}
                        {calculation.vessel_name && (
                          <>
                            <span>•</span>
                            <span>{calculation.vessel_name}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(calculation.status)}>
                        <StatusIcon className="w-3 h-3 mr-1" />
                        {calculation.status}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Created: {formatDate(calculation.created_at)}</span>
                    {calculation.completed_at && (
                      <span>Completed: {formatDate(calculation.completed_at)}</span>
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
