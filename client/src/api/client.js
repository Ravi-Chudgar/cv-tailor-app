import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

// Use VITE_API_BASE_URL for consistency with render.yaml
// Falls back to /api for local development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include token
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Add response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = useAuthStore.getState().refreshToken
        const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token } = response.data
        useAuthStore.getState().setTokens(access_token, refresh_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        useAuthStore.getState().logout()
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth endpoints
export const authAPI = {
  register: (data) => apiClient.post('/api/auth/register', data),
  login: (username, password) => {
    // Validate inputs
    if (!username || typeof username !== 'string') {
      console.error('[API] Invalid username:', { username, type: typeof username })
      return Promise.reject(new Error('Username must be a non-empty string'))
    }
    if (!password || typeof password !== 'string') {
      console.error('[API] Invalid password:', { password, type: typeof password })
      return Promise.reject(new Error('Password must be a non-empty string'))
    }
    
    const payload = { username: username.trim(), password }
    console.log('[API] Login request payload:', { username: payload.username, password: '***' })
    console.log('[API] Payload types:', { username: typeof payload.username, password: typeof payload.password })
    return apiClient.post('/api/auth/login', payload)
  },
  getCurrentUser: () => apiClient.get('/api/auth/current-user'),
  changePassword: (oldPassword, newPassword) =>
    apiClient.post('/api/auth/change-password', { old_password: oldPassword, new_password: newPassword }),
  logout: () => apiClient.post('/api/auth/logout'),
}

// CV endpoints
export const cvAPI = {
  upload: (file) => {
    console.log('[API] Uploading CV:', { name: file.name, size: file.size, type: file.type })
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/api/cv/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(response => {
      console.log('[API] Upload successful:', response.data)
      return response
    }).catch(error => {
      console.error('[API] Upload error:', { status: error.response?.status, detail: error.response?.data?.detail })
      throw error
    })
  },
  list: () => apiClient.get('/api/cv/list'),
  parse: (fileName) => apiClient.post('/api/cv/parse', { file_name: fileName }),
  delete: (fileName) => apiClient.delete(`/api/cv/${fileName}`),
}

// Job Description endpoints
export const jobAPI = {
  analyze: (jobDescription, jobTitle = '', company = '', cvFileId = '') => {
    const payload = {
      description: jobDescription,
      title: jobTitle || null,
      company: company || null,
      cv_file_id: cvFileId || null,
      url: null
    }
    console.log('[API] Job analyze request:', { description: jobDescription.substring(0, 50) + '...', title: jobTitle, cvFileId })
    return apiClient.post('/api/job/analyze', payload)
  },
}

// Tailor endpoints
export const tailorAPI = {
  tailor: (cvFile, jobDescription, mobileNumber = '', location = '') => {
    const payload = {
      cv_file: cvFile,
      job_description: jobDescription,
      mobile_number: mobileNumber || undefined,
      location: location || undefined,
    }
    console.log('[API] Tailor request:', { cvFile: cvFile, jobDescLength: jobDescription.length })
    return apiClient.post('/api/tailor/tailor', payload)
  },
  batchTailor: (cvFile, jobDescriptions) =>
    apiClient.post('/api/tailor/batch-tailor', {
      cv_file: cvFile,
      job_descriptions: jobDescriptions,
    }),
  preview: (cvFile, jobDescription) =>
    apiClient.get('/api/tailor/preview', {
      params: { cv_file: cvFile, job_description: jobDescription },
    }),
  compare: (cvFile, tailoredFile) =>
    apiClient.get('/api/tailor/compare', {
      params: { cv_file: cvFile, tailored_file: tailoredFile },
    }),
}

// PDF endpoints
export const pdfAPI = {
  generate: (cvContent, template = 'professional', fileName = 'cv.pdf') =>
    apiClient.post('/api/pdf/generate', {
      cv_content: cvContent,
      template: template,
      file_name: fileName,
    }, { responseType: 'blob' }),
  download: (fileName) =>
    apiClient.get(`/api/pdf/download/${fileName}`, { responseType: 'blob' }),
  getTemplates: () => apiClient.get('/api/pdf/templates'),
  preview: (cvContent, template = 'professional') =>
    apiClient.post('/api/pdf/preview', {
      cv_content: cvContent,
      template: template,
    }),
  batchGenerate: (cvsList) =>
    apiClient.post('/api/pdf/batch-generate', { cvs_content: cvsList }, { responseType: 'blob' }),
}

// Admin endpoints
export const adminAPI = {
  getUsers: () => apiClient.get('/api/admin/users'),
  getUserById: (userId) => apiClient.get(`/api/admin/users/${userId}`),
  deleteUser: (userId) => apiClient.delete(`/api/admin/users/${userId}`),
  toggleUserStatus: (userId, isActive) =>
    apiClient.put(`/api/admin/users/${userId}/status`, { is_active: isActive }),
  getSystemStats: () => apiClient.get('/api/admin/stats'),
  getActivityLog: () => apiClient.get('/api/admin/activity-log'),
  updateUserRole: (userId, role) =>
    apiClient.put(`/api/admin/users/${userId}/role`, { role }),
}

export default apiClient
