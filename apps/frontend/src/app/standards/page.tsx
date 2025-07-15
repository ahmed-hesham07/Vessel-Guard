'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  BookOpen, 
  Search, 
  Filter, 
  ExternalLink,
  Download,
  Star,
  Calendar,
  Users,
  FileText,
  Shield,
  Calculator,
  Eye
} from 'lucide-react'
import Link from 'next/link'

interface Standard {
  id: string
  name: string
  full_name: string
  organization: string
  version: string
  published_date: string
  description: string
  category: 'pressure_vessel' | 'piping' | 'materials' | 'inspection' | 'general'
  status: 'current' | 'superseded' | 'withdrawn' | 'draft'
  is_favorite: boolean
  url?: string
  related_standards: string[]
  applicable_vessels: string[]
  key_sections: {
    section: string
    title: string
    description: string
  }[]
}

const standards: Standard[] = [
  {
    id: 'asme-viii-1',
    name: 'ASME VIII Div 1',
    full_name: 'ASME Boiler and Pressure Vessel Code, Section VIII, Division 1',
    organization: 'ASME',
    version: '2021',
    published_date: '2021-07-01',
    description: 'Rules for construction of pressure vessels operating at pressures above 15 psig.',
    category: 'pressure_vessel',
    status: 'current',
    is_favorite: true,
    url: 'https://www.asme.org/codes-standards/find-codes-standards/bpvc-viii-1-bpvc-section-viii-rules-construction-pressure-vessels-division-1',
    related_standards: ['ASME VIII Div 2', 'ASME IX', 'ASME II'],
    applicable_vessels: ['pressure_vessel', 'storage_tank', 'heat_exchanger', 'reactor'],
    key_sections: [
      { section: 'UG', title: 'General Requirements', description: 'General requirements for all pressure vessels' },
      { section: 'UW', title: 'Welded Construction', description: 'Requirements for welded pressure vessels' },
      { section: 'UCS', title: 'Carbon Steel', description: 'Requirements for carbon steel construction' },
      { section: 'UHA', title: 'High Alloy Steel', description: 'Requirements for high alloy steel construction' }
    ]
  },
  {
    id: 'asme-viii-2',
    name: 'ASME VIII Div 2',
    full_name: 'ASME Boiler and Pressure Vessel Code, Section VIII, Division 2',
    organization: 'ASME',
    version: '2021',
    published_date: '2021-07-01',
    description: 'Alternative rules for construction of pressure vessels based on design by analysis.',
    category: 'pressure_vessel',
    status: 'current',
    is_favorite: false,
    url: 'https://www.asme.org/codes-standards/find-codes-standards/bpvc-viii-2-bpvc-section-viii-rules-construction-pressure-vessels-division-2',
    related_standards: ['ASME VIII Div 1', 'ASME IX', 'ASME II'],
    applicable_vessels: ['pressure_vessel', 'storage_tank', 'heat_exchanger', 'reactor'],
    key_sections: [
      { section: '4', title: 'Design by Analysis Requirements', description: 'Requirements for design by analysis' },
      { section: '5', title: 'Design by Analysis Methods', description: 'Methods for design by analysis' },
      { section: '6', title: 'Fabrication', description: 'Fabrication requirements' }
    ]
  },
  {
    id: 'asme-b31-3',
    name: 'ASME B31.3',
    full_name: 'Process Piping Code',
    organization: 'ASME',
    version: '2020',
    published_date: '2020-07-01',
    description: 'Code for pressure piping systems in petroleum refineries and chemical plants.',
    category: 'piping',
    status: 'current',
    is_favorite: true,
    url: 'https://www.asme.org/codes-standards/find-codes-standards/b31-3-process-piping',
    related_standards: ['ASME B31.1', 'ASME B31.4', 'ASME B31.8'],
    applicable_vessels: ['piping', 'fitting', 'valve'],
    key_sections: [
      { section: '302', title: 'Design Conditions', description: 'Design conditions for piping systems' },
      { section: '304', title: 'Design Criteria', description: 'Design criteria and allowable stresses' },
      { section: '341', title: 'Fabrication', description: 'Fabrication requirements' }
    ]
  },
  {
    id: 'api-579',
    name: 'API 579',
    full_name: 'API 579-1/ASME FFS-1 Fitness-For-Service',
    organization: 'API/ASME',
    version: '2021',
    published_date: '2021-01-01',
    description: 'Standard for fitness-for-service assessment of in-service equipment.',
    category: 'inspection',
    status: 'current',
    is_favorite: false,
    url: 'https://www.api.org/products-and-services/standards/api-579',
    related_standards: ['API 510', 'API 570', 'API 653'],
    applicable_vessels: ['pressure_vessel', 'storage_tank', 'piping', 'heat_exchanger'],
    key_sections: [
      { section: '4', title: 'General Assessment Procedures', description: 'General assessment procedures' },
      { section: '5', title: 'Thinning Assessment', description: 'Assessment of general and local thinning' },
      { section: '9', title: 'Crack Assessment', description: 'Assessment of crack-like flaws' }
    ]
  },
  {
    id: 'api-510',
    name: 'API 510',
    full_name: 'Pressure Vessel Inspection Code',
    organization: 'API',
    version: '2020',
    published_date: '2020-05-01',
    description: 'Code for inspection, rating, repair, and alteration of pressure vessels in service.',
    category: 'inspection',
    status: 'current',
    is_favorite: false,
    url: 'https://www.api.org/products-and-services/standards/api-510',
    related_standards: ['API 579', 'API 570', 'API 653'],
    applicable_vessels: ['pressure_vessel', 'storage_tank'],
    key_sections: [
      { section: '6', title: 'Inspection', description: 'Inspection requirements and methods' },
      { section: '7', title: 'Rating', description: 'Rating of pressure vessels' },
      { section: '8', title: 'Repair and Alteration', description: 'Repair and alteration requirements' }
    ]
  },
  {
    id: 'en-13445',
    name: 'EN 13445',
    full_name: 'Unfired pressure vessels',
    organization: 'CEN',
    version: '2014',
    published_date: '2014-12-01',
    description: 'European standard for unfired pressure vessels.',
    category: 'pressure_vessel',
    status: 'current',
    is_favorite: false,
    url: 'https://standards.cen.eu/dyn/www/f?p=204:110:0::::FSP_PROJECT:24953',
    related_standards: ['EN 13480', 'EN 10028'],
    applicable_vessels: ['pressure_vessel', 'storage_tank'],
    key_sections: [
      { section: '3', title: 'Design', description: 'Design requirements' },
      { section: '4', title: 'Materials', description: 'Materials requirements' },
      { section: '5', title: 'Manufacturing', description: 'Manufacturing requirements' }
    ]
  }
]

