// routes/AppRoute.jsx
// Defines all application routes and enforces authentication guards.
//
// Route structure:
//   /login      → Login page        (public, redirects to /dashboard if logged in)
//   /register   → Register page     (public, redirects to /dashboard if logged in)
//   /           → redirects to /dashboard
//   /dashboard  → Dashboard page    (protected)
//   /upload     → Upload page       (protected)
//   /report/:id → Report view page  (protected)
//   /history    → History page      (protected)
//   /settings   → Settings page     (protected)
//
// <ProtectedRoute> renders a full-page spinner while AuthContext resolves the
// session, then either renders the child or redirects to /login.
// <PublicRoute> redirects already-authenticated users away from auth pages.

import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import Loader from '../components/Loader'

// Pages
import Login    from '../pages/Login'
import Register from '../pages/Register'
import Dashboard from '../pages/Dashboard'
import Upload   from '../pages/Upload'
import Report   from '../pages/Report'
import History  from '../pages/History'
import Settings from '../pages/Settings'
import DatasetDashboardPage from '../pages/DatasetDashboardPage'

// ── Guard: require authentication ────────────────────────────────────────
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <Loader fullPage />
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

// ── Guard: redirect authenticated users away from auth pages ─────────────
function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <Loader fullPage />
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return children
}

export default function AppRoute() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login"    element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

      {/* Protected routes */}
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/upload"    element={<ProtectedRoute><Upload /></ProtectedRoute>} />
      <Route path="/report/:id" element={<ProtectedRoute><Report /></ProtectedRoute>} />
      <Route path="/history"   element={<ProtectedRoute><History /></ProtectedRoute>} />
      <Route path="/settings"  element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      <Route path="/dashboard/view/:fileId" element={<ProtectedRoute><DatasetDashboardPage /></ProtectedRoute>} />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>

  )
}