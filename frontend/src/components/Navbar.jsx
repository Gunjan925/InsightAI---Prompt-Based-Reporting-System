// components/Navbar.jsx
// Top navigation bar rendered on all authenticated pages.
// Features:
//   - Hamburger menu button (mobile only) to toggle the Sidebar
//   - Dynamic page title based on current route
//   - Theme toggle button (sun / moon icon)
//   - User avatar with username display
// Props:
//   onMenuToggle (fn) – called when the hamburger icon is clicked

import { useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import { Menu, Sun, Moon } from 'lucide-react'

// Map route paths → human-readable page titles
const PAGE_TITLES = {
  '/dashboard': 'Dashboard',
  '/upload':    'Upload & Generate Report',
  '/history':   'Report History',
  '/settings':  'Settings',
}

export default function Navbar({ onMenuToggle }) {
  const { user } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const { pathname } = useLocation()

  // Derive title: handle /report/:id dynamically
  const title = pathname.startsWith('/report/')
    ? 'Report Viewer'
    : PAGE_TITLES[pathname] ?? 'InsightAI'

  return (
    <header className="navbar" role="banner">
      {/* ── Hamburger (mobile) ────────────────────────── */}
      <button
        id="sidebar-toggle"
        onClick={onMenuToggle}
        aria-label="Toggle sidebar"
        style={{
          background: 'transparent',
          border: 'none',
          color: 'var(--text-secondary)',
          cursor: 'pointer',
          padding: 6,
          borderRadius: 8,
          display: 'none', // shown via media query below
        }}
        className="hamburger-btn"
      >
        <Menu size={22} />
      </button>

      {/* ── Page title ───────────────────────────────── */}
      <h1
        style={{
          flex: 1,
          fontSize: '1rem',
          fontWeight: 700,
          color: 'var(--text-primary)',
          margin: 0,
        }}
      >
        {title}
      </h1>

      {/* ── Right actions ────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {/* Theme toggle */}
        <button
          id="theme-toggle"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            padding: '6px 8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* User avatar */}
        {user && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '6px 12px',
              borderRadius: 8,
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
            }}
          >
            <div
              style={{
                width: 28,
                height: 28,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontWeight: 700,
                fontSize: '0.75rem',
                flexShrink: 0,
              }}
            >
              {user.username?.charAt(0).toUpperCase()}
            </div>
            <span
              style={{
                fontSize: '0.8rem',
                fontWeight: 600,
                color: 'var(--text-primary)',
                maxWidth: 100,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {user.username}
            </span>
          </div>
        )}
      </div>

      {/* Inline style: show hamburger on mobile */}
      <style>{`
        @media (max-width: 768px) {
          .hamburger-btn { display: flex !important; }
        }
      `}</style>
    </header>
  )
}