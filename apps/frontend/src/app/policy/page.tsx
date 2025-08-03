'use client'

import Link from 'next/link'
import { Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function PolicyPage() {
  return (
    <div className="min-h-screen dark-gradient-primary">
      {/* Header */}
      <header className="dark-navbar border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-blue-400" />
              <span className="text-xl font-bold text-gray-100">Vessel Guard</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/">
                <Button variant="ghost" className="text-gray-300 hover:text-gray-100 hover:bg-gray-800">
                  Back to Home
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-100 mb-6">Terms of Service</h1>
        <div className="space-y-6 text-gray-300">
          <p>
            These Terms of Service ("Terms") govern your use of the Vessel Guard platform. By accessing or using Vessel Guard, you agree to these Terms.
          </p>
          <h2 className="text-2xl font-semibold text-gray-100 mt-8 mb-2">Use of Service</h2>
          <ul className="list-disc list-inside ml-4 space-y-2">
            <li>You must provide accurate information and keep your account secure.</li>
            <li>You are responsible for all activity under your account.</li>
            <li>Do not misuse the platform or attempt unauthorized access.</li>
          </ul>
          <h2 className="text-2xl font-semibold text-gray-100 mt-8 mb-2">Subscription & Payment</h2>
          <ul className="list-disc list-inside ml-4 space-y-2">
            <li>Some features require a paid subscription.</li>
            <li>Fees are billed monthly or annually as selected.</li>
            <li>Refunds are available within 30 days of purchase.</li>
            <li>Failure to pay may result in suspension of service.</li>
          </ul>
          <h2 className="text-2xl font-semibold text-gray-100 mt-8 mb-2">Data & Privacy</h2>
          <ul className="list-disc list-inside ml-4 space-y-2">
            <li>Your data is encrypted at rest and in transit.</li>
            <li>We do not sell your personal information.</li>
            <li>See our Privacy Policy for more details.</li>
          </ul>
          <h2 className="text-2xl font-semibold text-gray-100 mt-8 mb-2">Termination</h2>
          <ul className="list-disc list-inside ml-4 space-y-2">
            <li>We may suspend or terminate your access for violation of these Terms.</li>
            <li>You may cancel your subscription at any time.</li>
          </ul>
          <h2 className="text-2xl font-semibold text-gray-100 mt-8 mb-2">Contact</h2>
          <p>
            For questions about these Terms, contact us at <a href="mailto:support@vesselguard.com" className="text-blue-400 underline">support@vesselguard.com</a>.
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className="dark-footer py-8 px-4 sm:px-6 lg:px-8 border-t border-gray-800 mt-12">
        <div className="max-w-7xl mx-auto text-center text-gray-400">
          <p>&copy; 2024 Vessel Guard. All rights reserved. | ASME/API Compliant | Enterprise Ready</p>
        </div>
      </footer>
    </div>
  )
} 