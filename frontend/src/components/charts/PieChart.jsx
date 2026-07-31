// components/charts/PieChart.jsx
// Renders a donut-style pie chart using Recharts to visualise the proportion
// of file types among all uploaded datasets on the Dashboard.
//
// Props:
//   data  (object) – key-value map of file type → count
//                    e.g. { csv: 12, xlsx: 5 }
//                    Comes from DashboardStats.file_type_distribution
//   title (string) – optional chart heading

import {
  PieChart as RechartsPie,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const COLORS = ['#6366f1', '#06b6d4', '#8b5cf6', '#f59e0b', '#22c55e', '#f43f5e']

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const { name, value } = payload[0]
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
      <strong>{name.toUpperCase()}</strong>: {value} file{value !== 1 ? 's' : ''}
    </div>
  )
}

function CustomLegend({ payload }) {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px 16px', justifyContent: 'center', marginTop: 12 }}>
      {payload?.map((entry) => (
        <div key={entry.value} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: entry.color, flexShrink: 0 }} />
          <span style={{ fontWeight: 600 }}>{entry.value.toUpperCase()}</span>
        </div>
      ))}
    </div>
  )
}

export default function PieChart({ data = {}, title = 'Upload Breakdown' }) {
  const chartData = Object.entries(data).map(([type, count]) => ({
    name: type,
    value: count,
  }))

  const isEmpty = chartData.length === 0 || chartData.every(d => d.value === 0)

  return (
    <div className="glass-card" style={{ padding: '20px 24px' }}>
      <div className="section-title" style={{ marginBottom: 4 }}>{title}</div>

      {isEmpty ? (
        <div
          style={{
            height: 220,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-muted)',
            fontSize: '0.875rem',
          }}
        >
          No upload data available yet.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <RechartsPie>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={90}
              paddingAngle={3}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend content={<CustomLegend />} />
          </RechartsPie>
        </ResponsiveContainer>
      )}
    </div>
  )
}