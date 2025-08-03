'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  Calculator, 
  FileCheck, 
  Users, 
  Database, 
  BarChart3,
  Zap,
  Target,
  CheckCircle,
  ArrowRight,
  Menu,
  X,
  Plus,
  Search,
  Filter,
  Eye,
  Edit,
  Trash2
} from 'lucide-react'
import { useState } from 'react'

export default function VesselsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')

  // Mock data for vessels
  const vessels = [
    {
      id: 1,
      name: 'Primary Heat Exchanger',
      tag: 'VES-001',
      type: 'Heat Exchanger',
      status: 'active',
      pressure: '150 PSI',
      temperature: '350°F',
      lastInspection: '2024-01-15',
      nextInspection: '2025-01-15',
      condition: 'excellent'
    }
  ]

  return (
    <div className="min-h-full w-full">
      {/* Page Header */}
      <div className="mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm p-8">
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Shield className="h-8 w-8 text-cyan-400" />
                  <h1 className="text-4xl font-bold text-slate-100">Vessel Registry</h1>
                </div>
                <p className="text-lg text-slate-300">
                  Secure pressure vessel certification and compliance tracking
                  <span className="text-cyan-400 font-medium"> - ASME certified</span>
                </p>
              </div>
              <div className="hidden lg:block">
                <div className="text-right">
                  <div className="text-3xl font-bold text-cyan-400">{vessels.length}</div>
                  <div className="text-sm text-slate-400">Active Vessels</div>
                </div>
              </div>
            </div>
            
            {/* Quick Stats */}
            <div className="flex items-center space-x-6 p-4 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-emerald-400" />
                <span className="text-slate-300 text-sm">ASME Certified</span>
              </div>
              <div className="flex items-center space-x-2">
                <Target className="h-4 w-4 text-blue-400" />
                <span className="text-slate-300 text-sm">Compliance Tracking</span>
              </div>
              <div className="flex items-center space-x-2">
                <Database className="h-4 w-4 text-purple-400" />
                <span className="text-slate-300 text-sm">Digital Records</span>
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
              placeholder="Search vessels..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all duration-200"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all duration-200"
          >
            <option value="all">All Types</option>
            <option value="heat_exchanger">Heat Exchangers</option>
            <option value="storage_tank">Storage Tanks</option>
            <option value="reactor">Reactors</option>
          </select>
        </div>
        
        {/* Add Vessel Button */}
        <Link href="/dashboard/vessels/new">
          <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 group">
            <Plus className="h-5 w-5 mr-2 group-hover:rotate-90 transition-transform duration-300" />
            Add Vessel
          </Button>
        </Link>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Vessels List */}
        <div className="lg:col-span-2 space-y-6">
          {vessels.length > 0 ? (
            vessels.map((vessel) => (
              <Card key={vessel.id} className="group relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm hover:border-cyan-500/50 transition-all duration-300">
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <CardContent className="p-6 relative">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-4">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 text-cyan-400 group-hover:scale-110 transition-transform duration-300">
                        <Shield className="w-6 h-6" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-slate-100 mb-1">{vessel.name}</h3>
                        <p className="text-slate-300 text-sm mb-2">{vessel.tag} • {vessel.type}</p>
                        <div className="flex items-center space-x-3">
                          <Badge className={`${
                            vessel.condition === 'excellent' 
                              ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' 
                              : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                          } text-xs`}>
                            {vessel.condition}
                          </Badge>
                          <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30 text-xs">
                            {vessel.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-cyan-400">{vessel.pressure}</div>
                      <div className="text-xs text-slate-400">{vessel.temperature}</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                    <div className="text-slate-400">
                      <span className="text-slate-300">Last Inspection:</span><br />
                      {vessel.lastInspection}
                    </div>
                    <div className="text-slate-400">
                      <span className="text-slate-300">Next Due:</span><br />
                      {vessel.nextInspection}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <Link href={`/dashboard/vessels/${vessel.id}`}>
                        <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50">
                          <Eye className="w-4 h-4 mr-2" />
                          View Details
                        </Button>
                      </Link>
                      <Link href={`/dashboard/vessels/${vessel.id}/edit`}>
                        <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50">
                          <Edit className="w-4 h-4 mr-2" />
                          Edit
                        </Button>
                      </Link>
                    </div>
                    <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all duration-300" />
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            /* Empty State */
            <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5"></div>
              <CardContent className="p-12 text-center relative">
                <div className="mb-6">
                  <Shield className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-100 mb-2">No Vessels Yet</h3>
                  <p className="text-slate-400 mb-6">
                    Get started by adding your first pressure vessel to begin FFS assessments.
                  </p>
                </div>
                <Link href="/dashboard/vessels/new">
                  <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300">
                    <Plus className="h-5 w-5 mr-2" />
                    Add Your First Vessel
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">

          {/* Vessel Categories */}
          <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5"></div>
            <CardHeader className="relative">
              <CardTitle className="text-slate-100 flex items-center space-x-2">
                <Target className="w-5 h-5 text-blue-400" />
                <span>Vessel Categories</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="relative">
              <div className="space-y-4">
                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-cyan-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20 text-cyan-400">
                      <Shield className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">Heat Exchangers</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Shell & tube, plate, and air-cooled heat exchangers.
                  </p>
                  <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30 text-xs">
                    High Priority
                  </Badge>
                </div>

                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-emerald-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-green-500/20 text-emerald-400">
                      <Database className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">Storage Tanks</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Atmospheric and pressure storage tanks.
                  </p>
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">
                    Standard
                  </Badge>
                </div>

                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-purple-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-indigo-500/20 text-purple-400">
                      <Zap className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">Reactors</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Chemical reactors and process vessels.
                  </p>
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                    Critical
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-orange-500/5"></div>
            <CardHeader className="relative">
              <CardTitle className="text-slate-100 flex items-center space-x-2">
                <Zap className="w-5 h-5 text-amber-400" />
                <span>Quick Actions</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="relative space-y-3">
              <Link href="/dashboard/vessels/import">
                <Button variant="ghost" className="w-full justify-start text-slate-300 hover:text-slate-100 hover:bg-slate-800/50 transition-all duration-200">
                  <Database className="w-4 h-4 mr-3" />
                  Import Vessels
                </Button>
              </Link>
              <Link href="/dashboard/vessels/reports">
                <Button variant="ghost" className="w-full justify-start text-slate-300 hover:text-slate-100 hover:bg-slate-800/50 transition-all duration-200">
                  <BarChart3 className="w-4 h-4 mr-3" />
                  Vessel Reports
                </Button>
              </Link>
              <Link href="/dashboard/vessels/maintenance">
                <Button variant="ghost" className="w-full justify-start text-slate-300 hover:text-slate-100 hover:bg-slate-800/50 transition-all duration-200">
                  <CheckCircle className="w-4 h-4 mr-3" />
                  Maintenance Schedule
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
