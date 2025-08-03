'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/auth-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  ArrowLeft, 
  FileText, 
  Download, 
  Share2, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Clock,
  Calculator,
  TrendingUp,
  Shield,
  Info
} from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface Calculation {
  id: number
  name: string
  description: string
  calculation_type: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  input_parameters: any
  results?: any
  created_at: string
  updated_at: string
  completed_at?: string
  calculated_by: {
    id: number
    first_name: string
    last_name: string
  }
  project: {
    id: number
    name: string
  }
  vessel?: {
    id: number
    name: string
    tag_number: string
  }
}

export default function CalculationDetailPage() {
  const { id } = useParams()
  const { token } = useAuth()
  const router = useRouter()
  const [calculation, setCalculation] = useState<Calculation | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)

  useEffect(() => {
    fetchCalculation()
  }, [id, token])

  const fetchCalculation = async () => {
    if (!token || !id) return

    try {
      const data = await apiService.getCalculation(parseInt(id as string), token)
      setCalculation(data as Calculation)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to fetch calculation')
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'running':
        return <Clock className="h-5 w-5 text-blue-500" />
      case 'pending':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      running: 'bg-blue-100 text-blue-800',
      pending: 'bg-yellow-100 text-yellow-800',
      cancelled: 'bg-gray-100 text-gray-800'
    }
    return variants[status as keyof typeof variants] || 'bg-gray-100 text-gray-800'
  }

  const handleGenerateReport = async () => {
    if (!calculation) return

    setIsGeneratingReport(true)
    try {
      await apiService.generateReport({
        calculation_id: calculation.id,
        report_type: 'calculation_report',
        format: 'pdf'
      }, token!)
      // Handle success - could show a toast or redirect
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to generate report')
    } finally {
      setIsGeneratingReport(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (!calculation) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>Calculation not found</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/calculations">
            <Button variant="outline" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{calculation.name}</h1>
            <p className="text-gray-600">{calculation.description}</p>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleGenerateReport} disabled={isGeneratingReport}>
            {isGeneratingReport ? (
              <>
                <Clock className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <FileText className="mr-2 h-4 w-4" />
                Generate Report
              </>
            )}
          </Button>
          <Button variant="outline">
            <Share2 className="mr-2 h-4 w-4" />
            Share
          </Button>
        </div>
      </div>

      {/* Status and Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              {getStatusIcon(calculation.status)}
              <div>
                <p className="text-sm font-medium text-gray-900">Status</p>
                <Badge className={getStatusBadge(calculation.status)}>
                  {calculation.status}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <Calculator className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">Type</p>
                <p className="text-sm text-gray-600">{calculation.calculation_type}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <TrendingUp className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">Created</p>
                <p className="text-sm text-gray-600">
                  {new Date(calculation.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Calculation Results */}
      {calculation.status === 'completed' && calculation.results && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-green-500" />
              <span>Calculation Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {calculation.results.allowable_pressure && (
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-sm font-medium text-green-800">Allowable Pressure</p>
                  <p className="text-2xl font-bold text-green-900">
                    {calculation.results.allowable_pressure} psi
                  </p>
                </div>
              )}
              
              {calculation.results.calculated_thickness && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-sm font-medium text-blue-800">Required Thickness</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {calculation.results.calculated_thickness} inches
                  </p>
                </div>
              )}
              
              {calculation.results.safety_factor && (
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-sm font-medium text-purple-800">Safety Factor</p>
                  <p className="text-2xl font-bold text-purple-900">
                    {calculation.results.safety_factor}
                  </p>
                </div>
              )}
              
              {calculation.results.compliance_status && (
                <div className={`p-4 rounded-lg ${
                  calculation.results.compliance_status === 'PASS' 
                    ? 'bg-green-50' 
                    : 'bg-red-50'
                }`}>
                  <p className="text-sm font-medium text-gray-800">Compliance Status</p>
                  <Badge className={
                    calculation.results.compliance_status === 'PASS' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }>
                    {calculation.results.compliance_status}
                  </Badge>
                </div>
              )}
            </div>

            {calculation.results.recommendations && calculation.results.recommendations.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Recommendations</h3>
                <ul className="space-y-2">
                  {calculation.results.recommendations.map((rec: string, index: number) => (
                    <li key={index} className="flex items-start space-x-2">
                      <Info className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {calculation.results.warnings && calculation.results.warnings.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Warnings</h3>
                <ul className="space-y-2">
                  {calculation.results.warnings.map((warning: string, index: number) => (
                    <li key={index} className="flex items-start space-x-2">
                      <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{warning}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Input Parameters */}
      <Card>
        <CardHeader>
          <CardTitle>Input Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(calculation.input_parameters).map(([key, value]) => (
              <div key={key} className="bg-gray-50 p-3 rounded-lg">
                <p className="text-sm font-medium text-gray-900">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </p>
                <p className="text-sm text-gray-600">
                  {typeof value === 'number' ? value.toLocaleString() : String(value)}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Calculation Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Project Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-900">Project</p>
              <p className="text-sm text-gray-600">{calculation.project.name}</p>
            </div>
            {calculation.vessel && (
              <div>
                <p className="text-sm font-medium text-gray-900">Vessel</p>
                <p className="text-sm text-gray-600">
                  {calculation.vessel.tag_number} - {calculation.vessel.name}
                </p>
              </div>
            )}
            <div>
              <p className="text-sm font-medium text-gray-900">Calculated By</p>
              <p className="text-sm text-gray-600">
                {calculation.calculated_by.first_name} {calculation.calculated_by.last_name}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Timing Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-900">Created</p>
              <p className="text-sm text-gray-600">
                {new Date(calculation.created_at).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Last Updated</p>
              <p className="text-sm text-gray-600">
                {new Date(calculation.updated_at).toLocaleString()}
              </p>
            </div>
            {calculation.completed_at && (
              <div>
                <p className="text-sm font-medium text-gray-900">Completed</p>
                <p className="text-sm text-gray-600">
                  {new Date(calculation.completed_at).toLocaleString()}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      {calculation.status === 'completed' && (
        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-4">
              <Button onClick={handleGenerateReport} disabled={isGeneratingReport}>
                {isGeneratingReport ? (
                  <>
                    <Clock className="mr-2 h-4 w-4 animate-spin" />
                    Generating Report...
                  </>
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Generate PDF Report
                  </>
                )}
              </Button>
              <Button variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Export Results
              </Button>
              <Button variant="outline">
                <Share2 className="mr-2 h-4 w-4" />
                Share Results
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 