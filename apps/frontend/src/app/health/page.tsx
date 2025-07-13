'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Loading } from '@/components/ui/loading'
import {
  Activity,
  Database,
  Server,
  Clock,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Cpu,
  HardDrive,
  MemoryStick
} from 'lucide-react'

interface HealthStatus {
  status: string
  timestamp: string
  service: string
  version: string
  dependencies?: {
    database?: {
      status: string
      response_time_ms?: number
      error?: string
    }
    redis?: {
      status: string
      response_time_ms?: number
      error?: string
    }
  }
  system?: {
    cpu: {
      usage_percent: number
      status: string
    }
    memory: {
      total_gb: number
      available_gb: number
      usage_percent: number
      status: string
    }
    disk: {
      total_gb: number
      free_gb: number
      usage_percent: number
      status: string
    }
  }
}

const StatusIcon = ({ status }: { status: string }) => {
  switch (status) {
    case 'healthy':
    case 'ready':
    case 'alive':
      return <CheckCircle className="w-5 h-5 text-green-500" />
    case 'warning':
    case 'degraded':
      return <AlertTriangle className="w-5 h-5 text-yellow-500" />
    case 'unhealthy':
    case 'critical':
    case 'not_ready':
      return <XCircle className="w-5 h-5 text-red-500" />
    default:
      return <AlertTriangle className="w-5 h-5 text-gray-500" />
  }
}

const StatusBadge = ({ status }: { status: string }) => {
  const variant = 
    status === 'healthy' || status === 'ready' || status === 'alive' ? 'default' :
    status === 'warning' || status === 'degraded' ? 'secondary' :
    'destructive'
  
  return <Badge variant={variant}>{status}</Badge>
}

