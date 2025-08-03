'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react'

export default function TestDarkTheme() {
  return (
    <div className="min-h-screen dark-gradient-primary">
      {/* Header */}
      <header className="dark-navbar border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-blue-400" />
              <span className="text-xl font-bold text-gray-100">Dark Theme Test</span>
            </div>
            <Link href="/">
              <Button variant="ghost" className="text-gray-300 hover:text-gray-100 hover:bg-gray-800">
                Back to Home
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-100 mb-4">
            Dark Theme Verification
          </h1>
          <p className="text-xl text-gray-300">
            Testing all dark theme components and styles
          </p>
        </div>

        {/* Test Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="dark-card border-gray-700">
            <CardHeader>
              <CardTitle className="text-gray-100 flex items-center">
                <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                Success Card
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300 mb-4">
                This card demonstrates the dark theme styling with proper contrast.
              </p>
              <Badge className="bg-green-900/50 text-green-300 border border-green-700">
                Success Badge
              </Badge>
            </CardContent>
          </Card>

          <Card className="dark-card border-gray-700">
            <CardHeader>
              <CardTitle className="text-gray-100 flex items-center">
                <AlertTriangle className="h-5 w-5 text-yellow-400 mr-2" />
                Warning Card
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300 mb-4">
                Another card showing different color schemes in dark mode.
              </p>
              <Badge className="bg-yellow-900/50 text-yellow-300 border border-yellow-700">
                Warning Badge
              </Badge>
            </CardContent>
          </Card>
        </div>

        {/* Button Tests */}
        <Card className="dark-card border-gray-700 mb-8">
          <CardHeader>
            <CardTitle className="text-gray-100">Button Tests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <Button className="dark-button-primary">
                Primary Button
              </Button>
              <Button variant="outline" className="dark-button-outline">
                Outline Button
              </Button>
              <Button variant="ghost" className="text-gray-300 hover:text-gray-100 hover:bg-gray-800">
                Ghost Button
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Text Tests */}
        <Card className="dark-card border-gray-700 mb-8">
          <CardHeader>
            <CardTitle className="text-gray-100">Text Color Tests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <h3 className="text-gray-100 font-semibold">High Contrast Text (gray-100)</h3>
              <p className="text-gray-300">Medium Contrast Text (gray-300)</p>
              <p className="text-gray-400">Low Contrast Text (gray-400)</p>
              <p className="text-gray-500">Muted Text (gray-500)</p>
            </div>
          </CardContent>
        </Card>

        {/* Navigation Test */}
        <Card className="dark-card border-gray-700">
          <CardHeader>
            <CardTitle className="text-gray-100 flex items-center">
              <Info className="h-5 w-5 text-blue-400 mr-2" />
              Navigation Test
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Link href="/features">
                <Button variant="outline" className="w-full dark-button-outline">
                  Features Page
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button variant="outline" className="w-full dark-button-outline">
                  Dashboard
                </Button>
              </Link>
              <Link href="/dashboard/vessels">
                <Button variant="outline" className="w-full dark-button-outline">
                  Vessels
                </Button>
              </Link>
              <Link href="/dashboard/calculations">
                <Button variant="outline" className="w-full dark-button-outline">
                  Calculations
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 