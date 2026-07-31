// hooks/useTheme.js
// Convenience hook that reads from ThemeContext.
// Usage: const { theme, toggleTheme } = useTheme()
// Returns the current theme ('dark' | 'light') and a toggle function.

import { useContext } from 'react'
import { ThemeContext } from '../context/ThemeContext'

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>')
  return ctx
}
