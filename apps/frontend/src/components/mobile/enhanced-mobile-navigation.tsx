'use client'

import { Fragment, useState, useEffect } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { X, ChevronRight, Sparkles, Crown, Star, Award, Bell, Settings, LogOut } from 'lucide-react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/auth-context'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Home,
  Shield,
  Calculator,
  FileCheck,
  Users,
  BarChart3,
  HelpCircle,
  Building,
  Activity,
  Zap,
  FileText
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home,
    description: 'Your control center',
    badge: null,
    priority: 'high'
  },
  {
    name: 'Quick Workflow',
    href: '/dashboard/workflow/new',
    icon: Zap,
    description: 'Smart engineering shortcuts',
    badge: 'New',
    priority: 'high'
  },
  {
    name: 'Projects',
    href: '/dashboard/projects',
    icon: Building,
    description: 'Manage engineering projects',
    badge: null,
    priority: 'high'
  },
  {
    name: 'Vessels',
    href: '/dashboard/vessels',
    icon: Shield,
    description: 'Vessel registry & compliance',
    badge: null,
    priority: 'high'
  },
  {
    name: 'Calculations',
    href: '/dashboard/calculations',
    icon: Calculator,
    description: 'ASME & API analysis',
    badge: null,
    priority: 'medium'
  },
  {
    name: 'Inspections',
    href: '/dashboard/inspections',
    icon: FileCheck,
    description: 'Schedule & track inspections',
    badge: '3 due',
    priority: 'medium'
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: BarChart3,
    description: 'Generate compliance reports',
    badge: null,
    priority: 'medium'
  }
]

const bottomNavigation = [
  {
    name: 'Organization',
    href: '/dashboard/organization',
    icon: Users,
    description: 'Team & company settings'
  },
  {
    name: 'Settings',
    href: '/dashboard/settings',
    icon: Settings,
    description: 'App preferences'
  },
  {
    name: 'Support',
    href: '/support',
    icon: HelpCircle,
    description: 'Get help & resources'
  }
]

interface EnhancedMobileNavigationProps {
  isOpen: boolean
  onClose: () => void
}

