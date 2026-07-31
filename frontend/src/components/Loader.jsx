// components/Loader.jsx
// Reusable loading indicator component.
// Props:
//   fullPage (bool) – if true, renders a centred full-viewport spinner
//                     used by route guards while the auth session resolves.
//   size     (str)  – 'sm' | 'md' (default) | 'lg'  controls spinner size.
//   text     (str)  – optional label shown below the spinner.

export default function Loader({ fullPage = false, size = 'md', text = '' }) {
  const sizes = { sm: 20, md: 32, lg: 48 }
  const px = sizes[size] ?? 32

  const spinner = (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
      <div
        style={{
          width: px,
          height: px,
          borderRadius: '50%',
          border: `3px solid var(--border)`,
          borderTopColor: 'var(--primary)',
          animation: 'spin 0.7s linear infinite',
        }}
      />
      {text && (
        <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)', fontWeight: 500 }}>
          {text}
        </span>
      )}
    </div>
  )

  if (fullPage) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'var(--bg-base)',
        }}
      >
        {spinner}
      </div>
    )
  }

  return spinner
}