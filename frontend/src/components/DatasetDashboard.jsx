// components/DatasetDashboard.jsx
// Renders instant dataset statistics and Plotly charts after the user clicks
// "Generate Dashboard" on the Upload page (Phase 1 — no LLM involved).
//
// Chart rendering strategy:
//   Uses the official 'react-plotly.js' component to render interactive charts natively
//   in the React tree, avoiding script injection, dangerouslySetInnerHTML, or iframes.

import { BarChart2, Table2, LayoutGrid } from 'lucide-react'
import Plot from 'react-plotly.js'

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
        minWidth: 140,
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

// Main exported component
// Props:
//   data — the full response from POST /api/dashboard/generate
//          { dataset_id, row_count, col_count, columns, charts[] }
export default function DatasetDashboard({ data }) {
  if (!data) return null

  const { row_count, col_count, columns, charts = [] } = data

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* ── Stat Cards ─────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
        <StatCard label="Total Rows"    value={row_count.toLocaleString()} icon={Table2}     color="var(--primary)"   />
        <StatCard label="Total Columns" value={col_count}                  icon={LayoutGrid} color="var(--secondary)" />
        <StatCard label="Charts Built"  value={charts.length}              icon={BarChart2}  color="#f59e0b"          />
      </div>

      {/* ── Column Schema Badges ────────────────────────────────────── */}
      {columns && Object.keys(columns).length > 0 && (
        <div
          className="glass-card"
          style={{ padding: '16px 20px' }}
        >
          <div className="section-title" style={{ marginBottom: 12, fontSize: '0.78rem' }}>
            Dataset Schema
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

      {/* ── Plotly Charts (Native React-Plotly) ─────────────────────── */}
      {charts.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {charts.map((chart, idx) => {
            let figure;
            try {
              figure = JSON.parse(chart.plotly_json);
            } catch (err) {
              console.error("Failed to parse plotly_json for chart:", err);
              return (
                <div key={idx} className="glass-card" style={{ padding: '20px 24px' }}>
                  <span style={{ color: 'var(--danger)', fontSize: '0.85rem' }}>
                    Failed to parse chart data.
                  </span>
                </div>
              );
            }

            return (
              <div
                key={idx}
                className="glass-card"
                style={{ padding: '20px 24px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
              >
                {/* Chart title and description */}
                <div style={{ marginBottom: 12 }}>
                  <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                    {chart.title}
                  </div>
                  {chart.description && (
                    <div style={{ fontSize: '0.77rem', color: 'var(--text-muted)', marginTop: 3 }}>
                      {chart.description}
                    </div>
                  )}
                </div>

                {/* React-Plotly Component */}
                <div style={{ width: '100%', height: 400 }}>
                  <Plot
                    data={figure.data}
                    layout={{
                      ...figure.layout,
                      autosize: true,
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      margin: { l: 48, r: 24, t: 48, b: 48 },
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
      )}
    </div>
  )
}
