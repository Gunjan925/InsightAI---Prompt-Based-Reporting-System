// pages/Upload.jsx
// The main workflow page where users:
//   1. Upload a CSV or Excel dataset (drag-and-drop or file browser)
//   2. Monitor upload progress
//   3. Enter a natural-language prompt
//   4. Trigger AI report generation
//   5. Are redirected to the Report page on success
//
// Workflow steps managed by local state:
//   'idle'       → initial state, file not yet selected
//   'uploading'  → file upload in progress (shows UploadProgress bar)
//   'ready'      → file uploaded, file_id obtained, prompt can be entered
//   'generating' → POST /report/generate in progress (spinner + message)
//   'done'       → report created, navigating to /report/:id
//
// API calls:
//   POST /api/upload          (via uploadDataset in upload.js)
//   POST /api/report/generate (via generateReport in report.js)

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout        from '../components/Layout'
import UploadButton  from '../components/upload/UploadButton'
import UploadProgress from '../components/upload/UploadProgress'
import PromptInput   from '../components/PromptInput'
import Loader        from '../components/Loader'
import { uploadDataset } from '../services/upload'
import { generateReport } from '../services/report'
import { CheckCircle2, Sparkles, AlertCircle, RefreshCcw } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Upload() {
  const navigate = useNavigate()

  // Upload state
  const [file,          setFile]          = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus,  setUploadStatus]  = useState('idle') // idle | uploading | done | error
  const [fileId,        setFileId]        = useState(null)

  // Report generation state
  const [prompt,        setPrompt]        = useState('')
  const [generating,    setGenerating]    = useState(false)
  const [genError,      setGenError]      = useState('')

  const isUploaded = uploadStatus === 'done' && fileId !== null
  const canGenerate = isUploaded && prompt.trim().length >= 5 && !generating

  // ── Step 1: File selected → start upload immediately ──────────────────
  async function handleFileSelect(selectedFile) {
    setFile(selectedFile)
    setUploadProgress(0)
    setUploadStatus('uploading')
    setFileId(null)
    setGenError('')

    try {
      const res = await uploadDataset(selectedFile, (pct) => setUploadProgress(pct))
      setFileId(res.id)
      setUploadStatus('done')
      toast.success(`"${selectedFile.name}" uploaded successfully!`)
    } catch (err) {
      setUploadStatus('error')
      const msg = err.response?.data?.detail ?? 'Upload failed. Please try again.'
      toast.error(msg)
    }
  }

  // ── Step 2: Generate report ────────────────────────────────────────────
  async function handleGenerate() {
    if (!canGenerate) return
    setGenerating(true)
    setGenError('')

    try {
      const report = await generateReport(fileId, prompt.trim())
      toast.success('Report generated successfully!')
      navigate(`/report/${report.id}`)
    } catch (err) {
      const msg = err.response?.data?.detail ?? 'Report generation failed. Please try again.'
      setGenError(msg)
      toast.error('Report generation failed')
    } finally {
      setGenerating(false)
    }
  }

  // ── Reset to upload another file ──────────────────────────────────────
  function handleReset() {
    setFile(null)
    setUploadProgress(0)
    setUploadStatus('idle')
    setFileId(null)
    setPrompt('')
    setGenError('')
    setGenerating(false)
  }

  return (
    <Layout>
      <div style={{ maxWidth: 760, margin: '0 auto' }}>

        {/* ── Page header ──────────────────────────────────── */}
        <div style={{ marginBottom: 28 }}>
          <h1 className="page-title">Upload & Generate Report</h1>
          <p style={{ marginTop: 6, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Upload your dataset, describe the analysis you want, and let InsightAI do the rest.
          </p>
        </div>

        {/* ── Progress indicator ────────────────────────────── */}
        <div style={{ display: 'flex', gap: 0, marginBottom: 32, position: 'relative' }}>
          {['Upload Dataset', 'Enter Prompt', 'Generate Report'].map((step, i) => {
            const stepDone = (i === 0 && isUploaded) || (i < 0)
            const stepActive = (i === 0 && !isUploaded) || (i === 1 && isUploaded && !generating) || (i === 2 && generating)
            return (
              <div key={step} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, position: 'relative' }}>
                <div style={{
                  width: 32, height: 32, borderRadius: '50%',
                  background: stepDone ? 'var(--success)' : stepActive ? 'var(--primary)' : 'var(--bg-elevated)',
                  border: `2px solid ${stepDone ? 'var(--success)' : stepActive ? 'var(--primary)' : 'var(--border)'}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: stepDone || stepActive ? '#fff' : 'var(--text-muted)',
                  fontWeight: 700, fontSize: '0.8rem', zIndex: 1,
                }}>
                  {stepDone ? <CheckCircle2 size={16} /> : i + 1}
                </div>
                <span style={{ fontSize: '0.72rem', fontWeight: 600, color: stepActive ? 'var(--primary)' : 'var(--text-muted)', textAlign: 'center' }}>
                  {step}
                </span>
                {i < 2 && (
                  <div style={{
                    position: 'absolute', top: 16, left: '50%', width: '100%',
                    height: 2, background: isUploaded && i === 0 ? 'var(--primary)' : 'var(--border)',
                    zIndex: 0,
                  }} />
                )}
              </div>
            )
          })}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

          {/* ── STEP 1: Upload ───────────────────────────────── */}
          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <div className="section-title">Step 1 — Upload Dataset</div>
              {isUploaded && (
                <button onClick={handleReset} className="btn-secondary" style={{ padding: '6px 14px', fontSize: '0.78rem' }}>
                  <RefreshCcw size={13} /> Upload different file
                </button>
              )}
            </div>

            {/* Show upload zone only if not yet uploading/done */}
            {uploadStatus === 'idle' && (
              <UploadButton onFileSelect={handleFileSelect} disabled={false} />
            )}

            {/* Show progress bar during/after upload */}
            {(uploadStatus === 'uploading' || uploadStatus === 'done' || uploadStatus === 'error') && file && (
              <UploadProgress
                fileName={file.name}
                fileSize={file.size}
                progress={uploadProgress}
                status={uploadStatus}
              />
            )}
          </div>

          {/* ── STEP 2: Prompt ───────────────────────────────── */}
          <div
            className="glass-card"
            style={{
              padding: '24px',
              opacity: isUploaded ? 1 : 0.5,
              pointerEvents: isUploaded ? 'auto' : 'none',
            }}
          >
            <div className="section-title" style={{ marginBottom: 16 }}>Step 2 — Describe Your Report</div>
            <PromptInput
              value={prompt}
              onChange={setPrompt}
              disabled={!isUploaded || generating}
              placeholder="e.g. Summarize the key trends and generate a monthly performance breakdown…"
            />
            {prompt.trim().length > 0 && prompt.trim().length < 5 && (
              <p style={{ marginTop: 8, fontSize: '0.78rem', color: 'var(--warning)' }}>
                Prompt must be at least 5 characters.
              </p>
            )}
          </div>

          {/* ── STEP 3: Generate ─────────────────────────────── */}
          <div
            className="glass-card"
            style={{
              padding: '24px',
              opacity: canGenerate || generating ? 1 : 0.5,
              pointerEvents: canGenerate || generating ? 'auto' : 'none',
            }}
          >
            <div className="section-title" style={{ marginBottom: 16 }}>Step 3 — Generate AI Report</div>

            {genError && (
              <div className="alert alert-error" style={{ marginBottom: 16 }}>
                <AlertCircle size={16} style={{ flexShrink: 0 }} />
                <span>{genError}</span>
              </div>
            )}

            {generating ? (
              /* Generation in progress */
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 16,
                  padding: '24px 0',
                }}
              >
                <div
                  style={{
                    width: 56,
                    height: 56,
                    borderRadius: 14,
                    background: 'var(--primary-light)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Sparkles size={26} color="var(--primary)" />
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
                    AI is generating your report…
                  </div>
                  <div style={{ marginTop: 6, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    This may take 30–120 seconds depending on dataset size.
                    Please do not close this tab.
                  </div>
                </div>
                <Loader size="md" />
              </div>
            ) : (
              <div>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.6 }}>
                  InsightAI will analyse your dataset using the prompt above and produce a
                  comprehensive HTML report with statistics, visualisations, and insights.
                </p>
                <button
                  id="generate-report-btn"
                  onClick={handleGenerate}
                  disabled={!canGenerate}
                  className="btn-primary"
                  style={{ padding: '12px 28px', fontSize: '0.95rem' }}
                >
                  <Sparkles size={18} />
                  Generate Report
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}