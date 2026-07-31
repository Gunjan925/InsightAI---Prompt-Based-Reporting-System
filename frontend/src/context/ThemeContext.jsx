// context/ThemeContext.jsx
// Provides dark / light theme state to the entire app.
// - Reads saved preference from localStorage on first load.
// - Applies the "dark" class to the <html> element so that Tailwind
//   dark: variants and CSS custom-property overrides (.dark {}) take effect.
// - Exposes: { theme, toggleTheme } via useContext(ThemeContext)

import { createContext, useEffect, useState } from 'react'

export const ThemeContext = createContext(null)

export function ThemeProvider({ children }) {
  // Initialise from localStorage, defaulting to 'dark'
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('insightai_theme') || 'dark'
  })

  // Keep the <html> class and localStorage in sync whenever theme changes
  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('insightai_theme', theme)
  }, [theme])

  function toggleTheme() {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'))
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
