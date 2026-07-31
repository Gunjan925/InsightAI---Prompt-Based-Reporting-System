// components/upload/UploadButton.jsx
// Drag-and-drop file upload zone component.
// Features:
//   - Click to open native file browser
//   - Drag-over visual highlight
//   - Accepts only .csv, .xlsx, .xls files (validated client-side)
//   - Displays selected file name and size after selection
//   - Shows an error if an unsupported file type is chosen
// Props:
//   onFileSelect (fn) – called with the validated File object when a file is chosen
//   disabled     (bool) – disables interaction during upload

import { useState, useRef } from 'react'
import { UploadCloud, FileSpreadsheet, AlertCircle } from 'lucide-react'

const ACCEPTED_TYPES = [
  'text/csv',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
]
const ACCEPTED_EXTENSIONS = ['.csv', '.xlsx', '.xls']
const MAX_SIZE_MB = 10

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function UploadButton({ onFileSelect, disabled = false }) {
  const [dragging, setDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  function validate(file) {
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    if (!ACCEPTED_EXTENSIONS.includes(ext)) {
      return `Unsupported file type "${ext}". Please upload a CSV or Excel file.`
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File is too large (${formatBytes(file.size)}). Maximum allowed size is ${MAX_SIZE_MB} MB.`
    }
    return null
  }

  function handleFile(file) {
    setError('')
    const validationError = validate(file)
    if (validationError) {
      setError(validationError)
      setSelectedFile(null)
      return
    }
    setSelectedFile(file)
    onFileSelect(file)
  }

  // ── Drag handlers ─────────────────────────────────────────────────────
  function onDragOver(e) {
    e.preventDefault()
    if (!disabled) setDragging(true)
  }
  function onDragLeave(e) {
    e.preventDefault()
    setDragging(false)
  }
  function onDrop(e) {
    e.preventDefault()
    setDragging(false)
    if (disabled) return
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  // ── Input change ──────────────────────────────────────────────────────
  function onInputChange(e) {
    const file = e.target.files[0]
    if (file) handleFile(file)
    e.target.value = '' // reset so same file can be re-selected
  }

  return (
    <div>
      {/* Hidden native file input */}
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        style={{ display: 'none' }}
        onChange={onInputChange}
        disabled={disabled}
        id="file-input"
        aria-label="Upload dataset file"
      />

      {/* Drop zone */}
      <div
        role="button"
        tabIndex={0}
        aria-label="Click or drag and drop to upload a dataset"
        className={`drop-zone ${dragging ? 'dragging' : ''}`}
        style={{ cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.6 : 1 }}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => e.key === 'Enter' && !disabled && inputRef.current?.click()}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
      >
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 14,
              background: dragging ? 'var(--primary)' : 'var(--primary-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <UploadCloud size={28} color={dragging ? '#fff' : 'var(--primary)'} />
          </div>

          {selectedFile ? (
            /* Selected file preview */
            <div style={{ textAlign: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                <FileSpreadsheet size={18} color="var(--success)" />
                <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                  {selectedFile.name}
                </span>
              </div>
              <div style={{ marginTop: 4, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {formatBytes(selectedFile.size)} · Click to change file
              </div>
            </div>
          ) : (
            /* Default prompt */
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-primary)' }}>
                Drop your dataset here or{' '}
                <span style={{ color: 'var(--primary)' }}>browse</span>
              </div>
              <div style={{ marginTop: 6, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Supported formats: CSV, XLSX, XLS · Max {MAX_SIZE_MB} MB
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Validation error */}
      {error && (
        <div className="alert alert-error" style={{ marginTop: 12 }}>
          <AlertCircle size={16} style={{ flexShrink: 0 }} />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}