'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowLeft, Save, Loader2, Calendar } from 'lucide-react'
import Link from 'next/link'
import { apiService } from '@/lib/api'

interface InspectionFormData {
  vessel_id: string
  inspection_type: string
  inspection_date: string
  inspector_name: string
  inspector_certification: string
  findings: string
  recommendations: string
  result: string
  next_inspection_date: string
  inspection_interval_months: string
}

export default function NewInspectionPage() {
  const { token } = useAuth()
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [vessels, setVessels] = useState<any[]>([])
  
  const [formData, setFormData] = useState<InspectionFormData>({
    vessel_id: '',
    inspection_type: 'visual',
    inspection_date: '',
    inspector_name: '',
    inspector_certification: '',
    findings: '',
    recommendations: '',
    result: 'pass',
    next_inspection_date: '',
    inspection_interval_months: '12'
  })

  // Load vessels on component mount
  useEffect(() => {
    const fetchVessels = async () => {
      if (!token) return
      
      try {
        const response = await apiService.getVessels(token)
        setVessels((response as any).items || (response as any[]))
      } catch (error) {
        console.error('Error fetching vessels:', error)
      }
    }
    
    fetchVessels()
  }, [token])

  const handleInputChange = (field: keyof InspectionFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!token) return

    setIsSubmitting(true)
    setError(null)

    try {
      const submitData = {
        vessel_id: parseInt(formData.vessel_id),
        inspection_type: formData.inspection_type,
        inspection_date: formData.inspection_date,
        inspector_name: formData.inspector_name,
        inspector_certification: formData.inspector_certification,
        findings: formData.findings,
        recommendations: formData.recommendations,
        result: formData.result,
        next_inspection_date: formData.next_inspection_date || null,
        inspection_interval_months: parseInt(formData.inspection_interval_months) || 12,
      }

      await apiService.createInspection(submitData, token)
      router.push('/dashboard/inspections')
    } catch (error: any) {
      console.error('Error creating inspection:', error)
      setError(error.message || 'Failed to create inspection')
    } finally {
      setIsSubmitting(false)
    }
  }

  const getTodayDate = () => {
    return new Date().toISOString().split('T')[0]
  }

  const getDefaultNextInspectionDate = () => {
    const today = new Date()
    const nextYear = new Date(today)
    nextYear.setFullYear(today.getFullYear() + 1)
    return nextYear.toISOString().split('T')[0]
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/dashboard/inspections">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Schedule Inspection</h1>
            <p className="text-gray-600">
              Create a new inspection record for a vessel
            </p>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle>Inspection Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="vessel_id">Vessel *</Label>
                <select
                  id="vessel_id"
                  value={formData.vessel_id}
                  onChange={(e) => handleInputChange('vessel_id', e.target.value)}
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="">Select a vessel</option>
                  {vessels.map((vessel) => (
                    <option key={vessel.id} value={vessel.id}>
                      {vessel.tag_number} - {vessel.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="inspection_type">Inspection Type *</Label>
                <select
                  id="inspection_type"
                  value={formData.inspection_type}
                  onChange={(e) => handleInputChange('inspection_type', e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="visual">Visual</option>
                  <option value="ultrasonic">Ultrasonic</option>
                  <option value="radiographic">Radiographic</option>
                  <option value="magnetic_particle">Magnetic Particle</option>
                  <option value="liquid_penetrant">Liquid Penetrant</option>
                  <option value="eddy_current">Eddy Current</option>
                  <option value="pressure_test">Pressure Test</option>
                  <option value="leak_test">Leak Test</option>
                  <option value="thickness_measurement">Thickness Measurement</option>
                  <option value="regulatory">Regulatory</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <Label htmlFor="inspection_date">Inspection Date *</Label>
                <Input
                  id="inspection_date"
                  type="date"
                  value={formData.inspection_date}
                  onChange={(e) => handleInputChange('inspection_date', e.target.value)}
                  max={getTodayDate()}
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="result">Result *</Label>
                <select
                  id="result"
                  value={formData.result}
                  onChange={(e) => handleInputChange('result', e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
                  <option value="pass">Pass</option>
                  <option value="fail">Fail</option>
                  <option value="conditional">Conditional</option>
                  <option value="not_applicable">Not Applicable</option>
                </select>
              </div>

              <div>
                <Label htmlFor="inspector_name">Inspector Name *</Label>
                <Input
                  id="inspector_name"
                  type="text"
                  value={formData.inspector_name}
                  onChange={(e) => handleInputChange('inspector_name', e.target.value)}
                  placeholder="Enter inspector name"
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="inspector_certification">Inspector Certification</Label>
                <Input
                  id="inspector_certification"
                  type="text"
                  value={formData.inspector_certification}
                  onChange={(e) => handleInputChange('inspector_certification', e.target.value)}
                  placeholder="e.g., ASNT Level II, API 510"
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="next_inspection_date">Next Inspection Date</Label>
                <Input
                  id="next_inspection_date"
                  type="date"
                  value={formData.next_inspection_date}
                  onChange={(e) => handleInputChange('next_inspection_date', e.target.value)}
                  min={getTodayDate()}
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="inspection_interval_months">Inspection Interval (months)</Label>
                <Input
                  id="inspection_interval_months"
                  type="number"
                  value={formData.inspection_interval_months}
                  onChange={(e) => handleInputChange('inspection_interval_months', e.target.value)}
                  placeholder="12"
                  min="1"
                  max="120"
                  className="mt-1"
                />
              </div>
            </div>

            {/* Findings and Recommendations */}
            <div className="space-y-6">
              <div>
                <Label htmlFor="findings">Findings</Label>
                <textarea
                  id="findings"
                  value={formData.findings}
                  onChange={(e) => handleInputChange('findings', e.target.value)}
                  placeholder="Document any findings, defects, or observations"
                  rows={4}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>

              <div>
                <Label htmlFor="recommendations">Recommendations</Label>
                <textarea
                  id="recommendations"
                  value={formData.recommendations}
                  onChange={(e) => handleInputChange('recommendations', e.target.value)}
                  placeholder="Provide recommendations for repairs, follow-up actions, or next steps"
                  rows={4}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3">
              <Button variant="outline" type="button" asChild>
                <Link href="/dashboard/inspections">Cancel</Link>
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Calendar className="w-4 h-4 mr-2" />
                    Schedule Inspection
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
