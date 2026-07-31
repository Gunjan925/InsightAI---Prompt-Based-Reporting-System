// pages/Dashboard.jsx
// The main landing page after login.
// Fetches and displays aggregated statistics for the authenticated user:
//   - Stat cards: total files uploaded, total reports generated, latest report
//   - BarChart:   horizontal bar for file type distribution
//   - PieChart:   donut chart of upload breakdown
//   - Recent activity table: last few reports from history
//
// Data is fetched from:
//   GET /api/dashboard/stats   → DashboardStats
//   GET /api/history           → ReportListItem[] (for recent table)
//
// Uses the Layout wrapper for the sidebar + navbar shell.

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import Layout from '../components/Layout'
import CardChart from '../components/charts/CardChart'
import BarChart  from '../components/charts/BarChart'
import PieChart  from '../components/charts/PieChart'
import Loader    from '../components/Loader'
import { getDashboardStats, getHistory } from '../services/report'
import { FileStack, BarChart2, Sparkles, ExternalLink, Download } from 'lucide-react'
import { downloadReport } from '../services/report'
import toast from 'react-hot-toast'

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-IN', { dateStyle: 'medium' })
}

export default function Dashboard() {
  const { user } = useAuth()
  const [stats,   setStats]   = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError('')
      try {
        const [s, h] = await Promise.all([getDashboardStats(), getHistory()])
        setStats(s)
        setHistory(h)
      } catch (err) {
        setError('Failed to load dashboard data. Please refresh.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  async function handleDownload(id) {
    try {
      await downloadReport(id)
      toast.success('Report downloaded')
    } catch {
      toast.error('Download failed')
    }
  }

  const recentReports = history.slice(0, 5)

  return (
    <Layout>
      {/* ── Welcome header ────────────────────────────────── */}
      <div style={{ marginBottom: 28 }}>
        <h1 className="page-title">
          Good {getGreeting()}, {user?.username} 👋
        </h1>
        <p style={{ marginTop: 6, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
          Here's an overview of your InsightAI activity.
        </p>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 80 }}>
          <Loader size="lg" text="Loading dashboard…" />
        </div>
      ) : error ? (
        <div className="alert alert-error">{error}</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

          {/* ── Stat cards ──────────────────────────────── */}
          <div className="stats-grid">
            <CardChart
              icon={<FileStack size={22} />}
              value={stats?.total_files_uploaded ?? 0}
              label="Files Uploaded"
              color="var(--primary)"
            />
            <CardChart
              icon={<BarChart2 size={22} />}
              value={stats?.total_reports_generated ?? 0}
              label="Reports Generated"
              color="var(--secondary)"
            />
            <CardChart
              icon={<Sparkles size={22} />}
              value={stats?.latest_report_title ? '1 new' : 'None yet'}
              label="Latest Report"
              sublabel={
                stats?.latest_report_title
                  ? `${stats.latest_report_title.slice(0, 30)}${stats.latest_report_title.length > 30 ? '…' : ''}`
                  : 'Generate your first report'
              }
              color="#22c55e"
            />
          </div>

          {/* ── Charts row ──────────────────────────────── */}
          {stats?.file_type_distribution && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: 16,
              }}
            >
              <BarChart data={stats.file_type_distribution} title="File Type Distribution" />
              <PieChart data={stats.file_type_distribution} title="Upload Breakdown" />
            </div>
          )}

          {/* ── Recent reports table ─────────────────────── */}
          <div className="glass-card" style={{ padding: '20px 24px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 16,
                flexWrap: 'wrap',
                gap: 8,
              }}
            >
              <div className="section-title">Recent Reports</div>
              {history.length > 5 && (
                <Link
                  to="/history"
                  style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 600, textDecoration: 'none' }}
                >
                  View all →
                </Link>
              )}
            </div>

            {recentReports.length === 0 ? (
              <div
                style={{
                  textAlign: 'center',
                  padding: '40px 20px',
                  color: 'var(--text-muted)',
                  fontSize: '0.875rem',
                }}
              >
                No reports yet.{' '}
                <Link to="/upload" style={{ color: 'var(--primary)', fontWeight: 600, textDecoration: 'none' }}>
                  Upload a dataset to get started →
                </Link>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Report Title</th>
                      <th>File</th>
                      <th>Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentReports.map((r) => (
                      <tr key={r.id}>
                        <td style={{ fontWeight: 600, color: 'var(--text-primary)', maxWidth: 240 }}>
                          <span title={r.report_title}>{r.report_title}</span>
                        </td>
                        <td>
                          <span className="badge badge-primary">{r.filename}</span>
                        </td>
                        <td>{formatDate(r.created_at)}</td>
                        <td>
                          <div style={{ display: 'flex', gap: 8 }}>
                            <Link
                              to={`/report/${r.id}`}
                              title="View report"
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: 4,
                                fontSize: '0.78rem',
                                color: 'var(--primary)',
                                fontWeight: 600,
                                textDecoration: 'none',
                              }}
                            >
                              <ExternalLink size={13} /> View
                            </Link>
                            <button
                              onClick={() => handleDownload(r.id)}
                              title="Download report"
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: 4,
                                fontSize: '0.78rem',
                                color: 'var(--text-muted)',
                                background: 'transparent',
                                border: 'none',
                                cursor: 'pointer',
                                fontWeight: 600,
                                fontFamily: 'inherit',
                                padding: 0,
                              }}
                            >
                              <Download size={13} /> Download
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </Layout>
  )
}

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
}