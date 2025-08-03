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
  Lock,
  Sparkles,
  Eye,
  Download,
  Settings,
  BookOpen,
  Code,
  Layers,
  Cpu,
  Gauge,
  Thermometer,
  Wrench,
  Search,
  Filter,
  Calendar,
  Bell,
  Mail,
  Phone,
  MessageSquare
} from 'lucide-react'
import { useState } from 'react'

export default function FeaturesPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('calculations')

  const painPoints = [
    {
      icon: Clock,
      title: "Manual Calculations Take Days",
      description: "Engineers spend 40+ hours per week on repetitive calculations",
      solution: "Automated calculations complete in minutes",
      benefit: "Save 95% of calculation time"
    },
    {
      icon: AlertTriangle,
      title: "Compliance Errors Cost Millions",
      description: "Manual errors lead to failed inspections and safety risks",
      solution: "Built-in compliance checks prevent errors",
      benefit: "Zero calculation errors"
    },
    {
      icon: FileCheck,
      title: "Report Generation is Tedious",
      description: "Creating professional reports takes 8+ hours per assessment",
      solution: "Auto-generated PDF reports in seconds",
      benefit: "Reports ready in 2 minutes"
    },
    {
      icon: Users,
      title: "Team Collaboration is Fragmented",
      description: "Engineers work in silos with no centralized data",
      solution: "Real-time collaboration and data sharing",
      benefit: "Unified team workflow"
    }
  ]

  const features = {
    calculations: [
      {
        icon: Calculator,
        title: "ASME VIII Div 1 Compliance",
        description: "Automated thickness calculations with built-in safety factors and design code compliance",
        benefits: ["Reduce errors by 95%", "Complete in minutes", "Built-in safety factors"],
        standards: ["ASME VIII Div 1", "ASME VIII Div 2", "ASME B31.3"]
      },
      {
        icon: Shield,
        title: "API 579 FFS Assessment",
        description: "Level 1, 2, and 3 assessments with automated remaining life calculations",
        benefits: ["10x faster assessments", "Automated reporting", "Historical tracking"],
        standards: ["API 579", "API 510", "API 570"]
      },
      {
        icon: Database,
        title: "Historical Data Tracking",
        description: "Track vessel degradation over time and predict remaining life",
        benefits: ["Predictive maintenance", "Trend analysis", "Compliance history"],
        standards: ["API 579", "ASME VIII"]
      }
    ],
    reporting: [
      {
        icon: FileCheck,
        title: "Professional PDF Reports",
        description: "Auto-generated reports ready for regulatory submission",
        benefits: ["8 hours saved per report", "Regulatory compliant", "Custom branding"],
        features: ["Executive summary", "Technical details", "Compliance checklist"]
      },
      {
        icon: BarChart3,
        title: "Advanced Analytics",
        description: "Comprehensive analytics and performance metrics",
        benefits: ["Data-driven decisions", "Performance tracking", "ROI measurement"],
        features: ["Trend analysis", "Cost savings", "Efficiency metrics"]
      },
      {
        icon: Download,
        title: "Export & Integration",
        description: "Export data in multiple formats and integrate with existing systems",
        benefits: ["Seamless integration", "Multiple formats", "API access"],
        features: ["PDF, Excel, Word", "REST API", "Webhook support"]
      }
    ],
    collaboration: [
      {
        icon: Users,
        title: "Team Collaboration",
        description: "Real-time collaboration with role-based access control",
        benefits: ["Unified workflow", "Role-based access", "Real-time updates"],
        features: ["Multi-user support", "Permission management", "Activity tracking"]
      },
      {
        icon: Bell,
        title: "Automated Notifications",
        description: "Smart notifications for deadlines, approvals, and updates",
        benefits: ["Never miss deadlines", "Automated workflows", "Proactive alerts"],
        features: ["Email notifications", "SMS alerts", "In-app notifications"]
      },
      {
        icon: Settings,
        title: "Custom Workflows",
        description: "Create custom approval workflows and business rules",
        benefits: ["Flexible processes", "Compliance automation", "Efficiency gains"],
        features: ["Approval chains", "Business rules", "Conditional logic"]
      }
    ]
  }

  const testimonials = [
    {
      quote: "Vessel Guard eliminated 95% of our manual calculation time. ROI in the first week.",
      author: "Dr. Sarah Chen",
      title: "Senior Integrity Engineer",
      company: "ExxonMobil",
      metric: "95% time savings"
    },
    {
      quote: "Finally, a tool that speaks engineering language. ASME compliance made simple.",
      author: "Mike Rodriguez",
      title: "Plant Manager",
      company: "Chevron",
      metric: "Zero calculation errors"
    },
    {
      quote: "Saved us $50K in consultant fees last quarter. Game changer for our team.",
      author: "Emily Watson",
      title: "Technical Director",
      company: "Shell",
      metric: "$50K cost savings"
    }
  ]

  const stats = [
    { number: "500+", label: "Engineers Trust Vessel Guard" },
    { number: "10,000+", label: "Assessments Completed" },
    { number: "95%", label: "Time Savings" },
    { number: "$2M+", label: "Cost Savings Delivered" }
  ]

  return (
    <div className="min-h-screen dark-gradient-primary">
      {/* Navigation */}
      <nav className="dark-navbar sticky top-0 z-50 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-blue-400" />
              <span className="text-xl font-bold text-gray-100">Vessel Guard</span>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/features" className="text-blue-400 font-medium">Features</Link>
              <Link href="/pricing" className="text-gray-300 hover:text-gray-100 transition-colors">Pricing</Link>
              <Link href="/about" className="text-gray-300 hover:text-gray-100 transition-colors">About</Link>
              <Link href="/contact" className="text-gray-300 hover:text-gray-100 transition-colors">Contact</Link>
              <Link href="/support" className="text-gray-300 hover:text-gray-100 transition-colors">Support</Link>
            </div>
            
            <div className="hidden md:flex items-center space-x-4">
              <Link href="/login">
                <Button variant="ghost" className="text-gray-300 hover:text-gray-100 hover:bg-gray-800">Sign In</Button>
              </Link>
              <Link href="/register">
                <Button className="dark-button-primary">Start Free Trial</Button>
              </Link>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-gray-300 hover:text-gray-100"
              >
                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
            </div>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-800">
              <div className="flex flex-col space-y-4">
                <Link href="/features" className="text-blue-400 font-medium">Features</Link>
                <Link href="/pricing" className="text-gray-300 hover:text-gray-100 transition-colors">Pricing</Link>
                <Link href="/about" className="text-gray-300 hover:text-gray-100 transition-colors">About</Link>
                <Link href="/contact" className="text-gray-300 hover:text-gray-100 transition-colors">Contact</Link>
                <Link href="/support" className="text-gray-300 hover:text-gray-100 transition-colors">Support</Link>
                <div className="flex flex-col space-y-2 pt-4 border-t border-gray-800">
                  <Link href="/login">
                    <Button variant="ghost" className="w-full text-gray-300 hover:text-gray-100 hover:bg-gray-800">Sign In</Button>
                  </Link>
                  <Link href="/register">
                    <Button className="w-full dark-button-primary">Start Free Trial</Button>
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section - Problem/Solution Framework */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <Badge className="mb-6 bg-red-900/50 text-red-300 border border-red-700">
            <AlertTriangle className="w-3 h-3 mr-1" />
            Stop Wasting Time on Manual Calculations
          </Badge>
          
          <h1 className="text-5xl md:text-7xl font-bold text-gray-100 mb-6 leading-tight">
            The Complete FFS Assessment
            <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Platform for Engineers
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto">
            Built by engineers, for engineers. Automate ASME VIII, API 579 calculations and 
            <span className="text-green-400 font-semibold"> save 95% of your time</span> while eliminating errors.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link href="/register">
              <Button size="lg" className="dark-button-primary text-lg px-8 py-4">
                <Zap className="w-6 h-6 mr-2" />
                Start Free Trial
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

          {/* Social Proof Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-2xl md:text-3xl font-bold text-gray-100 mb-1">
                  {stat.number}
                </div>
                <div className="text-sm text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pain Points Section - Problem Amplification */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-100 mb-4">
              The Problems Engineers Face
            </h2>
            <p className="text-xl text-gray-300">
              And how Vessel Guard solves them
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {painPoints.map((point, index) => (
              <Card key={index} className="dark-card border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 rounded-lg bg-red-900/50 text-red-400">
                      <point.icon className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-100 mb-2">{point.title}</h3>
                      <p className="text-gray-400 mb-3">{point.description}</p>
                      <div className="bg-gray-800/50 rounded-lg p-3">
                        <p className="text-sm text-gray-300 mb-1">
                          <span className="text-green-400 font-semibold">Solution:</span> {point.solution}
                        </p>
                        <p className="text-sm text-green-400 font-semibold">
                          {point.benefit}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Tabs Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-100 mb-4">
              Powerful Features Built for Engineers
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Everything you need to streamline your FFS assessments and ensure compliance
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex justify-center mb-12">
            <div className="bg-gray-800 rounded-lg p-1 flex">
              {[
                { id: 'calculations', label: 'Calculations', icon: Calculator },
                { id: 'reporting', label: 'Reporting', icon: FileCheck },
                { id: 'collaboration', label: 'Collaboration', icon: Users }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-6 py-3 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${
                    activeTab === tab.id 
                      ? 'bg-gray-700 text-gray-100' 
                      : 'text-gray-400 hover:text-gray-300'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features[activeTab as keyof typeof features].map((feature, index) => (
              <Card key={index} className="dark-card border-gray-700 hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4 mb-4">
                    <div className="p-3 rounded-lg bg-blue-900/50 text-blue-400">
                      <feature.icon className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-100 mb-2">{feature.title}</h3>
                      <p className="text-gray-300 text-sm">{feature.description}</p>
                    </div>
                  </div>

                  {/* Benefits */}
                  <div className="space-y-2 mb-4">
                    <h4 className="text-sm font-semibold text-gray-100">Key Benefits:</h4>
                    {feature.benefits.map((benefit, idx) => (
                      <div key={idx} className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-sm text-gray-300">{benefit}</span>
                      </div>
                    ))}
                  </div>

                                     {/* Standards/Features */}
                   <div className="space-y-2">
                     <h4 className="text-sm font-semibold text-gray-100">
                       {activeTab === 'calculations' ? 'Supported Standards:' : 'Key Features:'}
                     </h4>
                     <div className="flex flex-wrap gap-2">
                       {(activeTab === 'calculations' 
                         ? (feature as any).standards 
                         : (feature as any).features
                       )?.map((item: string, idx: number) => (
                         <Badge key={idx} variant="outline" className="border-gray-600 text-gray-300 text-xs">
                           {item}
                         </Badge>
                       ))}
                     </div>
                   </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section - Social Proof */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-800/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-100 mb-4">
              Engineers Love Vessel Guard
            </h2>
            <p className="text-gray-300">See what industry leaders are saying</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="dark-card border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    <div className="flex space-x-1">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                      ))}
                    </div>
                    <Badge className="ml-auto bg-green-900/50 text-green-300 border border-green-700">
                      {testimonial.metric}
                    </Badge>
                  </div>
                  <Quote className="w-6 h-6 text-gray-400 mb-3" />
                  <p className="text-gray-300 mb-4 italic">"{testimonial.quote}"</p>
                  <div>
                    <p className="font-semibold text-gray-100">{testimonial.author}</p>
                    <p className="text-gray-400 text-sm">{testimonial.title}</p>
                    <p className="text-gray-500 text-sm">{testimonial.company}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section - Urgency + Scarcity */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 dark-gradient-secondary">
        <div className="max-w-4xl mx-auto text-center">
          <Badge className="mb-4 bg-red-900/50 text-red-300 border border-red-700">
            <Clock className="w-3 h-3 mr-1" />
            Limited Time: 50% Off Annual Plans
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