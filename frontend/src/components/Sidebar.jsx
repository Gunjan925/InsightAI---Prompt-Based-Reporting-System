// components/Sidebar.jsx
// The main navigation sidebar displayed on all authenticated pages.
// Features:
//   - App logo + branding at the top
//   - Navigation links: Dashboard, Upload, History, Settings
//   - Logout button at the bottom
//   - Active link highlighting based on the current URL path
//   - Mobile: hidden by default; slides in when the Navbar hamburger is toggled.
//     The parent Layout component controls the `open` prop via shared state.
// Props:
//   open      (bool)     – controls mobile visibility
//   onClose   (fn)       – called when the backdrop overlay is clicked

import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import toast from 'react-hot-toast'

// Lucide icons
import {
  LayoutDashboard,
  Upload,
  History,
  Settings,
  LogOut,
  Sparkles,
  X,
} from 'lucide-react'

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/upload',    icon: Upload,          label: 'Upload & Generate' },
  { to: '/history',   icon: History,         label: 'History' },
  { to: '/settings',  icon: Settings,        label: 'Settings' },
]

export default function Sidebar({ open, onClose }) {
  const { logout, user } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    toast.success('Logged out successfully')
    navigate('/login')
  }

  return (
    <>
      {/* Mobile backdrop overlay */}
      <div
        className={`sidebar-overlay ${open ? 'open' : ''}`}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Sidebar panel */}
      <aside className={`sidebar ${open ? 'open' : ''}`} aria-label="Sidebar navigation">
        {/* ── Brand ─────────────────────────────────────────── */}
        <div
          style={{
            padding: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid var(--border)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 10,
                background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <Sparkles size={18} color="#fff" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.95rem', color: 'var(--text-primary)', lineHeight: 1.1 }}>
                InsightAI
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                Reporting System
              </div>
            </div>
          </div>

          {/* Close button – visible on mobile only */}
          <button
            onClick={onClose}
            style={{
              display: 'none',
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: 4,
            }}
            className="mobile-close-btn"
            aria-label="Close sidebar"
          >
            <X size={18} />
          </button>
        </div>

        {/* ── User info ──────────────────────────────────────── */}
        {user && (
          <div
            style={{
              padding: '16px 20px',
              borderBottom: '1px solid var(--border)',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '10px 12px',
                borderRadius: 10,
                background: 'var(--bg-elevated)',
              }}
            >
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  fontWeight: 700,
                  fontSize: '0.8rem',
                  flexShrink: 0,
                }}
              >
                {user.username?.charAt(0).toUpperCase()}
              </div>
              <div style={{ overflow: 'hidden' }}>
                <div style={{ fontWeight: 600, fontSize: '0.8rem', color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {user.username}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {user.email}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Navigation links ───────────────────────────────── */}
        <nav style={{ flex: 1, padding: '12px 12px', display: 'flex', flexDirection: 'column', gap: 4 }}>
          <div style={{ fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', padding: '4px 8px 8px' }}>
            Navigation
          </div>
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
              aria-label={label}
            >
              <Icon size={18} style={{ flexShrink: 0 }} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* ── Logout button ──────────────────────────────────── */}
        <div style={{ padding: '12px', borderTop: '1px solid var(--border)' }}>
          <button
            onClick={handleLogout}
            className="sidebar-link"
            style={{ color: 'var(--danger)', width: '100%' }}
            aria-label="Logout"
          >
            <LogOut size={18} style={{ flexShrink: 0 }} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Inline style for mobile close button display */}
      <style>{`
        @media (max-width: 768px) {
          .mobile-close-btn { display: flex !important; }
        }
      `}</style>
    </>
  )
}