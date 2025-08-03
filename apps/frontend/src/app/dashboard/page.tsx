'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import MobileDashboard from '@/components/mobile/mobile-dashboard'
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
  Clock,
  AlertTriangle,
  User,
  Calendar,
  TrendingUp,
  Award,
  Star,
  Flame,
  Timer,
  Eye,
  Activity,
  Layers,
  Gauge,
  AlertCircle,
  ChevronRight,
  Sparkles,
  Crown,
  Trophy,
  Rocket,
  Brain,
  Lightbulb,
  Heart
} from 'lucide-react'
import { useState, useEffect } from 'react'

export default function DashboardPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [recentActivity, setRecentActivity] = useState<any[]>([])
  const [completionLevel, setCompletionLevel] = useState(23)
  const [streakDays, setStreakDays] = useState(7)
  const [timeUntilExpiry, setTimeUntilExpiry] = useState(45)

  // Simulate recent activity with enhanced data
  useEffect(() => {
    const mockActivity = [
      {
        id: 1,
        type: 'vessel_added',
        title: 'Critical Pressure Vessel Certified',
        description: 'ASME VIII-compliant vessel successfully registered - Safety rating: 98%',
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
        description: 'Fitness-for-Service analysis finished - Remaining life: 15.3 years',
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
        description: 'High-pressure vessel VES-2024-001 requires immediate attention',
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
      return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`
    } else {
      const diffInDays = Math.floor(diffInHours / 24)
      return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`
    }
  }

  const getActivityIcon = (activity: any) => {
    const IconComponent = activity.icon
    return <IconComponent className={`w-4 h-4 ${activity.color}`} />
  }

  return (
    <>
      {/* Mobile Dashboard - Shows on mobile/tablet */}
      <div className="lg:hidden">
        <MobileDashboard />
      </div>
      
      {/* Desktop Dashboard - Shows on desktop */}
      <div className="hidden lg:block min-h-full">
        {/* Main Content */}
        <div className="w-full">
        {/* Hero Section with Clean Psychological Elements */}
        <div className="mb-8">
          <div className="relative overflow-hidden rounded-2xl card-accent p-8">
            <div className="absolute inset-0 gradient-accent opacity-5"></div>
            <div className="relative">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h1 className="text-4xl font-bold text-slate-100 mb-2">
                    Welcome back, Engineer
                    <Sparkles className="inline-block ml-2 h-8 w-8 text-amber-400" />
                  </h1>
                  <p className="text-lg text-secondary">
                    Your vessel safety command center - 
                    <span className="social-proof-counter"> protecting 847,392 vessels worldwide</span>
                  </p>
                </div>
                <div className="hidden lg:block">
                  <div className="text-right">
                    <div className="text-3xl font-bold text-cyan-400">{completionLevel}%</div>
                    <div className="text-sm text-slate-400">Profile Complete</div>
                    <div className="progress-clean w-24 mt-2">
                      <div 
                        className="progress-fill"
                        style={{ width: `${completionLevel}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Clean Achievement Bar */}
              <div className="flex items-center space-x-6 p-4 card-secondary rounded-xl">
                <div className="achievement-quiet">
                  <Trophy className="h-4 w-4 text-amber-400" />
                  <span>Safety Expert Level 3</span>
                </div>
                <div className="certification-mark">
                  <Award className="h-4 w-4" />
                  <span>ASME Certified</span>
                </div>
                <div className="trust-signal">
                  <Star className="h-4 w-4 text-yellow-400" />
                  <span>98% Accuracy Rate</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Enhanced Quick Actions with Psychological Marketing */}
          <div className="lg:col-span-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {/* Vessel Management - Clean Premium Feel */}
              <Link href="/dashboard/vessels">
                <Card className="group relative overflow-hidden card-primary hover:border-cyan-500/50 transition-all duration-300 cursor-pointer micro-lift">
                  <div className="absolute inset-0 psych-bg-premium opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <CardContent className="p-6 relative">
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 text-cyan-400 group-hover:scale-110 transition-transform duration-300">
                        <Shield className="w-7 h-7" />
                      </div>
                      <div className="social-proof-subtle">
                        <Eye className="w-4 h-4" />
                        <span>143 watching</span>
                      </div>
                    </div>
                    <div>
                      <h3 className="heading-tertiary mb-1">Vessel Registry</h3>
                      <p className="text-sm text-secondary mb-3">Secure vessel certification & compliance tracking</p>
                      <div className="flex items-center justify-between">
                        <div className="certification-mark">
                          <CheckCircle className="w-3 h-3" />
                          <span>ASME Certified</span>
                        </div>
                        <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-cyan-400 transition-colors" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>

              {/* Calculations - Clean Advanced Engineering */}
              <Link href="/dashboard/calculations">
                <Card className="group relative overflow-hidden card-primary hover:border-emerald-500/50 transition-all duration-300 cursor-pointer micro-lift">
                  <div className="absolute inset-0 psych-bg-success opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <CardContent className="p-6 relative">
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/20 to-green-500/20 text-emerald-400 group-hover:scale-110 transition-transform duration-300">
                        <Calculator className="w-7 h-7" />
                      </div>
                      <div className="authority-badge">
                        <Brain className="w-3 h-3" />
                        <span>AI-Powered</span>
                      </div>
                    </div>
                    <div>
                      <h3 className="heading-tertiary mb-1">Smart Calculations</h3>
                      <p className="text-sm text-secondary mb-3">API 579 & ASME VIII automated analysis</p>
                      <div className="flex items-center justify-between">
                        <div className="trust-signal psych-authority">
                          <CheckCircle className="verification-mark" />
                          <span>99.7% Accurate</span>
                        </div>
                        <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-emerald-400 transition-colors" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>

              {/* Inspections - Clean Urgency Element */}
              <Link href="/dashboard/inspections">
                <Card className="group relative overflow-hidden card-primary hover:border-amber-500/50 transition-all duration-300 cursor-pointer micro-lift">
                  <div className="absolute inset-0 psych-bg-urgency opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <CardContent className="p-6 relative">
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 text-amber-400 group-hover:scale-110 transition-transform duration-300">
                        <FileCheck className="w-7 h-7" />
                      </div>
                      <div className="urgency-subtle psych-urgency animate-pulse">
                        <AlertCircle className="w-4 h-4" />
                        <span className="text-xs font-medium">3 Due Soon</span>
                      </div>
                    </div>
                    <div>
                      <h3 className="heading-tertiary mb-1">Inspection Hub</h3>
                      <p className="text-sm text-secondary mb-3">Schedule & track critical inspections</p>
                      <div className="flex items-center justify-between">
                        <div className="scarcity-indicator">
                          Priority System
                        </div>
                        <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-amber-400 transition-colors" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>

              {/* Reports - Clean Professional Authority */}
              <Link href="/reports">
                <Card className="group relative overflow-hidden card-primary hover:border-purple-500/50 transition-all duration-300 cursor-pointer micro-lift">
                  <div className="absolute inset-0 psych-bg-authority opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <CardContent className="p-6 relative">
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-indigo-500/20 text-purple-400 group-hover:scale-110 transition-transform duration-300">
                        <BarChart3 className="w-7 h-7" />
                      </div>
                      <div className="trust-signal">
                        <Layers className="w-4 h-4" />
                        <span>Export Ready</span>
                      </div>
                    </div>
                    <div>
                      <h3 className="heading-tertiary mb-1">Pro Reports</h3>
                      <p className="text-sm text-secondary mb-3">Industry-standard compliance documentation</p>
                      <div className="flex items-center justify-between">
                        <div className="certification-mark">
                          <CheckCircle className="w-3 h-3" />
                          <span>ISO Compliant</span>
                        </div>
                        <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-purple-400 transition-colors" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </div>

            {/* Clean Onboarding with Subtle Psychological Triggers */}
            <Card className="relative overflow-hidden card-primary">
              <div className="absolute inset-0 gradient-accent opacity-5"></div>
              <CardHeader className="relative">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Rocket className="h-6 w-6 text-blue-400" />
                    <CardTitle className="text-slate-100 text-xl">Master Engineer's Journey</CardTitle>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-slate-400">Progress</div>
                    <div className="text-2xl font-bold text-cyan-400">{completionLevel}%</div>
                  </div>
                </div>
                <div className="progress-clean mt-4">
                  <div 
                    className="progress-fill"
                    style={{ width: `${completionLevel}%` }}
                  ></div>
                </div>
              </CardHeader>
              <CardContent className="relative">
                <div className="space-y-6">
                  {/* Step 1 - With Urgency */}
                  <div className="group flex items-center space-x-4 p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-cyan-500/30 transition-all duration-300">
                    <div className="relative">
                      <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
                        1
                      </div>
                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full flex items-center justify-center">
                        <CheckCircle className="w-2.5 h-2.5 text-white" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-bold text-slate-100">Deploy First Vessel</h3>
                        <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">
                          Critical Path
                        </Badge>
                      </div>
                      <p className="text-slate-300 text-sm">Join 12,847 engineers who've secured their first vessel</p>
                      <div className="flex items-center space-x-2 mt-2">
                        <Heart className="w-3 h-3 text-emerald-400" />
                        <span className="text-xs text-emerald-400">+25 Safety Points</span>
                      </div>
                    </div>
                    <Link href="/dashboard/vessels">
                      <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-medium group-hover:scale-105 transition-transform duration-200">
                        <Plus className="w-4 h-4 mr-2" />
                        Start Now
                      </Button>
                    </Link>
                  </div>

                  {/* Step 2 - With Social Proof */}
                  <div className="group flex items-center space-x-4 p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-emerald-500/30 transition-all duration-300">
                    <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
                      2
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-bold text-slate-100">Execute Advanced Analysis</h3>
                        <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                          AI-Enhanced
                        </Badge>
                      </div>
                      <p className="text-slate-300 text-sm">Perform calculations like 98.7% of successful engineers</p>
                      <div className="flex items-center space-x-2 mt-2">
                        <Lightbulb className="w-3 h-3 text-amber-400" />
                        <span className="text-xs text-amber-400">Save 4.2 hours average</span>
                      </div>
                    </div>
                    <Link href="/dashboard/calculations">
                      <Button className="bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-medium group-hover:scale-105 transition-transform duration-200">
                        <Calculator className="w-4 h-4 mr-2" />
                        Calculate
                      </Button>
                    </Link>
                  </div>

                  {/* Step 3 - With Authority */}
                  <div className="group flex items-center space-x-4 p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-purple-500/30 transition-all duration-300">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
                      3
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-bold text-slate-100">Generate Certified Reports</h3>
                        <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 text-xs">
                          Industry Standard
                        </Badge>
                      </div>
                      <p className="text-slate-300 text-sm">Create compliance reports trusted by Fortune 500 companies</p>
                      <div className="flex items-center space-x-2 mt-2">
                        <Award className="w-3 h-3 text-blue-400" />
                        <span className="text-xs text-blue-400">ISO 9001 Compliant</span>
                      </div>
                    </div>
                    <Link href="/reports">
                      <Button className="bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white font-medium group-hover:scale-105 transition-transform duration-200">
                        <FileCheck className="w-4 h-4 mr-2" />
                        Generate
                      </Button>
                    </Link>
                  </div>
                </div>

                {/* Achievement Unlock Preview */}
                <div className="mt-6 p-4 bg-gradient-to-r from-amber-500/10 to-orange-500/10 rounded-xl border border-amber-500/20">
                  <div className="flex items-center space-x-3">
                    <Trophy className="h-5 w-5 text-amber-400" />
                    <div>
                      <p className="text-sm font-medium text-slate-100">
                        Next Unlock: <span className="text-amber-400">Master Engineer Badge</span>
                      </p>
                      <p className="text-xs text-slate-400">Complete all steps to join the elite 5% of certified engineers</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Enhanced Activity Feed with Social Proof */}
          <div className="lg:col-span-1">
            <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border-slate-700/50 backdrop-blur-sm">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-purple-500/5"></div>
              <CardHeader className="relative">
                <CardTitle className="text-slate-100 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Activity className="w-5 h-5 text-cyan-400" />
                    <span>Live Engineering Feed</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                    <span className="text-xs text-emerald-400">Live</span>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="relative">
                {recentActivity.length > 0 ? (
                  <div className="space-y-4">
                    {recentActivity.map((activity) => (
                      <div key={activity.id} className="group flex items-start space-x-3 p-4 rounded-xl bg-slate-800/40 border border-slate-700/50 hover:border-cyan-500/30 transition-all duration-300">
                        <div className={`p-2.5 rounded-xl ${
                          activity.priority === 'urgent' 
                            ? 'bg-gradient-to-br from-amber-500/30 to-orange-500/30' 
                            : activity.priority === 'high'
                              ? 'bg-gradient-to-br from-emerald-500/30 to-green-500/30'
                              : 'bg-gradient-to-br from-blue-500/30 to-purple-500/30'
                        }`}>
                          {getActivityIcon(activity)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <p className="text-sm font-semibold text-slate-100 truncate">
                              {activity.title}
                            </p>
                            {activity.priority === 'urgent' && (
                              <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 text-xs animate-pulse">
                                URGENT
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-slate-300 truncate mb-2">
                            {activity.description}
                          </p>
                          <div className="flex items-center justify-between">
                            <p className="text-xs text-slate-500">
                              {formatTimeAgo(activity.timestamp)}
                            </p>
                            <div className="flex items-center space-x-1">
                              <Gauge className="w-3 h-3 text-cyan-400" />
                              <span className="text-xs text-cyan-400 font-medium">
                                {activity.impact}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Activity className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                    <p className="text-slate-400 text-sm">Your activity stream awaits</p>
                    <p className="text-slate-500 text-xs mt-1">Start your first vessel assessment to see real-time updates</p>
                  </div>
                )}
                
                {recentActivity.length > 0 && (
                  <div className="mt-6 pt-4 border-t border-slate-700/50">
                    <Link href="/dashboard/activity">
                      <Button variant="ghost" size="sm" className="w-full text-slate-400 hover:text-slate-100 hover:bg-slate-800/50 transition-all duration-200 group">
                        <span>View Complete Timeline</span>
                        <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Enhanced Performance Dashboard */}
            <Card className="relative overflow-hidden bg-gradient-to-br from-slate-800/60 to-slate-900/60 border-slate-700/50 backdrop-blur-sm mt-6">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-cyan-500/5"></div>
              <CardHeader className="relative">
                <CardTitle className="text-slate-100 flex items-center space-x-2">
                  <Target className="w-5 h-5 text-emerald-400" />
                  <span>Performance Metrics</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="relative">
                <div className="space-y-6">
                  {/* Vessels with Progress */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Shield className="w-4 h-4 text-cyan-400" />
                        <span className="text-slate-300 text-sm">Secured Vessels</span>
                      </div>
                      <div className="text-right">
                        <span className="text-slate-100 font-bold text-lg">3</span>
                        <span className="text-xs text-slate-400 ml-1">/ 10 goal</span>
                      </div>
                    </div>
                    <div className="w-full h-2 bg-slate-700 rounded-full">
                      <div className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full" style={{width: '30%'}}></div>
                    </div>
                    <div className="flex items-center space-x-1">
                      <TrendingUp className="w-3 h-3 text-emerald-400" />
                      <span className="text-xs text-emerald-400">+2 this week</span>
                    </div>
                  </div>

                  {/* Calculations with Achievement */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Calculator className="w-4 h-4 text-emerald-400" />
                        <span className="text-slate-300 text-sm">Smart Calculations</span>
                      </div>
                      <div className="text-right">
                        <span className="text-slate-100 font-bold text-lg">12</span>
                        <div className="flex items-center space-x-1 mt-1">
                          <Star className="w-3 h-3 text-amber-400" />
                          <span className="text-xs text-amber-400">98.9% accurate</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Inspections with Urgency */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <FileCheck className="w-4 h-4 text-purple-400" />
                        <span className="text-slate-300 text-sm">Inspections</span>
                      </div>
                      <div className="text-right">
                        <span className="text-slate-100 font-bold text-lg">8</span>
                        <div className="flex items-center space-x-1 mt-1">
                          <Timer className="w-3 h-3 text-amber-400" />
                          <span className="text-xs text-amber-400">3 due soon</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Reports with Authority */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <BarChart3 className="w-4 h-4 text-blue-400" />
                        <span className="text-slate-300 text-sm">Pro Reports</span>
                      </div>
                      <div className="text-right">
                        <span className="text-slate-100 font-bold text-lg">5</span>
                        <div className="flex items-center space-x-1 mt-1">
                          <Award className="w-3 h-3 text-blue-400" />
                          <span className="text-xs text-blue-400">ISO certified</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Performance Score */}
                <div className="mt-6 p-4 bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 rounded-xl border border-emerald-500/20">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Gauge className="w-4 h-4 text-emerald-400" />
                      <span className="text-sm font-medium text-slate-100">Safety Score</span>
                    </div>
                    <span className="text-2xl font-bold text-emerald-400">94</span>
                  </div>
                  <div className="w-full h-2 bg-slate-700 rounded-full">
                    <div className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-full" style={{width: '94%'}}></div>
                  </div>
                  <p className="text-xs text-slate-400 mt-2">
                    Excellent performance! You're in the top 8% of engineers.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      </div>
    </>
  )
}

