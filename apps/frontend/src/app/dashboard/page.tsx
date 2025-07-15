'use client'

import { useAuth } from '@/contexts/auth-context'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  BarChart3, 
  Building, 
  Calculator, 
  FileCheck, 
  Shield, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle2,
  Clock,
  Users,
  Plus
} from 'lucide-react'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { apiService } from '@/lib/api'

interface DashboardStats {
  projects: { total: number; active: number; completed: number }
  vessels: { total: number; active: number; inspectionsDue: number }
  calculations: { total: number; recent: number }
  inspections: { total: number; pending: number; overdue: number }
}

export default function DashboardPage() {
  const { user, token } = useAuth()
  const [stats, setStats] = useState<DashboardStats>({
    projects: { total: 0, active: 0, completed: 0 },
    vessels: { total: 0, active: 0, inspectionsDue: 0 },
    calculations: { total: 0, recent: 0 },
    inspections: { total: 0, pending: 0, overdue: 0 }
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!token) return

      try {
        const [projects, vessels, calculations, inspections] = await Promise.all([
          apiService.getProjects(token),
          apiService.getVessels(token),
          apiService.getCalculations(token),
          apiService.getInspections(token)
        ])

        setStats({
          projects: {
            total: (projects as any[]).length,
            active: (projects as any[]).filter((p: any) => p.status === 'active').length,
            completed: (projects as any[]).filter((p: any) => p.status === 'completed').length
          },
          vessels: {
            total: (vessels as any[]).length,
            active: (vessels as any[]).filter((v: any) => v.status === 'active').length,
            inspectionsDue: (vessels as any[]).filter((v: any) => v.next_inspection_date && new Date(v.next_inspection_date) <= new Date()).length
          },
          calculations: {
            total: (calculations as any[]).length,
            recent: (calculations as any[]).filter((c: any) => new Date(c.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length
          },
          inspections: {
            total: (inspections as any[]).length,
            pending: (inspections as any[]).filter((i: any) => i.status === 'pending').length,
            overdue: (inspections as any[]).filter((i: any) => i.status === 'overdue').length
          }
        })
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [token])

  const quickActions = [
    {
      title: 'New Project',
      description: 'Create a new engineering project',
      icon: Building,
      href: '/dashboard/projects/new',
      color: 'bg-blue-500'
    },
    {
      title: 'Add Vessel',
      description: 'Register a new vessel or component',
      icon: Shield,
      href: '/dashboard/vessels/new',
      color: 'bg-green-500'
    },
    {
      title: 'Run Calculation',
      description: 'Perform engineering calculations',
      icon: Calculator,
      href: '/calculations/new',
      color: 'bg-purple-500'
    },
    {
      title: 'Schedule Inspection',
      description: 'Plan a new inspection',
      icon: FileCheck,
      href: '/dashboard/inspections/new',
      color: 'bg-orange-500'
    }
  ]

  const recentActivity = [
    { type: 'project', title: 'Pressure vessel analysis completed', time: '2 hours ago' },
    { type: 'inspection', title: 'Vessel V-101 inspection scheduled', time: '4 hours ago' },
    { type: 'calculation', title: 'ASME B31.3 calculation updated', time: '1 day ago' },
    { type: 'report', title: 'Monthly compliance report generated', time: '2 days ago' }
  ]

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
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
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.first_name}!
          </h1>
          <p className="text-gray-600">
            Here's what's happening with your engineering projects today.
          </p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" asChild>
            <Link href="/reports/new">
              <BarChart3 className="h-4 w-4 mr-2" />
              Generate Report
            </Link>
          </Button>
          <Button asChild>
            <Link href="/dashboard/projects/new">
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
            <Building className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.projects.total}</div>
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <span>{stats.projects.active} active</span>
              <span>•</span>
              <span>{stats.projects.completed} completed</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vessels</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.vessels.total}</div>
            <div className="flex items-center space-x-2 text-xs">
              <span className="text-muted-foreground">{stats.vessels.active} active</span>
              {stats.vessels.inspectionsDue > 0 && (
                <>
                  <span>•</span>
                  <Badge variant="warning" className="text-xs">
                    {stats.vessels.inspectionsDue} due
                  </Badge>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Calculations</CardTitle>
            <Calculator className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.calculations.total}</div>
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <TrendingUp className="h-3 w-3" />
              <span>{stats.calculations.recent} this week</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Inspections</CardTitle>
            <FileCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.inspections.total}</div>
            <div className="flex items-center space-x-2 text-xs">
              <span className="text-muted-foreground">{stats.inspections.pending} pending</span>
              {stats.inspections.overdue > 0 && (
                <>
                  <span>•</span>
                  <Badge variant="destructive" className="text-xs">
                    {stats.inspections.overdue} overdue
                  </Badge>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {quickActions.map((action) => (
          <Card key={action.title} className="hover:shadow-md transition-shadow cursor-pointer">
            <Link href={action.href}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className={`p-2 rounded-lg ${action.color} text-white`}>
                    <action.icon className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{action.title}</h3>
                    <p className="text-sm text-gray-500">{action.description}</p>
                  </div>
                </div>
              </CardContent>
            </Link>
          </Card>
        ))}
      </div>

      {/* Recent Activity and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="h-5 w-5 mr-2" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {activity.type === 'project' && <Building className="h-4 w-4 text-blue-500" />}
                    {activity.type === 'inspection' && <FileCheck className="h-4 w-4 text-green-500" />}
                    {activity.type === 'calculation' && <Calculator className="h-4 w-4 text-purple-500" />}
                    {activity.type === 'report' && <BarChart3 className="h-4 w-4 text-orange-500" />}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Alerts and Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Alerts & Notifications
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.inspections.overdue > 0 && (
                <div className="flex items-center space-x-3 p-3 bg-red-50 rounded-lg">
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                  <div>
                    <p className="text-sm font-medium text-red-800">
                      {stats.inspections.overdue} overdue inspections
                    </p>
                    <p className="text-xs text-red-600">Immediate attention required</p>
                  </div>
                </div>
              )}
              
              {stats.vessels.inspectionsDue > 0 && (
                <div className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
                  <Clock className="h-4 w-4 text-yellow-500" />
                  <div>
                    <p className="text-sm font-medium text-yellow-800">
                      {stats.vessels.inspectionsDue} inspections due soon
                    </p>
                    <p className="text-xs text-yellow-600">Schedule within 30 days</p>
                  </div>
                </div>
              )}
              
              <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <div>
                  <p className="text-sm font-medium text-green-800">
                    All systems operational
                  </p>
                  <p className="text-xs text-green-600">No critical issues detected</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
