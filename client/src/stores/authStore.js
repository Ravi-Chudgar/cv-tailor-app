import { create } from 'zustand'

// Validate and clean localStorage on initialization
const validateToken = (token) => {
  return token && typeof token === 'string' && token.length > 10 ? token : null
}

const accessToken = validateToken(localStorage.getItem('accessToken'))
const refreshToken = validateToken(localStorage.getItem('refreshToken'))

// Clear invalid tokens
if (!accessToken) {
  localStorage.removeItem('accessToken')
}
if (!refreshToken) {
  localStorage.removeItem('refreshToken')
}

export const useAuthStore = create((set) => ({
  user: null,
  accessToken: accessToken,
  refreshToken: refreshToken,
  isLoading: false,
  isAuthenticated: !!accessToken,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  setTokens: (accessToken, refreshToken) => {
    if (accessToken && typeof accessToken === 'string' && refreshToken && typeof refreshToken === 'string') {
      localStorage.setItem('accessToken', accessToken)
      localStorage.setItem('refreshToken', refreshToken)
      set({ accessToken, refreshToken, isAuthenticated: true })
    } else {
      console.warn('[AUTH] Invalid tokens provided to setTokens')
    }
  },

  logout: () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('username')
    localStorage.removeItem('email')
    set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false })
  },

  setLoading: (isLoading) => set({ isLoading }),
}))
