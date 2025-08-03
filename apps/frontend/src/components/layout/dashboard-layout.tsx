'use client'

import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/auth-context'
import Header from '@/components/header'
import Sidebar from '@/components/sidebar'
import MobileNavigation from '@/components/mobile-navigation'
import EnhancedMobileNavigation from '@/components/mobile/enhanced-mobile-navigation'
import MobileTabBar from '@/components/mobile/mobile-tab-bar'
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
        <div className="h-screen flex overflow-hidden bg-slate-950">
          <Sidebar />
          <EnhancedMobileNavigation 
            isOpen={mobileMenuOpen} 
            onClose={() => setMobileMenuOpen(false)} 
          />
          
          <div className="flex flex-col w-0 flex-1 overflow-hidden md:ml-64">
            {/* Enhanced Mobile header for dashboard */}
            <div className="lg:hidden bg-slate-900/95 backdrop-blur-sm shadow-lg border-b border-slate-800/50 mobile-safe-top">
              <div className="px-4 py-3 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setMobileMenuOpen(true)}
                    className="touch-icon-button text-slate-400 hover:text-slate-100 hover:bg-slate-800/50 mobile-focus"
                  >
                    <Menu className="mobile-engineering-icon" />
                  </Button>
                  <div className="flex items-center space-x-2">
                    <Shield className="mobile-engineering-icon text-cyan-400" />
                    <span className="mobile-heading-3 text-slate-100">Vessel Guard Pro</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg touch-target">
                    <span className="text-sm font-medium text-white">
                      {user?.email?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <main className="flex-1 relative overflow-y-auto focus:outline-none bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
              <div className="min-h-full w-full">
                <div className="w-full px-4 sm:px-6 lg:px-8 py-6 pb-24 lg:pb-6">
                  {children}
                </div>
              </div>
            </main>
          </div>
          
          {/* Mobile Tab Bar */}
          <MobileTabBar />
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
