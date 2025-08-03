'use client'

import Link from 'next/link'
import { Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function PrivacyPage() {
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
        <h1 className="text-4xl font-bold text-gray-100 mb-6">Privacy Policy</h1>
        <div className="space-y-6 text-gray-300">
          <p>
            <span className="font-semibold text-gray-100">Vessel Guard</span> is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard your information when you use our platform.
          </p>
          <h2 className="text-2xl font-semibold text-gray-100 mt-8 mb-2">Information We Collect</h2>
          <ul className="list-disc list-inside ml-4 space-y-2">
            <li>Personal information (name, email, organization, etc.)</li>
            <li>Usage data (logins, actions, device/browser info)</li>
            <li>Uploaded files and engineering data</li>
            <li>Cookies and tracking technologies</li>
          </ul>
          <h2 className="text-2xl font-semibold text-gray-100 mt-8 mb-2">How We Use Your Information</h2>
          <ul className="list-disc list-inside ml-4 space-y-2">
            <li>To provide and improve the Vessel Guard platform</li>
            <li>To communicate with you about your account and updates</li>
            <li>To ensure security, compliance, and fraud prevention</li>
            <li>To comply with legal obligations</li>
          </ul>
          <h2 className="text-2xl font-semibold text-gray-100 mt-8 mb-2">Data Security</h2>
          <p>
            We use industry-standard security measures to protect your data, including encryption, access controls, and regular audits. Your data is encrypted at rest and in transit.
          </p>
          <h2 className="text-2xl font-semibold text-gray-100 mt-8 mb-2">Your Rights</h2>
          <ul className="list-disc list-inside ml-4 space-y-2">
            <li>Access, update, or delete your personal information</li>
            <li>Request a copy of your data</li>
            <li>Opt out of marketing communications</li>
            <li>Contact us for privacy-related questions</li>
          </ul>
          <h2 className="text-2xl font-semibold text-gray-100 mt-8 mb-2">Contact</h2>
          <p>
            If you have any questions about this Privacy Policy, please contact us at <a href="mailto:support@vesselguard.com" className="text-blue-400 underline">support@vesselguard.com</a>.
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
