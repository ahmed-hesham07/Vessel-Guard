'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Shield, 
  Bell, 
  Key, 
  Activity,
  Calendar,
  Settings,
  Camera,
  Edit,
  Save,
  Check,
  AlertCircle,
  Globe,
  Briefcase,
  Award
} from 'lucide-react'

interface UserProfile {
  id: string
  name: string
  email: string
  phone: string
  title: string
  department: string
  location: string
  bio: string
  avatar: string
  role: 'admin' | 'manager' | 'inspector' | 'viewer'
  status: 'active' | 'inactive'
  joined_at: string
  last_login: string
  certifications: {
    name: string
    issuer: string
    expires_at: string
    status: 'active' | 'expired' | 'pending'
  }[]
  preferences: {
    timezone: string
    language: string
    notifications: {
      email: boolean
      sms: boolean
      push: boolean
    }
    dashboard: {
      layout: 'grid' | 'list'
      widgets: string[]
    }
  }
  security: {
    two_factor: boolean
    last_password_change: string
    login_attempts: number
    active_sessions: number
  }
}

const userProfile: UserProfile = {
  id: 'user-1',
  name: 'John Smith',
  email: 'john@atlanticmaritime.com',
  phone: '+1-555-0123',
  title: 'Senior Vessel Inspector',
  department: 'Inspection Services',
  location: 'Boston, MA',
  bio: 'Experienced marine engineer with over 15 years in vessel inspection and safety assessment.',
  avatar: '/avatars/john-smith.jpg',
  role: 'admin',
  status: 'active',
  joined_at: '2023-06-01T00:00:00Z',
  last_login: '2024-01-15T10:30:00Z',
  certifications: [
    {
      name: 'API 510 Pressure Vessel Inspector',
      issuer: 'American Petroleum Institute',
      expires_at: '2025-06-01',
      status: 'active'
    },
    {
      name: 'ASME Section VIII Inspector',
      issuer: 'American Society of Mechanical Engineers',
      expires_at: '2024-12-31',
      status: 'active'
    },
    {
      name: 'AWS Certified Welding Inspector',
      issuer: 'American Welding Society',
      expires_at: '2024-03-15',
      status: 'pending'
    }
  ],
  preferences: {
    timezone: 'America/New_York',
    language: 'English',
    notifications: {
      email: true,
      sms: false,
      push: true
    },
    dashboard: {
      layout: 'grid',
      widgets: ['recent_inspections', 'upcoming_tasks', 'vessel_status', 'reports']
    }
  },
  security: {
    two_factor: true,
    last_password_change: '2023-12-01T00:00:00Z',
    login_attempts: 0,
    active_sessions: 2
  }
}

const roleColors = {
  admin: 'bg-red-100 text-red-800',
  manager: 'bg-blue-100 text-blue-800',
  inspector: 'bg-green-100 text-green-800',
  viewer: 'bg-gray-100 text-gray-800'
}

const statusColors = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  expired: 'bg-red-100 text-red-800',
  pending: 'bg-yellow-100 text-yellow-800'
}

export default function ProfilePage() {
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
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'preferences', label: 'Preferences', icon: Settings },
    { id: 'activity', label: 'Activity', icon: Activity },
    { id: 'certifications', label: 'Certifications', icon: Award }
  ]

  const renderProfileTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Profile Information</h3>
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
            Profile updated successfully!
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Avatar</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <div className="relative w-32 h-32 mx-auto mb-4">
              <div className="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center">
                <User className="h-16 w-16 text-gray-400" />
              </div>
              {editingProfile && (
                <Button 
                  size="sm" 
                  className="absolute -bottom-2 -right-2 rounded-full w-8 h-8 p-0"
                >
                  <Camera className="h-4 w-4" />
                </Button>
              )}
            </div>
            <p className="text-sm text-gray-600 mb-2">
              {userProfile.title}
            </p>
            <Badge className={roleColors[userProfile.role]}>
              {userProfile.role}
            </Badge>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Personal Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <Input
                  value={userProfile.name}
                  readOnly={!editingProfile}
                  className={editingProfile ? '' : 'bg-gray-50'}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <Input
                  value={userProfile.email}
                  readOnly={!editingProfile}
                  className={editingProfile ? '' : 'bg-gray-50'}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone
                </label>
                <Input
                  value={userProfile.phone}
                  readOnly={!editingProfile}
                  className={editingProfile ? '' : 'bg-gray-50'}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <Input
                  value={userProfile.location}
                  readOnly={!editingProfile}
                  className={editingProfile ? '' : 'bg-gray-50'}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Title
                </label>
                <Input
                  value={userProfile.title}
                  readOnly={!editingProfile}
                  className={editingProfile ? '' : 'bg-gray-50'}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Department
                </label>
                <Input
                  value={userProfile.department}
                  readOnly={!editingProfile}
                  className={editingProfile ? '' : 'bg-gray-50'}
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bio
              </label>
              <textarea
                value={userProfile.bio}
                readOnly={!editingProfile}
                className={`w-full px-3 py-2 border border-gray-300 rounded-md ${
                  editingProfile ? '' : 'bg-gray-50'
                }`}
                rows={3}
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderSecurityTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Security Settings</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Authentication</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Two-Factor Authentication</p>
                <p className="text-sm text-gray-600">
                  Add an extra layer of security
                </p>
              </div>
              <Badge className={userProfile.security.two_factor ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                {userProfile.security.two_factor ? 'Enabled' : 'Disabled'}
              </Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Password</p>
                <p className="text-sm text-gray-600">
                  Last changed: {new Date(userProfile.security.last_password_change).toLocaleDateString()}
                </p>
              </div>
              <Button variant="outline" size="sm">
                <Key className="h-4 w-4 mr-2" />
                Change
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Account Activity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Active Sessions</p>
                <p className="text-sm text-gray-600">
                  Devices currently signed in
                </p>
              </div>
              <Badge variant="outline">
                {userProfile.security.active_sessions} active
              </Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Last Login</p>
                <p className="text-sm text-gray-600">
                  {new Date(userProfile.last_login).toLocaleString()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Failed Login Attempts</p>
                <p className="text-sm text-gray-600">
                  Recent security events
                </p>
              </div>
              <Badge variant="outline">
                {userProfile.security.login_attempts} attempts
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderCertificationsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Certifications</h3>
        <Button>
          <Award className="h-4 w-4 mr-2" />
          Add Certification
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {userProfile.certifications.map((cert, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <Award className="h-5 w-5 text-blue-500 mt-1" />
                <Badge className={statusColors[cert.status]}>
                  {cert.status}
                </Badge>
              </div>
              <h4 className="font-medium text-gray-900 mb-1">{cert.name}</h4>
              <p className="text-sm text-gray-600 mb-2">{cert.issuer}</p>
              <div className="flex items-center text-sm text-gray-500">
                <Calendar className="h-4 w-4 mr-1" />
                Expires: {new Date(cert.expires_at).toLocaleDateString()}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
          <p className="text-gray-600">
            Manage your personal information and account settings
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge className={statusColors[userProfile.status]}>
            {userProfile.status}
          </Badge>
          <Badge variant="outline">
            Joined {new Date(userProfile.joined_at).toLocaleDateString()}
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
          {activeTab === 'security' && renderSecurityTab()}
          {activeTab === 'certifications' && renderCertificationsTab()}
          {activeTab === 'preferences' && (
            <div className="text-center py-12">
              <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Preferences settings coming soon</p>
            </div>
          )}
          {activeTab === 'activity' && (
            <div className="text-center py-12">
              <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Activity log coming soon</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
