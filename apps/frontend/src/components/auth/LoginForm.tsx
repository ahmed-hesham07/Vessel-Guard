'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/auth-context'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Shield, Eye, EyeOff, Loader2 } from 'lucide-react'
import { Checkbox } from '@/components/ui/checkbox'

interface LoginFormProps {
  onSuccess?: () => void
  className?: string
}

interface FormErrors {
  email?: string
  password?: string
}

export default function LoginForm({ onSuccess, className }: LoginFormProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [formErrors, setFormErrors] = useState<FormErrors>({})
  const [isLoading, setIsLoading] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  
  const { login } = useAuth()

  // Load remembered email on component mount
  useEffect(() => {
    const rememberedEmail = localStorage.getItem('remembered_email')
    if (rememberedEmail) {
      setEmail(rememberedEmail)
      setRememberMe(true)
    }
  }, [])

  // Clear error when user starts typing
  useEffect(() => {
    if (error && (email || password)) {
      setError('')
    }
  }, [email, password, error])

  // Store email in localStorage when remember me is checked
  useEffect(() => {
    if (rememberMe && email) {
      localStorage.setItem('remembered_email', email)
    } else if (!rememberMe) {
      localStorage.removeItem('remembered_email')
    }
  }, [rememberMe, email])

  const validateForm = (): boolean => {
    const errors: FormErrors = {}
    
    if (!email) {
      errors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Please enter a valid email address'
    }
    
    if (!password) {
      errors.password = 'Password is required'
    } else if (password.length < 6) {
      errors.password = 'Password must be at least 6 characters'
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
      await login(email, password)
      setSuccessMessage('Login successful!')
      onSuccess?.()
    } catch (error) {
      if (error instanceof Error) {
        if (error.message.includes('Invalid credentials')) {
          setError('Invalid credentials')
        } else if (error.message.includes('network') || error.message.includes('fetch')) {
          setError('Network error. Please try again.')
        } else {
          setError(error.message)
        }
      } else {
        setError('Login failed. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value)
    if (formErrors.email) {
      setFormErrors(prev => ({ ...prev, email: undefined }))
    }
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value)
    if (formErrors.password) {
      setFormErrors(prev => ({ ...prev, password: undefined }))
    }
  }

  return (
    <div className={`max-w-md w-full space-y-8 ${className || ''}`}>
      <div className="text-center">
        <div className="flex justify-center">
          <Shield className="h-12 w-12 text-primary-600" />
        </div>
        <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
          Sign in to Vessel Guard
        </h2>
        <p className="mt-2 text-sm text-gray-600">
          Professional vessel inspection and compliance management
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Welcome Back</CardTitle>
          <CardDescription>
            Sign in to your account to continue
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
              <div>
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={handleEmailChange}
                  required
                  disabled={isLoading}
                  placeholder="Enter your email"
                  className="mt-1"
                  aria-required="true"
                  aria-describedby={formErrors.email ? 'email-error' : undefined}
                />
                {formErrors.email && (
                  <div id="email-error" className="text-sm text-red-600 mt-1">
                    {formErrors.email}
                  </div>
                )}
              </div>

              <div>
                <Label htmlFor="password">Password</Label>
                <div className="relative mt-1">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={handlePasswordChange}
                    required
                    disabled={isLoading}
                    placeholder="Enter your password"
                    className="pr-10"
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
                  <div id="password-error" className="text-sm text-red-600 mt-1">
                    {formErrors.password}
                  </div>
                )}
              </div>

              <div className="flex items-center">
                <Checkbox
                  id="remember-me"
                  checked={rememberMe}
                  onCheckedChange={(checked) => setRememberMe(checked as boolean)}
                  disabled={isLoading}
                />
                <Label htmlFor="remember-me" className="ml-2 text-sm">
                  Remember me
                </Label>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
