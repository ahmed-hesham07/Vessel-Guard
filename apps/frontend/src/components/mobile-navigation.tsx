'use client'

import { Fragment } from 'react'

import { Dialog, Transition } from '@headlessui/react'
import { X } from 'lucide-react'
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
  },
  {
    name: 'Quick Workflow',
    href: '/dashboard/workflow/new',
    icon: Zap,
    badge: 'New'
  },
  {
    name: 'Projects',
    href: '/dashboard/projects',
    icon: Building,
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: BarChart3,
  },
  {
    name: 'Inspections',
    href: '/dashboard/inspections',
    icon: FileCheck,
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

const adminNavigation = [
  {
    name: 'System Health',
    href: '/health',
    icon: Activity,
  },
]

interface MobileNavigationProps {
  isOpen: boolean
  onClose: () => void
}

export default function MobileNavigation({ isOpen, onClose }: MobileNavigationProps) {
  const pathname = usePathname()
  const { user } = useAuth()

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50 md:hidden" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-in-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in-out duration-300"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
        </Transition.Child>

        <div className="fixed inset-0 z-40 flex">
          <Transition.Child
            as={Fragment}
            enter="transition ease-in-out duration-300 transform"
            enterFrom="-translate-x-full"
            enterTo="translate-x-0"
            leave="transition ease-in-out duration-300 transform"
            leaveFrom="translate-x-0"
            leaveTo="-translate-x-full"
          >
            <Dialog.Panel className="relative flex w-full max-w-xs flex-1 flex-col bg-white">
              <Transition.Child
                as={Fragment}
                enter="ease-in-out duration-300"
                enterFrom="opacity-0"
                enterTo="opacity-100"
                leave="ease-in-out duration-300"
                leaveFrom="opacity-100"
                leaveTo="opacity-0"
              >
                <div className="absolute top-0 right-0 -mr-12 pt-2">
                  <button
                    type="button"
                    className="ml-1 flex h-10 w-10 items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                    onClick={onClose}
                  >
                    <span className="sr-only">Close sidebar</span>
                    <X className="h-6 w-6 text-white" aria-hidden="true" />
                  </button>
                </div>
              </Transition.Child>

              <div className="flex flex-shrink-0 items-center px-4 pt-5">
                <Shield className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">Vessel Guard</span>
              </div>

              {/* User info */}
              <div className="mt-5 px-4">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
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

              {/* Quick Workflow CTA */}
              <div className="mt-6 px-4">
                <Link href="/dashboard/workflow/new" onClick={onClose}>
                  <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-lg shadow-lg">
                    <div className="flex items-center space-x-3">
                      <Zap className="h-5 w-5" />
                      <div>
                        <p className="text-sm font-semibold">Quick Workflow</p>
                        <p className="text-xs text-blue-100">Streamline your process</p>
                      </div>
                    </div>
                  </div>
                </Link>
              </div>

              <div className="mt-8 flex flex-1 flex-col">
                <nav className="flex-1 space-y-1 px-2">
                  {navigation.map((item) => {
                    const Icon = item.icon
                    const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
                    
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        onClick={onClose}
                        className={cn(
                          'group flex items-center px-2 py-2 text-base font-medium rounded-md transition-colors',
                          isActive
                            ? 'bg-blue-50 text-blue-700'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        )}
                      >
                        <Icon
                          className={cn(
                            'mr-4 flex-shrink-0 h-6 w-6',
                            isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                          )}
                        />
                        {item.name}
                        {item.badge && (
                          <Badge variant="secondary" className="ml-auto text-xs bg-blue-100 text-blue-800">
                            {item.badge}
                          </Badge>
                        )}
                      </Link>
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
                              onClick={onClose}
                              className={cn(
                                'group flex items-center px-2 py-2 text-base font-medium rounded-md transition-colors',
                                isActive
                                  ? 'bg-gray-100 text-gray-900'
                                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                              )}
                            >
                              <Icon
                                className={cn(
                                  'mr-4 flex-shrink-0 h-6 w-6',
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
                          onClick={onClose}
                          className={cn(
                            'group flex items-center px-2 py-2 text-base font-medium rounded-md transition-colors',
                            isActive
                              ? 'bg-gray-100 text-gray-900'
                              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          )}
                        >
                          <Icon
                            className={cn(
                              'mr-4 flex-shrink-0 h-6 w-6',
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
            </Dialog.Panel>
          </Transition.Child>
          <div className="w-14 flex-shrink-0" aria-hidden="true">
            {/* Force sidebar to shrink to fit close icon */}
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  )
}
