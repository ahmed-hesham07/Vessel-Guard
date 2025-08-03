'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { MobileCard } from './mobile-card'
import { 
  Shield, 
  Calculator, 
  FileCheck, 
  BarChart3,
  Zap,
  Target,
  CheckCircle,
  ArrowRight,
  Plus,
  Clock,
  AlertTriangle,
  TrendingUp,
  Award,
  Star,
  Trophy,
  Rocket,
  Brain,
  Lightbulb,
  Heart,
  Eye,
  Activity,
  Gauge,
  AlertCircle,
  ChevronRight,
  Sparkles,
  Crown,
  Timer,
  Layers
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/auth-context'

interface MobileDashboardProps {
  className?: string
}

export default function MobileDashboard({ className }: MobileDashboardProps) {
  const { user } = useAuth()
  const [recentActivity, setRecentActivity] = useState<any[]>([])
  const [completionLevel, setCompletionLevel] = useState(23)
  const [streakDays, setStreakDays] = useState(7)

  // Simulate recent activity
  useEffect(() => {
    const mockActivity = [
      {
        id: 1,
        type: 'vessel_added',
        title: 'Critical Pressure Vessel Certified',
        description: 'ASME VIII-compliant vessel successfully registered',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        icon: Shield,
        color: 'text-emerald-400',
        priority: 'high',
        impact: '+12 Safety Score'
      },
      {
        id: 2,
        type: 'calculation_completed',
        title: 'API 579-1 Assessment Completed',
        description: 'Fitness-for-Service analysis finished',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
        icon: Calculator,
        color: 'text-blue-400',
        priority: 'medium',
        impact: '+8 Compliance Points'
      },
      {
        id: 3,
        type: 'inspection_overdue',
        title: 'Urgent: Inspection Due Tomorrow',
        description: 'High-pressure vessel VES-2024-001',
        timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
        icon: AlertTriangle,
        color: 'text-amber-400',
        priority: 'urgent',
        impact: 'Action Required'
      }
    ]
    setRecentActivity(mockActivity)
  }, [])

  const formatTimeAgo = (date: Date) => {
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) {
      return 'Just now'
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`
    } else {
      const diffInDays = Math.floor(diffInHours / 24)
      return `${diffInDays}d ago`
    }
  }

  const quickActions = [
    {
      name: 'Vessel Registry',
      href: '/dashboard/vessels',
      icon: Shield,
      description: 'Secure vessel certification',
      color: 'from-cyan-500/20 to-blue-500/20',
      iconColor: 'text-cyan-400',
      borderColor: 'hover:border-cyan-500/50',
      status: 'ASME Certified',
      stats: '143 watching'
    },
    {
      name: 'Smart Calculations',
      href: '/dashboard/calculations',
      icon: Calculator,
      description: 'AI-powered analysis',
      color: 'from-emerald-500/20 to-green-500/20',
      iconColor: 'text-emerald-400',
      borderColor: 'hover:border-emerald-500/50',
      status: '99.7% Accurate',
      stats: 'AI-Enhanced'
    },
    {
      name: 'Inspection Hub',
      href: '/dashboard/inspections',
      icon: FileCheck,
      description: 'Track critical inspections',
      color: 'from-amber-500/20 to-orange-500/20',
      iconColor: 'text-amber-400',
      borderColor: 'hover:border-amber-500/50',
      status: 'Priority System',
      stats: '3 Due Soon'
    },
    {
      name: 'Pro Reports',
      href: '/reports',
      icon: BarChart3,
      description: 'Compliance documentation',
      color: 'from-purple-500/20 to-indigo-500/20',
      iconColor: 'text-purple-400',
      borderColor: 'hover:border-purple-500/50',
      status: 'ISO Compliant',
      stats: 'Export Ready'
    }
  ]

  return (
    <div className={cn("mobile-container pb-20", className)}>
      {/* Hero Section - Mobile Optimized */}
      <div className="mobile-section">
        <MobileCard variant="elevated" className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-purple-500/5"></div>
          <div className="relative">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h1 className="mobile-heading-1 text-slate-100 mb-2">
                  Welcome back, Engineer
                  <Sparkles className="inline-block ml-2 w-6 h-6 text-amber-400" />
                </h1>
                <p className="mobile-body text-slate-300">
                  Your vessel safety command center
                </p>
                <p className="mobile-caption text-slate-400 mt-1">
                  Protecting 847,392 vessels worldwide
                </p>
              </div>
              <div className="text-right ml-4">
                <div className="text-2xl font-bold text-cyan-400">{completionLevel}%</div>
                <div className="mobile-caption text-slate-400">Profile Complete</div>
                <div className="mobile-progress-bar w-16 mt-2">
                  <div 
                    className="mobile-progress-fill"
                    style={{ width: `${completionLevel}%` }}
                  ></div>
                </div>
              </div>
            </div>
            
            {/* Achievement Bar */}
            <div className="flex flex-wrap items-center gap-3 p-3 bg-slate-800/30 rounded-lg">
              <div className="flex items-center space-x-1">
                <Trophy className="mobile-status-icon text-amber-400" />
                <span className="mobile-caption text-amber-400 font-medium">Level 3</span>
              </div>
              <div className="flex items-center space-x-1">
                <Award className="mobile-status-icon text-emerald-400" />
                <span className="mobile-caption text-emerald-400 font-medium">ASME Certified</span>
              </div>
              <div className="flex items-center space-x-1">
                <Star className="mobile-status-icon text-yellow-400" />
                <span className="mobile-caption text-yellow-400 font-medium">98% Accuracy</span>
              </div>
            </div>
          </div>
        </MobileCard>
      </div>

      {/* Quick Workflow CTA - Mobile Priority */}
      <div className="mb-6">
        <Link href="/dashboard/workflow/new">
          <MobileCard variant="interactive" className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white border-none">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-white/20 rounded-xl">
                <Zap className="mobile-engineering-icon" />
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <h3 className="mobile-heading-3 font-bold">Smart Workflow</h3>
                  <Sparkles className="w-4 h-4 text-yellow-300" />
                  <Badge className="bg-white/20 text-white border-white/30 text-xs">
                    New
                  </Badge>
                </div>
                <p className="mobile-caption text-cyan-100">Save 4.2 hours on average</p>
                <div className="flex items-center space-x-1 mt-1">
                  <Star className="w-3 h-3 text-yellow-300" />
                  <span className="text-xs text-yellow-300">98% efficiency gain</span>
                </div>
              </div>
              <ChevronRight className="mobile-engineering-icon" />
            </div>
          </MobileCard>
        </Link>
      </div>

      {/* Quick Actions Grid - Mobile Optimized */}
      <div className="mobile-spacing-md">
        <h2 className="mobile-heading-2 text-slate-100 mb-4">Quick Actions</h2>
        <div className="mobile-grid-2">
          {quickActions.map((action) => {
            const Icon = action.icon
            return (
              <Link key={action.name} href={action.href}>
                <MobileCard variant="interactive" className={cn("group", action.borderColor)}>
                  <div className="text-center">
                    <div className={cn(
                      "p-4 rounded-2xl bg-gradient-to-br mx-auto mb-3 w-16 h-16 flex items-center justify-center group-hover:scale-110 transition-transform duration-300",
                      action.color
                    )}>
                      <Icon className={cn("mobile-engineering-icon", action.iconColor)} />
                    </div>
                    <h3 className="mobile-heading-3 text-slate-100 mb-1">{action.name}</h3>
                    <p className="mobile-caption text-slate-400 mb-2">{action.description}</p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-emerald-400">{action.status}</span>
                      <span className="text-slate-500">{action.stats}</span>
                    </div>
                  </div>
                </MobileCard>
              </Link>
            )
          })}
        </div>
      </div>

      {/* Progress Journey - Mobile Optimized */}
      <div className="mobile-spacing-md">
        <MobileCard variant="elevated">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Rocket className="mobile-engineering-icon text-blue-400" />
              <h2 className="mobile-heading-2 text-slate-100">Master Engineer's Journey</h2>
            </div>
            <div className="text-right">
              <div className="mobile-caption text-slate-400">Progress</div>
              <div className="text-xl font-bold text-cyan-400">{completionLevel}%</div>
            </div>
          </div>
          
          <div className="mobile-progress-bar mb-6">
            <div 
              className="mobile-progress-fill"
              style={{ width: `${completionLevel}%` }}
            ></div>
          </div>

          <div className="mobile-spacing-sm">
            {/* Step 1 */}
            <div className="flex items-center space-x-4 p-4 rounded-xl bg-slate-800/40 border border-slate-700/50">
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
                  1
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-2.5 h-2.5 text-white" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <h3 className="mobile-heading-3 text-slate-100">Deploy First Vessel</h3>
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">
                    Critical
                  </Badge>
                </div>
                <p className="mobile-caption text-slate-400">Join 12,847 engineers</p>
                <div className="flex items-center space-x-2 mt-1">
                  <Heart className="w-3 h-3 text-emerald-400" />
                  <span className="text-xs text-emerald-400">+25 Safety Points</span>
                </div>
              </div>
              <Link href="/dashboard/vessels">
                <Button size="sm" className="mobile-button-primary">
                  <Plus className="w-4 h-4 mr-1" />
                  Start
                </Button>
              </Link>
            </div>

            {/* Step 2 */}
            <div className="flex items-center space-x-4 p-4 rounded-xl bg-slate-800/40 border border-slate-700/50">
              <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
                2
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <h3 className="mobile-heading-3 text-slate-100">Execute Analysis</h3>
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                    AI
                  </Badge>
                </div>
                <p className="mobile-caption text-slate-400">Like 98.7% of engineers</p>
                <div className="flex items-center space-x-2 mt-1">
                  <Lightbulb className="w-3 h-3 text-amber-400" />
                  <span className="text-xs text-amber-400">Save 4.2 hours</span>
                </div>
              </div>
              <Link href="/dashboard/calculations">
                <Button size="sm" className="mobile-button-secondary">
                  <Calculator className="w-4 h-4 mr-1" />
                  Calculate
                </Button>
              </Link>
            </div>
          </div>
        </MobileCard>
      </div>

      {/* Activity Feed - Mobile Optimized */}
      <div className="mobile-spacing-md">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Activity className="mobile-engineering-icon text-cyan-400" />
            <h2 className="mobile-heading-2 text-slate-100">Live Feed</h2>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="mobile-caption text-emerald-400">Live</span>
          </div>
        </div>

        <div className="mobile-spacing-sm">
          {recentActivity.map((activity) => {
            const Icon = activity.icon
            return (
              <MobileCard key={activity.id} variant="interactive">
                <div className="flex items-start space-x-3">
                  <div className={cn(
                    "p-2.5 rounded-xl flex-shrink-0",
                    activity.priority === 'urgent' 
                      ? 'bg-gradient-to-br from-amber-500/30 to-orange-500/30' 
                      : activity.priority === 'high'
                        ? 'bg-gradient-to-br from-emerald-500/30 to-green-500/30'
                        : 'bg-gradient-to-br from-blue-500/30 to-purple-500/30'
                  )}>
                    <Icon className={cn("mobile-status-icon", activity.color)} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-1">
                      <h3 className="mobile-heading-3 text-slate-100 line-clamp-1">
                        {activity.title}
                      </h3>
                      {activity.priority === 'urgent' && (
                        <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 text-xs animate-pulse ml-2">
                          URGENT
                        </Badge>
                      )}
                    </div>
                    <p className="mobile-caption text-slate-300 line-clamp-2 mb-2">
                      {activity.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="mobile-caption text-slate-500">
                        {formatTimeAgo(activity.timestamp)}
                      </span>
                      <div className="flex items-center space-x-1">
                        <Gauge className="w-3 h-3 text-cyan-400" />
                        <span className="mobile-caption text-cyan-400 font-medium">
                          {activity.impact}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </MobileCard>
            )
          })}
        </div>

        <Link href="/dashboard/activity">
          <Button variant="ghost" className="w-full mt-4 mobile-button-ghost group">
            <span>View Complete Timeline</span>
            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
          </Button>
        </Link>
      </div>

      {/* Performance Metrics - Mobile Optimized */}
      <div className="mobile-spacing-md">
        <div className="flex items-center space-x-2 mb-4">
          <Target className="mobile-engineering-icon text-emerald-400" />
          <h2 className="mobile-heading-2 text-slate-100">Performance</h2>
        </div>

        <div className="mobile-grid-2">
          {/* Vessels */}
          <MobileCard>
            <div className="text-center">
              <Shield className="mobile-engineering-icon text-cyan-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-slate-100 mb-1">3</div>
              <div className="mobile-caption text-slate-400 mb-2">Secured Vessels</div>
              <div className="mobile-progress-bar">
                <div className="mobile-progress-fill" style={{width: '30%'}}></div>
              </div>
              <div className="flex items-center justify-center space-x-1 mt-2">
                <TrendingUp className="w-3 h-3 text-emerald-400" />
                <span className="text-xs text-emerald-400">+2 this week</span>
              </div>
            </div>
          </MobileCard>

          {/* Calculations */}
          <MobileCard>
            <div className="text-center">
              <Calculator className="mobile-engineering-icon text-emerald-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-slate-100 mb-1">12</div>
              <div className="mobile-caption text-slate-400 mb-2">Smart Calculations</div>
              <div className="flex items-center justify-center space-x-1 mt-2">
                <Star className="w-3 h-3 text-amber-400" />
                <span className="text-xs text-amber-400">98.9% accurate</span>
              </div>
            </div>
          </MobileCard>

          {/* Inspections */}
          <MobileCard>
            <div className="text-center">
              <FileCheck className="mobile-engineering-icon text-purple-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-slate-100 mb-1">8</div>
              <div className="mobile-caption text-slate-400 mb-2">Inspections</div>
              <div className="flex items-center justify-center space-x-1 mt-2">
                <Timer className="w-3 h-3 text-amber-400" />
                <span className="text-xs text-amber-400">3 due soon</span>
              </div>
            </div>
          </MobileCard>

          {/* Reports */}
          <MobileCard>
            <div className="text-center">
              <BarChart3 className="mobile-engineering-icon text-blue-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-slate-100 mb-1">5</div>
              <div className="mobile-caption text-slate-400 mb-2">Pro Reports</div>
              <div className="flex items-center justify-center space-x-1 mt-2">
                <Award className="w-3 h-3 text-blue-400" />
                <span className="text-xs text-blue-400">ISO certified</span>
              </div>
            </div>
          </MobileCard>
        </div>

        {/* Safety Score */}
        <MobileCard variant="elevated" className="mt-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Gauge className="mobile-engineering-icon text-emerald-400" />
              <h3 className="mobile-heading-3 text-slate-100">Safety Score</h3>
            </div>
            <span className="text-3xl font-bold text-emerald-400">94</span>
          </div>
          <div className="mobile-progress-bar mb-3">
            <div className="mobile-progress-fill" style={{width: '94%'}}></div>
          </div>
          <p className="mobile-caption text-slate-400 text-center">
            Excellent! You're in the top 8% of engineers.
          </p>
        </MobileCard>
      </div>
    </div>
  )
}