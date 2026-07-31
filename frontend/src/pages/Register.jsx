// pages/Register.jsx
// Public registration page for InsightAI.
// Features:
//   - Username, email, password, and confirm-password inputs (all controlled)
//   - Client-side validation: required fields, email format, password length (≥8),
//     and password match confirmation
//   - Calls AuthContext.register() on valid submit, auto-logs in, redirects to /dashboard
//   - Shows inline error on API failure
//   - Link to /login for returning users

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Sparkles, User, Mail, Lock, Eye, EyeOff, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Register() {
  const { register } = useAuth()
  const navigate     = useNavigate()

  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '' })
  const [showPwd,  setShowPwd]  = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)

  function update(field) {
    return (e) => setForm(prev => ({ ...prev, [field]: e.target.value }))
  }

  function validate() {
    if (!form.username.trim() || !form.email || !form.password || !form.confirm) {
      return 'All fields are required.'
    }
    if (form.username.trim().length < 3) {
      return 'Username must be at least 3 characters.'
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      return 'Please enter a valid email address.'
    }
    if (form.password.length < 8) {
      return 'Password must be at least 8 characters.'
    }
    if (form.password !== form.confirm) {
      return 'Passwords do not match.'
    }
    return null
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    const validationError = validate()
    if (validationError) { setError(validationError); return }

    setLoading(true)
    try {
      await register(form.username.trim(), form.email, form.password)
      toast.success('Account created! Welcome to InsightAI 🎉')
      navigate('/dashboard')
    } catch (err) {
      const msg = err.response?.data?.detail ?? 'Registration failed. Please try again.'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  const inputIcon = (IconComponent) => (
    <IconComponent
      size={16}
      color="var(--text-muted)"
      style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}
    />
  )

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* ── Brand ─────────────────────────────────────── */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div
            style={{
              width: 52,
              height: 52,
              borderRadius: 14,
              background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px',
            }}
          >
            <Sparkles size={24} color="#fff" />
          </div>
          <h1 className="page-title" style={{ fontSize: '1.5rem', marginBottom: 6 }}>
            Create your account
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            Start generating AI-powered reports today
          </p>
        </div>

        {/* ── Error ─────────────────────────────────────── */}
        {error && (
          <div className="alert alert-error" style={{ marginBottom: 16 }}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {/* ── Form ──────────────────────────────────────── */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }} noValidate>

          {/* Username */}
          <div>
            <label htmlFor="reg-username" style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 5 }}>
              Username
            </label>
            <div style={{ position: 'relative' }}>
              {inputIcon(User)}
              <input id="reg-username" type="text" value={form.username} onChange={update('username')}
                placeholder="johndoe" className="input-field" style={{ paddingLeft: 38 }} autoComplete="username" required />
            </div>
          </div>

          {/* Email */}
          <div>
            <label htmlFor="reg-email" style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 5 }}>
              Email address
            </label>
            <div style={{ position: 'relative' }}>
              {inputIcon(Mail)}
              <input id="reg-email" type="email" value={form.email} onChange={update('email')}
                placeholder="you@example.com" className="input-field" style={{ paddingLeft: 38 }} autoComplete="email" required />
            </div>
          </div>

          {/* Password */}
          <div>
            <label htmlFor="reg-password" style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 5 }}>
              Password <span style={{ fontWeight: 400, color: 'var(--text-muted)' }}>(min. 8 characters)</span>
            </label>
            <div style={{ position: 'relative' }}>
              {inputIcon(Lock)}
              <input id="reg-password" type={showPwd ? 'text' : 'password'} value={form.password} onChange={update('password')}
                placeholder="••••••••" className="input-field" style={{ paddingLeft: 38, paddingRight: 42 }} autoComplete="new-password" required />
              <button type="button" onClick={() => setShowPwd(v => !v)} aria-label="Toggle password visibility"
                style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}>
                {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label htmlFor="reg-confirm" style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 5 }}>
              Confirm password
            </label>
            <div style={{ position: 'relative' }}>
              {inputIcon(Lock)}
              <input id="reg-confirm" type={showConfirm ? 'text' : 'password'} value={form.confirm} onChange={update('confirm')}
                placeholder="••••••••" className="input-field" style={{ paddingLeft: 38, paddingRight: 42 }} autoComplete="new-password" required />
              <button type="button" onClick={() => setShowConfirm(v => !v)} aria-label="Toggle confirm password visibility"
                style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}>
                {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            id="register-submit"
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: '100%', padding: '12px', marginTop: 6, fontSize: '0.95rem' }}
          >
            {loading ? (
              <>
                <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                Creating account…
              </>
            ) : 'Create Account'}
          </button>
        </form>

        {/* ── Login link ─────────────────────────────────── */}
        <p style={{ textAlign: 'center', marginTop: 20, fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--primary)', fontWeight: 600, textDecoration: 'none' }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}