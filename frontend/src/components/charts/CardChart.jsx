// components/charts/CardChart.jsx
// A statistical summary card used on the Dashboard page.
// Displays a single key metric (e.g., "Total Reports: 42") with:
//   - An icon in a coloured rounded box
//   - A large numeric value
//   - A descriptive label
//   - An optional sub-label (e.g., date of latest event)
//
// Props:
//   icon      (ReactNode) – Lucide icon element
//   value     (string | number) – the primary metric value
//   label     (string)   – metric name
//   sublabel  (string?)  – optional secondary info (shown in muted text)
//   color     (string)   – CSS variable or hex for the icon background accent

export default function CardChart({ icon, value, label, sublabel, color = 'var(--primary)' }) {
  // Derive a light background from the accent colour
  const bgLight = color === 'var(--primary)'
    ? 'var(--primary-light)'
    : color === 'var(--success)' || color === '#22c55e'
    ? 'rgba(34,197,94,0.12)'
    : color === 'var(--secondary)' || color === '#06b6d4'
    ? 'rgba(6,182,212,0.12)'
    : 'rgba(99,102,241,0.12)'

  return (
    <div
      className="glass-card"
      style={{ padding: '20px 24px', display: 'flex', alignItems: 'center', gap: 16 }}
    >
      {/* Icon box */}
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: 12,
          background: bgLight,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          color,
        }}
      >
        {icon}
      </div>

      {/* Text */}
      <div style={{ minWidth: 0 }}>
        <div
          style={{
            fontSize: '1.6rem',
            fontWeight: 800,
            color: 'var(--text-primary)',
            lineHeight: 1.1,
            letterSpacing: '-0.02em',
          }}
        >
          {value ?? '—'}
        </div>
        <div style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--text-secondary)', marginTop: 4 }}>
          {label}
        </div>
        {sublabel && (
          <div
            style={{
              fontSize: '0.72rem',
              color: 'var(--text-muted)',
              marginTop: 2,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              maxWidth: '180px',
            }}
            title={sublabel}
          >
            {sublabel}
          </div>
        )}
      </div>
    </div>
  )
}