'use client'

import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/auth-context'
import Header from '@/components/header'
import Sidebar from '@/components/sidebar'
import MobileNavigation from '@/components/mobile-navigation'
import ErrorBoundary from '@/components/error-boundary'
import { Shield, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname()
  const { isAuthenticated, user } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Don't show dashboard layout on auth pages
  const isAuthPage = pathname?.startsWith('/auth')
  const isLandingPage = pathname === '/'
  const isDashboardPage = pathname?.startsWith('/dashboard') || pathname === '/dashboard'
  
  if (isAuthPage || isLandingPage) {
    return (
      <ErrorBoundary>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main>{children}</main>
        </div>
      </ErrorBoundary>
    )
  }

  if (!isAuthenticated) {
    return (
      <ErrorBoundary>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main>{children}</main>
        </div>
      </ErrorBoundary>
    )
  }

  // For dashboard pages, use sidebar layout
  if (isDashboardPage) {
    return (
      <ErrorBoundary>
        <div className="h-screen flex overflow-hidden bg-gray-50">
          <Sidebar />
          <MobileNavigation 
            isOpen={mobileMenuOpen} 
            onClose={() => setMobileMenuOpen(false)} 
          />
          
          <div className="flex flex-col w-0 flex-1 overflow-hidden md:ml-64">
            {/* Mobile header for dashboard */}
            <div className="md:hidden bg-white shadow-sm border-b border-gray-200">
              <div className="px-4 py-3 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setMobileMenuOpen(true)}
                    className="h-8 w-8"
                  >
                    <Menu className="h-4 w-4" />
                  </Button>
                  <div className="flex items-center space-x-2">
                    <Shield className="h-6 w-6 text-blue-600" />
                    <span className="font-semibold text-gray-900">Vessel Guard</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-white">
                      {user?.email?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <main className="flex-1 relative overflow-y-auto focus:outline-none">
              <div className="py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
                  {children}
                </div>
              </div>
            </main>
          </div>
        </div>
      </ErrorBoundary>
    )
  }

  // For other authenticated pages, use header layout
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main>{children}</main>
      </div>
    </ErrorBoundary>
  )
}
