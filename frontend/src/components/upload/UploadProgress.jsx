// components/upload/UploadProgress.jsx
// Displays real-time upload progress feedback.
// Shown after the user selects a file and the upload begins.
// Features:
//   - Animated gradient progress bar that fills from 0 → 100 %
//   - File name and formatted file size
//   - Status label: Uploading… / Upload complete ✓ / Failed
//   - Percentage counter
// Props:
//   fileName  (string) – the name of the file being uploaded
//   fileSize  (number) – file size in bytes
//   progress  (number) – 0–100, drives the progress bar width
//   status    ('uploading' | 'done' | 'error') – controls status message / colour

import { CheckCircle2, XCircle, FileSpreadsheet } from 'lucide-react'

function formatBytes(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function UploadProgress({ fileName, fileSize, progress, status }) {
  const isDone  = status === 'done'
  const isError = status === 'error'

  const statusColor = isDone
    ? 'var(--success)'
    : isError
    ? 'var(--danger)'
    : 'var(--primary)'

  const StatusIcon = isDone
    ? <CheckCircle2 size={18} color="var(--success)" />
    : isError
    ? <XCircle size={18} color="var(--danger)" />
    : <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />

  const statusText = isDone
    ? 'Upload complete'
    : isError
    ? 'Upload failed'
    : `Uploading… ${progress}%`

  return (
    <div
      className="glass-card"
      style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}
    >
      {/* File info row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: 10,
            background: 'var(--primary-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <FileSpreadsheet size={20} color="var(--primary)" />
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              fontWeight: 600,
              fontSize: '0.875rem',
              color: 'var(--text-primary)',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {fileName}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
            {formatBytes(fileSize)}
          </div>
        </div>

        {/* Status icon + text */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
          {StatusIcon}
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: statusColor }}>
            {statusText}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{
            width: `${Math.min(progress, 100)}%`,
            background: isError
              ? 'var(--danger)'
              : 'linear-gradient(90deg, var(--primary), var(--secondary))',
          }}
        />
      </div>
    </div>
  )
}