'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Building, 
  Users, 
  Shield, 
  Globe, 
  CreditCard, 
  Bell, 
  FileText,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Crown,
  Settings,
  Plus,
  Trash2,
  Edit,
  Check,
  X,
  Save,
  UserPlus,
  AlertCircle,
  Lock
} from 'lucide-react'

interface Organization {
  id: string
  name: string
  type: 'enterprise' | 'professional' | 'standard'
  industry: string
  description: string
  website: string
  email: string
  phone: string
  address: {
    street: string
    city: string
    state: string
    country: string
    zip: string
  }
  subscription: {
    plan: string
    status: 'active' | 'canceled' | 'expired'
    expires_at: string
    features: string[]
  }
  settings: {
    notifications: {
      email: boolean
      sms: boolean
      slack: boolean
    }
    security: {
      two_factor: boolean
      sso: boolean
      password_policy: 'basic' | 'strong' | 'custom'
    }
    api: {
      enabled: boolean
      rate_limit: number
      webhooks: boolean
    }
    branding: {
      logo: string
      colors: {
        primary: string
        secondary: string
      }
    }
  }
}

interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'manager' | 'inspector' | 'viewer'
  status: 'active' | 'inactive' | 'pending'
  last_login: string
  created_at: string
}

const organization: Organization = {
  id: 'org-1',
  name: 'Atlantic Maritime Solutions',
  type: 'enterprise',
  industry: 'Marine Engineering',
  description: 'Leading provider of vessel inspection and engineering solutions for the maritime industry.',
  website: 'https://atlanticmaritime.com',
  email: 'info@atlanticmaritime.com',
  phone: '+1-555-0123',
  address: {
    street: '123 Harbor Street',
    city: 'Boston',
    state: 'MA',
    country: 'United States',
    zip: '02101'
  },
  subscription: {
    plan: 'Enterprise',
    status: 'active',
    expires_at: '2024-12-31',
    features: ['Unlimited vessels', 'Advanced reporting', 'API access', 'SSO', 'Custom branding']
  },
  settings: {
    notifications: {
      email: true,
      sms: false,
      slack: true
    },
    security: {
      two_factor: true,
      sso: true,
      password_policy: 'strong'
    },
    api: {
      enabled: true,
      rate_limit: 1000,
      webhooks: true
    },
    branding: {
      logo: '/logo.png',
      colors: {
        primary: '#2563eb',
        secondary: '#64748b'
      }
    }
  }
}

const users: User[] = [
  {
    id: 'user-1',
    name: 'John Smith',
    email: 'john@atlanticmaritime.com',
    role: 'admin',
    status: 'active',
    last_login: '2024-01-15T10:30:00Z',
    created_at: '2023-06-01T00:00:00Z'
  },
  {
    id: 'user-2',
    name: 'Sarah Johnson',
    email: 'sarah@atlanticmaritime.com',
    role: 'manager',
    status: 'active',
    last_login: '2024-01-15T09:15:00Z',
    created_at: '2023-08-15T00:00:00Z'
  },
  {
    id: 'user-3',
    name: 'Mike Wilson',
    email: 'mike@atlanticmaritime.com',
    role: 'inspector',
    status: 'active',
    last_login: '2024-01-14T16:45:00Z',
    created_at: '2023-09-01T00:00:00Z'
  },
  {
    id: 'user-4',
    name: 'Emily Davis',
    email: 'emily@atlanticmaritime.com',
    role: 'viewer',
    status: 'pending',
    last_login: '',
    created_at: '2024-01-10T00:00:00Z'
  }
]

const roleColors = {
  admin: 'bg-red-100 text-red-800',
  manager: 'bg-blue-100 text-blue-800',
  inspector: 'bg-green-100 text-green-800',
  viewer: 'bg-gray-100 text-gray-800'
}

const statusColors = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  pending: 'bg-yellow-100 text-yellow-800',
  canceled: 'bg-red-100 text-red-800',
  expired: 'bg-red-100 text-red-800'
}

