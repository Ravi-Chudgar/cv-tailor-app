import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { authAPI } from './api/client'
import Header from './components/Header'
import ProtectedRoute from './components/ProtectedRoute'
import AdminRoute from './components/AdminRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import AdminPage from './pages/AdminPage'

const ADMIN_EMAIL = 'ravi.chudgar@gmail.com'

export default function App() {
  const { user, setUser, isAuthenticated, setLoading } = useAuthStore()
  const [isInitializing, setIsInitializing] = useState(true)

  useEffect(() => {
    // Try to restore user session on app load
    if (isAuthenticated && !user) {
      const loadUser = async () => {
        try {
          const response = await authAPI.getCurrentUser()
          setUser(response.data)
        } catch (err) {
          console.error('Failed to load user:', err)
        } finally {
          setIsInitializing(false)
        }
      }
      loadUser()
    } else {
      setIsInitializing(false)
    }
  }, [isAuthenticated, user, setUser])

  // Determine where to redirect authenticated users
  const getAuthenticatedRoute = () => {
    if (user && (user.email === ADMIN_EMAIL || user.username === 'admin')) {
      return '/admin'
    }
    return '/dashboard'
  }

  // Show nothing while initializing to prevent flash of wrong page
  if (isInitializing && isAuthenticated) {
    return <div className="min-h-screen bg-gray-50" />
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          {/* Admin routes */}
          <Route
            path="/admin"
            element={
              <AdminRoute>
                <AdminPage />
              </AdminRoute>
            }
          />

          {/* Redirect home to dashboard (admin can access /admin manually) */}
          <Route
            path="/"
            element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
            }
          />

          {/* Catch all other routes */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  )
}
