// components/Layout.jsx
// The main authenticated layout shell that wraps all protected pages.
// Renders:
//   - <Sidebar>  – fixed left navigation panel
//   - <Navbar>   – sticky top bar
//   - <main>     – scrollable content area where the page content is rendered
//
// Manages the sidebar open/close state for mobile responsiveness.
// Usage: wrap any protected page content with <Layout>...</Layout>

import { useState } from 'react'
import Sidebar from './Sidebar'
import Navbar  from './Navbar'

export default function Layout({ children }) {
  // Controls sidebar visibility on mobile
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="app-shell">
      {/* ── Sidebar ───────────────────────────────────── */}
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* ── Main content area ─────────────────────────── */}
      <div className="main-content">
        <Navbar onMenuToggle={() => setSidebarOpen(prev => !prev)} />

        <main role="main" style={{ flex: 1, overflowY: 'auto' }}>
          <div className="page-body">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
