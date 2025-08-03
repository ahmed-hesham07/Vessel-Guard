"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { LucideIcon, TrendingUp, TrendingDown, Sparkles, Target, Award } from "lucide-react"

interface StatsCardProps {
  title: string
  value: string | number
  description?: string
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
    period: string
  }
  variant?: "default" | "success" | "warning" | "danger" | "premium" | "achievement"
  className?: string
  badge?: string
  progress?: number
  isHighlighted?: boolean
}

export function StatsCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  variant = "default",
  className,
  badge,
  progress,
  isHighlighted = false,
}: StatsCardProps) {
  const variantStyles = {
    default: "bg-gradient-to-br from-slate-800/60 to-slate-900/60 border-slate-700/50",
    success: "bg-gradient-to-br from-emerald-500/10 to-green-500/10 border-emerald-500/30",
    warning: "bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/30",
    danger: "bg-gradient-to-br from-red-500/10 to-pink-500/10 border-red-500/30",
    premium: "bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border-cyan-500/30",
    achievement: "bg-gradient-to-br from-purple-500/10 to-indigo-500/10 border-purple-500/30",
  }

  const iconStyles = {
    default: "text-slate-400",
    success: "text-emerald-400",
    warning: "text-amber-400",
    danger: "text-red-400",
    premium: "text-cyan-400",
    achievement: "text-purple-400",
  }

  const iconBgStyles = {
    default: "bg-gradient-to-br from-slate-500/20 to-slate-600/20",
    success: "bg-gradient-to-br from-emerald-500/20 to-green-500/20",
    warning: "bg-gradient-to-br from-amber-500/20 to-orange-500/20",
    danger: "bg-gradient-to-br from-red-500/20 to-pink-500/20",
    premium: "bg-gradient-to-br from-cyan-500/20 to-blue-500/20",
    achievement: "bg-gradient-to-br from-purple-500/20 to-indigo-500/20",
  }

  return (
    <Card className={cn(
      "relative overflow-hidden backdrop-blur-sm transition-all duration-300 hover:shadow-xl group",
      variantStyles[variant],
      isHighlighted && "ring-2 ring-cyan-500/50 shadow-lg shadow-cyan-500/20",
      className
    )}>
      {isHighlighted && (
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5" />
      )}
      
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3 relative">
        <div className="flex items-center space-x-2">
          <div className={cn("p-2.5 rounded-xl group-hover:scale-110 transition-transform duration-200", iconBgStyles[variant])}>
            <Icon className={cn("h-5 w-5", iconStyles[variant])} />
          </div>
          <div>
            <CardTitle className="text-sm font-medium text-slate-300">
              {title}
            </CardTitle>
            {badge && (
              <Badge className={cn(
                "text-xs mt-1",
                variant === "success" && "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
                variant === "warning" && "bg-amber-500/20 text-amber-400 border-amber-500/30",
                variant === "danger" && "bg-red-500/20 text-red-400 border-red-500/30",
                variant === "premium" && "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
                variant === "achievement" && "bg-purple-500/20 text-purple-400 border-purple-500/30",
                variant === "default" && "bg-slate-500/20 text-slate-400 border-slate-500/30"
              )}>
                {badge}
              </Badge>
            )}
          </div>
        </div>
        {isHighlighted && (
          <Sparkles className="h-4 w-4 text-cyan-400 animate-pulse" />
        )}
      </CardHeader>
      
      <CardContent className="relative">
        <div className="flex items-end justify-between mb-2">
          <div className="text-3xl font-bold text-slate-100 group-hover:text-white transition-colors">
            {value}
          </div>
          {variant === "achievement" && (
            <Award className="h-5 w-5 text-amber-400" />
          )}
          {variant === "premium" && (
            <Target className="h-5 w-5 text-cyan-400" />
          )}
        </div>
        
        {description && (
          <p className="text-xs text-slate-400 mb-3">{description}</p>
        )}
        
        {progress !== undefined && (
          <div className="mb-3">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-slate-400">Progress</span>
              <span className="text-slate-300 font-medium">{progress}%</span>
            </div>
            <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
              <div 
                className={cn(
                  "h-full transition-all duration-1000 rounded-full",
                  variant === "success" && "bg-gradient-to-r from-emerald-500 to-green-500",
                  variant === "warning" && "bg-gradient-to-r from-amber-500 to-orange-500",
                  variant === "premium" && "bg-gradient-to-r from-cyan-500 to-blue-500",
                  variant === "achievement" && "bg-gradient-to-r from-purple-500 to-indigo-500",
                  variant === "default" && "bg-gradient-to-r from-slate-500 to-slate-600"
                )}
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
        
        {trend && (
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              {trend.isPositive ? (
                <TrendingUp className="h-3 w-3 text-emerald-400 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-400 mr-1" />
              )}
              <span
                className={cn(
                  "text-xs font-medium",
                  trend.isPositive ? "text-emerald-400" : "text-red-400"
                )}
              >
                {trend.isPositive ? "+" : ""}{trend.value}%
              </span>
            </div>
            <span className="text-xs text-slate-500">
              vs {trend.period}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 