const planColors = {
  enterprise: 'bg-purple-100 text-purple-800',
  professional: 'bg-blue-100 text-blue-800',
  standard: 'bg-green-100 text-green-800'
}

export default function OrganizationSettingsPage() {
  const [activeTab, setActiveTab] = useState('profile')
  const [editingProfile, setEditingProfile] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)

  const handleSave = async () => {
    setIsLoading(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsLoading(false)
    setEditingProfile(false)
    setShowSuccess(true)
    setTimeout(() => setShowSuccess(false), 3000)
  }

  const tabs = [
    { id: 'profile', label: 'Organization Profile', icon: Building },
    { id: 'users', label: 'Users & Roles', icon: Users },
    { id: 'subscription', label: 'Subscription & Billing', icon: CreditCard },
    { id: 'security', label: 'Security Settings', icon: Shield },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'api', label: 'API Settings', icon: Settings },
    { id: 'branding', label: 'Branding', icon: FileText }
  ]

  const renderProfileTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Organization Profile</h3>
        <Button 
          onClick={() => editingProfile ? handleSave() : setEditingProfile(true)}
          disabled={isLoading}
        >
          {editingProfile ? (
            <>
              <Save className="h-4 w-4 mr-2" />
              {isLoading ? 'Saving...' : 'Save Changes'}
            </>
          ) : (
            <>
              <Edit className="h-4 w-4 mr-2" />
              Edit Profile
            </>
          )}
        </Button>
      </div>

      {showSuccess && (
        <Alert>
          <Check className="h-4 w-4" />
          <AlertDescription>
            Organization profile updated successfully!
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Organization Name
              </label>
              <Input
                value={organization.name}
                readOnly={!editingProfile}
                className={editingProfile ? '' : 'bg-gray-50'}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Industry
              </label>
              <Input
                value={organization.industry}
                readOnly={!editingProfile}
                className={editingProfile ? '' : 'bg-gray-50'}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={organization.description}
                readOnly={!editingProfile}
                className={`w-full px-3 py-2 border border-gray-300 rounded-md ${
                  editingProfile ? '' : 'bg-gray-50'
                }`}
                rows={3}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Website
              </label>
              <Input
                value={organization.website}
                readOnly={!editingProfile}
                className={editingProfile ? '' : 'bg-gray-50'}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Contact Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Mail className="h-4 w-4 inline mr-1" />
                Email
              </label>
              <Input
                value={organization.email}
                readOnly={!editingProfile}
                className={editingProfile ? '' : 'bg-gray-50'}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Phone className="h-4 w-4 inline mr-1" />
                Phone
              </label>
              <Input
                value={organization.phone}
                readOnly={!editingProfile}
                className={editingProfile ? '' : 'bg-gray-50'}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <MapPin className="h-4 w-4 inline mr-1" />
                Address
              </label>
              <div className="space-y-2">
                <Input
                  value={organization.address.street}
                  readOnly={!editingProfile}
                  className={editingProfile ? '' : 'bg-gray-50'}
                  placeholder="Street"
                />
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    value={organization.address.city}
                    readOnly={!editingProfile}
                    className={editingProfile ? '' : 'bg-gray-50'}
                    placeholder="City"
                  />
                  <Input
                    value={organization.address.state}
                    readOnly={!editingProfile}
                    className={editingProfile ? '' : 'bg-gray-50'}
                    placeholder="State"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    value={organization.address.country}
                    readOnly={!editingProfile}
                    className={editingProfile ? '' : 'bg-gray-50'}
                    placeholder="Country"
                  />
                  <Input
                    value={organization.address.zip}
                    readOnly={!editingProfile}
                    className={editingProfile ? '' : 'bg-gray-50'}
                    placeholder="ZIP"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderUsersTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Users & Roles</h3>
        <Button>
          <UserPlus className="h-4 w-4 mr-2" />
          Invite User
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-500 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">{users.length}</p>
                <p className="text-sm text-gray-600">Total Users</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-green-500 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {users.filter(u => u.status === 'active').length}
                </p>
                <p className="text-sm text-gray-600">Active Users</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Crown className="h-8 w-8 text-purple-500 mr-3" />
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {users.filter(u => u.role === 'admin').length}
                </p>
                <p className="text-sm text-gray-600">Administrators</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">User List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Name</th>
                  <th className="text-left py-2">Email</th>
                  <th className="text-left py-2">Role</th>
                  <th className="text-left py-2">Status</th>
                  <th className="text-left py-2">Last Login</th>
                  <th className="text-left py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b">
                    <td className="py-3 font-medium">{user.name}</td>
                    <td className="py-3 text-gray-600">{user.email}</td>
                    <td className="py-3">
                      <Badge className={roleColors[user.role]}>
                        {user.role}
                      </Badge>
                    </td>
                    <td className="py-3">
                      <Badge className={statusColors[user.status]}>
                        {user.status}
                      </Badge>
                    </td>
                    <td className="py-3 text-gray-600">
                      {user.last_login 
                        ? new Date(user.last_login).toLocaleDateString() 
                        : 'Never'}
                    </td>
                    <td className="py-3">
                      <div className="flex space-x-1">
                        <Button variant="outline" size="sm">
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderSubscriptionTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Subscription & Billing</h3>
        <Button>
          <CreditCard className="h-4 w-4 mr-2" />
          Manage Billing
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Current Plan</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Badge className={planColors[organization.type]}>
                  {organization.subscription.plan}
                </Badge>
                <Badge className={statusColors[organization.subscription.status]}>
                  {organization.subscription.status}
                </Badge>
              </div>
              <p className="text-sm text-gray-600">
                Expires: {new Date(organization.subscription.expires_at).toLocaleDateString()}
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-gray-900">$299</p>
              <p className="text-sm text-gray-600">per month</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Plan Features</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {organization.subscription.features.map((feature, index) => (
              <div key={index} className="flex items-center">
                <Check className="h-4 w-4 text-green-500 mr-2" />
                <span className="text-sm">{feature}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderSecurityTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Security Settings</h3>
      
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Authentication</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Two-Factor Authentication</p>
              <p className="text-sm text-gray-600">
                Require 2FA for all organization users
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Badge className={organization.settings.security.two_factor ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                {organization.settings.security.two_factor ? 'Enabled' : 'Disabled'}
              </Badge>
              <Button variant="outline" size="sm">
                Configure
              </Button>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Single Sign-On (SSO)</p>
              <p className="text-sm text-gray-600">
                Allow users to sign in with corporate credentials
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Badge className={organization.settings.security.sso ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                {organization.settings.security.sso ? 'Enabled' : 'Disabled'}
              </Badge>
              <Button variant="outline" size="sm">
                Configure
              </Button>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Password Policy</p>
              <p className="text-sm text-gray-600">
                Current policy: {organization.settings.security.password_policy}
              </p>
            </div>
            <Button variant="outline" size="sm">
              Update Policy
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Organization Settings</h1>
          <p className="text-gray-600">
            Manage your organization profile, users, and preferences
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge className={planColors[organization.type]}>
            {organization.subscription.plan}
          </Badge>
          <Badge className={statusColors[organization.subscription.status]}>
            {organization.subscription.status}
          </Badge>
        </div>
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
          {activeTab === 'profile' && renderProfileTab()}
          {activeTab === 'users' && renderUsersTab()}
          {activeTab === 'subscription' && renderSubscriptionTab()}
          {activeTab === 'security' && renderSecurityTab()}
          {activeTab === 'notifications' && (
            <div className="text-center py-12">
              <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Notification settings coming soon</p>
            </div>
          )}
          {activeTab === 'api' && (
            <div className="text-center py-12">
              <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">API settings coming soon</p>
            </div>
          )}
          {activeTab === 'branding' && (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Branding settings coming soon</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
