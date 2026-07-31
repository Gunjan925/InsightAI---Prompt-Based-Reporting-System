// pages/Settings.jsx
// Settings Page
// Features
// ✓ View username
// ✓ View email
// ✓ Toggle Light/Dark Theme
// ✓ Logout
// ✓ Form validation
// ✓ Loading states
// ✓ Uses AuthContext
// ✓ Uses ThemeContext
// ✓ Uses react-hot-toast

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

import {
    User,
    Mail,
    Moon,
    Sun,
    LogOut,
    Save,
} from 'lucide-react'

import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'

export default function Settings() {
    const navigate = useNavigate()

    {/* ── Context ───────────────────────────────── */ }
    const { user, logout } = useAuth()

    const { theme, toggleTheme } = useTheme()

    {/* ── Form State ───────────────────────────────── */ }
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')

    {/* ── Loading States ───────────────────────────────── */ }
    const [saving, setSaving] = useState(false)
    const [loggingOut, setLoggingOut] = useState(false)

    {/* ── Populate data from AuthContext ───────────────────────────────── */ }
    useEffect(() => {
        if (user) {
            setUsername(user.username || '')
            setEmail(user.email || '')
        }
    }, [user])

    {/* ── Validation ───────────────────────────────── */ }
    function validate() {
        if (!username.trim()) {
            toast.error('Username cannot be empty')
            return false
        }

        if (!email.trim()) {
            toast.error('Email cannot be empty')
            return false
        }

        const emailRegex =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/

        if (!emailRegex.test(email)) {
            toast.error('Please enter a valid email')
            return false
        }

        return true
    }

    {/* ── Save Profile ───────────────────────────────── */ }
    // Backend API not implemented yet.
    // Only validates and shows notification.
    async function handleSave() {
        if (!validate()) return

        try {
            setSaving(true)

            // TODO:
            // await updateProfile(username,email)

            await new Promise((resolve) =>
                setTimeout(resolve, 800)
            )

            toast.success(
                'Profile update API not implemented yet.'
            )
        } catch (error) {
            toast.error('Unable to save profile.')
        } finally {
            setSaving(false)
        }
    }

    {/* ── Theme toggle ───────────────────────────────── */ }
    function handleThemeToggle() {
        toggleTheme()

        toast.success(
            theme === 'dark'
                ? 'Light mode enabled'
                : 'Dark mode enabled'
        )
    }

    {/* ── Logout ───────────────────────────────── */ }
    async function handleLogout() {
        try {
            setLoggingOut(true)

            await logout()

            toast.success('Logged out successfully')

            navigate('/login')
        } catch (error) {
            toast.error('Logout failed')
        } finally {
            setLoggingOut(false)
        }
    }

    {/* ── UI ───────────────────────────────── */ }
    return (
        <div className="page-body">
            <h1 className="page-title" style={{ marginBottom: 28 }}>
                Settings
            </h1>

            {/* ---------------- Profile ---------------- */}
            <div
                className="glass-card"
                style={{
                    padding: 24,
                    marginBottom: 24,
                }}
            >
                <div
                    className="section-title"
                    style={{ marginBottom: 20 }}
                >
                    Profile Information
                </div>

                <div
                    style={{
                        display: 'grid',
                        gap: 18,
                    }}
                >
                    {/* Username */}
                    <div>
                        <label
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 8,
                                marginBottom: 8,
                                fontWeight: 600,
                            }}
                        >
                            <User size={18} />
                            Username
                        </label>

                        <input
                            type="text"
                            className="input-field"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter username"
                        />
                    </div>

                    {/* Email */}
                    <div>
                        <label
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 8,
                                marginBottom: 8,
                                fontWeight: 600,
                            }}
                        >
                            <Mail size={18} />
                            Email Address
                        </label>

                        <input
                            type="email"
                            className="input-field"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter email"
                        />
                    </div>

                    <div>
                        <button
                            className="btn-primary"
                            onClick={handleSave}
                            disabled={saving}
                        >
                            <Save size={18} />

                            {saving
                                ? 'Saving...'
                                : 'Save Changes'}
                        </button>
                    </div>
                </div>
            </div>

            {/* ---------------- Theme ---------------- */}
            <div
                className="glass-card"
                style={{
                    padding: 24,
                    marginBottom: 24,
                }}
            >
                <div
                    className="section-title"
                    style={{ marginBottom: 20 }}
                >
                    Appearance
                </div>

                <div
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: 20,
                        flexWrap: 'wrap',
                    }}
                >
                    <div>
                        <div
                            style={{
                                fontWeight: 600,
                                marginBottom: 4,
                            }}
                        >
                            Theme
                        </div>

                        <div
                            style={{
                                color: 'var(--text-secondary)',
                                fontSize: '0.9rem',
                            }}
                        >
                            Current Theme:
                            {' '}
                            <strong>
                                {theme === 'dark'
                                    ? 'Dark'
                                    : 'Light'}
                            </strong>
                        </div>
                    </div>

                    <button
                        className="btn-secondary"
                        onClick={handleThemeToggle}
                    >
                        {theme === 'dark'
                            ? (
                                <>
                                    <Sun size={18} />
                                    Switch to Light
                                </>
                            )
                            : (
                                <>
                                    <Moon size={18} />
                                    Switch to Dark
                                </>
                            )}
                    </button>
                </div>
            </div>

            {/* ---------------- Account ---------------- */}
            <div
                className="glass-card"
                style={{
                    padding: 24,
                }}
            >
                <div
                    className="section-title"
                    style={{ marginBottom: 20 }}
                >
                    Account
                </div>

                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        gap: 20,
                        flexWrap: 'wrap',
                    }}
                >
                    <div>
                        <div
                            style={{
                                fontWeight: 600,
                            }}
                        >
                            Logout
                        </div>

                        <div
                            style={{
                                color: 'var(--text-secondary)',
                                fontSize: '0.9rem',
                            }}
                        >
                            End your current session securely.
                        </div>
                    </div>

                    <button
                        className="btn-danger"
                        onClick={handleLogout}
                        disabled={loggingOut}
                    >
                        <LogOut size={18} />

                        {loggingOut
                            ? 'Logging Out...'
                            : 'Logout'}
                    </button>
                </div>
            </div>
        </div>
    )
}