const categoryLabels = {
  pressure_vessel: 'Pressure Vessels',
  piping: 'Piping Systems',
  materials: 'Materials',
  inspection: 'Inspection',
  general: 'General'
}

const statusColors = {
  current: 'bg-green-100 text-green-800',
  superseded: 'bg-yellow-100 text-yellow-800',
  withdrawn: 'bg-red-100 text-red-800',
  draft: 'bg-blue-100 text-blue-800'
}

export default function StandardsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [organizationFilter, setOrganizationFilter] = useState<string>('all')

  const filteredStandards = standards.filter(standard => {
    const matchesSearch = standard.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         standard.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         standard.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = categoryFilter === 'all' || standard.category === categoryFilter
    const matchesStatus = statusFilter === 'all' || standard.status === statusFilter
    const matchesOrganization = organizationFilter === 'all' || standard.organization === organizationFilter
    
    return matchesSearch && matchesCategory && matchesStatus && matchesOrganization
  })

  const toggleFavorite = (standardId: string) => {
    // In a real app, this would update the backend
    console.log('Toggle favorite for:', standardId)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Standards & Codes</h1>
          <p className="text-gray-600">
            Browse engineering standards and codes for vessel design and inspection
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" asChild>
            <Link href="/standards/favorites">
              <Star className="h-4 w-4 mr-2" />
              Favorites
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/standards/calculator">
              <Calculator className="h-4 w-4 mr-2" />
              Standards Calculator
            </Link>
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <BookOpen className="h-8 w-8 text-blue-500 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{standards.length}</p>
                <p className="text-sm text-gray-600">Total Standards</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Star className="h-8 w-8 text-yellow-500 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {standards.filter(s => s.is_favorite).length}
                </p>
                <p className="text-sm text-gray-600">Favorites</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-green-500 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {standards.filter(s => s.category === 'pressure_vessel').length}
                </p>
                <p className="text-sm text-gray-600">Pressure Vessel</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-purple-500 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {standards.filter(s => s.category === 'piping').length}
                </p>
                <p className="text-sm text-gray-600">Piping</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search standards..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <div className="flex gap-2">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Categories</option>
            <option value="pressure_vessel">Pressure Vessels</option>
            <option value="piping">Piping Systems</option>
            <option value="materials">Materials</option>
            <option value="inspection">Inspection</option>
            <option value="general">General</option>
          </select>
          <select
            value={organizationFilter}
            onChange={(e) => setOrganizationFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Organizations</option>
            <option value="ASME">ASME</option>
            <option value="API">API</option>
            <option value="CEN">CEN</option>
            <option value="API/ASME">API/ASME</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Status</option>
            <option value="current">Current</option>
            <option value="superseded">Superseded</option>
            <option value="withdrawn">Withdrawn</option>
            <option value="draft">Draft</option>
          </select>
        </div>
      </div>

      {/* Standards List */}
      <div className="space-y-4">
        {filteredStandards.map((standard) => (
          <Card key={standard.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {standard.name}
                    </h3>
                    <Badge variant="outline">
                      {categoryLabels[standard.category]}
                    </Badge>
                    <Badge className={statusColors[standard.status]}>
                      {standard.status}
                    </Badge>
                    <Badge variant="outline">
                      {standard.organization}
                    </Badge>
                    <Badge variant="outline">
                      v{standard.version}
                    </Badge>
                  </div>
                  
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    {standard.full_name}
                  </h4>
                  
                  <p className="text-sm text-gray-600 mb-3">
                    {standard.description}
                  </p>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-1" />
                      Published: {new Date(standard.published_date).toLocaleDateString()}
                    </div>
                    <div className="flex items-center">
                      <Users className="h-4 w-4 mr-1" />
                      Applies to: {standard.applicable_vessels.join(', ')}
                    </div>
                  </div>
                  
                  {standard.key_sections.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm font-medium text-gray-700 mb-2">Key Sections:</p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {standard.key_sections.slice(0, 4).map((section, index) => (
                          <div key={index} className="text-sm">
                            <span className="font-medium text-gray-900">{section.section}:</span>{' '}
                            <span className="text-gray-600">{section.title}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {standard.related_standards.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">Related Standards:</p>
                      <div className="flex flex-wrap gap-1">
                        {standard.related_standards.map((related, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {related}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleFavorite(standard.id)}
                    className="h-8 w-8 p-0"
                  >
                    <Star className={`h-4 w-4 ${standard.is_favorite ? 'text-yellow-500 fill-current' : 'text-gray-400'}`} />
                  </Button>
                  
                  <Button variant="outline" size="sm" asChild>
                    <Link href={`/standards/${standard.id}`}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Link>
                  </Button>
                  
                  {standard.url && (
                    <Button variant="outline" size="sm" asChild>
                      <a href={standard.url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4 mr-1" />
                        Official
                      </a>
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredStandards.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No standards found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || categoryFilter !== 'all' || statusFilter !== 'all' || organizationFilter !== 'all'
              ? 'No standards match your current filters.' 
              : 'Browse our comprehensive collection of engineering standards.'}
          </p>
        </div>
      )}
    </div>
  )
}
