'use client'

import Link from 'next/link'
import { Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'
import LoginForm from '@/components/auth/LoginForm'

export default function LoginPage() {
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
      <main className="flex flex-col items-center justify-center min-h-[70vh] px-4 py-12">
        <div className="w-full max-w-md bg-gray-900 border border-gray-700 rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-100 mb-6 text-center">Sign In to Vessel Guard</h1>
          <LoginForm />
          <div className="mt-6 text-center">
            <span className="text-gray-400">Don't have an account?</span>{' '}
            <Link href="/register" className="text-blue-400 hover:underline">Sign Up</Link>
          </div>
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
