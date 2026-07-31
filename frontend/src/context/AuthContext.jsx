// context/AuthContext.jsx
// Manages authentication state for the entire application.
// - Persists JWT token and user object in localStorage so the session
//   survives page refresh.
// - Provides: { user, token, login, register, logout, loading }
//   via useContext(AuthContext).
// - All child components call useAuth() (hooks/useAuth.js) instead of
//   accessing this context directly.

import { createContext, useState, useEffect } from 'react'
import * as authService from '../services/auth'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]     = useState(null)
  const [token, setToken]   = useState(null)
  const [loading, setLoading] = useState(true) // true while restoring session

  // ── Restore session from localStorage on first mount ──────────────────
  useEffect(() => {
    const savedToken = localStorage.getItem('insightai_token')
    const savedUser  = localStorage.getItem('insightai_user')
    if (savedToken && savedUser) {
      setToken(savedToken)
      setUser(JSON.parse(savedUser))
    }
    setLoading(false)
  }, [])

  // ── Persist helpers ───────────────────────────────────────────────────
  function persist(tokenVal, userVal) {
    setToken(tokenVal)
    setUser(userVal)
    localStorage.setItem('insightai_token', tokenVal)
    localStorage.setItem('insightai_user', JSON.stringify(userVal))
  }

  function clear() {
    setToken(null)
    setUser(null)
    localStorage.removeItem('insightai_token')
    localStorage.removeItem('insightai_user')
  }

  // ── Public actions ────────────────────────────────────────────────────

  // Registers a new user and auto-logs them in.
  // Returns the user object on success; throws on error.
  async function register(username, email, password) {
    const data = await authService.registerUser({ username, email, password })
    // Auto login after register
    const loginData = await authService.loginUser({ email, password })
    persist(loginData.access_token, loginData.user)
    return loginData.user
  }

  // Logs in with email + password, stores JWT and user data.
  async function login(email, password) {
    const data = await authService.loginUser({ email, password })
    persist(data.access_token, data.user)
    return data.user
  }

  // Calls the backend logout endpoint, then clears local state.
  async function logout() {
    try {
      await authService.logoutUser()
    } catch (_) {
      // Even if the server call fails, clear local session
    } finally {
      clear()
    }
  }

  const value = { user, token, login, register, logout, loading, isAuthenticated: !!token }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}