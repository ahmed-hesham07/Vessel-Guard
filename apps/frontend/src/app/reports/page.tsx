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
  Download
} from 'lucide-react'
import { useState } from 'react'

export default function ReportsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [reportType, setReportType] = useState('all')

  // Mock data for reports
  const reports = [
    {
      id: 1,
      name: 'ASME VIII Compliance Report - VES-001',
      type: 'Calculation Report',
      vessel: 'Primary Heat Exchanger',
      date: '2024-01-15',
      status: 'completed',
      format: 'PDF',
      size: '2.4 MB'
    }
  ]

  return (
    <div className="min-h-full w-full">
      {/* Page Header */}
      <div className="mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm p-8">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-indigo-500/5"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <BarChart3 className="h-8 w-8 text-purple-400" />
                  <h1 className="text-4xl font-bold text-slate-100">Professional Reports</h1>
                </div>
                <p className="text-lg text-slate-300">
                  Industry-standard compliance documentation and analytics
                  <span className="text-purple-400 font-medium"> - ISO compliant</span>
                </p>
              </div>
              <div className="hidden lg:block">
                <div className="text-right">
                  <div className="text-3xl font-bold text-purple-400">{reports.length}</div>
                  <div className="text-sm text-slate-400">Generated Reports</div>
                </div>
              </div>
            </div>
            
            {/* Quick Stats */}
            <div className="flex items-center space-x-6 p-4 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-emerald-400" />
                <span className="text-slate-300 text-sm">ISO Compliant</span>
              </div>
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4 text-cyan-400" />
                <span className="text-slate-300 text-sm">ASME Certified</span>
              </div>
              <div className="flex items-center space-x-2">
                <Download className="h-4 w-4 text-blue-400" />
                <span className="text-slate-300 text-sm">Export Ready</span>
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
              placeholder="Search reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all duration-200"
            />
          </div>
          <select
            value={reportType}
            onChange={(e) => setReportType(e.target.value)}
            className="px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-100 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all duration-200"
          >
            <option value="all">All Reports</option>
            <option value="calculation">Calculation Reports</option>
            <option value="inspection">Inspection Reports</option>
            <option value="analytics">Analytics Reports</option>
          </select>
        </div>
        
        {/* Generate Report Button */}
        <Link href="/dashboard/calculations">
          <Button className="bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 group">
            <Plus className="h-5 w-5 mr-2 group-hover:rotate-90 transition-transform duration-300" />
            Generate Report
          </Button>
        </Link>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Reports List */}
        <div className="lg:col-span-2 space-y-6">
          {reports.length > 0 ? (
            reports.map((report) => (
              <Card key={report.id} className="group relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300">
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <CardContent className="p-6 relative">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-4">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-indigo-500/20 text-purple-400 group-hover:scale-110 transition-transform duration-300">
                        <BarChart3 className="w-6 h-6" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-slate-100 mb-1">{report.name}</h3>
                        <p className="text-slate-300 text-sm mb-2">{report.vessel}</p>
                        <div className="flex items-center space-x-3">
                          <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">
                            {report.status}
                          </Badge>
                          <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                            {report.type}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-purple-400">{report.format}</div>
                      <div className="text-xs text-slate-400">{report.size}</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 gap-4 mb-4 text-sm">
                    <div className="text-slate-400">
                      <span className="text-slate-300">Generated:</span> {report.date}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50">
                        <Eye className="w-4 h-4 mr-2" />
                        Preview
                      </Button>
                      <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-100 hover:bg-slate-800/50">
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </div>
                    <ArrowRight className="w-5 h-5 text-slate-400 group-hover:text-purple-400 group-hover:translate-x-1 transition-all duration-300" />
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            /* Empty State */
            <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-indigo-500/5"></div>
              <CardContent className="p-12 text-center relative">
                <div className="mb-6">
                  <BarChart3 className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-100 mb-2">No Reports Generated</h3>
                  <p className="text-slate-400 mb-6">
                    Generate your first compliance report from completed calculations and inspections.
                  </p>
                </div>
                <Link href="/dashboard/calculations">
                  <Button className="bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300">
                    <Plus className="h-5 w-5 mr-2" />
                    Run Calculations to Generate Reports
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">

          {/* Report Types */}
          <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5"></div>
            <CardHeader className="relative">
              <CardTitle className="text-slate-100 flex items-center space-x-2">
                <Target className="w-5 h-5 text-blue-400" />
                <span>Available Report Types</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="relative">
              <div className="space-y-4">
                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-blue-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500/20 to-cyan-500/20 text-blue-400">
                      <Calculator className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">Calculation Reports</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Detailed reports from ASME VIII, API 579 calculations.
                  </p>
                  <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-xs">
                    Technical
                  </Badge>
                </div>

                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-emerald-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-green-500/20 text-emerald-400">
                      <FileCheck className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">Inspection Reports</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Comprehensive inspection findings and compliance docs.
                  </p>
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">
                    Compliance
                  </Badge>
                </div>

                <div className="group p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-purple-500/30 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-indigo-500/20 text-purple-400">
                      <BarChart3 className="w-4 h-4" />
                    </div>
                    <h4 className="font-semibold text-slate-100">Analytics Reports</h4>
                  </div>
                  <p className="text-slate-400 text-sm mb-3">
                    Performance metrics and operational insights.
                  </p>
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                    Analytics
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Export Options */}
          <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-orange-500/5"></div>
            <CardHeader className="relative">
              <CardTitle className="text-slate-100 flex items-center space-x-2">
                <Download className="w-5 h-5 text-amber-400" />
                <span>Export Options</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="relative space-y-3">
              <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-700/50">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-100">PDF Reports</span>
                  <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-xs">Standard</Badge>
                </div>
                <p className="text-xs text-slate-400">Professional PDF with charts and data</p>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-700/50">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-100">Excel Export</span>
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">Data</Badge>
                </div>
                <p className="text-xs text-slate-400">Raw data for further analysis</p>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-700/50">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-100">Interactive Dashboard</span>
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">Premium</Badge>
                </div>
                <p className="text-xs text-slate-400">Live charts and real-time updates</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
