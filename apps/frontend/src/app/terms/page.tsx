'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  FileText, 
  Calendar, 
  AlertTriangle,
  Check,
  Scale,
  Users,
  Lock,
  Globe,
  Mail
} from 'lucide-react'

export default function TermsOfServicePage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-blue-100 rounded-full">
            <Scale className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Terms of Service</h1>
        <p className="text-gray-600 mb-4">
          Please read these terms carefully before using Vessel Guard services
        </p>
        <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
          <div className="flex items-center">
            <Calendar className="h-4 w-4 mr-1" />
            Last updated: January 15, 2024
          </div>
          <div className="flex items-center">
            <FileText className="h-4 w-4 mr-1" />
            Version 2.1
          </div>
        </div>
      </div>

      {/* Quick Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center">
            <Check className="h-5 w-5 text-green-500 mr-2" />
            Quick Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-green-50 rounded-lg">
              <h4 className="font-medium text-green-900 mb-2">You Can:</h4>
              <ul className="text-sm text-green-800 space-y-1">
                <li>• Use our service for commercial purposes</li>
                <li>• Store your vessel inspection data</li>
                <li>• Share reports with your team</li>
                <li>• Export your data at any time</li>
              </ul>
            </div>
            <div className="p-4 bg-red-50 rounded-lg">
              <h4 className="font-medium text-red-900 mb-2">You Cannot:</h4>
              <ul className="text-sm text-red-800 space-y-1">
                <li>• Reverse engineer our software</li>
                <li>• Share your account credentials</li>
                <li>• Use the service for illegal activities</li>
                <li>• Violate intellectual property rights</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Terms Content */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">1. Acceptance of Terms</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              By accessing and using Vessel Guard ("the Service"), you accept and agree to be bound by the terms and provision of this agreement.
            </p>
            <p className="text-gray-700">
              If you do not agree to abide by the above, please do not use this service. These terms apply to all users of the Service, including without limitation users who are browsers, customers, merchants, vendors, and/or contributors of content.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">2. Service Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              Vessel Guard is a cloud-based platform that provides:
            </p>
            <ul className="text-gray-700 space-y-2 mb-4">
              <li className="flex items-start">
                <Check className="h-4 w-4 text-green-500 mr-2 mt-1" />
                Vessel inspection management and tracking
              </li>
              <li className="flex items-start">
                <Check className="h-4 w-4 text-green-500 mr-2 mt-1" />
                Pressure vessel calculations and compliance tools
              </li>
              <li className="flex items-start">
                <Check className="h-4 w-4 text-green-500 mr-2 mt-1" />
                Report generation and document management
              </li>
              <li className="flex items-start">
                <Check className="h-4 w-4 text-green-500 mr-2 mt-1" />
                Team collaboration and project management
              </li>
            </ul>
            <p className="text-gray-700">
              We reserve the right to modify or discontinue, temporarily or permanently, the Service (or any part thereof) with or without notice.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">3. User Accounts</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              To access certain features of the Service, you must register for an account. You agree to:
            </p>
            <ul className="text-gray-700 space-y-2 mb-4">
              <li>• Provide accurate, current, and complete information</li>
              <li>• Maintain the security of your password</li>
              <li>• Accept responsibility for all activities under your account</li>
              <li>• Notify us immediately of any unauthorized use</li>
            </ul>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mr-2 mt-1" />
                <div>
                  <p className="font-medium text-yellow-900">Important:</p>
                  <p className="text-sm text-yellow-800">
                    You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">4. Data and Privacy</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              Your privacy is important to us. Our Privacy Policy explains how we collect, use, and protect your information when you use our Service.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Data Ownership</h4>
                <p className="text-sm text-gray-700">
                  You retain all rights to your data. We do not claim ownership of any content you upload to our Service.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Data Security</h4>
                <p className="text-sm text-gray-700">
                  We implement industry-standard security measures to protect your data from unauthorized access.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">5. Acceptable Use</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              You agree not to use the Service:
            </p>
            <ul className="text-gray-700 space-y-2 mb-4">
              <li>• For any unlawful purpose or to solicit others to unlawful acts</li>
              <li>• To violate any international, federal, provincial, or state regulations or laws</li>
              <li>• To infringe upon or violate our intellectual property rights or the intellectual property rights of others</li>
              <li>• To harass, abuse, insult, harm, defame, slander, disparage, intimidate, or discriminate</li>
              <li>• To submit false or misleading information</li>
              <li>• To upload or transmit viruses or any other type of malicious code</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">6. Intellectual Property</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              The Service and its original content, features, and functionality are and will remain the exclusive property of Vessel Guard and its licensors.
            </p>
            <p className="text-gray-700">
              The Service is protected by copyright, trademark, and other laws. You may not reproduce, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on our Service without our prior written consent.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">7. Termination</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              We may terminate or suspend your account and bar access to the Service immediately, without prior notice or liability, under our sole discretion, for any reason whatsoever and without limitation, including but not limited to a breach of the Terms.
            </p>
            <p className="text-gray-700">
              If you wish to terminate your account, you may simply discontinue using the Service. Upon termination, your right to use the Service will cease immediately.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">8. Limitation of Liability</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              In no event shall Vessel Guard, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your use of the Service.
            </p>
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-start">
                <Shield className="h-5 w-5 text-blue-600 mr-2 mt-1" />
                <div>
                  <p className="font-medium text-blue-900">Professional Use Notice</p>
                  <p className="text-sm text-blue-800">
                    While our calculations and tools are designed to assist engineering professionals, they do not replace professional judgment and expertise. Always verify results independently.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">9. Governing Law</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              These Terms shall be interpreted and governed by the laws of the State of Massachusetts, United States, without regard to its conflict of law provisions.
            </p>
            <p className="text-gray-700">
              Our failure to enforce any right or provision of these Terms will not be considered a waiver of those rights.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">10. Contact Information</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              If you have any questions about these Terms of Service, please contact us:
            </p>
            <div className="space-y-2">
              <div className="flex items-center">
                <Mail className="h-4 w-4 text-gray-500 mr-2" />
                <span className="text-gray-700">legal@vesselguard.com</span>
              </div>
              <div className="flex items-center">
                <Globe className="h-4 w-4 text-gray-500 mr-2" />
                <span className="text-gray-700">https://vesselguard.com/legal</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Footer */}
      <div className="text-center border-t pt-6">
        <p className="text-sm text-gray-500 mb-4">
          By using Vessel Guard, you acknowledge that you have read and understood these Terms of Service.
        </p>
        <div className="flex justify-center space-x-4">
          <Button variant="outline" size="sm">
            <FileText className="h-4 w-4 mr-2" />
            Download PDF
          </Button>
          <Button variant="outline" size="sm">
            <Mail className="h-4 w-4 mr-2" />
            Email Copy
          </Button>
        </div>
      </div>
    </div>
  )
}
