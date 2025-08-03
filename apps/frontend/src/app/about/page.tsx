"use client"

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  Users, 
  Target, 
  Award,
  ArrowRight,
  CheckCircle,
  Globe,
  Zap,
  Heart,
  Lightbulb,
  Menu,
  X
} from 'lucide-react'
import { useState } from 'react'

export default function About() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen dark-gradient-primary">
      {/* Navigation */}
      <nav className="dark-navbar sticky top-0 z-50 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Link href="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-gray-100">Vessel Guard</span>
              </Link>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/about" className="text-blue-400 font-medium">About</Link>
              <Link href="/pricing" className="text-gray-300 hover:text-gray-100 transition-colors">Pricing</Link>
              <Link href="/privacy" className="text-gray-300 hover:text-gray-100 transition-colors">Privacy</Link>
              <Link href="/policy" className="text-gray-300 hover:text-gray-100 transition-colors">Policy</Link>
              <Link href="/contact" className="text-gray-300 hover:text-gray-100 transition-colors">Contact</Link>
            </div>
            
            <div className="hidden md:flex items-center space-x-4">
              <Link href="/login">
                <Button variant="ghost" className="text-gray-300 hover:text-gray-100 hover:bg-gray-800">Sign In</Button>
              </Link>
              <Link href="/register">
                <Button className="dark-button-primary">Get Started</Button>
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
                <Link href="/about" className="text-blue-400 font-medium">About</Link>
                <Link href="/pricing" className="text-gray-300 hover:text-gray-100 transition-colors">Pricing</Link>
                <Link href="/privacy" className="text-gray-300 hover:text-gray-100 transition-colors">Privacy</Link>
                <Link href="/policy" className="text-gray-300 hover:text-gray-100 transition-colors">Policy</Link>
                <Link href="/contact" className="text-gray-300 hover:text-gray-100 transition-colors">Contact</Link>
                <div className="flex flex-col space-y-2 pt-4 border-t border-gray-800">
                  <Link href="/login">
                    <Button variant="ghost" className="w-full text-gray-300 hover:text-gray-100 hover:bg-gray-800">Sign In</Button>
                  </Link>
                  <Link href="/register">
                    <Button className="w-full dark-button-primary">Get Started</Button>
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <Badge variant="secondary" className="mb-4 bg-blue-900/50 text-blue-300 border border-blue-700">
            <Heart className="w-4 h-4 mr-2" />
            Our Story
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-100 mb-6">
            Revolutionizing
            <span className="text-blue-400 block">Vessel Compliance</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            We're on a mission to make vessel safety and compliance accessible, accurate, and efficient 
            for engineering professionals worldwide.
          </p>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-16 bg-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-gray-100 mb-6">
                Our Mission
              </h2>
              <p className="text-lg text-gray-300 mb-6">
                At Vessel Guard, we believe that vessel safety shouldn't be complicated. Our platform 
                combines cutting-edge engineering calculations with intuitive design to ensure that every 
                vessel meets the highest safety standards.
              </p>
              <p className="text-lg text-gray-300 mb-8">
                Founded by a team of experienced engineers and software developers, we understand the 
                challenges faced by professionals in the vessel inspection industry. That's why we've 
                built a platform that not only meets current standards but anticipates future requirements.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/register">
                  <Button size="lg" className="dark-button-primary text-lg px-8 py-3">
                    Join Our Mission
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                </Link>
                <Link href="/pricing">
                  <Button variant="outline" size="lg" className="dark-button-outline text-lg px-8 py-3">
                    View Pricing
                  </Button>
                </Link>
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-8 text-white">
                <div className="flex items-center mb-6">
                  <Target className="w-8 h-8 mr-3" />
                  <h3 className="text-2xl font-bold">Our Vision</h3>
                </div>
                <p className="text-lg mb-6">
                  To become the global standard for vessel compliance, making safety accessible to 
                  every engineering professional.
                </p>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold">99.9%</div>
                    <div className="text-sm opacity-90">Accuracy Rate</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold">24/7</div>
                    <div className="text-sm opacity-90">Support Available</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-100 mb-4">
              Our Core Values
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              The principles that guide everything we do
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="dark-card border-gray-700 shadow-lg hover:shadow-xl transition-shadow hover-lift">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-900/50 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-blue-400" />
                </div>
                <CardTitle className="text-gray-100">Safety First</CardTitle>
                <CardDescription className="text-gray-300">
                  Every calculation, every report, every feature is designed with safety as the top priority.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="dark-card border-gray-700 shadow-lg hover:shadow-xl transition-shadow hover-lift">
              <CardHeader>
                <div className="w-12 h-12 bg-green-900/50 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="w-6 h-6 text-green-400" />
                </div>
                <CardTitle className="text-gray-100">Innovation</CardTitle>
                <CardDescription className="text-gray-300">
                  We continuously innovate to provide the most advanced engineering solutions available.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="dark-card border-gray-700 shadow-lg hover:shadow-xl transition-shadow hover-lift">
              <CardHeader>
                <div className="w-12 h-12 bg-purple-900/50 rounded-lg flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-purple-400" />
                </div>
                <CardTitle className="text-gray-100">Community</CardTitle>
                <CardDescription className="text-gray-300">
                  We build for and with the engineering community, ensuring our solutions meet real needs.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="dark-card border-gray-700 shadow-lg hover:shadow-xl transition-shadow hover-lift">
              <CardHeader>
                <div className="w-12 h-12 bg-orange-900/50 rounded-lg flex items-center justify-center mb-4">
                  <Award className="w-6 h-6 text-orange-400" />
                </div>
                <CardTitle className="text-gray-100">Excellence</CardTitle>
                <CardDescription className="text-gray-300">
                  We strive for excellence in every aspect of our platform and customer service.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="dark-card border-gray-700 shadow-lg hover:shadow-xl transition-shadow hover-lift">
              <CardHeader>
                <div className="w-12 h-12 bg-red-900/50 rounded-lg flex items-center justify-center mb-4">
                  <Globe className="w-6 h-6 text-red-400" />
                </div>
                <CardTitle className="text-gray-100">Global Impact</CardTitle>
                <CardDescription className="text-gray-300">
                  Our platform serves engineers worldwide, contributing to global safety standards.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="dark-card border-gray-700 shadow-lg hover:shadow-xl transition-shadow hover-lift">
              <CardHeader>
                <div className="w-12 h-12 bg-indigo-900/50 rounded-lg flex items-center justify-center mb-4">
                  <Lightbulb className="w-6 h-6 text-indigo-400" />
                </div>
                <CardTitle className="text-gray-100">Continuous Learning</CardTitle>
                <CardDescription className="text-gray-300">
                  We constantly learn from our users and industry developments to improve our platform.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-24 bg-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-100 mb-4">
              Meet Our Team
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Experienced engineers and developers passionate about vessel safety
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="dark-card border-gray-700 shadow-lg hover:shadow-xl transition-shadow hover-lift">
              <CardHeader className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <Users className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-gray-100">Engineering Experts</CardTitle>
                <CardDescription className="text-gray-300">
                  Our team includes certified engineers with decades of experience in vessel design and inspection.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="dark-card border-gray-700 shadow-lg hover:shadow-xl transition-shadow hover-lift">
              <CardHeader className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <Zap className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-gray-100">Software Engineers</CardTitle>
                <CardDescription className="text-gray-300">
                  Expert developers who build robust, scalable solutions for complex engineering challenges.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="dark-card border-gray-700 shadow-lg hover:shadow-xl transition-shadow hover-lift">
              <CardHeader className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <Award className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-gray-100">Quality Assurance</CardTitle>
                <CardDescription className="text-gray-300">
                  Dedicated QA team ensuring every calculation and feature meets the highest standards.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 dark-gradient-secondary">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-gray-100 mb-6">
            Ready to Join Our Mission?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Start your journey with Vessel Guard and experience the future of vessel compliance.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button size="lg" variant="secondary" className="dark-button-primary text-lg px-8 py-3">
                Start Free Trial
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link href="/contact">
              <Button size="lg" variant="outline" className="dark-button-outline text-lg px-8 py-3">
                Contact Us
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="dark-footer py-12 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-gray-100">Vessel Guard</span>
              </div>
              <p className="text-gray-400">
                Professional vessel inspection and compliance management system.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4 text-gray-100">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about" className="hover:text-gray-100 transition-colors">About</Link></li>
                <li><Link href="/pricing" className="hover:text-gray-100 transition-colors">Pricing</Link></li>
                <li><Link href="/features" className="hover:text-gray-100 transition-colors">Features</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4 text-gray-100">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/privacy" className="hover:text-gray-100 transition-colors">Privacy</Link></li>
                <li><Link href="/policy" className="hover:text-gray-100 transition-colors">Policy</Link></li>
                <li><Link href="/support" className="hover:text-gray-100 transition-colors">Support</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4 text-gray-100">Connect</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/contact" className="hover:text-gray-100 transition-colors">Contact</Link></li>
                <li><Link href="/login" className="hover:text-gray-100 transition-colors">Sign In</Link></li>
                <li><Link href="/register" className="hover:text-gray-100 transition-colors">Get Started</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Vessel Guard. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
} 