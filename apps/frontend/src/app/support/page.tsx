'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  MessageSquare,
  Send,
  Clock,
  CheckCircle,
  X
} from 'lucide-react'
import LandingNavbar from '@/components/landing-navbar'
import Footer from '@/components/footer'
import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'

// API fetch helper (replace with your real API service or fetch wrapper)
interface Ticket {
  id: number | string;
  subject: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: 'technical' | 'billing' | 'general' | 'feature_request';
  description: string;
  created_at: string;
  updated_at: string;
}

interface FetchTicketsParams {
  token?: string;
  search?: string;
  status?: string;
  priority?: string;
  category?: string;
  skip?: number;
  limit?: number;
}

async function fetchTickets({ token, search, status, priority, category, skip = 0, limit = 20 }: FetchTicketsParams): Promise<{ items: Ticket[] }> {
  const params = new URLSearchParams()
  if (search) params.append('search', search)
  if (status) params.append('status', status)
  if (priority) params.append('priority', priority)
  if (category) params.append('category', category)
  params.append('skip', skip.toString())
  params.append('limit', limit.toString())
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/tickets?${params.toString()}`, {
    headers: token ? { 
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    } : { 'Content-Type': 'application/json' }
  })
  if (!res.ok) throw new Error('Failed to fetch tickets')
  return res.json()
}

const statusColors = {
  open: 'bg-blue-900/50 text-blue-300 border border-blue-700',
  in_progress: 'bg-yellow-900/50 text-yellow-300 border border-yellow-700',
  resolved: 'bg-green-900/50 text-green-300 border border-green-700',
  closed: 'bg-gray-900/50 text-gray-300 border border-gray-700'
}

const priorityColors = {
  low: 'bg-green-900/50 text-green-300 border border-green-700',
  medium: 'bg-yellow-900/50 text-yellow-300 border border-yellow-700',
  high: 'bg-orange-900/50 text-orange-300 border border-orange-700',
  urgent: 'bg-red-900/50 text-red-300 border border-red-700'
}

export default function SupportPage() {
  const { token, isAuthenticated } = useAuth()
  const router = useRouter()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [priorityFilter, setPriorityFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createForm, setCreateForm] = useState({ subject: '', category: '', priority: '', description: '' })
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState('')
  const [createSuccess, setCreateSuccess] = useState(false)

  // Fetch tickets from backend
  useEffect(() => {
    // Only fetch tickets if user is authenticated
    if (!isAuthenticated || !token) {
      setTickets([])
      return
    }

    setLoading(true)
    setError('')
    fetchTickets({
      token: token || undefined,
      search: searchTerm,
      status: statusFilter,
      priority: priorityFilter,
      category: categoryFilter
    })
      .then(data => setTickets(data.items || []))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [searchTerm, statusFilter, priorityFilter, categoryFilter, token, isAuthenticated])

  // Stats (replace with real stats from backend if available)
  const stats = [
    { label: 'Avg. Response Time', value: '1.2h', icon: <Clock className="h-5 w-5 text-blue-400" /> },
    { label: 'Tickets Resolved', value: '98%', icon: <CheckCircle className="h-5 w-5 text-green-400" /> },
    { label: 'Satisfaction Rate', value: '97%', icon: <MessageSquare className="h-5 w-5 text-purple-400" /> },
  ]

  // Compliance badges (replace with real ones if available)
  const compliance = [
    { label: 'SOC2', color: 'bg-blue-800 text-blue-200' },
    { label: 'ISO 27001', color: 'bg-green-800 text-green-200' },
    { label: 'GDPR', color: 'bg-purple-800 text-purple-200' },
  ]

  // Authentication required component
  const renderAuthRequired = () => (
    <div className="space-y-6">
      <Card className="dark-card border-gray-700">
        <CardContent className="p-8 text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="h-8 w-8 text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-100 mb-2">Login Required for Support</h3>
            <p className="text-gray-300 mb-6">
              To access our support system and create tickets, you need to be logged in to your account.
              This ensures we can track your tickets and provide personalized assistance.
            </p>
          </div>
          
          <div className="space-y-4">
            <Button 
              className="w-full dark-button-primary"
              onClick={() => router.push('/login')}
            >
              <Send className="h-4 w-4 mr-2" />
              Login to Access Support
            </Button>
            
            <div className="text-sm text-gray-400">
              Don't have an account? {' '}
              <button 
                onClick={() => router.push('/register')}
                className="text-blue-400 hover:text-blue-300 underline"
              >
                Sign up here
              </button>
            </div>
          </div>
          
          <div className="mt-8 pt-6 border-t border-gray-700">
            <h4 className="text-sm font-medium text-gray-300 mb-3">Why do I need to login?</h4>
            <div className="space-y-2 text-xs text-gray-400">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-green-400" />
                <span>Track your support tickets and their status</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-green-400" />
                <span>Receive updates and notifications</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-green-400" />
                <span>Access your account-specific information</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-green-400" />
                <span>Ensure secure and personalized support</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  // Ticket list UI (for authenticated users)
  const renderTickets = () => (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center gap-4 mb-4">
        <Input
          placeholder="Search tickets..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          className="bg-gray-800 border-gray-700 text-gray-100 placeholder:text-gray-400 md:w-64"
        />
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-800 text-gray-100"
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
        <select
          value={priorityFilter}
          onChange={e => setPriorityFilter(e.target.value)}
          className="px-3 py-2 border border-gray-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-800 text-gray-100"
        >
          <option value="">All Priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
        <select
          value={categoryFilter}
          onChange={e => setCategoryFilter(e.target.value)}
          className="px-3 py-2 border border-gray-700 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-800 text-gray-100"
        >
          <option value="">All Categories</option>
          <option value="technical">Technical</option>
          <option value="billing">Billing</option>
          <option value="general">General</option>
          <option value="feature_request">Feature Request</option>
        </select>
        <Button className="ml-auto dark-button-primary" onClick={() => setShowCreateModal(true)}>
          <Send className="h-4 w-4 mr-2" />
          New Ticket
        </Button>
      </div>
      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading tickets...</div>
      ) : error ? (
        <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>
      ) : tickets.length === 0 ? (
        <div className="text-center text-gray-400 py-12">No tickets found.</div>
      ) : (
        <div className="space-y-4">
          {tickets.map((ticket: Ticket) => (
            <Card key={ticket.id} className="dark-card border-gray-700 hover:shadow-md transition-shadow cursor-pointer" onClick={() => setSelectedTicket(ticket)}>
              <CardContent className="p-4 flex flex-col md:flex-row md:items-center md:justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="font-mono text-sm font-medium text-gray-300">#{ticket.id}</span>
                    <Badge className={(statusColors as any)[ticket.status]}>{ticket.status}</Badge>
                    <Badge className={(priorityColors as any)[ticket.priority]}>{ticket.priority}</Badge>
                    <Badge variant="outline" className="border-gray-600 text-gray-300">{ticket.category}</Badge>
                  </div>
                  <h4 className="font-medium text-gray-100 mb-1 truncate">{ticket.subject}</h4>
                  <div className="flex items-center space-x-4 text-xs text-gray-400">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      Created {new Date(ticket.created_at).toLocaleDateString()}
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Updated {new Date(ticket.updated_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <Button variant="outline" size="sm" className="dark-button-outline mt-4 md:mt-0 md:ml-6" onClick={e => { e.stopPropagation(); setSelectedTicket(ticket); }}>
                  View Details
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )

  // Ticket details modal
  const renderTicketDetails = () => (
    selectedTicket && (
      <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
        <div className="w-full max-w-lg bg-gray-900 border border-gray-700 rounded-xl shadow-lg p-6 relative">
          <button className="absolute top-4 right-4 text-gray-400 hover:text-gray-100" onClick={() => setSelectedTicket(null)}>
            <X className="h-5 w-5" />
          </button>
          <h2 className="text-2xl font-bold text-gray-100 mb-2">{selectedTicket.subject}</h2>
          <div className="flex items-center space-x-2 mb-4">
            <Badge className={(statusColors as any)[selectedTicket.status]}>{selectedTicket.status}</Badge>
            <Badge className={(priorityColors as any)[selectedTicket.priority]}>{selectedTicket.priority}</Badge>
            <Badge variant="outline" className="border-gray-600 text-gray-300">{selectedTicket.category}</Badge>
          </div>
          <p className="text-gray-300 mb-4">{selectedTicket.description}</p>
          <div className="flex items-center space-x-4 text-xs text-gray-400 mb-4">
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              Created {new Date(selectedTicket.created_at).toLocaleDateString()}
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 mr-1" />
              Updated {new Date(selectedTicket.updated_at).toLocaleDateString()}
            </div>
          </div>
          <Button className="w-full dark-button-outline mt-4" onClick={() => setSelectedTicket(null)}>
            Close
          </Button>
        </div>
      </div>
    )
  )

  // Create ticket modal
  const renderCreateTicketModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="w-full max-w-lg bg-gray-900 border border-gray-700 rounded-xl shadow-lg p-6 relative">
        <button className="absolute top-4 right-4 text-gray-400 hover:text-gray-100" onClick={() => setShowCreateModal(false)}>
          <X className="h-5 w-5" />
        </button>
        <h2 className="text-2xl font-bold text-gray-100 mb-4">Create Support Ticket</h2>
        {createError && <Alert variant="destructive"><AlertDescription>{createError}</AlertDescription></Alert>}
        {createSuccess ? (
          <div className="text-center text-green-400 font-semibold py-8">Ticket created successfully!</div>
        ) : (
          <form
            className="space-y-4"
            onSubmit={async e => {
              e.preventDefault()
              if (!isAuthenticated || !token) {
                setCreateError('You must be logged in to create a ticket')
                return
              }
              setCreating(true)
              setCreateError('')
              setCreateSuccess(false)
              try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/tickets`, {
                  method: 'POST',
                  headers: { 
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                  },
                  body: JSON.stringify(createForm)
                })
                if (!res.ok) throw new Error('Failed to create ticket')
                setCreateSuccess(true)
                setCreateForm({ subject: '', category: '', priority: '', description: '' })
                // Refresh tickets list
                fetchTickets({
                  token: token || undefined,
                  search: searchTerm,
                  status: statusFilter,
                  priority: priorityFilter,
                  category: categoryFilter
                })
                  .then(data => setTickets(data.items || []))
                  .catch(err => console.error('Failed to refresh tickets:', err))
              } catch (err) {
                setCreateError(err instanceof Error ? err.message : 'Unknown error')
              } finally {
                setCreating(false)
              }
            }}
          >
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Subject</label>
              <Input
                value={createForm.subject}
                onChange={e => setCreateForm(f => ({ ...f, subject: e.target.value }))}
                required
                className="bg-gray-800 border-gray-700 text-gray-100 placeholder:text-gray-400"
                placeholder="Brief description of your issue"
              />
            </div>
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-300 mb-1">Category</label>
                <select
                  value={createForm.category}
                  onChange={e => setCreateForm(f => ({ ...f, category: e.target.value }))}
                  required
                  className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-800 text-gray-100"
                >
                  <option value="">Select category</option>
                  <option value="technical">Technical</option>
                  <option value="billing">Billing</option>
                  <option value="general">General</option>
                  <option value="feature_request">Feature Request</option>
                </select>
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-300 mb-1">Priority</label>
                <select
                  value={createForm.priority}
                  onChange={e => setCreateForm(f => ({ ...f, priority: e.target.value }))}
                  required
                  className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-800 text-gray-100"
                >
                  <option value="">Select priority</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
              <textarea
                value={createForm.description}
                onChange={e => setCreateForm(f => ({ ...f, description: e.target.value }))}
                required
                rows={4}
                className="w-full px-3 py-2 border border-gray-700 rounded-md bg-gray-800 text-gray-100 placeholder:text-gray-400"
                placeholder="Please provide detailed information about your issue..."
              />
            </div>
            <div className="flex space-x-2">
              <Button type="submit" className="flex-1 dark-button-primary" disabled={creating}>
                <Send className="h-4 w-4 mr-2" />
                {creating ? 'Creating...' : 'Create Ticket'}
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowCreateModal(false)} className="dark-button-outline flex-1">
                Cancel
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  )

  return (
    <>
      <LandingNavbar />
      <div className="min-h-screen flex flex-col justify-between bg-gray-900">
        <div className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-16">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Sidebar */}
            <aside className="lg:w-64 flex-shrink-0">
              <Card className="dark-card border-gray-700 mb-6">
                <CardContent className="p-4">
                  <nav className="space-y-2">
                    {isAuthenticated ? (
                      <button
                        className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors bg-blue-900/50 text-blue-300 border border-blue-700`}
                        disabled
                      >
                        <MessageSquare className="h-4 w-4 mr-3" />
                        My Tickets
                      </button>
                    ) : (
                      <button
                        className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors bg-gray-900/50 text-gray-400 border border-gray-700 cursor-not-allowed`}
                        disabled
                      >
                        <MessageSquare className="h-4 w-4 mr-3" />
                        Login Required
                      </button>
                    )}
                  </nav>
                </CardContent>
              </Card>
              {/* Compliance/Trust Badges */}
              <div className="flex flex-wrap gap-2 justify-center mt-4">
                {compliance.map(badge => (
                  <span key={badge.label} className={`px-2 py-1 rounded text-xs font-semibold ${badge.color}`}>{badge.label}</span>
                ))}
              </div>
            </aside>
            {/* Main Content */}
            <main className="flex-1 space-y-8">
              {/* Urgency Banner */}
              <div className="rounded-lg bg-gradient-to-r from-red-900/80 to-yellow-900/80 border border-red-700 px-4 py-3 flex items-center gap-3 mb-2 animate-pulse">
                <span className="inline-block bg-red-700 text-xs font-bold px-2 py-1 rounded mr-2">URGENT</span>
                <span className="text-yellow-200 font-semibold">Experiencing a critical issue? <span className="underline">Emergency support available 24/7</span>.</span>
              </div>
              {/* Stats/Social Proof Bar */}
              <div className="flex flex-wrap gap-6 mb-4">
                {stats.map(stat => (
                  <div key={stat.label} className="flex items-center gap-2 bg-gray-800/80 border border-gray-700 rounded-lg px-4 py-2 shadow-sm">
                    {stat.icon}
                    <span className="text-lg font-bold text-gray-100">{stat.value}</span>
                    <span className="text-xs text-gray-400 font-medium ml-1">{stat.label}</span>
                  </div>
                ))}
              </div>
              <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold text-gray-100 flex items-center gap-2">
                  Support Center
                  <span className="ml-2 px-2 py-1 rounded bg-blue-900/60 text-blue-200 text-xs font-semibold">Certified Support</span>
                </h1>
                {isAuthenticated ? (
                  <Button className="dark-button-primary shadow-lg hover:scale-105 transition-transform" onClick={() => setShowCreateModal(true)}>
                    <Send className="h-4 w-4 mr-2" />
                    Get Help Now
                  </Button>
                ) : (
                  <Button className="dark-button-primary shadow-lg hover:scale-105 transition-transform" onClick={() => router.push('/login')}>
                    <Send className="h-4 w-4 mr-2" />
                    Login for Support
                  </Button>
                )}
              </div>
              {/* Value Stacking & Risk Reversal Copy */}
              <div className="mb-4">
                <div className="text-gray-300 text-sm flex flex-wrap gap-4 items-center">
                  <span className="inline-flex items-center gap-1"><CheckCircle className="h-4 w-4 text-green-400" /> All tickets receive a guaranteed response</span>
                  <span className="inline-flex items-center gap-1"><MessageSquare className="h-4 w-4 text-blue-400" /> Get help with calculations, compliance, inspections, and more</span>
                  <span className="inline-flex items-center gap-1"><Clock className="h-4 w-4 text-yellow-400" /> Fastest response if you submit now</span>
                </div>
              </div>
              {isAuthenticated ? renderTickets() : renderAuthRequired()}
            </main>
            {isAuthenticated && selectedTicket && renderTicketDetails()}
            {isAuthenticated && showCreateModal && renderCreateTicketModal()}
          </div>
        </div>
        <Footer />
      </div>
    </>
  )
}
