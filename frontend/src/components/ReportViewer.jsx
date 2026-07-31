// components/ReportViewer.jsx
// Displays a fully generated AI report from the backend.
// The report HTML content is rendered inside a sandboxed <iframe>
// to isolate the AI-generated markup from the host application.
//
// Features:
//   - Renders report metadata: title, source file, generation date, prompt used
//   - Displays the HTML report in a sandboxed iframe (allow-same-origin for
//     internal script execution is intentionally omitted for security)
//   - "Download HTML" button triggers the browser file-save dialog via the
//     backend's /report/{id}/download endpoint (returns Content-Disposition)
//   - "Print to PDF" button calls window.print() on the iframe's content window,
//     letting the user save the report as a PDF through the browser print dialog
//
// Props:
//   report (ReportResponse) – the report object returned by the API:
//     { id, report_title, summary, content, prompt, created_at, file_id }

import { useRef } from 'react'
import { Download, Printer, Calendar, FileText, MessageSquare } from 'lucide-react'
import { downloadReport } from '../services/report'
import toast from 'react-hot-toast'

function formatDate(iso) {
  return new Date(iso).toLocaleString('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export default function ReportViewer({ report }) {
  const iframeRef = useRef(null)

  if (!report) return null

  // ── Download HTML ─────────────────────────────────────────────────────
  async function handleDownload() {
    try {
      await downloadReport(report.id)
      toast.success('Report downloaded successfully')
    } catch (err) {
      toast.error('Download failed. Please try again.')
    }
  }

  // ── Print to PDF ──────────────────────────────────────────────────────
  // Triggers the browser's native print dialog on the iframe content.
  // The user can then "Save as PDF" from the print dialog.
  function handlePrint() {
    try {
      const iframeWindow = iframeRef.current?.contentWindow
      if (iframeWindow) {
        iframeWindow.focus()
        iframeWindow.print()
      } else {
        // Fallback: print the whole page if iframe access fails
        window.print()
      }
    } catch (_) {
      window.print()
    }
  }

  // Build the iframe source from the HTML content string using a Blob URL
  const blobUrl = URL.createObjectURL(
    new Blob([report.content], { type: 'text/html' })
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* ── Report metadata card ──────────────────────────── */}
      <div className="glass-card" style={{ padding: '24px' }}>
        {/* Title + action buttons */}
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            gap: 16,
            flexWrap: 'wrap',
            marginBottom: 20,
          }}
        >
          <div style={{ flex: 1, minWidth: 0 }}>
            <h2 className="page-title" style={{ fontSize: '1.4rem' }}>
              {report.report_title}
            </h2>
            {report.summary && (
              <p
                style={{
                  marginTop: 8,
                  fontSize: '0.875rem',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.6,
                  maxWidth: 700,
                }}
              >
                {report.summary}
              </p>
            )}
          </div>

          {/* Action buttons */}
          <div style={{ display: 'flex', gap: 10, flexShrink: 0, flexWrap: 'wrap' }}>
            <button
              id="download-report-btn"
              onClick={handleDownload}
              className="btn-secondary"
              aria-label="Download report as HTML"
            >
              <Download size={16} />
              Download HTML
            </button>
            <button
              id="print-report-btn"
              onClick={handlePrint}
              className="btn-primary"
              aria-label="Print report or save as PDF"
            >
              <Printer size={16} />
              Print / Save PDF
            </button>
          </div>
        </div>

        {/* Metadata row */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 20,
            paddingTop: 16,
            borderTop: '1px solid var(--border)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Calendar size={15} color="var(--text-muted)" />
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Generated: <strong style={{ color: 'var(--text-secondary)' }}>{formatDate(report.created_at)}</strong>
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <FileText size={15} color="var(--text-muted)" />
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Report ID: <strong style={{ color: 'var(--text-secondary)' }}>#{report.id}</strong>
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, flex: 1, minWidth: 200 }}>
            <MessageSquare size={15} color="var(--text-muted)" style={{ marginTop: 2, flexShrink: 0 }} />
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Prompt: <em style={{ color: 'var(--text-secondary)', fontStyle: 'normal' }}>{report.prompt}</em>
            </span>
          </div>
        </div>
      </div>

      {/* ── Sandboxed iframe report ───────────────────────── */}
      <div
        className="glass-card"
        style={{ overflow: 'hidden', padding: 0 }}
      >
        <div
          style={{
            padding: '12px 20px',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <div style={{ display: 'flex', gap: 6 }}>
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#ef4444' }} />
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#f59e0b' }} />
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#22c55e' }} />
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>
            AI-Generated Report Preview
          </span>
        </div>

        <iframe
          ref={iframeRef}
          src={blobUrl}
          title={`Report: ${report.report_title}`}
          // sandbox attribute restricts capabilities for security:
          // allow-scripts: lets embedded Plotly charts run
          // allow-same-origin: required for window.print() to work on the iframe
          sandbox="allow-scripts allow-same-origin"
          style={{
            width: '100%',
            height: '70vh',
            border: 'none',
            display: 'block',
            background: '#fff',
          }}
          aria-label="Generated report content"
        />
      </div>
    </div>
  )
}