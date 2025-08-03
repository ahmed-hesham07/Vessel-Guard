import Link from 'next/link'
import { Shield, Globe, Lock, Award } from 'lucide-react'

export default function Footer() {
  return (
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
  )
}