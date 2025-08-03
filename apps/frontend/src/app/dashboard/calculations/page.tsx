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
  Download,
  Clock,
  Activity,
  Settings,
  ChevronRight,
  Sparkles,
  Brain,
  Award
} from 'lucide-react'
import { useState } from 'react'

export default function CalculationsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')

  // Mock data for calculations
  const calculations = [
    {
      id: 1,
      name: 'ASME VIII Analysis - VES-001',
      type: 'ASME VIII Div 1',
      vessel: 'Primary Heat Exchanger',
      status: 'completed',
      result: 'Passed',
      date: '2024-01-15',
      progress: 100,
      icon: Shield,
      color: 'text-emerald-400'
    },
    {
      id: 2,
      name: 'API 579 FFS Assessment - VES-002',
      type: 'API 579',
      vessel: 'Storage Tank A',
      status: 'in_progress',
      result: 'Pending',
      date: '2024-01-20',
      progress: 65,
      icon: FileCheck,
      color: 'text-blue-400'
    }
  ]

  return (
    <div className="min-h-full w-full">
      {/* Page Header */}
      <div className="mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm p-8">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-cyan-500/5"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Calculator className="h-8 w-8 text-emerald-400" />
                  <h1 className="text-4xl font-bold text-slate-100">Smart Calculations</h1>
                  <Sparkles className="h-6 w-6 text-amber-400" />
                </div>
                <p className="text-lg text-slate-300">
                  Advanced engineering calculations and FFS assessments
                  <span className="text-emerald-400 font-medium"> - 99.7% accuracy rate</span>
                </p>
              </div>
              <div className="hidden lg:block">
                <div className="text-right">
                  <div className="text-3xl font-bold text-emerald-400">12</div>
                  <div className="text-sm text-slate-400">Calculations</div>
                </div>
              </div>
            </div>
            
            {/* Quick Stats */}
            <div className="flex items-center space-x-6 p-4 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <div className="flex items-center space-x-2">
                <Brain className="h-4 w-4 text-purple-400" />
                <span className="text-slate-300 text-sm">AI-Enhanced</span>
              </div>
              <div className="flex items-center space-x-2">
                <Award className="h-4 w-4 text-amber-400" />
                <span className="text-slate-300 text-sm">Industry Certified</span>
              </div>
              <div className="flex items-center space-x-2">
                <Activity className="h-4 w-4 text-cyan-400" />
                <span className="text-slate-300 text-sm">Real-time Results</span>
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
              placeholder="Search calculations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all duration-200"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all duration-200"
          >
            <option value="all">All Types</option>
            <option value="asme">ASME VIII</option>
            <option value="api579">API 579</option>
            <option value="remaining_life">Remaining Life</option>
          </select>
        </div>
        
        {/* New Calculation Button */}
        <Link href="/dashboard/calculations/new">
          <Button className="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 group">
            <Plus className="h-5 w-5 mr-2 group-hover:rotate-90 transition-transform duration-300" />
            New Calculation
          </Button>
        </Link>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Calculations List */}
        <div className="lg:col-span-2 space-y-6">
          {calculations.length > 0 ? (
            calculations.map((calc) => {
              const IconComponent = calc.icon
              return (
                <Card key={calc.id} className="group relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm hover:border-emerald-500/50 transition-all duration-300">
                  <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <CardContent className="p-6 relative">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start space-x-4">
                        <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/20 to-green-500/20 text-emerald-400 group-hover:scale-110 transition-transform duration-300">
                          <IconComponent className="w-6 h-6" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-bold text-slate-100 mb-1">{calc.name}</h3>
                          <p className="text-slate-300 text-sm mb-2">{calc.vessel}</p>
                          <div className="flex items-center space-x-3">
                            <Badge className={`${
                              calc.status === 'completed' 
                                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' 
                                : 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                            } text-xs`}>
                              {calc.status === 'completed' ? 'Completed' : 'In Progress'}
                            </Badge>
                            <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                              {calc.type}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${
                          calc.result === 'Passed' ? 'text-emerald-400' : 'text-slate-400'
                        }`}>
                          {calc.result}
                        </div>
                        <div className="text-xs text-slate-400">{calc.date}</div>
                      </div>
                    </div>
                    
                    {calc.status === 'in_progress' && (
                      <div className="mb-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-slate-300">Progress</span>
                          <span className="text-sm text-slate-400">{calc.progress}%</span>
                        </div>
                        <div className="w-full h-2 bg-slate-700/50 rounded-full">
                          <div 
                            className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full transition-all duration-300" 
                            style={{ width: `${calc.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <Link href={`/dashboard/calculations/${calc.id}`}>
                          <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50">
                            <Eye className="w-4 h-4 mr-2" />
                            View Details
                          </Button>
                        </Link>
                        {calc.status === 'completed' && (
                          <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50">
                            <Download className="w-4 h-4 mr-2" />
                            Download Report
                          </Button>
                        )}
                      </div>
                      <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all duration-300" />
                    </div>
                  </CardContent>
                </Card>
              )
            })
          ) : (
            /* Empty State */
            <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-cyan-500/5"></div>
              <CardContent className="p-12 text-center relative">
                <div className="mb-6">
                  <Calculator className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-100 mb-2">No Calculations Yet</h3>
                  <p className="text-slate-400 mb-6">
                    Start your first FFS assessment by running calculations on your vessels.
                  </p>
                </div>
                <Link href="/dashboard/calculations/new">
                  <Button className="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300">
                    <Plus className="h-5 w-5 mr-2" />
                    Start Your First Calculation
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">

          {/* Calculation Types */}
          <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-blue-500/5"></div>
            <CardHeader className="relative">
              <CardTitle className="text-slate-100 flex items-center space-x-2">
                <Target className="w-5 h-5 text-purple-400" />
                <span>Available Calculation Types</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="relative">
              <div className="space-y-4">
                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-cyan-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20 text-cyan-400">
                      <Shield className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">ASME VIII Div 1</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Thickness calculations for pressure vessels according to ASME Code.
                  </p>
                  <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30 text-xs">
                    Design Code
                  </Badge>
                </div>

                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-emerald-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-green-500/20 text-emerald-400">
                      <FileCheck className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">API 579 FFS</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Fitness-For-Service assessments for equipment with flaws.
                  </p>
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">
                    Assessment
                  </Badge>
                </div>

                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-purple-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-indigo-500/20 text-purple-400">
                      <Database className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">Remaining Life</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Calculate remaining life based on corrosion rates.
                  </p>
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                    Analysis
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
              <Link href="/dashboard/calculations/batch">
                <Button variant="ghost" className="w-full justify-start text-slate-300 hover:text-slate-100 hover:bg-slate-800/50 transition-all duration-200">
                  <Database className="w-4 h-4 mr-3" />
                  Batch Calculations
                </Button>
              </Link>
              <Link href="/dashboard/calculations/templates">
                <Button variant="ghost" className="w-full justify-start text-slate-300 hover:text-slate-100 hover:bg-slate-800/50 transition-all duration-200">
                  <FileCheck className="w-4 h-4 mr-3" />
                  Calculation Templates
                </Button>
              </Link>
              <Link href="/dashboard/calculations/reports">
                <Button variant="ghost" className="w-full justify-start text-slate-300 hover:text-slate-100 hover:bg-slate-800/50 transition-all duration-200">
                  <BarChart3 className="w-4 h-4 mr-3" />
                  View All Reports
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
