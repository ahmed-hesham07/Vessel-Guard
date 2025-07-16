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
  Activity
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  {
    name: 'Overview',
    href: '/dashboard',
    icon: Home,
    current: false,
  },
  {
    name: 'Projects',
    href: '/dashboard/projects',
    icon: Building,
    current: false,
  },
  {
    name: 'Vessels',
    href: '/dashboard/vessels',
    icon: Shield,
    current: false,
  },
  {
    name: 'Calculations',
    href: '/calculations',
    icon: Calculator,
    current: false,
    children: [
      { name: 'ASME B31.3', href: '/calculations/asme-b31-3' },
      { name: 'API 579', href: '/calculations/api-579' },
      { name: 'ASME VIII', href: '/calculations/asme-viii' },
    ],
  },
  {
    name: 'Inspections',
    href: '/dashboard/inspections',
    icon: FileCheck,
    current: false,
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: BarChart3,
    current: false,
  },
  {
    name: 'Standards',
    href: '/standards',
    icon: BookOpen,
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
      <div className="flex flex-col flex-grow pt-5 bg-white overflow-y-auto border-r border-gray-200 shadow-sm">
        <div className="flex items-center flex-shrink-0 px-4">
          <Shield className="h-8 w-8 text-blue-600" />
          <span className="ml-2 text-xl font-bold text-gray-900">Vessel Guard</span>
        </div>

        {/* User info */}
        <div className="mt-5 px-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {user?.email?.[0]?.toUpperCase() || 'U'}
                </span>
              </div>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700">
                {user?.email?.split('@')[0] || 'User'}
              </p>
              <p className="text-xs text-gray-500">Engineering Team</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="mt-8 flex-1 px-2 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            
            return (
              <div key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <Icon
                    className={cn(
                      'mr-3 flex-shrink-0 h-5 w-5',
                      isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                    )}
                  />
                  {item.name}
                  {item.name === 'Calculations' && (
                    <Badge variant="secondary" className="ml-auto text-xs">
                      New
                    </Badge>
                  )}
                </Link>

                {/* Sub-navigation for calculations */}
                {item.children && isActive && (
                  <div className="mt-1 ml-8 space-y-1">
                    {item.children.map((child) => (
                      <Link
                        key={child.name}
                        href={child.href}
                        className={cn(
                          'group flex items-center px-2 py-1 text-sm text-gray-600 rounded-md hover:text-gray-900 hover:bg-gray-50',
                          pathname === child.href && 'text-blue-600 bg-blue-50'
                        )}
                      >
                        <Wrench className="mr-2 h-4 w-4" />
                        {child.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </nav>

        {/* Bottom navigation */}
        <div className="flex-shrink-0 border-t border-gray-200 p-4">
          <div className="space-y-1">
            {/* Admin navigation */}
            {(user as any)?.role === 'admin' && (
              <>
                <div className="mb-2">
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wider px-2">
                    Administration
                  </p>
                </div>
                {adminNavigation.map((item) => {
                  const Icon = item.icon
                  const isActive = pathname === item.href
                  
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={cn(
                        'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                        isActive
                          ? 'bg-gray-100 text-gray-900'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      )}
                    >
                      <Icon
                        className={cn(
                          'mr-3 flex-shrink-0 h-5 w-5',
                          isActive ? 'text-gray-500' : 'text-gray-400 group-hover:text-gray-500'
                        )}
                      />
                      {item.name}
                    </Link>
                  )
                })}
                <div className="border-t border-gray-200 my-2" />
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
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <Icon
                    className={cn(
                      'mr-3 flex-shrink-0 h-5 w-5',
                      isActive ? 'text-gray-500' : 'text-gray-400 group-hover:text-gray-500'
                    )}
                  />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
