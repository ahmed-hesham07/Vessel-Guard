'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  Calculator, 
  FileCheck, 
  Users, 
  Database, 
  BarChart3,
  Zap,
  Target,
  CheckCircle,
  ArrowRight,
  Menu,
  X,
  Star,
  Clock,
  TrendingUp,
  AlertTriangle,
  Play,
  ChevronRight,
  ChevronLeft,
  Quote,
  Award,
  Globe,
  Lock
} from 'lucide-react'
import { useState } from 'react'

export default function HomePage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  const testimonials = [
    {
      quote: "Vessel Guard cut our FFS assessment time from 3 days to 2 hours. ROI in the first month.",
      author: "Sarah Chen, Senior Integrity Engineer",
      company: "ExxonMobil",
      rating: 5
    },
    {
      quote: "Finally, a tool that speaks engineering language. ASME compliance made simple.",
      author: "Mike Rodriguez, Plant Manager",
      company: "Chevron",
      rating: 5
    },
    {
      quote: "Saved us $50K in consultant fees last quarter. Game changer for our team.",
      author: "Dr. Emily Watson, Technical Director",
      company: "Shell",
      rating: 5
    }
  ]

  const features = [
    {
      icon: Calculator,
      title: "ASME VIII Div 1 Compliance",
      description: "Automated thickness calculations with built-in safety factors",
      benefit: "Reduce calculation errors by 95%"
    },
    {
      icon: Shield,
      title: "API 579 FFS Assessment",
      description: "Level 1, 2, and 3 assessments with automated reporting",
      benefit: "Complete assessments 10x faster"
    },
    {
      icon: FileCheck,
      title: "PDF Report Generation",
      description: "Professional reports ready for regulatory submission",
      benefit: "Save 8 hours per report"
    },
    {
      icon: Database,
      title: "Historical Data Tracking",
      description: "Track vessel degradation and predict remaining life",
      benefit: "Prevent unexpected failures"
    }
  ]

  const stats = [
    { number: "500+", label: "Engineers Trust Vessel Guard" },
    { number: "10,000+", label: "Assessments Completed" },
    { number: "95%", label: "Time Savings" },
    { number: "$2M+", label: "Cost Savings Delivered" }
  ]

  const logos = [
    "ExxonMobil", "Chevron", "Shell", "BP", "TotalEnergies", "ConocoPhillips"
  ]

  return (
    <div className="min-h-screen gradient-primary">
      {/* Navigation */}
      <nav className="glass-subtle sticky top-0 z-50 border-b border-clean">
        <div className="psych-container">
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
                <span className="social-proof-counter">12,847</span>
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
          <div className="md:hidden py-4 border-t border-clean">
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
              <div className="py-2 px-3 card-secondary rounded-lg">
                <div className="social-proof-subtle justify-center">
                  <Users className="w-3 h-3" />
                  <span className="social-proof-counter">12,847</span>
                  <span>engineers trust us</span>
                </div>
              </div>
              
              <div className="flex flex-col space-y-2 pt-4 border-t border-clean">
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

      {/* Hero Section - Psychological Trigger: Urgency + Authority */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          {/* Urgency Badge */}
          <div className="mb-6">
            <Badge className="bg-red-900/50 text-red-300 border border-red-700 animate-pulse">
              <Clock className="w-3 h-3 mr-1" />
              Limited Time: 50% Off Annual Plans
            </Badge>
          </div>

          {/* Authority Headline */}
          <h1 className="text-5xl md:text-7xl font-bold text-gray-100 mb-6 leading-tight">
            The #1 FFS Assessment Platform
            <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              for ASME/API Compliance
            </span>
          </h1>

          {/* Social Proof Subheadline */}
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto">
            Trusted by <span className="text-blue-400 font-semibold">500+ engineers</span> at Fortune 500 companies. 
            Complete ASME VIII, API 579 assessments in <span className="text-green-400 font-semibold">minutes, not days</span>.
          </p>

          {/* CTA Buttons - Multiple Options */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link href="/register">
              <Button size="lg" className="dark-button-primary text-lg px-8 py-4">
                <Zap className="w-6 h-6 mr-2" />
                Start Free Trial (No Credit Card)
                <ArrowRight className="w-6 h-6 ml-2" />
              </Button>
            </Link>
            <Link href="/demo">
              <Button variant="outline" size="lg" className="dark-button-outline text-lg px-8 py-4">
                <Play className="w-6 h-6 mr-2" />
                Watch 2-Min Demo
              </Button>
            </Link>
          </div>

          {/* Trust Indicators */}
          <div className="mb-8">
            <p className="text-gray-400 mb-4">Trusted by leading energy companies</p>
            <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
              {logos.map((logo, index) => (
                <div key={index} className="text-gray-300 font-semibold text-sm">
                  {logo}
                </div>
              ))}
            </div>
          </div>

          {/* Risk Reversal */}
          <div className="bg-gray-800/50 rounded-lg p-6 max-w-2xl mx-auto">
            <div className="flex items-center justify-center space-x-4 text-gray-300">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span>30-day money-back guarantee</span>
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span>No setup fees</span>
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span>Cancel anytime</span>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof Section - Testimonials */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-800/30">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-100 mb-4">
              Engineers Love Vessel Guard
            </h2>
            <p className="text-gray-300">See what industry leaders are saying</p>
          </div>

          <div className="relative">
            <div className="flex overflow-hidden">
              {testimonials.map((testimonial, index) => (
                <div
                  key={index}
                  className={`w-full flex-shrink-0 transition-transform duration-500 ${
                    index === currentTestimonial ? 'translate-x-0' : 'translate-x-full'
                  }`}
                >
                  <Card className="dark-card border-gray-700">
                    <CardContent className="p-8 text-center">
                      <div className="flex justify-center mb-4">
                        {[...Array(testimonial.rating)].map((_, i) => (
                          <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                        ))}
                      </div>
                      <Quote className="w-8 h-8 text-gray-400 mx-auto mb-4" />
                      <p className="text-lg text-gray-300 mb-6 italic">"{testimonial.quote}"</p>
                      <div>
                        <p className="font-semibold text-gray-100">{testimonial.author}</p>
                        <p className="text-gray-400">{testimonial.company}</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>

            {/* Navigation Dots */}
            <div className="flex justify-center mt-6 space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-colors ${
                    index === currentTestimonial ? 'bg-blue-400' : 'bg-gray-600'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section - Benefit-Focused */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-100 mb-4">
              Why Engineers Choose Vessel Guard
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Built by engineers, for engineers. Every feature designed to eliminate manual calculations and reduce errors.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="dark-card border-gray-700 hover:shadow-lg transition-shadow">
                <CardContent className="p-8">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 rounded-lg bg-gray-700 text-blue-400">
                      <feature.icon className="w-8 h-8" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-100 mb-2">{feature.title}</h3>
                      <p className="text-gray-300 mb-4">{feature.description}</p>
                      <Badge className="bg-green-900/50 text-green-300 border border-green-700">
                        {feature.benefit}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section - Social Proof */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-gray-100 mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section - Urgency + Scarcity */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 dark-gradient-secondary">
        <div className="max-w-4xl mx-auto text-center">
          <Badge className="mb-4 bg-red-900/50 text-red-300 border border-red-700">
            <AlertTriangle className="w-3 h-3 mr-1" />
            Limited Time Offer
          </Badge>
          <h2 className="text-4xl font-bold text-gray-100 mb-4">
            Ready to Transform Your FFS Assessments?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join 500+ engineers who've already saved thousands of hours and dollars.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button size="lg" className="dark-button-primary text-lg px-8 py-4">
                <Zap className="w-6 h-6 mr-2" />
                Start Free Trial Now
                <ArrowRight className="w-6 h-6 ml-2" />
              </Button>
            </Link>
            <Link href="/pricing">
              <Button variant="outline" size="lg" className="dark-button-outline text-lg px-8 py-4">
                View Pricing
              </Button>
            </Link>
          </div>
          <p className="text-sm text-gray-400 mt-4">
            No credit card required • 30-day free trial • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="dark-footer py-12 px-4 sm:px-6 lg:px-8 border-t border-gray-800">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <Shield className="h-8 w-8 text-blue-400" />
                <span className="text-xl font-bold text-gray-100">Vessel Guard</span>
              </div>
              <p className="text-gray-400 mb-4">
                The #1 FFS assessment platform for ASME/API compliance. Trusted by 500+ engineers worldwide.
              </p>
              <div className="flex space-x-4">
                <Globe className="h-5 w-5 text-gray-400" />
                <Lock className="h-5 w-5 text-gray-400" />
                <Award className="h-5 w-5 text-gray-400" />
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4 text-gray-100">Platform</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/dashboard" className="hover:text-gray-100 transition-colors">Dashboard</Link></li>
                <li><Link href="/dashboard/workflow/new" className="hover:text-gray-100 transition-colors">Quick Workflow</Link></li>
                <li><Link href="/dashboard/projects" className="hover:text-gray-100 transition-colors">Projects</Link></li>
                <li><Link href="/dashboard/vessels" className="hover:text-gray-100 transition-colors">Vessels</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4 text-gray-100">Features</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/dashboard/calculations" className="hover:text-gray-100 transition-colors">Calculations</Link></li>
                <li><Link href="/dashboard/inspections" className="hover:text-gray-100 transition-colors">Inspections</Link></li>
                <li><Link href="/reports" className="hover:text-gray-100 transition-colors">Reports</Link></li>
                <li><Link href="/support" className="hover:text-gray-100 transition-colors">Support</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4 text-gray-100">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about" className="hover:text-gray-100 transition-colors">About</Link></li>
                <li><Link href="/pricing" className="hover:text-gray-100 transition-colors">Pricing</Link></li>
                <li><Link href="/contact" className="hover:text-gray-100 transition-colors">Contact</Link></li>
                <li><Link href="/privacy" className="hover:text-gray-100 transition-colors">Privacy</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Vessel Guard. All rights reserved. | ASME/API Compliant | Enterprise Ready</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
