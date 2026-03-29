import React, { useState, useEffect } from 'react'
import { Users, Trash2, Lock, Unlock, AlertCircle, CheckCircle, Loader, Plus, Download, RefreshCw } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { useNavigate } from 'react-router-dom'
import { adminAPI } from '../api/client'
import * as XLSX from 'xlsx'

const ADMIN_EMAIL = 'ravi.chudgar@gmail.com'

export default function AdminPage() {
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [isExporting, setIsExporting] = useState(false)
  const [isAdminAuthorized, setIsAdminAuthorized] = useState(false)
  const navigate = useNavigate()
  const { user: currentUser } = useAuthStore()

  useEffect(() => {
    // Check if user is the admin
    if (!currentUser || (currentUser.email !== ADMIN_EMAIL && currentUser.username !== 'admin')) {
      setError('Unauthorized: Admin access only')
      setTimeout(() => navigate('/dashboard'), 2000)
      return
    }
    setIsAdminAuthorized(true)
    loadUsers()
  }, [currentUser, navigate])

  const loadUsers = async () => {
    try {
      setIsLoading(true)
      const response = await adminAPI.getUsers()
      setUsers(response.data.users || [])
      setError('')
    } catch (err) {
      setError('Failed to load users')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefresh = async () => {
    if (isAdminAuthorized) {
      await loadUsers()
    }
  }

  const handleDeleteUser = async (userId) => {
    try {
      await adminAPI.deleteUser(userId)
      setUsers(users.filter(u => u.user_id !== userId))
      setSuccess('User deleted successfully')
      setDeleteConfirm(null)
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to delete user')
    }
  }

  const handleToggleActive = async (userId, isActive) => {
    try {
      await adminAPI.toggleUserStatus(userId, !isActive)
      setUsers(users.map(u => 
        u.user_id === userId ? { ...u, is_active: !u.is_active } : u
      ))
      setSuccess(`User ${isActive ? 'deactivated' : 'activated'} successfully`)
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to update user status')
    }
  }

  const exportToExcel = () => {
    try {
      setIsExporting(true)
      
      // Prepare data for Excel
      const exportData = users.map(user => ({
        'User ID': user.user_id,
        'Username': user.username,
        'Email': user.email,
        'Status': user.is_active ? 'Active' : 'Inactive',
        'Created At': new Date(user.created_at).toLocaleString(),
        'Updated At': new Date(user.updated_at || user.created_at).toLocaleString(),
      }))

      // Create worksheet
      const worksheet = XLSX.utils.json_to_sheet(exportData)
      
      // Set column widths
      worksheet['!cols'] = [
        { wch: 12 },
        { wch: 20 },
        { wch: 25 },
        { wch: 10 },
        { wch: 20 },
        { wch: 20 },
      ]

      // Create workbook
      const workbook = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Users')

      // Generate filename with timestamp
      const timestamp = new Date().toISOString().slice(0, 10)
      const filename = `users_${timestamp}.xlsx`

      // Save file
      XLSX.writeFile(workbook, filename)
      setSuccess('Users exported to Excel successfully')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to export users to Excel')
      console.error(err)
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50/30">
      {!isAdminAuthorized && (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center slide-up">
            <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="text-red-600" size={32} />
            </div>
            <h1 className="text-2xl font-bold text-red-600 mb-2">Access Denied</h1>
            <p className="text-gray-600 mb-4">You do not have permission to access the admin panel.</p>
            <p className="text-gray-400 text-sm">Redirecting to dashboard...</p>
          </div>
        </div>
      )}

      {isAdminAuthorized && (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-10 gap-4 slide-up">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-200">
              <Users className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-extrabold bg-gradient-to-r from-indigo-700 to-purple-600 bg-clip-text text-transparent">Admin Dashboard</h1>
              <p className="text-gray-500 text-sm mt-0.5">Manage users and system settings</p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleRefresh}
              disabled={isLoading || !isAdminAuthorized}
              className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
              title="Refresh user list"
            >
              <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
              Refresh
            </button>
            <button
              onClick={exportToExcel}
              disabled={isExporting || users.length === 0}
              className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-xl hover:shadow-lg hover:shadow-green-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm font-medium"
              title="Export users to Excel"
            >
              <Download size={16} />
              Export Excel
            </button>
          </div>
        </div>

        {/* Success Message */}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-700 rounded-2xl flex items-center gap-3 slide-up">
            <CheckCircle size={18} className="flex-shrink-0" />
            <span className="text-sm">{success}</span>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl flex items-center gap-3 slide-up">
            <AlertCircle size={18} className="flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-10 slide-up" style={{ animationDelay: '0.05s' }}>
          <div className="bg-white rounded-2xl border border-gray-100 p-6 hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-xs font-medium uppercase tracking-wider">Total Users</p>
                <p className="text-4xl font-extrabold text-gray-900 mt-1">{users.length}</p>
              </div>
              <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center">
                <Users className="text-indigo-600" size={24} />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 p-6 hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-xs font-medium uppercase tracking-wider">Active</p>
                <p className="text-4xl font-extrabold text-gray-900 mt-1">
                  {users.filter(u => u.is_active).length}
                </p>
              </div>
              <div className="w-12 h-12 bg-emerald-50 rounded-2xl flex items-center justify-center">
                <Unlock className="text-emerald-600" size={24} />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 p-6 hover-lift">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-xs font-medium uppercase tracking-wider">Inactive</p>
                <p className="text-4xl font-extrabold text-gray-900 mt-1">
                  {users.filter(u => !u.is_active).length}
                </p>
              </div>
              <div className="w-12 h-12 bg-red-50 rounded-2xl flex items-center justify-center">
                <Lock className="text-red-500" size={24} />
              </div>
            </div>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden slide-up" style={{ animationDelay: '0.1s' }}>
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-xl font-bold text-gray-900">Users</h2>
          </div>

          {isLoading ? (
            <div className="p-12 text-center">
              <Loader size={28} className="animate-spin mx-auto text-indigo-600 mb-4" />
              <p className="text-gray-500 text-sm">Loading users...</p>
            </div>
          ) : users.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50/80">
                  <tr>
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Email</th>
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Joined</th>
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3.5 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {users.map((u) => (
                    <tr key={u.user_id} className="hover:bg-indigo-50/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center">
                            <span className="text-white text-sm font-bold">
                              {u.username.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <span className="font-semibold text-gray-900 text-sm">{u.username}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-500 text-sm">{u.email}</td>
                      <td className="px-6 py-4 text-gray-500 text-sm">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                            u.is_active
                              ? 'bg-emerald-50 text-emerald-700'
                              : 'bg-red-50 text-red-700'
                          }`}
                        >
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleToggleActive(u.user_id, u.is_active)}
                            className={`p-2 rounded-xl text-sm transition ${
                              u.is_active
                                ? 'bg-amber-50 text-amber-600 hover:bg-amber-100'
                                : 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100'
                            }`}
                            title={u.is_active ? 'Deactivate' : 'Activate'}
                          >
                            {u.is_active ? <Lock size={15} /> : <Unlock size={15} />}
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(u.user_id)}
                            className="p-2 bg-red-50 text-red-500 hover:bg-red-100 rounded-xl transition"
                            title="Delete user"
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-12 text-center">
              <Users size={40} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 text-sm">No users found</p>
            </div>
          )}
        </div>

        {/* Delete Confirmation Modal */}
        {deleteConfirm && (
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full slide-up">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-red-100 rounded-2xl flex items-center justify-center">
                  <AlertCircle className="text-red-600" size={20} />
                </div>
                <h3 className="text-lg font-bold text-gray-900">Delete User</h3>
              </div>
              <p className="text-gray-500 text-sm mb-6">
                Are you sure you want to delete this user? This action cannot be undone.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setDeleteConfirm(null)}
                  className="flex-1 px-4 py-2.5 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleDeleteUser(deleteConfirm)}
                  className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-xl font-medium hover:bg-red-700 transition text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      )}
    </div>
  )
}
