// hooks/useAuth.js
// Convenience hook that reads from AuthContext.
// Usage: const { user, login, logout, isAuthenticated } = useAuth()
// Throws an error if used outside of <AuthProvider>.

import { useContext } from 'react'
import { AuthContext } from '../context/AuthContext'

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
