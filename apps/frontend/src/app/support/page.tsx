'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  HelpCircle, 
  MessageSquare, 
  Phone, 
  Mail, 
  FileText, 
  Search, 
  Clock,
  CheckCircle,
  AlertCircle,
  Book,
  Video,
  Download,
  ExternalLink,
  Send,
  Zap,
  Users,
  Shield,
  Database,
  Settings,
  BarChart
} from 'lucide-react'
import Link from 'next/link'

interface SupportTicket {
  id: string
  subject: string
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  category: 'technical' | 'billing' | 'general' | 'feature_request'
  created_at: string
  updated_at: string
  messages: number
}

interface FAQItem {
  id: string
  question: string
  answer: string
  category: string
  helpful: number
  views: number
}

const supportTickets: SupportTicket[] = [
  {
    id: 'TKT-001',
    subject: 'Unable to generate pressure vessel calculation report',
    status: 'in_progress',
    priority: 'high',
    category: 'technical',
    created_at: '2024-01-14T10:30:00Z',
    updated_at: '2024-01-15T14:20:00Z',
    messages: 3
  },
  {
    id: 'TKT-002',
    subject: 'Question about API 510 compliance features',
    status: 'resolved',
    priority: 'medium',
    category: 'general',
    created_at: '2024-01-12T09:15:00Z',
    updated_at: '2024-01-13T16:45:00Z',
    messages: 5
  },
  {
    id: 'TKT-003',
    subject: 'Request for custom inspection template',
    status: 'open',
    priority: 'low',
    category: 'feature_request',
    created_at: '2024-01-10T14:20:00Z',
    updated_at: '2024-01-10T14:20:00Z',
    messages: 1
  }
]

const faqItems: FAQItem[] = [
  {
    id: 'faq-1',
    question: 'How do I create a new vessel in the system?',
    answer: 'To create a new vessel, navigate to the Vessels section and click "Add New Vessel". Fill in the required information including vessel name, type, specifications, and certification details.',
    category: 'Getting Started',
    helpful: 45,
    views: 120
  },
  {
    id: 'faq-2',
    question: 'What pressure vessel calculation standards are supported?',
    answer: 'Our system supports ASME VIII Division 1 & 2, API 510, EN 13445, and other international pressure vessel codes. You can select the appropriate standard when creating calculations.',
    category: 'Calculations',
    helpful: 38,
    views: 95
  },
  {
    id: 'faq-3',
    question: 'How do I schedule automatic inspection reminders?',
    answer: 'In the vessel details page, go to the Maintenance section and set up inspection intervals. The system will automatically send reminders based on your schedule.',
    category: 'Inspections',
    helpful: 52,
    views: 140
  },
  {
    id: 'faq-4',
    question: 'Can I export inspection reports to PDF?',
    answer: 'Yes, all inspection reports can be exported to PDF format. Use the "Export" button in the reports section and select your preferred format.',
    category: 'Reports',
    helpful: 41,
    views: 110
  },
  {
    id: 'faq-5',
    question: 'How do I invite team members to my organization?',
    answer: 'Go to Organization Settings > Users & Roles and click "Invite User". Enter their email address and assign appropriate permissions.',
    category: 'User Management',
    helpful: 29,
    views: 75
  }
]

const resources = [
  {
    title: 'Getting Started Guide',
    description: 'Complete guide to setting up your first vessel and inspection workflow',
    type: 'guide',
    icon: Book,
    url: '/docs/getting-started'
  },
  {
    title: 'API Documentation',
    description: 'Technical documentation for integrating with our API',
    type: 'technical',
    icon: Database,
    url: '/docs/api'
  },
  {
    title: 'Video Tutorials',
    description: 'Step-by-step video guides for common tasks',
    type: 'video',
    icon: Video,
    url: '/tutorials'
  },
  {
    title: 'Calculation Examples',
    description: 'Sample calculations for different vessel types and standards',
    type: 'examples',
    icon: BarChart,
    url: '/examples'
  },
  {
    title: 'Security Best Practices',
    description: 'Guidelines for keeping your data secure',
    type: 'security',
    icon: Shield,
    url: '/docs/security'
  },
  {
    title: 'System Status',
    description: 'Real-time status of our systems and services',
    type: 'status',
    icon: Zap,
    url: 'https://status.vesselguard.com'
  }
]

const statusColors = {
  open: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  resolved: 'bg-green-100 text-green-800',
  closed: 'bg-gray-100 text-gray-800'
}

const priorityColors = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  urgent: 'bg-red-100 text-red-800'
}