export default function EnhancedMobileNavigation({ isOpen, onClose }: EnhancedMobileNavigationProps) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuth()
  const [notifications, setNotifications] = useState(3)

  const handleLogout = async () => {
    try {
      await logout()
      onClose()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const handleNavigation = (href: string) => {
    onClose()
    router.push(href)
  }

  // High-priority navigation items for quick access
  const highPriorityItems = navigation.filter(item => item.priority === 'high')
  const mediumPriorityItems = navigation.filter(item => item.priority === 'medium')

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50 lg:hidden" onClose={onClose}>
        {/* Background overlay with blur */}
        <Transition.Child
          as={Fragment}
          enter="ease-in-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in-out duration-300"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="pointer-events-none fixed inset-y-0 left-0 flex max-w-full pr-10">
              <Transition.Child
                as={Fragment}
                enter="transform transition ease-in-out duration-300"
                enterFrom="-translate-x-full"
                enterTo="translate-x-0"
                leave="transform transition ease-in-out duration-300"
                leaveFrom="translate-x-0"
                leaveTo="-translate-x-full"
              >
                <Dialog.Panel className="pointer-events-auto relative w-screen max-w-sm">
                  {/* Enhanced Mobile Navigation Panel */}
                  <div className="flex h-full flex-col bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 shadow-2xl mobile-safe-top mobile-safe-bottom">
                    {/* Header with user info and close button */}
                    <div className="relative px-6 pt-6 pb-4">
                      {/* Close button */}
                      <div className="absolute top-4 right-4">
                        <button
                          type="button"
                          className="touch-icon-button text-slate-400 hover:text-slate-100 hover:bg-slate-800/50 mobile-focus"
                          onClick={onClose}
                        >
                          <span className="sr-only">Close navigation</span>
                          <X className="h-5 w-5" />
                        </button>
                      </div>

                      {/* Brand */}
                      <div className="flex items-center space-x-3 mb-6">
                        <div className="relative">
                          <Shield className="h-8 w-8 text-cyan-400 drop-shadow-lg" />
                          <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
                        </div>
                        <div>
                          <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                            Vessel Guard Pro
                          </h1>
                          <div className="flex items-center space-x-1">
                            <Crown className="h-3 w-3 text-amber-400" />
                            <span className="text-xs text-amber-400 font-medium">Engineering Excellence</span>
                          </div>
                        </div>
                      </div>

                      {/* Enhanced User Profile */}
                      <div className="mobile-card bg-gradient-to-r from-slate-800/40 to-slate-700/40 border-slate-700/30">
                        <div className="flex items-center space-x-3">
                          <div className="relative">
                            <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                              <span className="text-sm font-bold text-white">
                                {user?.email?.[0]?.toUpperCase() || 'U'}
                              </span>
                            </div>
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full flex items-center justify-center">
                              <Star className="w-2.5 h-2.5 text-white" />
                            </div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2">
                              <p className="mobile-heading-3 text-slate-100 truncate">
                                {user?.email?.split('@')[0] || 'Engineer'}
                              </p>
                              <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs">
                                Pro
                              </Badge>
                            </div>
                            <div className="flex items-center space-x-1 mt-1">
                              <Award className="mobile-status-icon text-amber-400" />
                              <p className="mobile-caption text-amber-400">Level 3 Expert</p>
                            </div>
                          </div>
                          {notifications > 0 && (
                            <div className="relative">
                              <Bell className="mobile-engineering-icon text-slate-400" />
                              <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
                                <span className="text-xs font-bold text-white">{notifications}</span>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Navigation Content */}
                    <div className="flex-1 overflow-y-auto px-6 pb-6">
                      {/* Quick Workflow CTA */}
                      <div className="mb-6">
                        <button
                          onClick={() => handleNavigation('/dashboard/workflow/new')}
                          className="w-full mobile-card bg-gradient-to-r from-cyan-500 to-blue-600 text-white border-none hover:from-cyan-600 hover:to-blue-700 mobile-focus group"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="p-2 bg-white/20 rounded-lg group-hover:scale-110 transition-transform duration-200">
                              <Zap className="mobile-engineering-icon" />
                            </div>
                            <div className="flex-1 text-left">
                              <div className="flex items-center space-x-2">
                                <p className="mobile-heading-3">Smart Workflow</p>
                                <Sparkles className="w-3 h-3 text-yellow-300" />
                              </div>
                              <p className="mobile-caption text-cyan-100">Save 4.2 hours on average</p>
                            </div>
                            <ChevronRight className="mobile-status-icon group-hover:translate-x-1 transition-transform duration-200" />
                          </div>
                        </button>
                      </div>

                      {/* High Priority Navigation */}
                      <div className="mobile-spacing-md">
                        <div className="mb-4">
                          <h2 className="mobile-heading-3 text-slate-300 mb-3">Quick Access</h2>
                          <div className="mobile-spacing-sm">
                            {highPriorityItems.map((item) => {
                              const Icon = item.icon
                              const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
                              
                              return (
                                <button
                                  key={item.name}
                                  onClick={() => handleNavigation(item.href)}
                                  className={cn(
                                    'w-full mobile-nav-item mobile-focus',
                                    isActive
                                      ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border border-cyan-500/30'
                                      : 'text-slate-300 hover:bg-slate-800/50 hover:text-slate-100 border border-transparent hover:border-slate-700/50'
                                  )}
                                >
                                  <Icon className={cn(
                                    'mobile-engineering-icon flex-shrink-0',
                                    isActive ? 'text-cyan-400' : 'text-slate-400'
                                  )} />
                                  <div className="flex-1 text-left">
                                    <p className="mobile-heading-3">{item.name}</p>
                                    <p className="mobile-caption text-slate-400">{item.description}</p>
                                  </div>
                                  {item.badge && (
                                    <Badge className={cn(
                                      "text-xs",
                                      isActive 
                                        ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/30" 
                                        : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                                    )}>
                                      {item.badge}
                                    </Badge>
                                  )}
                                  <ChevronRight className={cn(
                                    "mobile-status-icon flex-shrink-0",
                                    isActive ? "text-cyan-400" : "text-slate-500"
                                  )} />
                                </button>
                              )
                            })}
                          </div>
                        </div>

                        {/* Medium Priority Navigation */}
                        <div className="mb-4">
                          <h2 className="mobile-heading-3 text-slate-300 mb-3">Engineering Tools</h2>
                          <div className="mobile-spacing-sm">
                            {mediumPriorityItems.map((item) => {
                              const Icon = item.icon
                              const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
                              
                              return (
                                <button
                                  key={item.name}
                                  onClick={() => handleNavigation(item.href)}
                                  className={cn(
                                    'w-full mobile-nav-item mobile-focus',
                                    isActive
                                      ? 'bg-gradient-to-r from-purple-500/20 to-indigo-500/20 text-purple-400 border border-purple-500/30'
                                      : 'text-slate-300 hover:bg-slate-800/50 hover:text-slate-100 border border-transparent hover:border-slate-700/50'
                                  )}
                                >
                                  <Icon className={cn(
                                    'mobile-engineering-icon flex-shrink-0',
                                    isActive ? 'text-purple-400' : 'text-slate-400'
                                  )} />
                                  <div className="flex-1 text-left">
                                    <p className="mobile-heading-3">{item.name}</p>
                                    <p className="mobile-caption text-slate-400">{item.description}</p>
                                  </div>
                                  {item.badge && (
                                    <Badge className={cn(
                                      "text-xs",
                                      isActive 
                                        ? "bg-purple-500/20 text-purple-400 border-purple-500/30" 
                                        : item.badge.includes('due')
                                          ? "bg-amber-500/20 text-amber-400 border-amber-500/30 animate-pulse"
                                          : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                                    )}>
                                      {item.badge}
                                    </Badge>
                                  )}
                                  <ChevronRight className={cn(
                                    "mobile-status-icon flex-shrink-0",
                                    isActive ? "text-purple-400" : "text-slate-500"
                                  )} />
                                </button>
                              )
                            })}
                          </div>
                        </div>

                        {/* Bottom Navigation */}
                        <div className="border-t border-slate-700/50 pt-4">
                          <h2 className="mobile-heading-3 text-slate-300 mb-3">Account</h2>
                          <div className="mobile-spacing-sm">
                            {bottomNavigation.map((item) => {
                              const Icon = item.icon
                              const isActive = pathname === item.href
                              
                              return (
                                <button
                                  key={item.name}
                                  onClick={() => handleNavigation(item.href)}
                                  className={cn(
                                    'w-full mobile-nav-item mobile-focus',
                                    isActive
                                      ? 'bg-gradient-to-r from-slate-700/50 to-slate-600/50 text-slate-100 border border-slate-600/50'
                                      : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border border-transparent hover:border-slate-700/50'
                                  )}
                                >
                                  <Icon className={cn(
                                    'mobile-engineering-icon flex-shrink-0',
                                    isActive ? 'text-slate-100' : 'text-slate-500'
                                  )} />
                                  <div className="flex-1 text-left">
                                    <p className="mobile-heading-3">{item.name}</p>
                                    <p className="mobile-caption text-slate-400">{item.description}</p>
                                  </div>
                                  <ChevronRight className={cn(
                                    "mobile-status-icon flex-shrink-0",
                                    isActive ? "text-slate-100" : "text-slate-600"
                                  )} />
                                </button>
                              )
                            })}
                          </div>
                        </div>

                        {/* Logout Button */}
                        <div className="mt-6 pt-4 border-t border-slate-700/50">
                          <button
                            onClick={handleLogout}
                            className="w-full mobile-nav-item text-red-400 hover:bg-red-500/10 hover:text-red-300 border border-transparent hover:border-red-500/20 mobile-focus"
                          >
                            <LogOut className="mobile-engineering-icon flex-shrink-0" />
                            <div className="flex-1 text-left">
                              <p className="mobile-heading-3">Sign Out</p>
                              <p className="mobile-caption text-slate-400">Secure logout</p>
                            </div>
                            <ChevronRight className="mobile-status-icon flex-shrink-0" />
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="px-6 py-4 border-t border-slate-700/50 mobile-safe-bottom">
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-2 mb-2">
                          <Shield className="mobile-status-icon text-cyan-400" />
                          <span className="mobile-caption text-slate-400 font-medium">Vessel Guard Pro</span>
                        </div>
                        <p className="text-xs text-slate-500">Engineering Excellence Since 2024</p>
                      </div>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  )
}