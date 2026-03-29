import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Loader, AlertCircle } from 'lucide-react'
import { authAPI } from '../api/client'
import { useAuthStore } from '../stores/authStore'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { setTokens, setUser, logout } = useAuthStore()

  // Clear invalid session data on page load
  useEffect(() => {
    // Check if we have stored tokens but can't use them
    const storedToken = localStorage.getItem('accessToken')
    if (storedToken && !storedToken.includes('.')) {
      // Token format is invalid - clear everything
      console.warn('[LOGIN] Invalid token format detected, clearing storage')
      logout()
    }
  }, [logout])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      // Validate input
      if (!username.trim() || !password.trim()) {
        setError('Username and password are required')
        setIsLoading(false)
        return
      }

      // Additional validation - ensure strings
      if (typeof username !== 'string' || typeof password !== 'string') {
        setError('Invalid input - please refresh the page and try again')
        setIsLoading(false)
        return
      }

      console.log('[LOGIN] Form values:', { username: username, password: '***' })
      const response = await authAPI.login(username.trim(), password)
      console.log('[LOGIN] Login response:', response.data)
      const { access_token, refresh_token } = response.data
      
      setTokens(access_token, refresh_token)
      
      // Fetch user info
      const userResponse = await authAPI.getCurrentUser()
      setUser(userResponse.data)
      
      // Redirect admin users to admin panel
      if (username === 'admin' || userResponse.data.email === 'ravi.chudgar@gmail.com') {
        navigate('/admin')
      } else {
        navigate('/dashboard')
      }
    } catch (err) {
      console.error('[LOGIN] Error:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message,
        code: err.code
      })
      
      const detail = err.response?.data?.detail
      let errorMessage = 'Login failed'
      
      if (Array.isArray(detail)) {
        // Handle validation errors array (Pydantic)
        errorMessage = detail.map(d => d.msg || d.toString()).join(', ')
      } else if (typeof detail === 'string') {
        errorMessage = detail
      } else if (err.response?.data) {
        errorMessage = JSON.stringify(err.response.data)
      } else if (err.message) {
        errorMessage = err.message
      }
      
      // Help message for validation errors
      if (err.response?.status === 422) {
        errorMessage += '. Please check your input and try again. If the error persists, refresh the page.'
      }
      
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-800 flex items-center justify-center px-4">
      <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl p-8 sm:p-10 max-w-md w-full slide-up">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-300">
            <span className="font-extrabold text-white text-2xl">CV</span>
          </div>
          <h1 className="text-3xl font-extrabold bg-gradient-to-r from-indigo-700 to-purple-600 bg-clip-text text-transparent">CV Tailor</h1>
          <p className="text-gray-500 mt-2 text-sm">Intelligent CV Tailoring</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold mb-2 text-gray-700">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2 text-gray-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              required
            />
          </div>

          {error && (
            <div className="p-3.5 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm flex items-start gap-2">
              <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-indigo-200 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader size={18} className="animate-spin" />
                Logging in...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <p className="text-center text-gray-500 mt-6 text-sm">
          Don't have an account?{' '}
          <Link to="/register" className="text-indigo-600 font-semibold hover:text-purple-600 transition-colors">
            Register here
          </Link>
        </p>
      </div>
    </div>
  )
}
