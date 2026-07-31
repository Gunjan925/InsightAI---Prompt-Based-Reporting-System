// components/charts/BarChart.jsx
// Renders a horizontal bar chart showing the distribution of uploaded file types.
// Uses the Recharts library (BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer).
//
// Props:
//   data (object) – key-value mapping of file type → count
//                   e.g. { csv: 12, xlsx: 5, xls: 2 }
//                   Comes from DashboardStats.file_type_distribution
//   title (string) – optional chart heading

import {
  BarChart as RechartsBar,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'

const COLORS = ['#6366f1', '#06b6d4', '#8b5cf6', '#f59e0b', '#22c55e']

// Custom tooltip that respects the current theme CSS variables
function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  return (
    <div
      style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: '8px 14px',
        fontSize: '0.8rem',
        color: 'var(--text-primary)',
        boxShadow: 'var(--shadow-md)',
      }}
    >
      <strong>{payload[0].name}</strong>: {payload[0].value} file{payload[0].value !== 1 ? 's' : ''}
    </div>
  )
}

export default function BarChart({ data = {}, title = 'File Type Distribution' }) {
  // Convert object → array for Recharts
  const chartData = Object.entries(data).map(([type, count]) => ({
    name: type.toUpperCase(),
    count,
  }))

  const isEmpty = chartData.length === 0 || chartData.every(d => d.count === 0)

  return (
    <div className="glass-card" style={{ padding: '20px 24px' }}>
      <div className="section-title" style={{ marginBottom: 20 }}>{title}</div>

      {isEmpty ? (
        <div
          style={{
            height: 200,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-muted)',
            fontSize: '0.875rem',
          }}
        >
          No file data available yet.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <RechartsBar
            data={chartData}
            layout="vertical"
            margin={{ top: 0, right: 16, bottom: 0, left: 0 }}
          >
            <XAxis
              type="number"
              allowDecimals={false}
              tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
              axisLine={{ stroke: 'var(--border)' }}
              tickLine={false}
            />
            <YAxis
              dataKey="name"
              type="category"
              width={40}
              tick={{ fontSize: 11, fill: 'var(--text-secondary)', fontWeight: 600 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'var(--bg-elevated)' }} />
            <Bar dataKey="count" radius={[0, 6, 6, 0]} maxBarSize={32}>
              {chartData.map((entry, index) => (
                <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </RechartsBar>
        </ResponsiveContainer>
      )}
    </div>
  )
}