'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/auth-context'
import { Badge } from '@/components/ui/badge'
import {
  Home,
  Shield,
  Calculator,
  FileCheck,
  Users,
  Settings,
  BarChart3,
  BookOpen,
  HelpCircle,
  Building,
  Wrench,
  Activity,
  Zap,
  Target,
  FileText,
  Crown,
  Star,
  TrendingUp,
  Award,
  ChevronRight,
  Sparkles
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home,
    current: false,
  },
  {
    name: 'Quick Workflow',
    href: '/dashboard/workflow/new',
    icon: Zap,
    current: false,
    badge: 'New'
  },
  {
    name: 'Projects',
    href: '/dashboard/projects',
    icon: Building,
    current: false,
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: BarChart3,
    current: false,
  },
  {
    name: 'Inspections',
    href: '/dashboard/inspections',
    icon: FileCheck,
    current: false,
  },
]

const bottomNavigation = [
  {
    name: 'Organization',
    href: '/dashboard/organization',
    icon: Users,
  },
  {
    name: 'Settings',
    href: '/dashboard/settings',
    icon: Settings,
  },
  {
    name: 'Support',
    href: '/support',
    icon: HelpCircle,
  },
]

// Admin only navigation
const adminNavigation = [
  {
    name: 'System Health',
    href: '/health',
    icon: Activity,
  },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { user, isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 md:z-10">
      <div className="flex flex-col flex-grow pt-5 bg-gradient-to-b from-slate-950 to-slate-900 overflow-y-auto border-r border-slate-800/50 shadow-2xl backdrop-blur-sm">
        <div className="flex items-center flex-shrink-0 px-4 mb-2">
          <div className="relative">
            <Shield className="h-8 w-8 text-cyan-400 drop-shadow-lg" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
          </div>
          <div className="ml-2">
            <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              Vessel Guard Pro
            </span>
            <div className="flex items-center space-x-1 mt-0.5">
              <Crown className="h-3 w-3 text-amber-400" />
              <span className="text-xs text-amber-400 font-medium">Engineering Excellence</span>
            </div>
          </div>
        </div>

        {/* Enhanced User Profile */}
        <div className="mt-5 px-4">
          <div className="relative p-4 bg-gradient-to-r from-slate-800/50 to-slate-700/50 rounded-xl border border-slate-700/50">
            <div className="flex items-center">
              <div className="flex-shrink-0 relative">
                <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-sm font-bold text-white">
                    {user?.email?.[0]?.toUpperCase() || 'U'}
                  </span>
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full flex items-center justify-center">
                  <Star className="w-2.5 h-2.5 text-white" />
                </div>
              </div>
              <div className="ml-3 flex-1">
                <div className="flex items-center space-x-2">
                  <p className="text-sm font-bold text-slate-100">
                    {user?.email?.split('@')[0] || 'Engineer'}
                  </p>
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">
                    Pro
                  </Badge>
                </div>
                <div className="flex items-center space-x-1 mt-1">
                  <Award className="h-3 w-3 text-amber-400" />
                  <p className="text-xs text-amber-400 font-medium">Certified Expert</p>
                </div>
                <div className="flex items-center space-x-1 mt-1">
                  <TrendingUp className="h-3 w-3 text-emerald-400" />
                  <p className="text-xs text-emerald-400">Level 3 Engineer</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Quick Workflow CTA */}
        <div className="mt-6 px-4">
          <Link href="/dashboard/workflow/new">
            <div className="relative overflow-hidden bg-gradient-to-r from-cyan-500 to-blue-600 text-white p-4 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative flex items-center space-x-3">
                <div className="p-2 bg-white/20 rounded-lg group-hover:scale-110 transition-transform duration-200">
                  <Zap className="h-5 w-5" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <p className="text-sm font-bold">Smart Workflow</p>
                    <Sparkles className="h-3 w-3 text-yellow-300" />
                  </div>
                  <p className="text-xs text-cyan-100">Save 4.2 hours average</p>
                  <div className="flex items-center space-x-1 mt-1">
                    <Star className="h-3 w-3 text-yellow-300" />
                    <span className="text-xs text-yellow-300">98% efficiency gain</span>
                  </div>
                </div>
                <ChevronRight className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-200" />
              </div>
            </div>
          </Link>
        </div>

        {/* Enhanced Navigation */}
        <nav className="mt-8 flex-1 px-2 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            
            return (
              <div key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    'group flex items-center px-3 py-3 text-sm font-medium rounded-xl transition-all duration-200 relative',
                    isActive
                      ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border border-cyan-500/30 shadow-lg'
                      : 'text-slate-300 hover:bg-slate-800/50 hover:text-slate-100 border border-transparent hover:border-slate-700/50'
                  )}
                >
                  <Icon
                    className={cn(
                      'mr-3 flex-shrink-0 h-5 w-5 transition-colors duration-200',
                      isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-300'
                    )}
                  />
                  <span className="flex-1">{item.name}</span>
                  {item.badge && (
                    <Badge className={cn(
                      "text-xs font-medium",
                      isActive 
                        ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/30" 
                        : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                    )}>
                      {item.badge}
                    </Badge>
                  )}
                  <ChevronRight className={cn(
                    "ml-2 h-4 w-4 transition-all duration-200",
                    isActive ? "text-cyan-400" : "text-slate-500 group-hover:text-slate-300 group-hover:translate-x-1"
                  )} />
                </Link>
              </div>
            )
          })}
        </nav>

        {/* Enhanced Bottom Navigation */}
        <div className="flex-shrink-0 border-t border-slate-800/50 p-4">
          <div className="space-y-2">
            {/* Admin navigation */}
            {(user as any)?.role === 'admin' && (
              <>
                <div className="mb-3">
                  <div className="flex items-center space-x-2 px-3">
                    <Crown className="h-3 w-3 text-amber-400" />
                    <p className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                      Admin Console
                    </p>
                  </div>
                </div>
                {adminNavigation.map((item) => {
                  const Icon = item.icon
                  const isActive = pathname === item.href
                  
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={cn(
                        'group flex items-center px-3 py-2 text-sm font-medium rounded-xl transition-all duration-200',
                        isActive
                          ? 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-400 border border-amber-500/30'
                          : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border border-transparent hover:border-slate-700/50'
                      )}
                    >
                      <Icon
                        className={cn(
                          'mr-3 flex-shrink-0 h-4 w-4 transition-colors duration-200',
                          isActive ? 'text-amber-400' : 'text-slate-500 group-hover:text-slate-400'
                        )}
                      />
                      {item.name}
                      <ChevronRight className={cn(
                        "ml-auto h-3 w-3 transition-all duration-200",
                        isActive ? "text-amber-400" : "text-slate-600 group-hover:text-slate-400 group-hover:translate-x-1"
                      )} />
                    </Link>
                  )
                })}
                <div className="border-t border-slate-800/50 my-3" />
              </>
            )}
            
            {/* Regular bottom navigation */}
            {bottomNavigation.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-xl transition-all duration-200',
                    isActive
                      ? 'bg-gradient-to-r from-purple-500/20 to-indigo-500/20 text-purple-400 border border-purple-500/30'
                      : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border border-transparent hover:border-slate-700/50'
                  )}
                >
                  <Icon
                    className={cn(
                      'mr-3 flex-shrink-0 h-4 w-4 transition-colors duration-200',
                      isActive ? 'text-purple-400' : 'text-slate-500 group-hover:text-slate-400'
                    )}
                  />
                  {item.name}
                  <ChevronRight className={cn(
                    "ml-auto h-3 w-3 transition-all duration-200",
                    isActive ? "text-purple-400" : "text-slate-600 group-hover:text-slate-400 group-hover:translate-x-1"
                  )} />
                </Link>
              )
            })}
          </div>
          
          {/* Professional Footer */}
          <div className="mt-6 pt-4 border-t border-slate-800/50">
            <div className="text-center">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Shield className="h-4 w-4 text-cyan-400" />
                <span className="text-xs font-medium text-slate-400">Vessel Guard Pro</span>
              </div>
              <p className="text-xs text-slate-500">Engineering Excellence Since 2024</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
