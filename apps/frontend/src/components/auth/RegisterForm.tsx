'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Shield, Eye, EyeOff, Loader2 } from 'lucide-react'

interface RegisterFormProps {
  onSuccess?: () => void
  className?: string
}

interface FormErrors {
  email?: string
  password?: string
  confirmPassword?: string
  first_name?: string
  last_name?: string
  phone?: string
  job_title?: string
  department?: string
  organization_name?: string
}

interface FormData {
  email: string
  password: string
  confirmPassword: string
  first_name: string
  last_name: string
  phone: string
  job_title: string
  department: string
  organization_name: string
}

export default function RegisterForm({ onSuccess, className }: RegisterFormProps) {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: '',
    job_title: '',
    department: '',
    organization_name: ''
  })
  
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState('')
  const [formErrors, setFormErrors] = useState<FormErrors>({})
  const [isLoading, setIsLoading] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  
  const { register } = useAuth()

  // Clear error when user starts typing
  useEffect(() => {
    if (error && Object.values(formData).some(value => value)) {
      setError('')
    }
  }, [formData, error])

  const validateForm = (): boolean => {
    const errors: FormErrors = {}
    
    if (!formData.email) {
      errors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address'
    }
    
    if (!formData.password) {
      errors.password = 'Password is required'
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters'
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      errors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    }

    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password'
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match'
    }

    if (!formData.first_name) {
      errors.first_name = 'First name is required'
    } else if (formData.first_name.length < 2) {
      errors.first_name = 'First name must be at least 2 characters'
    }

    if (!formData.last_name) {
      errors.last_name = 'Last name is required'
    } else if (formData.last_name.length < 2) {
      errors.last_name = 'Last name must be at least 2 characters'
    }

    if (formData.phone && !/^\+?[\d\s\-\(\)]+$/.test(formData.phone)) {
      errors.phone = 'Please enter a valid phone number'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccessMessage('')
    
    if (!validateForm()) {
      return
    }

    setIsLoading(true)

    try {
      const registerData = {
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone || undefined,
        job_title: formData.job_title || undefined,
        department: formData.department || undefined,
        organization_name: formData.organization_name || undefined
      }

      await register(registerData)
      setSuccessMessage('Registration successful! Redirecting to dashboard...')
      onSuccess?.()
    } catch (error) {
      if (error instanceof Error) {
        if (error.message.includes('already exists') || error.message.includes('already registered')) {
          setError('An account with this email already exists. Please try logging in instead.')
        } else if (error.message.includes('network') || error.message.includes('fetch')) {
          setError('Network error. Please check your connection and try again.')
        } else {
          setError(error.message)
        }
      } else {
        setError('Registration failed. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (field: keyof FormData) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear field-specific error when user starts typing
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <div className={`max-w-md w-full space-y-8 ${className || ''}`}>
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-gray-100">Create Your Account</CardTitle>
          <CardDescription className="text-gray-400">
            Join Vessel Guard to manage your engineering compliance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {successMessage && (
              <Alert>
                <AlertDescription className="text-green-700">{successMessage}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-4">
              {/* Name Fields */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="first_name" className="text-gray-300">First Name</Label>
                  <Input
                    id="first_name"
                    type="text"
                    value={formData.first_name}
                    onChange={handleInputChange('first_name')}
                    required
                    disabled={isLoading}
                    placeholder="John"
                    className="mt-1 bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                    aria-required="true"
                    aria-describedby={formErrors.first_name ? 'first_name-error' : undefined}
                  />
                  {formErrors.first_name && (
                    <div id="first_name-error" className="text-sm text-red-400 mt-1">
                      {formErrors.first_name}
                    </div>
                  )}
                </div>

                <div>
                  <Label htmlFor="last_name" className="text-gray-300">Last Name</Label>
                  <Input
                    id="last_name"
                    type="text"
                    value={formData.last_name}
                    onChange={handleInputChange('last_name')}
                    required
                    disabled={isLoading}
                    placeholder="Doe"
                    className="mt-1 bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                    aria-required="true"
                    aria-describedby={formErrors.last_name ? 'last_name-error' : undefined}
                  />
                  {formErrors.last_name && (
                    <div id="last_name-error" className="text-sm text-red-400 mt-1">
                      {formErrors.last_name}
                    </div>
                  )}
                </div>
              </div>

              {/* Email */}
              <div>
                <Label htmlFor="email" className="text-gray-300">Email address</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange('email')}
                  required
                  disabled={isLoading}
                  placeholder="john.doe@company.com"
                  className="mt-1 bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                  aria-required="true"
                  aria-describedby={formErrors.email ? 'email-error' : undefined}
                />
                {formErrors.email && (
                  <div id="email-error" className="text-sm text-red-400 mt-1">
                    {formErrors.email}
                  </div>
                )}
              </div>

              {/* Password */}
              <div>
                <Label htmlFor="password" className="text-gray-300">Password</Label>
                <div className="relative mt-1">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange('password')}
                    required
                    disabled={isLoading}
                    placeholder="Create a strong password"
                    className="pr-10 bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                    aria-required="true"
                    aria-describedby={formErrors.password ? 'password-error' : undefined}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                {formErrors.password && (
                  <div id="password-error" className="text-sm text-red-400 mt-1">
                    {formErrors.password}
                  </div>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <Label htmlFor="confirmPassword" className="text-gray-300">Confirm Password</Label>
                <div className="relative mt-1">
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={handleInputChange('confirmPassword')}
                    required
                    disabled={isLoading}
                    placeholder="Confirm your password"
                    className="pr-10 bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                    aria-required="true"
                    aria-describedby={formErrors.confirmPassword ? 'confirmPassword-error' : undefined}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                {formErrors.confirmPassword && (
                  <div id="confirmPassword-error" className="text-sm text-red-400 mt-1">
                    {formErrors.confirmPassword}
                  </div>
                )}
              </div>

              {/* Optional Fields */}
              <div>
                <Label htmlFor="phone" className="text-gray-300">Phone (Optional)</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={handleInputChange('phone')}
                  disabled={isLoading}
                  placeholder="+1 (555) 123-4567"
                  className="mt-1 bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                  aria-describedby={formErrors.phone ? 'phone-error' : undefined}
                />
                {formErrors.phone && (
                  <div id="phone-error" className="text-sm text-red-400 mt-1">
                    {formErrors.phone}
                  </div>
                )}
              </div>

              <div>
                <Label htmlFor="job_title" className="text-gray-300">Job Title (Optional)</Label>
                <Input
                  id="job_title"
                  type="text"
                  value={formData.job_title}
                  onChange={handleInputChange('job_title')}
                  disabled={isLoading}
                  placeholder="Marine Engineer"
                  className="mt-1 bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                />
              </div>

              <div>
                <Label htmlFor="department" className="text-gray-300">Department (Optional)</Label>
                <Input
                  id="department"
                  type="text"
                  value={formData.department}
                  onChange={handleInputChange('department')}
                  disabled={isLoading}
                  placeholder="Engineering"
                  className="mt-1 bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                />
              </div>

              <div>
                <Label htmlFor="organization_name" className="text-gray-300">Organization (Optional)</Label>
                <Input
                  id="organization_name"
                  type="text"
                  value={formData.organization_name}
                  onChange={handleInputChange('organization_name')}
                  disabled={isLoading}
                  placeholder="Your Company Name"
                  className="mt-1 bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                />
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
