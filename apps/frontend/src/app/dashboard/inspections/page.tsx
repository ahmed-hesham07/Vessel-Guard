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
  Calendar
} from 'lucide-react'
import { useState } from 'react'

export default function InspectionsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  // Mock data for inspections
  const inspections = [
    {
      id: 1,
      vessel: 'Primary Heat Exchanger',
      vesselTag: 'VES-001',
      type: 'Annual Inspection',
      status: 'scheduled',
      date: '2024-02-15',
      inspector: 'John Smith',
      priority: 'high',
      location: 'Unit 1'
    }
  ]

  return (
    <div className="min-h-full w-full">
      {/* Page Header */}
      <div className="mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm p-8">
          <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-orange-500/5"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <FileCheck className="h-8 w-8 text-amber-400" />
                  <h1 className="text-4xl font-bold text-slate-100">Inspection Hub</h1>
                </div>
                <p className="text-lg text-slate-300">
                  Schedule and track critical vessel inspections
                  <span className="text-amber-400 font-medium"> - Priority system</span>
                </p>
              </div>
              <div className="hidden lg:block">
                <div className="text-right">
                  <div className="text-3xl font-bold text-amber-400">{inspections.length}</div>
                  <div className="text-sm text-slate-400">Active Inspections</div>
                </div>
              </div>
            </div>
            
            {/* Quick Stats */}
            <div className="flex items-center space-x-6 p-4 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-blue-400" />
                <span className="text-slate-300 text-sm">Scheduled Tracking</span>
              </div>
              <div className="flex items-center space-x-2">
                <Target className="h-4 w-4 text-emerald-400" />
                <span className="text-slate-300 text-sm">Compliance Focus</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-purple-400" />
                <span className="text-slate-300 text-sm">Quality Assurance</span>
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
              placeholder="Search inspections..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50 transition-all duration-200"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 focus:outline-none focus:ring-2 focus:ring-amber-500/50 transition-all duration-200"
          >
            <option value="all">All Status</option>
            <option value="scheduled">Scheduled</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="overdue">Overdue</option>
          </select>
        </div>
        
        {/* Schedule Inspection Button */}
        <Link href="/dashboard/inspections/new">
          <Button className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 group">
            <Plus className="h-5 w-5 mr-2 group-hover:rotate-90 transition-transform duration-300" />
            Schedule Inspection
          </Button>
        </Link>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Inspections List */}
        <div className="lg:col-span-2 space-y-6">
          {inspections.length > 0 ? (
            inspections.map((inspection) => (
              <Card key={inspection.id} className="group relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm hover:border-amber-500/50 transition-all duration-300">
                <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-orange-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <CardContent className="p-6 relative">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-4">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 text-amber-400 group-hover:scale-110 transition-transform duration-300">
                        <FileCheck className="w-6 h-6" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-slate-100 mb-1">{inspection.type}</h3>
                        <p className="text-slate-300 text-sm mb-2">{inspection.vessel} • {inspection.vesselTag}</p>
                        <div className="flex items-center space-x-3">
                          <Badge className={`${
                            inspection.status === 'scheduled' 
                              ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' 
                              : inspection.status === 'completed'
                              ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                              : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                          } text-xs`}>
                            {inspection.status.replace('_', ' ')}
                          </Badge>
                          <Badge className={`${
                            inspection.priority === 'high'
                              ? 'bg-red-500/20 text-red-400 border-red-500/30'
                              : 'bg-slate-500/20 text-slate-400 border-slate-500/30'
                          } text-xs`}>
                            {inspection.priority} priority
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-amber-400">{inspection.date}</div>
                      <div className="text-xs text-slate-400">{inspection.location}</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 gap-4 mb-4 text-sm">
                    <div className="text-slate-400">
                      <span className="text-slate-300">Inspector:</span> {inspection.inspector}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <Link href={`/dashboard/inspections/${inspection.id}`}>
                        <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50">
                          <Eye className="w-4 h-4 mr-2" />
                          View Details
                        </Button>
                      </Link>
                      <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50">
                        <Calendar className="w-4 h-4 mr-2" />
                        Reschedule
                      </Button>
                    </div>
                    <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-amber-400 group-hover:translate-x-1 transition-all duration-300" />
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            /* Empty State */
            <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-orange-500/5"></div>
              <CardContent className="p-12 text-center relative">
                <div className="mb-6">
                  <FileCheck className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-100 mb-2">No Inspections Scheduled</h3>
                  <p className="text-slate-400 mb-6">
                    Schedule your first vessel inspection to ensure compliance and safety.
                  </p>
                </div>
                <Link href="/dashboard/inspections/new">
                  <Button className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300">
                    <Plus className="h-5 w-5 mr-2" />
                    Schedule Your First Inspection
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">

          {/* Inspection Types */}
          <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5"></div>
            <CardHeader className="relative">
              <CardTitle className="text-slate-100 flex items-center space-x-2">
                <Target className="w-5 h-5 text-blue-400" />
                <span>Inspection Types</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="relative">
              <div className="space-y-4">
                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-blue-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500/20 to-cyan-500/20 text-blue-400">
                      <Calendar className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">Annual Inspection</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Regular annual inspections to ensure vessel integrity.
                  </p>
                  <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-xs">
                    Required
                  </Badge>
                </div>

                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-emerald-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-green-500/20 text-emerald-400">
                      <FileCheck className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">Fitness-For-Service</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Detailed assessments when vessels have flaws.
                  </p>
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">
                    Assessment
                  </Badge>
                </div>

                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-purple-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-indigo-500/20 text-purple-400">
                      <Shield className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">Pre-Startup</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Inspections before vessel startup or maintenance.
                  </p>
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                    Safety
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Calendar Overview */}
          <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-orange-500/5"></div>
            <CardHeader className="relative">
              <CardTitle className="text-slate-100 flex items-center space-x-2">
                <Calendar className="w-5 h-5 text-amber-400" />
                <span>Upcoming Schedule</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="relative space-y-3">
              <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-700/50">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-100">This Week</span>
                  <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 text-xs">3 Due</Badge>
                </div>
                <p className="text-xs text-slate-400">2 vessels require inspection</p>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-700/50">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-100">Next Month</span>
                  <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-xs">5 Scheduled</Badge>
                </div>
                <p className="text-xs text-slate-400">Regular maintenance inspections</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
