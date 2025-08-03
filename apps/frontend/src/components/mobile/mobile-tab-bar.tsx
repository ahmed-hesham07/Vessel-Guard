'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Badge } from '@/components/ui/badge'
import {
  Home,
  Shield,
  Calculator,
  FileCheck,
  BarChart3,
  Plus,
  Zap
} from 'lucide-react'
import { cn } from '@/lib/utils'

const tabBarItems = [
  {
    name: 'Home',
    shortName: 'Home',
    href: '/dashboard',
    icon: Home,
    badge: null
  },
  {
    name: 'Vessels',
    shortName: 'Vessels',
    href: '/dashboard/vessels',
    icon: Shield,
    badge: null
  },
  {
    name: 'Quick Action',
    shortName: 'Quick',
    href: '/dashboard/workflow/new',
    icon: Plus,
    badge: 'New',
    isSpecial: true
  },
  {
    name: 'Calculations',
    shortName: 'Calc',
    href: '/dashboard/calculations',
    icon: Calculator,
    badge: null
  },
  {
    name: 'Reports',
    shortName: 'Reports',
    href: '/reports',
    icon: BarChart3,
    badge: null
  }
]

interface MobileTabBarProps {
  className?: string
}

export default function MobileTabBar({ className }: MobileTabBarProps) {
  const pathname = usePathname()

  // Don't show tab bar on certain pages
  const hideTabBarPaths = ['/login', '/register', '/forgot-password', '/']
  const shouldHideTabBar = hideTabBarPaths.some(path => pathname.startsWith(path))

  if (shouldHideTabBar) {
    return null
  }

  return (
    <div className={cn(
      "fixed bottom-0 left-0 right-0 z-40 lg:hidden",
      "bg-slate-900/95 backdrop-blur-sm border-t border-slate-800/50",
      "mobile-safe-bottom",
      className
    )}>
      <div className="mobile-tab-bar px-2 py-1">
        {tabBarItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href || 
            (item.href !== '/dashboard' && pathname.startsWith(item.href))
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "mobile-tab-item transition-all duration-200 relative",
                "hover:bg-slate-800/50 rounded-lg mobile-focus",
                isActive && !item.isSpecial && "text-cyan-400",
                !isActive && !item.isSpecial && "text-slate-400",
                item.isSpecial && "text-white"
              )}
            >
              {/* Special Quick Action Button */}
              {item.isSpecial ? (
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200">
                    <Icon className="w-6 h-6" />
                  </div>
                  {item.badge && (
                    <div className="absolute -top-1 -right-1">
                      <Badge className="bg-emerald-500 text-white text-xs px-1.5 py-0.5 min-w-0 h-auto">
                        {item.badge}
                      </Badge>
                    </div>
                  )}
                </div>
              ) : (
                <>
                  {/* Regular Tab Item */}
                  <div className="relative">
                    <Icon className={cn(
                      "mobile-engineering-icon",
                      isActive ? "text-cyan-400" : "text-slate-400"
                    )} />
                    {item.badge && (
                      <div className="absolute -top-1 -right-1">
                        <Badge className="bg-red-500 text-white text-xs px-1.5 py-0.5 min-w-0 h-auto">
                          {item.badge}
                        </Badge>
                      </div>
                    )}
                    
                    {/* Active indicator */}
                    {isActive && (
                      <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-cyan-400 rounded-full" />
                    )}
                  </div>
                </>
              )}
              
              {/* Label for non-special items */}
              {!item.isSpecial && (
                <span className={cn(
                  "text-xs font-medium truncate max-w-[60px]",
                  isActive ? "text-cyan-400" : "text-slate-400"
                )}>
                  {item.shortName}
                </span>
              )}
              
              {/* Special label for quick action */}
              {item.isSpecial && (
                <span className="text-xs font-medium text-white mt-1">
                  {item.shortName}
                </span>
              )}
            </Link>
          )
        })}
      </div>
      
      {/* Home indicator for iOS-like experience */}
      <div className="flex justify-center pb-1">
        <div className="w-32 h-1 bg-slate-600 rounded-full" />
      </div>
    </div>
  )
}