import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Shield, Menu, X, Users, Star, Zap, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function LandingNavbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [userCount, setUserCount] = useState(12847)
  
  // Subtle social proof counter animation
  useEffect(() => {
    const interval = setInterval(() => {
      setUserCount(prev => prev + Math.floor(Math.random() * 3))
    }, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])
  
  return (
    <nav className="glass-subtle sticky top-0 z-50 border-b border-slate-700/30 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-3">
            <div className="relative micro-glow">
              <Shield className="h-8 w-8 text-cyan-400 drop-shadow-lg" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                Vessel Guard
              </span>
              <div className="flex items-center space-x-1 mt-0.5">
                <Star className="h-3 w-3 text-amber-400" />
                <span className="text-xs text-amber-400 font-medium">Engineering Excellence</span>
              </div>
            </div>
          </div>
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/features" className="text-secondary hover:text-primary transition-all duration-200 micro-lift">
              Features
            </Link>
            <div className="relative">
              <Link href="/pricing" className="text-secondary hover:text-primary transition-all duration-200 micro-lift">
                Pricing
              </Link>
              <div className="absolute -top-2 -right-3 scarcity-indicator">
                Save 25%
              </div>
            </div>
            <Link href="/about" className="text-secondary hover:text-primary transition-all duration-200 micro-lift">
              About
            </Link>
            <Link href="/support" className="text-secondary hover:text-primary transition-all duration-200 micro-lift">
              Support
            </Link>
            <Link href="/contact" className="text-secondary hover:text-primary transition-all duration-200 micro-lift">
              Contact
            </Link>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            {/* Subtle Social Proof */}
            <div className="social-proof-subtle">
              <Users className="w-3 h-3" />
              <span className="social-proof-counter">{userCount.toLocaleString()}</span>
              <span>engineers</span>
            </div>
            
            <Link href="/login">
              <Button variant="ghost" className="cta-ghost">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button className="cta-primary micro-lift">
                <Zap className="w-4 h-4 mr-2" />
                Start Free Trial
              </Button>
            </Link>
          </div>
          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="cta-ghost"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>
        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-700/30">
            <div className="flex flex-col space-y-4">
              <Link href="/features" className="text-secondary hover:text-primary transition-colors">Features</Link>
              <div className="relative">
                <Link href="/pricing" className="text-secondary hover:text-primary transition-colors">Pricing</Link>
                <span className="ml-2 scarcity-indicator">Save 25%</span>
              </div>
              <Link href="/about" className="text-secondary hover:text-primary transition-colors">About</Link>
              <Link href="/support" className="text-secondary hover:text-primary transition-colors">Support</Link>
              <Link href="/contact" className="text-secondary hover:text-primary transition-colors">Contact</Link>
              
              {/* Mobile Social Proof */}
              <div className="py-2 px-3 bg-slate-800/30 rounded-lg border border-slate-700/30">
                <div className="social-proof-subtle justify-center">
                  <Users className="w-3 h-3" />
                  <span className="social-proof-counter">{userCount.toLocaleString()}</span>
                  <span>engineers trust us</span>
                </div>
              </div>
              
              <div className="flex flex-col space-y-2 pt-4 border-t border-slate-700/30">
                <Link href="/login">
                  <Button variant="ghost" className="w-full cta-ghost">Sign In</Button>
                </Link>
                <Link href="/register">
                  <Button className="w-full cta-primary">
                    <Zap className="w-4 h-4 mr-2" />
                    Start Free Trial
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}