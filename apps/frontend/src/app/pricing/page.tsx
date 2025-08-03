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
  Crown,
  Sparkles,
  Lock,
  Globe,
  Award,
  Play
} from 'lucide-react'
import { useState } from 'react'

export default function PricingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('annual')
  const [selectedPlan, setSelectedPlan] = useState('pro')

  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      description: 'Perfect for individual engineers',
      price: { monthly: 49, annual: 39 },
      originalPrice: { monthly: 79, annual: 59 },
      features: [
        'Up to 10 assessments per month',
        'ASME VIII Div 1 calculations',
        'Basic PDF reports',
        'Email support',
        'Single user'
      ],
      missing: [
        'API 579 FFS assessments',
        'Advanced reporting',
        'Team collaboration',
        'Priority support',
        'API access'
      ],
      popular: false,
      savings: 'Save 20%'
    },
    {
      id: 'pro',
      name: 'Professional',
      description: 'Most popular for engineering teams',
      price: { monthly: 149, annual: 119 },
      originalPrice: { monthly: 199, annual: 159 },
      features: [
        'Unlimited assessments',
        'ASME VIII Div 1 & API 579',
        'Advanced PDF reports',
        'Team collaboration (up to 5 users)',
        'Priority support',
        'Historical data tracking',
        'Custom calculations',
        'API access'
      ],
      missing: [
        'Enterprise features',
        'White-label reports',
        'Dedicated account manager'
      ],
      popular: true,
      savings: 'Save 25%'
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      description: 'For large organizations',
      price: { monthly: 399, annual: 319 },
      originalPrice: { monthly: 499, annual: 399 },
      features: [
        'Everything in Professional',
        'Unlimited team members',
        'White-label reports',
        'Dedicated account manager',
        'Custom integrations',
        'Advanced analytics',
        'Compliance automation',
        '24/7 phone support'
      ],
      missing: [],
      popular: false,
      savings: 'Save 20%'
    }
  ]

  const testimonials = [
    {
      quote: "Switched from Excel to Vessel Guard. ROI in first month.",
      author: "Sarah Chen",
      company: "ExxonMobil",
      plan: "Professional"
    },
    {
      quote: "Saves us 40 hours per week on calculations.",
      author: "Mike Rodriguez", 
      company: "Chevron",
      plan: "Enterprise"
    }
  ]

  const faqs = [
    {
      question: "Can I cancel anytime?",
      answer: "Yes, you can cancel your subscription at any time. No long-term contracts."
    },
    {
      question: "Do you offer refunds?",
      answer: "30-day money-back guarantee. If you're not satisfied, we'll refund your payment."
    },
    {
      question: "What payment methods do you accept?",
      answer: "Credit cards, PayPal, and wire transfers for Enterprise plans."
    },
    {
      question: "Can I upgrade or downgrade my plan?",
      answer: "Yes, you can change your plan at any time. Changes take effect immediately."
    }
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
              <Link href="/features" className="text-gray-300 hover:text-gray-100 transition-colors">Features</Link>
              <Link href="/pricing" className="text-blue-400 font-medium">Pricing</Link>
              <Link href="/about" className="text-gray-300 hover:text-gray-100 transition-colors">About</Link>
              <Link href="/support" className="text-gray-300 hover:text-gray-100 transition-colors">Support</Link>
              <Link href="/contact" className="text-gray-300 hover:text-gray-100 transition-colors">Contact</Link>
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
                <Link href="/features" className="text-gray-300 hover:text-gray-100 transition-colors">Features</Link>
                <Link href="/pricing" className="text-blue-400 font-medium">Pricing</Link>
                <Link href="/about" className="text-gray-300 hover:text-gray-100 transition-colors">About</Link>
                <Link href="/support" className="text-gray-300 hover:text-gray-100 transition-colors">Support</Link>
                <Link href="/contact" className="text-gray-300 hover:text-gray-100 transition-colors">Contact</Link>
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

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          {/* Urgency Badge */}
          <div className="mb-6">
            <Badge className="bg-red-900/50 text-red-300 border border-red-700 animate-pulse">
              <Clock className="w-3 h-3 mr-1" />
              Limited Time: 50% Off Annual Plans
            </Badge>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold text-gray-100 mb-6">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Choose the plan that fits your needs. All plans include our 30-day money-back guarantee.
          </p>

          {/* Billing Toggle - Anchoring Strategy */}
          <div className="flex justify-center mb-12">
            <div className="bg-gray-800 rounded-lg p-1 flex">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  billingCycle === 'monthly' 
                    ? 'bg-gray-700 text-gray-100' 
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('annual')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  billingCycle === 'annual' 
                    ? 'bg-gray-700 text-gray-100' 
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                Annual
                <Badge className="ml-2 bg-green-900/50 text-green-300 border border-green-700 text-xs">
                  Save 20%
                </Badge>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan) => (
              <Card 
                key={plan.id}
                className={`dark-card border-gray-700 relative ${
                  plan.popular 
                    ? 'border-blue-500 shadow-lg scale-105' 
                    : 'hover:shadow-lg transition-shadow'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-blue-900/50 text-blue-300 border border-blue-700">
                      <Crown className="w-3 h-3 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center pb-4">
                  <CardTitle className="text-2xl font-bold text-gray-100">{plan.name}</CardTitle>
                  <p className="text-gray-400">{plan.description}</p>
                  
                  {/* Price Display - Psychological Pricing */}
                  <div className="mt-6">
                    <div className="flex items-center justify-center space-x-2">
                      <span className="text-4xl font-bold text-gray-100">
                        ${plan.price[billingCycle]}
                      </span>
                      <span className="text-gray-400">/month</span>
                    </div>
                    
                    {/* Original Price - Anchoring */}
                    <div className="flex items-center justify-center space-x-2 mt-2">
                      <span className="text-gray-500 line-through">
                        ${plan.originalPrice[billingCycle]}
                      </span>
                      <Badge className="bg-green-900/50 text-green-300 border border-green-700">
                        {plan.savings}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>

                <CardContent>
                  {/* Features List */}
                  <div className="space-y-3 mb-8">
                    {plan.features.map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                        <span className="text-gray-300">{feature}</span>
                      </div>
                    ))}
                    
                    {/* Missing Features - Scarcity */}
                    {plan.missing.map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3 opacity-50">
                        <X className="w-5 h-5 text-gray-500 flex-shrink-0" />
                        <span className="text-gray-500">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* CTA Button */}
                  <Link href="/register">
                    <Button 
                      className={`w-full ${
                        plan.popular 
                          ? 'dark-button-primary' 
                          : 'dark-button-outline'
                      }`}
                      onClick={() => setSelectedPlan(plan.id)}
                    >
                      {plan.popular ? (
                        <>
                          <Sparkles className="w-4 h-4 mr-2" />
                          Start Free Trial
                        </>
                      ) : (
                        'Start Free Trial'
                      )}
                    </Button>
                  </Link>

                  {/* Risk Reversal */}
                  <p className="text-xs text-gray-400 text-center mt-3">
                    30-day money-back guarantee
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-800/30">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-100 mb-4">
              Trusted by Industry Leaders
            </h2>
            <p className="text-gray-300">See what our customers are saying</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="dark-card border-gray-700">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    <div className="flex space-x-1">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                      ))}
                    </div>
                    <Badge className="ml-auto bg-blue-900/50 text-blue-300 border border-blue-700">
                      {testimonial.plan}
                    </Badge>
                  </div>
                  <p className="text-gray-300 mb-4 italic">"{testimonial.quote}"</p>
                  <div>
                    <p className="font-semibold text-gray-100">{testimonial.author}</p>
                    <p className="text-gray-400">{testimonial.company}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-100 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-gray-300">Everything you need to know about our pricing</p>
          </div>

          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <Card key={index} className="dark-card border-gray-700">
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold text-gray-100 mb-2">
                    {faq.question}
                  </h3>
                  <p className="text-gray-300">{faq.answer}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA - Urgency + Scarcity */}
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
            <Link href="/demo">
              <Button variant="outline" size="lg" className="dark-button-outline text-lg px-8 py-4">
                <Play className="w-6 h-6 mr-2" />
                Watch Demo
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
              <h3 className="font-semibold mb-4 text-gray-100">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/features" className="hover:text-gray-100 transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-gray-100 transition-colors">Pricing</Link></li>
                <li><Link href="/demo" className="hover:text-gray-100 transition-colors">Demo</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4 text-gray-100">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about" className="hover:text-gray-100 transition-colors">About</Link></li>
                <li><Link href="/contact" className="hover:text-gray-100 transition-colors">Contact</Link></li>
                <li><Link href="/privacy" className="hover:text-gray-100 transition-colors">Privacy</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4 text-gray-100">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/support" className="hover:text-gray-100 transition-colors">Help Center</Link></li>
                <li><Link href="/docs" className="hover:text-gray-100 transition-colors">Documentation</Link></li>
                <li><Link href="/status" className="hover:text-gray-100 transition-colors">Status</Link></li>
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