export default function SupportPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showNewTicket, setShowNewTicket] = useState(false)

  const filteredFAQs = faqItems.filter(item => {
    const matchesSearch = item.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.answer.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const categories = ['all', ...Array.from(new Set(faqItems.map(item => item.category)))]

  const tabs = [
    { id: 'overview', label: 'Support Overview', icon: HelpCircle },
    { id: 'tickets', label: 'My Tickets', icon: MessageSquare },
    { id: 'faq', label: 'FAQ', icon: Book },
    { id: 'resources', label: 'Resources', icon: FileText },
    { id: 'contact', label: 'Contact', icon: Phone }
  ]

  const renderOverviewTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <MessageSquare className="h-8 w-8 text-blue-500 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {supportTickets.length}
                </p>
                <p className="text-sm text-gray-600">Open Tickets</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-green-500 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">2.4h</p>
                <p className="text-sm text-gray-600">Avg Response Time</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-purple-500 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">98%</p>
                <p className="text-sm text-gray-600">Resolution Rate</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button 
                className="w-full justify-start" 
                variant="outline"
                onClick={() => setShowNewTicket(true)}
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Create Support Ticket
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="#faq">
                  <Book className="h-4 w-4 mr-2" />
                  Browse FAQ
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/docs">
                  <FileText className="h-4 w-4 mr-2" />
                  View Documentation
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="mailto:support@vesselguard.com">
                  <Mail className="h-4 w-4 mr-2" />
                  Email Support
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Tickets</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {supportTickets.slice(0, 3).map((ticket) => (
                <div key={ticket.id} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">{ticket.id}</span>
                    <Badge className={statusColors[ticket.status]}>
                      {ticket.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">{ticket.subject}</p>
                  <p className="text-xs text-gray-500">
                    Updated {new Date(ticket.updated_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderTicketsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Support Tickets</h3>
        <Button onClick={() => setShowNewTicket(true)}>
          <MessageSquare className="h-4 w-4 mr-2" />
          New Ticket
        </Button>
      </div>

      <div className="space-y-4">
        {supportTickets.map((ticket) => (
          <Card key={ticket.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="font-mono text-sm font-medium">{ticket.id}</span>
                    <Badge className={statusColors[ticket.status]}>
                      {ticket.status}
                    </Badge>
                    <Badge className={priorityColors[ticket.priority]}>
                      {ticket.priority}
                    </Badge>
                    <Badge variant="outline">
                      {ticket.category}
                    </Badge>
                  </div>
                  <h4 className="font-medium text-gray-900 mb-2">{ticket.subject}</h4>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      Created {new Date(ticket.created_at).toLocaleDateString()}
                    </div>
                    <div className="flex items-center">
                      <MessageSquare className="h-4 w-4 mr-1" />
                      {ticket.messages} messages
                    </div>
                  </div>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <Link href={`/support/tickets/${ticket.id}`}>
                    View Details
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )

  const renderFAQTab = () => (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search FAQ..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {categories.map(category => (
            <option key={category} value={category}>
              {category === 'all' ? 'All Categories' : category}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-4">
        {filteredFAQs.map((item) => (
          <Card key={item.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-medium text-gray-900">{item.question}</h4>
                <Badge variant="outline">{item.category}</Badge>
              </div>
              <p className="text-sm text-gray-600 mb-3">{item.answer}</p>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <div className="flex items-center">
                  <CheckCircle className="h-4 w-4 mr-1 text-green-500" />
                  {item.helpful} helpful
                </div>
                <div className="flex items-center">
                  <HelpCircle className="h-4 w-4 mr-1" />
                  {item.views} views
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )

  const renderResourcesTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Help Resources</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {resources.map((resource, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start">
                <resource.icon className="h-6 w-6 text-blue-500 mr-3 mt-1" />
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">{resource.title}</h4>
                  <p className="text-sm text-gray-600 mb-3">{resource.description}</p>
                  <Button variant="outline" size="sm" asChild>
                    <Link href={resource.url}>
                      View Resource
                      <ExternalLink className="h-3 w-3 ml-1" />
                    </Link>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )

  const renderContactTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Contact Information</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Support Channels</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center">
              <Mail className="h-5 w-5 text-blue-500 mr-3" />
              <div>
                <p className="font-medium">Email Support</p>
                <p className="text-sm text-gray-600">support@vesselguard.com</p>
                <p className="text-xs text-gray-500">Response within 24 hours</p>
              </div>
            </div>
            <div className="flex items-center">
              <Phone className="h-5 w-5 text-green-500 mr-3" />
              <div>
                <p className="font-medium">Phone Support</p>
                <p className="text-sm text-gray-600">+1-800-VESSEL-1</p>
                <p className="text-xs text-gray-500">Mon-Fri 9AM-6PM EST</p>
              </div>
            </div>
            <div className="flex items-center">
              <MessageSquare className="h-5 w-5 text-purple-500 mr-3" />
              <div>
                <p className="font-medium">Live Chat</p>
                <p className="text-sm text-gray-600">Available in-app</p>
                <p className="text-xs text-gray-500">Mon-Fri 9AM-6PM EST</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Business Hours</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Monday - Friday</span>
              <span className="text-sm font-medium">9:00 AM - 6:00 PM EST</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Saturday</span>
              <span className="text-sm font-medium">10:00 AM - 4:00 PM EST</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Sunday</span>
              <span className="text-sm font-medium">Closed</span>
            </div>
            <div className="mt-4 p-3 bg-yellow-50 rounded-md">
              <p className="text-sm text-yellow-800">
                Emergency support available 24/7 for critical issues
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Support Center</h1>
          <p className="text-gray-600">
            Get help with Vessel Guard and find answers to common questions
          </p>
        </div>
        <Button onClick={() => setShowNewTicket(true)}>
          <MessageSquare className="h-4 w-4 mr-2" />
          New Ticket
        </Button>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-64">
          <Card>
            <CardContent className="p-4">
              <nav className="space-y-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <tab.icon className="h-4 w-4 mr-3" />
                    {tab.label}
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'tickets' && renderTicketsTab()}
          {activeTab === 'faq' && renderFAQTab()}
          {activeTab === 'resources' && renderResourcesTab()}
          {activeTab === 'contact' && renderContactTab()}
        </div>
      </div>

      {/* New Ticket Modal */}
      {showNewTicket && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-base">Create Support Ticket</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subject
                </label>
                <Input placeholder="Brief description of your issue" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option>Technical Issue</option>
                  <option>Billing Question</option>
                  <option>General Support</option>
                  <option>Feature Request</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option>Low</option>
                  <option>Medium</option>
                  <option>High</option>
                  <option>Urgent</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  rows={4}
                  placeholder="Please provide detailed information about your issue..."
                />
              </div>
              <div className="flex space-x-2">
                <Button className="flex-1">
                  <Send className="h-4 w-4 mr-2" />
                  Create Ticket
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowNewTicket(false)}
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
