import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

const ADMIN_EMAIL = 'ravi.chudgar@gmail.com'

export default function AdminRoute({ children }) {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Only allow access if user email matches admin email or username is 'admin'
  if (!user || (user.email !== ADMIN_EMAIL && user.username !== 'admin')) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}