export default function HealthPage() {
  const [basicHealth, setBasicHealth] = useState<HealthStatus | null>(null)
  const [detailedHealth, setDetailedHealth] = useState<HealthStatus | null>(null)
  const [systemHealth, setSystemHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  const fetchHealthData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // Fetch all health endpoints
      const [basicRes, detailedRes, systemRes] = await Promise.allSettled([
        fetch(`${baseUrl}/api/v1/health`),
        fetch(`${baseUrl}/api/v1/health/detailed`),
        fetch(`${baseUrl}/api/v1/health/system`)
      ])

      if (basicRes.status === 'fulfilled' && basicRes.value.ok) {
        const basicData = await basicRes.value.json()
        setBasicHealth(basicData)
      }

      if (detailedRes.status === 'fulfilled' && detailedRes.value.ok) {
        const detailedData = await detailedRes.value.json()
        setDetailedHealth(detailedData)
      }

      if (systemRes.status === 'fulfilled' && systemRes.value.ok) {
        const systemData = await systemRes.value.json()
        setSystemHealth(systemData)
      }

      setLastRefresh(new Date())
    } catch (err) {
      setError('Failed to fetch health status')
      console.error('Health check error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealthData()
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchHealthData, 30000)
    
    return () => clearInterval(interval)
  }, [])

  if (loading && !basicHealth) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loading loading={true} loadingText="Loading health status..." />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Health</h1>
          <p className="text-gray-600">Monitor the health and status of all system components</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </div>
          <Button
            onClick={fetchHealthData}
            disabled={loading}
            size="sm"
            variant="outline"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <XCircle className="w-5 h-5 text-red-400 mr-2" />
            <div className="text-sm text-red-700">{error}</div>
          </div>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Basic Health Status */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Service Status</CardTitle>
            <Activity className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              {basicHealth && <StatusIcon status={basicHealth.status} />}
              <div className="text-2xl font-bold">
                {basicHealth ? basicHealth.service : 'Unknown'}
              </div>
            </div>
            <div className="flex items-center space-x-2 mt-2">
              {basicHealth && <StatusBadge status={basicHealth.status} />}
              <span className="text-xs text-muted-foreground">
                v{basicHealth?.version || '1.0.0'}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Database Status */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Database</CardTitle>
            <Database className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              {detailedHealth?.dependencies?.database && (
                <StatusIcon status={detailedHealth.dependencies.database.status} />
              )}
              <div className="text-2xl font-bold">
                {detailedHealth?.dependencies?.database?.status || 'Unknown'}
              </div>
            </div>
            {detailedHealth?.dependencies?.database?.response_time_ms && (
              <p className="text-xs text-muted-foreground mt-1">
                Response: {detailedHealth.dependencies.database.response_time_ms}ms
              </p>
            )}
            {detailedHealth?.dependencies?.database?.error && (
              <p className="text-xs text-red-500 mt-1">
                {detailedHealth.dependencies.database.error}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Redis Status */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cache (Redis)</CardTitle>
            <Server className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              {detailedHealth?.dependencies?.redis && (
                <StatusIcon status={detailedHealth.dependencies.redis.status} />
              )}
              <div className="text-2xl font-bold">
                {detailedHealth?.dependencies?.redis?.status || 'Not configured'}
              </div>
            </div>
            {detailedHealth?.dependencies?.redis?.response_time_ms && (
              <p className="text-xs text-muted-foreground mt-1">
                Response: {detailedHealth.dependencies.redis.response_time_ms}ms
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* System Resources */}
      {systemHealth?.system && (
        <Card>
          <CardHeader>
            <CardTitle>System Resources</CardTitle>
            <CardDescription>
              Current system resource utilization and status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              {/* CPU */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Cpu className="w-4 h-4" />
                  <span className="text-sm font-medium">CPU Usage</span>
                  <StatusBadge status={systemHealth.system.cpu.status} />
                </div>
                <div className="text-2xl font-bold">
                  {systemHealth.system.cpu.usage_percent.toFixed(1)}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      systemHealth.system.cpu.usage_percent > 80
                        ? 'bg-red-500'
                        : systemHealth.system.cpu.usage_percent > 60
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${systemHealth.system.cpu.usage_percent}%` }}
                  />
                </div>
              </div>

              {/* Memory */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <MemoryStick className="w-4 h-4" />
                  <span className="text-sm font-medium">Memory Usage</span>
                  <StatusBadge status={systemHealth.system.memory.status} />
                </div>
                <div className="text-2xl font-bold">
                  {systemHealth.system.memory.usage_percent.toFixed(1)}%
                </div>
                <div className="text-xs text-muted-foreground">
                  {systemHealth.system.memory.available_gb.toFixed(1)}GB / {systemHealth.system.memory.total_gb.toFixed(1)}GB available
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      systemHealth.system.memory.usage_percent > 80
                        ? 'bg-red-500'
                        : systemHealth.system.memory.usage_percent > 60
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${systemHealth.system.memory.usage_percent}%` }}
                  />
                </div>
              </div>

              {/* Disk */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <HardDrive className="w-4 h-4" />
                  <span className="text-sm font-medium">Disk Usage</span>
                  <StatusBadge status={systemHealth.system.disk.status} />
                </div>
                <div className="text-2xl font-bold">
                  {systemHealth.system.disk.usage_percent.toFixed(1)}%
                </div>
                <div className="text-xs text-muted-foreground">
                  {systemHealth.system.disk.free_gb.toFixed(1)}GB / {systemHealth.system.disk.total_gb.toFixed(1)}GB free
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      systemHealth.system.disk.usage_percent > 80
                        ? 'bg-red-500'
                        : systemHealth.system.disk.usage_percent > 60
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${systemHealth.system.disk.usage_percent}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Health Check Endpoints */}
      <Card>
        <CardHeader>
          <CardTitle>Health Check Endpoints</CardTitle>
          <CardDescription>
            Available health check endpoints for monitoring and orchestration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
              <div>
                <div className="font-medium">Basic Health</div>
                <div className="text-sm text-gray-500">/api/v1/health</div>
              </div>
              <Badge variant="outline">GET</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
              <div>
                <div className="font-medium">Detailed Health</div>
                <div className="text-sm text-gray-500">/api/v1/health/detailed</div>
              </div>
              <Badge variant="outline">GET</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
              <div>
                <div className="font-medium">System Health</div>
                <div className="text-sm text-gray-500">/api/v1/health/system</div>
              </div>
              <Badge variant="outline">GET</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
              <div>
                <div className="font-medium">Readiness Check</div>
                <div className="text-sm text-gray-500">/api/v1/health/readiness</div>
              </div>
              <Badge variant="outline">GET</Badge>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
              <div>
                <div className="font-medium">Liveness Check</div>
                <div className="text-sm text-gray-500">/api/v1/health/liveness</div>
              </div>
              <Badge variant="outline">GET</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
