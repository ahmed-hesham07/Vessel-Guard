'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  FileText, 
  Plus, 
  Search, 
  Download, 
  Calendar, 
  Filter,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  BarChart3,
  PieChart,
  TrendingUp
} from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface Report {
  id: number
  title: string
  type: 'inspection' | 'compliance' | 'analysis' | 'summary' | 'custom'
  status: 'generating' | 'completed' | 'error' | 'archived'
  description: string
  created_at: string
  updated_at: string
  file_url?: string
  file_size?: number
  page_count?: number
  project: {
    id: number
    name: string
  }
  generated_by: {
    id: number
    first_name: string
    last_name: string
  }
  parameters: {
    date_range: {
      start_date: string
      end_date: string
    }
    include_vessels: boolean
    include_calculations: boolean
    include_inspections: boolean
    format: 'pdf' | 'excel' | 'word'
  }
}

const reportTypeLabels = {
  inspection: 'Inspection Report',
  compliance: 'Compliance Report',
  analysis: 'Analysis Report',
  summary: 'Summary Report',
  custom: 'Custom Report'
}

const statusColors = {
  generating: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
  archived: 'bg-gray-100 text-gray-800'
}

export default function ReportsPage() {
  const { token } = useAuth()
  const [reports, setReports] = useState<Report[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    const fetchReports = async () => {
      if (!token) return

      try {
        const data = await apiService.getReports(token)
        setReports(data as Report[])
      } catch (error) {
        console.error('Error fetching reports:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchReports()
  }, [token])

  const filteredReports = reports.filter(report => {
    const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = typeFilter === 'all' || report.type === typeFilter
    const matchesStatus = statusFilter === 'all' || report.status === statusFilter
    
    return matchesSearch && matchesType && matchesStatus
  })

  const handleDownload = (report: Report) => {
    if (report.file_url) {
      window.open(report.file_url, '_blank')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getReportIcon = (type: string) => {
    switch (type) {
      case 'inspection': return <FileText className="h-5 w-5 text-blue-500" />
      case 'compliance': return <BarChart3 className="h-5 w-5 text-green-500" />
      case 'analysis': return <TrendingUp className="h-5 w-5 text-purple-500" />
      case 'summary': return <PieChart className="h-5 w-5 text-orange-500" />
      default: return <FileText className="h-5 w-5 text-gray-500" />
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
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600">
            Generate and manage inspection, compliance, and analysis reports
          </p>
        </div>
        <Button asChild>
          <Link href="/reports/new">
            <Plus className="h-4 w-4 mr-2" />
            Generate Report
          </Link>
        </Button>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <Link href="/reports/new?type=inspection">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <FileText className="h-8 w-8 text-blue-500" />
                <div>
                  <h3 className="font-medium text-gray-900">Inspection Report</h3>
                  <p className="text-sm text-gray-500">Vessel inspection status</p>
                </div>
              </div>
            </CardContent>
          </Link>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <Link href="/reports/new?type=compliance">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <BarChart3 className="h-8 w-8 text-green-500" />
                <div>
                  <h3 className="font-medium text-gray-900">Compliance Report</h3>
                  <p className="text-sm text-gray-500">Regulatory compliance</p>
                </div>
              </div>
            </CardContent>
          </Link>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <Link href="/reports/new?type=analysis">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <TrendingUp className="h-8 w-8 text-purple-500" />
                <div>
                  <h3 className="font-medium text-gray-900">Analysis Report</h3>
                  <p className="text-sm text-gray-500">Engineering analysis</p>
                </div>
              </div>
            </CardContent>
          </Link>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <Link href="/reports/new?type=summary">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <PieChart className="h-8 w-8 text-orange-500" />
                <div>
                  <h3 className="font-medium text-gray-900">Summary Report</h3>
                  <p className="text-sm text-gray-500">Project summary</p>
                </div>
              </div>
            </CardContent>
          </Link>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search reports..."
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
            <option value="inspection">Inspection</option>
            <option value="compliance">Compliance</option>
            <option value="analysis">Analysis</option>
            <option value="summary">Summary</option>
            <option value="custom">Custom</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Status</option>
            <option value="generating">Generating</option>
            <option value="completed">Completed</option>
            <option value="error">Error</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      {/* Reports List */}
      <div className="space-y-4">
        {filteredReports.map((report) => (
          <Card key={report.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    {getReportIcon(report.type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-medium text-gray-900">
                        {report.title}
                      </h3>
                      <Badge variant="outline">
                        {reportTypeLabels[report.type]}
                      </Badge>
                      <Badge className={statusColors[report.status]}>
                        {report.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {report.description}
                    </p>
                    <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
                      <span>Project: {report.project.name}</span>
                      <span>•</span>
                      <span>By: {report.generated_by.first_name} {report.generated_by.last_name}</span>
                      <span>•</span>
                      <span>Created: {new Date(report.created_at).toLocaleDateString()}</span>
                      {report.file_size && (
                        <>
                          <span>•</span>
                          <span>{formatFileSize(report.file_size)}</span>
                        </>
                      )}
                      {report.page_count && (
                        <>
                          <span>•</span>
                          <span>{report.page_count} pages</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {report.status === 'completed' && report.file_url && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDownload(report)}
                    >
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                  )}
                  <Button variant="outline" size="sm" asChild>
                    <Link href={`/reports/${report.id}`}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Link>
                  </Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredReports.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No reports found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || typeFilter !== 'all' || statusFilter !== 'all'
              ? 'No reports match your current filters.' 
              : 'Generate your first report to get started.'}
          </p>
          <Button asChild>
            <Link href="/reports/new">
              <Plus className="h-4 w-4 mr-2" />
              Generate Report
            </Link>
          </Button>
        </div>
      )}
    </div>
  )
}
