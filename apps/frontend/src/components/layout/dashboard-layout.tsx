'use client'

import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/auth-context'
import Header from '@/components/header'
import Sidebar from '@/components/sidebar'
import ErrorBoundary from '@/components/error-boundary'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname()
  const { isAuthenticated } = useAuth()

  // Don't show dashboard layout on auth pages
  const isAuthPage = pathname?.startsWith('/auth')
  const isLandingPage = pathname === '/'
  
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

  return (
    <ErrorBoundary>
      <div className="h-screen flex overflow-hidden bg-gray-50">
        <Sidebar />
        
        <div className="flex flex-col w-0 flex-1 overflow-hidden">
          <Header />
          
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
