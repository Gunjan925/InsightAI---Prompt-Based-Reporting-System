// pages/Report.jsx
// Displays a single AI-generated report identified by its URL parameter :id.
//
// Fetches the report from GET /api/report/:id on mount.
// If the fetch succeeds, passes the report data to <ReportViewer> which:
//   - Shows metadata (title, summary, date, prompt)
//   - Renders the HTML content in a sandboxed <iframe>
//   - Provides Download HTML and Print to PDF buttons
//
// Handles loading, not-found, and error states gracefully.

import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout       from '../components/Layout'
import ReportViewer from '../components/ReportViewer'
import Loader       from '../components/Loader'
import { getReport } from '../services/report'
import { ArrowLeft, AlertCircle } from 'lucide-react'

export default function Report() {
  const { id } = useParams()
  const [report,  setReport]  = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError('')
      try {
        const data = await getReport(Number(id))
        setReport(data)
      } catch (err) {
        if (err.response?.status === 404) {
          setError('Report not found or you do not have permission to view it.')
        } else {
          setError('Failed to load report. Please try again.')
        }
      } finally {
        setLoading(false)
      }
    }
    if (id) load()
  }, [id])

  return (
    <Layout>
      {/* ── Back navigation ───────────────────────────────── */}
      <div style={{ marginBottom: 20 }}>
        <Link
          to="/history"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            fontSize: '0.8rem',
            color: 'var(--text-muted)',
            textDecoration: 'none',
            fontWeight: 600,
          }}
        >
          <ArrowLeft size={15} />
          Back to History
        </Link>
      </div>

      {/* ── Content ───────────────────────────────────────── */}
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', paddingTop: 80 }}>
          <Loader size="lg" text="Loading report…" />
        </div>
      ) : error ? (
        <div className="alert alert-error" style={{ maxWidth: 600 }}>
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <div>
            <strong>Error</strong>
            <div style={{ marginTop: 4 }}>{error}</div>
          </div>
        </div>
      ) : (
        <ReportViewer report={report} />
      )}
    </Layout>
  )
}