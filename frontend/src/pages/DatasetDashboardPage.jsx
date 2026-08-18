// pages/DatasetDashboardPage.jsx
// Displays a full-screen standalone dashboard for an uploaded dataset.
//
// Layout:
//   - Back button returning to Upload page.
//   - Stat Cards showing row counts, column counts, and recommended chart counts.
//   - Dataset Schema badge listing.
//   - Side-by-side responsive Plotly chart grid (columns/rows format).
//
// Data Flow:
//   Fetches the dashboard data from GET /api/dashboard/generate/:fileId
//   upon component mounting, ensuring durability on page refresh.

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import Loader from '../components/Loader'
import Plot from 'react-plotly.js'
import { getDashboard } from '../services/report'
import { 
  BarChart2, Table2, LayoutGrid, ArrowLeft, 
  AlertCircle 
} from 'lucide-react'
import toast from 'react-hot-toast'

// Stat card — small metric widget shown at the top of the dashboard
function StatCard({ label, value, icon: Icon, color }) {
  return (
    <div
      style={{
        background: 'var(--bg-surface)',
        border: '1.5px solid var(--border-light)',
        borderRadius: 14,
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: 14,
        boxShadow: 'var(--shadow-sm)',
        flex: 1,
        minWidth: 200,
      }}
    >
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: 10,
          background: color + '20',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <Icon size={20} color={color} />
      </div>
      <div>
        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
          {value}
        </div>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, marginTop: 3, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {label}
        </div>
      </div>
    </div>
  )
}

export default function DatasetDashboardPage() {
  const { fileId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchDashboard() {
      setLoading(true)
      setError('')
      try {
        const dashboardData = await getDashboard(fileId)
        setData(dashboardData)
      } catch (err) {
        const msg = err.response?.data?.detail ?? 'Failed to load visual dashboard. Please try again.'
        setError(msg)
        toast.error('Failed to load visual dashboard')
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [fileId])

  if (loading) {
    return (
      <Layout>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh', gap: 14 }}>
          <Loader size="lg" />
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Generating visual insights...</p>
        </div>
      </Layout>
    )
  }

  if (error || !data) {
    return (
      <Layout>
        <div style={{ maxWidth: 600, margin: '40px auto', textAlign: 'center' }}>
          <div className="alert alert-error" style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
            <AlertCircle size={20} />
            <span>{error || 'Dashboard configuration could not be loaded.'}</span>
          </div>
          <button onClick={() => navigate('/upload')} className="btn-primary">
            <ArrowLeft size={16} /> Back to Upload
          </button>
        </div>
      </Layout>
    )
  }

  const { row_count, col_count, columns, charts = [], dataset_id } = data

  return (
    <Layout>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        
        {/* ── Page Header ── */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <button 
              onClick={() => navigate(-1)} 
              className="btn-secondary" 
              style={{ padding: '8px 12px', borderRadius: 10 }}
              title="Return to upload and prompts page"
            >
              <ArrowLeft size={18} />
            </button>
            <div>
              <h1 className="page-title" style={{ fontSize: '1.5rem', fontWeight: 800 }}>Dataset Visual Dashboard</h1>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2, fontFamily: 'monospace' }}>
                Dataset: {dataset_id}
              </p>
            </div>
          </div>
          
          <button 
            onClick={() => navigate(-1)} 
            className="btn-primary"
            style={{ padding: '10px 20px', fontSize: '0.85rem' }}
          >
            <ArrowLeft size={14} /> Back to Upload &amp; Prompts
          </button>
        </div>

        {/* ── Stat Cards Summary Row ── */}
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <StatCard label="Total Rows"    value={row_count.toLocaleString()} icon={Table2}     color="var(--primary)"   />
          <StatCard label="Total Columns" value={col_count}                  icon={LayoutGrid} color="var(--secondary)" />
          <StatCard label="Charts Built"  value={charts.length}              icon={BarChart2}  color="#f59e0b"          />
        </div>

        {/* ── Dataset Schema Metadata ── */}
        {columns && Object.keys(columns).length > 0 && (
          <div className="glass-card" style={{ padding: '16px 20px' }}>
            <div className="section-title" style={{ marginBottom: 12, fontSize: '0.78rem' }}>
              Dataset Attributes Schema
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {Object.entries(columns).map(([col, info]) => (
                <span
                  key={col}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '4px 10px',
                    borderRadius: 20,
                    background: 'var(--primary-light)',
                    border: '1px solid var(--border)',
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    color: 'var(--primary)',
                  }}
                >
                  <span style={{ color: 'var(--text-primary)', fontFamily: 'monospace' }}>{col}</span>
                  <span style={{ color: 'var(--text-muted)' }}>{info.type}</span>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* ── Side-by-Side Responsive Grid Charts (2 Columns) ── */}
        {charts.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" style={{ marginTop: 8 }}>
            {charts.map((chart, idx) => {
              let figure;
              try {
                figure = JSON.parse(chart.plotly_json);
              } catch (err) {
                console.error("Failed to parse chart plotly_json:", err);
                return (
                  <div key={idx} className="glass-card" style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 300 }}>
                    <span style={{ color: 'var(--danger)', fontSize: '0.85rem' }}>Failed to parse chart metadata.</span>
                  </div>
                );
              }

              return (
                <div
                  key={idx}
                  className="glass-card"
                  style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: 14 }}
                >
                  {/* Title and Description */}
                  <div>
                    <h3 style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                      {chart.title}
                    </h3>
                    {chart.description && (
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 3 }}>
                        {chart.description}
                      </p>
                    )}
                  </div>

                  {/* React-Plotly graph */}
                  <div style={{ width: '100%', height: 350 }}>
                    <Plot
                      data={figure.data}
                      layout={{
                        ...figure.layout,
                        autosize: true,
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        margin: { l: 48, r: 24, t: 40, b: 48 },
                      }}
                      useResizeHandler={true}
                      style={{ width: '100%', height: '100%' }}
                      config={{
                        responsive: true,
                        displayModeBar: false
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="glass-card" style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
            No charts were suggested for this dataset.
          </div>
        )}

      </div>
    </Layout>
  )
}
