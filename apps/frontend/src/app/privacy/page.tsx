'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  FileText, 
  Calendar, 
  Eye,
  Lock,
  Database,
  Users,
  Globe,
  Mail,
  Cookie,
  Settings,
  Download,
  ExternalLink
} from 'lucide-react'

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-green-100 rounded-full">
            <Shield className="h-8 w-8 text-green-600" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
        <p className="text-gray-600 mb-4">
          Learn how we collect, use, and protect your personal information
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

      {/* Privacy Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center">
            <Eye className="h-5 w-5 text-blue-500 mr-2" />
            Privacy at a Glance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg text-center">
              <Lock className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h4 className="font-medium text-blue-900 mb-1">Data Protection</h4>
              <p className="text-sm text-blue-800">
                We use industry-standard encryption and security measures
              </p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg text-center">
              <Users className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <h4 className="font-medium text-green-900 mb-1">No Data Selling</h4>
              <p className="text-sm text-green-800">
                We never sell your personal information to third parties
              </p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg text-center">
              <Settings className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <h4 className="font-medium text-purple-900 mb-1">Your Control</h4>
              <p className="text-sm text-purple-800">
                You can access, update, or delete your data at any time
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Content */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">1. Information We Collect</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Personal Information</h4>
                <p className="text-gray-700 mb-2">
                  When you register for an account, we collect:
                </p>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Name and email address</li>
                  <li>• Company information and job title</li>
                  <li>• Phone number (optional)</li>
                  <li>• Billing and payment information</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Technical Information</h4>
                <p className="text-gray-700 mb-2">
                  We automatically collect certain technical information:
                </p>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• IP address and browser information</li>
                  <li>• Device type and operating system</li>
                  <li>• Usage patterns and feature interactions</li>
                  <li>• Log files and error reports</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Vessel Data</h4>
                <p className="text-gray-700 mb-2">
                  Information you provide about your vessels and inspections:
                </p>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Vessel specifications and documentation</li>
                  <li>• Inspection reports and calculations</li>
                  <li>• Maintenance records and schedules</li>
                  <li>• Photos and supporting documents</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">2. How We Use Your Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Service Provision</h4>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Provide and maintain the Vessel Guard service</li>
                  <li>• Process calculations and generate reports</li>
                  <li>• Enable collaboration between team members</li>
                  <li>• Provide customer support</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Communication</h4>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Send important service announcements</li>
                  <li>• Respond to your inquiries and support requests</li>
                  <li>• Send inspection reminders and notifications</li>
                  <li>• Provide updates about new features (with consent)</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Improvement</h4>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Analyze usage patterns to improve our service</li>
                  <li>• Identify and fix technical issues</li>
                  <li>• Develop new features and functionality</li>
                  <li>• Ensure security and prevent fraud</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">3. Data Sharing and Disclosure</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">We Do Not Sell Your Data</h4>
                <p className="text-sm text-green-800">
                  We never sell, rent, or trade your personal information to third parties for marketing purposes.
                </p>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Limited Sharing</h4>
                <p className="text-gray-700 mb-2">
                  We may share your information only in these specific circumstances:
                </p>
                <ul className="text-gray-700 space-y-2 ml-4">
                  <li>• <strong>Service Providers:</strong> With trusted third-party service providers who help us operate our service (e.g., cloud hosting, payment processing)</li>
                  <li>• <strong>Legal Requirements:</strong> When required by law or to protect our rights and safety</li>
                  <li>• <strong>Business Transfers:</strong> In the event of a merger, acquisition, or sale of assets</li>
                  <li>• <strong>With Your Consent:</strong> When you explicitly authorize us to share your information</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">4. Data Security</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Technical Safeguards</h4>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• End-to-end encryption for data transmission</li>
                  <li>• Encrypted storage of sensitive information</li>
                  <li>• Regular security audits and penetration testing</li>
                  <li>• Multi-factor authentication support</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Operational Security</h4>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Access controls and role-based permissions</li>
                  <li>• Employee security training and background checks</li>
                  <li>• Incident response and breach notification procedures</li>
                  <li>• Regular data backups and disaster recovery</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Compliance</h4>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• SOC 2 Type II certification</li>
                  <li>• GDPR compliance for EU users</li>
                  <li>• CCPA compliance for California residents</li>
                  <li>• Industry-standard security frameworks</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">5. Your Rights and Choices</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Access and Control</h4>
                <p className="text-gray-700 mb-2">You have the right to:</p>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Access your personal information</li>
                  <li>• Update or correct your data</li>
                  <li>• Download your data in a portable format</li>
                  <li>• Delete your account and associated data</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Communication Preferences</h4>
                <p className="text-gray-700 mb-2">You can control:</p>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Email notification settings</li>
                  <li>• Marketing communication preferences</li>
                  <li>• Mobile push notifications</li>
                  <li>• Inspection reminder frequency</li>
                </ul>
              </div>
              
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">How to Exercise Your Rights</h4>
                <p className="text-sm text-blue-800 mb-2">
                  To exercise any of these rights, contact us at:
                </p>
                <div className="flex items-center text-sm text-blue-800">
                  <Mail className="h-4 w-4 mr-1" />
                  privacy@vesselguard.com
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">6. Cookies and Tracking</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Types of Cookies</h4>
                <div className="space-y-3">
                  <div className="flex items-start">
                    <Cookie className="h-5 w-5 text-orange-500 mr-2 mt-1" />
                    <div>
                      <p className="font-medium text-gray-900">Essential Cookies</p>
                      <p className="text-sm text-gray-600">Required for basic functionality and security</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <Cookie className="h-5 w-5 text-blue-500 mr-2 mt-1" />
                    <div>
                      <p className="font-medium text-gray-900">Functional Cookies</p>
                      <p className="text-sm text-gray-600">Remember your preferences and settings</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <Cookie className="h-5 w-5 text-green-500 mr-2 mt-1" />
                    <div>
                      <p className="font-medium text-gray-900">Analytics Cookies</p>
                      <p className="text-sm text-gray-600">Help us understand how you use our service</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Cookie Management</h4>
                <p className="text-gray-700 mb-2">
                  You can control cookies through your browser settings or our cookie preferences panel. 
                  Note that disabling essential cookies may affect service functionality.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">7. Data Retention</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Retention Periods</h4>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Account information: For the life of your account</li>
                  <li>• Vessel data: Until you delete it or close your account</li>
                  <li>• Usage logs: Up to 2 years for security and analytics</li>
                  <li>• Support communications: Up to 3 years</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Data Deletion</h4>
                <p className="text-gray-700 mb-2">
                  When you delete your account, we will:
                </p>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Remove your personal information within 30 days</li>
                  <li>• Delete vessel data according to your preferences</li>
                  <li>• Retain anonymized usage data for analytics</li>
                  <li>• Keep records required by law or regulation</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">8. International Data Transfers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Global Operations</h4>
                <p className="text-gray-700 mb-2">
                  Vessel Guard operates globally. Your information may be transferred to and processed in:
                </p>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• United States (primary data centers)</li>
                  <li>• European Union (regional processing)</li>
                  <li>• Other countries where our service providers operate</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Transfer Safeguards</h4>
                <p className="text-gray-700 mb-2">
                  We ensure adequate protection through:
                </p>
                <ul className="text-gray-700 space-y-1 ml-4">
                  <li>• Standard contractual clauses</li>
                  <li>• Data processing agreements</li>
                  <li>• Adequacy decisions where available</li>
                  <li>• Binding corporate rules</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">9. Updates to This Policy</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              We may update this Privacy Policy from time to time. When we do, we will:
            </p>
            <ul className="text-gray-700 space-y-1 ml-4 mb-4">
              <li>• Post the updated policy on our website</li>
              <li>• Update the "Last Modified" date</li>
              <li>• Notify you of significant changes via email</li>
              <li>• Provide a summary of changes when applicable</li>
            </ul>
            <p className="text-gray-700">
              Your continued use of our service after any changes indicates your acceptance of the updated policy.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">10. Contact Us</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">
              If you have questions about this Privacy Policy or our data practices, please contact us:
            </p>
            <div className="space-y-2">
              <div className="flex items-center">
                <Mail className="h-4 w-4 text-gray-500 mr-2" />
                <span className="text-gray-700">privacy@vesselguard.com</span>
              </div>
              <div className="flex items-center">
                <Globe className="h-4 w-4 text-gray-500 mr-2" />
                <span className="text-gray-700">https://vesselguard.com/privacy</span>
              </div>
            </div>
            
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Data Protection Officer</h4>
              <p className="text-sm text-gray-700">
                For EU residents, you can also contact our Data Protection Officer at:
              </p>
              <div className="flex items-center text-sm text-gray-700 mt-1">
                <Mail className="h-4 w-4 mr-1" />
                dpo@vesselguard.com
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Footer */}
      <div className="text-center border-t pt-6">
        <p className="text-sm text-gray-500 mb-4">
          This Privacy Policy is effective as of January 15, 2024.
        </p>
        <div className="flex justify-center space-x-4">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Download PDF
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Cookie Settings
          </Button>
          <Button variant="outline" size="sm">
            <ExternalLink className="h-4 w-4 mr-2" />
            Data Request
          </Button>
        </div>
      </div>
    </div>
  )
}
