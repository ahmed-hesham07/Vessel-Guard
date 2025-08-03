'use client'

import { forwardRef, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface MobileCardProps {
  children: ReactNode
  className?: string
  onClick?: () => void
  disabled?: boolean
  variant?: 'default' | 'interactive' | 'elevated' | 'minimal'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const MobileCard = forwardRef<HTMLDivElement, MobileCardProps>(
  ({ children, className, onClick, disabled = false, variant = 'default', padding = 'md' }, ref) => {
    const baseStyles = "rounded-xl border transition-all duration-200"
    
    const variantStyles = {
      default: "bg-slate-800/60 border-slate-700/50 backdrop-blur-sm",
      interactive: "bg-slate-800/60 border-slate-700/50 backdrop-blur-sm hover:border-cyan-500/30 hover:bg-slate-800/80 cursor-pointer active:scale-[0.98]",
      elevated: "bg-gradient-to-br from-slate-800/60 to-slate-900/60 border-slate-700/50 backdrop-blur-sm shadow-lg hover:shadow-xl",
      minimal: "bg-transparent border-slate-700/30"
    }
    
    const paddingStyles = {
      none: "",
      sm: "p-3",
      md: "p-4 sm:p-6",
      lg: "p-6 sm:p-8"
    }
    
    const disabledStyles = disabled ? "opacity-50 cursor-not-allowed" : ""
    const interactiveStyles = onClick && !disabled ? "touch-target mobile-focus" : ""

    return (
      <div
        ref={ref}
        className={cn(
          baseStyles,
          variantStyles[variant],
          paddingStyles[padding],
          disabledStyles,
          interactiveStyles,
          className
        )}
        onClick={onClick && !disabled ? onClick : undefined}
        role={onClick ? "button" : undefined}
        tabIndex={onClick && !disabled ? 0 : undefined}
        onKeyDown={onClick && !disabled ? (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onClick()
          }
        } : undefined}
      >
        {children}
      </div>
    )
  }
)

MobileCard.displayName = "MobileCard"

export { MobileCard }