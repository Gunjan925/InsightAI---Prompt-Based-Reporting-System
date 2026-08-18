// pages/Upload.jsx
// Two-phase AI workflow page:
//
// Phase 1 — Instant Dataset Dashboard (no LLM)
//   Step 1: User uploads a CSV/Excel file OR selects a previously uploaded one
//   Step 2: User clicks "Generate Dashboard" -> Navigates in same tab: /dashboard/view/:fileId
//           -> AI Service cleans data, computes stats, builds Plotly charts
//           -> User hits Back to return here with state restored from sessionStorage
//
// Phase 2 — AI Report (Gemini LLM)
//   Step 3: Prompt textarea — active as soon as a dataset is selected/uploaded
//   Step 4: User clicks "Generate Report" -> POST /api/report/generate
//           -> AI Service embeds data in ChromaDB, calls Gemini, compiles HTML report
//           -> User redirected to /report/:id

import { useState, useEffect } from 'react'
import { useNavigate }         from 'react-router-dom'
import Layout                  from '../components/Layout'
import UploadButton            from '../components/upload/UploadButton'
import UploadProgress          from '../components/upload/UploadProgress'
import PromptInput             from '../components/PromptInput'
import Loader                  from '../components/Loader'
import { uploadDataset, getUploadedDatasets, deleteDataset } from '../services/upload'
import { generateReport }      from '../services/report'
import {
  CheckCircle2, Sparkles, AlertCircle,
  RefreshCcw, BarChart2, ArrowRight, Database, Trash2, Info,
} from 'lucide-react'
import toast from 'react-hot-toast'

// Step indicator config — drives the top progress bar
const STEPS = [
  { label: 'Upload Dataset'   },
  { label: 'View Dashboard'   },
  { label: 'Enter Prompt'     },
  { label: 'Generate Report'  },
]

// Heuristic: reject prompts that are clearly not dataset-specific
// Blocks single generic words like "hi", "hello", "what", "tell me" with no context
const GENERIC_PROMPTS = ['hi', 'hello', 'hey', 'what', 'who', 'why', 'yes', 'no', 'ok', 'okay', 'test', 'testing']

function isPromptDatasetRelevant(text) {
  const trimmed = text.trim().toLowerCase()
  // Too short
  if (trimmed.length < 10) return false
  // Exact match to a generic word
  if (GENERIC_PROMPTS.includes(trimmed)) return false
  return true
}

export default function Upload() {
  const navigate = useNavigate()

  // ── File upload state ────────────────────────────────────────────────────
  const [file,           setFile]           = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus,   setUploadStatus]   = useState('idle')  // idle | uploading | done | error
  const [fileId,         setFileId]         = useState(null)

  // ── Previous uploads state ───────────────────────────────────────────────
  const [prevDatasets,   setPrevDatasets]   = useState([])
  const [showPrev,       setShowPrev]       = useState(false)
  const [loadingPrev,    setLoadingPrev]    = useState(false)

  // ── Report generation state (Phase 2) ───────────────────────────────────
  const [prompt,         setPrompt]         = useState('')
  const [generating,     setGenerating]     = useState(false)
  const [genError,       setGenError]       = useState('')

  // ── Derived flags ────────────────────────────────────────────────────────
  // isUploaded: a dataset has been selected (freshly uploaded or chosen from history)
  const isUploaded = uploadStatus === 'done' && fileId !== null
  // canGenerate: dataset selected + prompt is long enough + not currently generating
  const canGenerate = isUploaded && isPromptDatasetRelevant(prompt) && !generating
  // prompt validation message
  const promptTooShort = prompt.trim().length > 0 && !isPromptDatasetRelevant(prompt)

  // Current active step index (0-based) for the progress bar
  const activeStep = !isUploaded   ? 0
    : prompt.trim().length === 0   ? 1   // uploaded, waiting for dashboard visit / prompt entry
    : !generating                  ? 2   // prompt entered
    :                                3   // generating

  // ── Restore state from sessionStorage when returning via Back button ─────
  useEffect(() => {
    const savedId   = sessionStorage.getItem('upload_fileId')
    const savedName = sessionStorage.getItem('upload_filename')
    const savedSize = sessionStorage.getItem('upload_filesize')
    if (savedId && savedName) {
      setFileId(parseInt(savedId, 10))
      setFile({ name: savedName, size: parseInt(savedSize || '0', 10) })
      setUploadStatus('done')
    }
  }, [])

  // ── Step 1: File selected → upload immediately ───────────────────────────
  async function handleFileSelect(selectedFile) {
    clearSession()
    setFile(selectedFile)
    setUploadProgress(0)
    setUploadStatus('uploading')
    setFileId(null)
    setGenError('')
    setPrompt('')
    setShowPrev(false)

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

  // ── Step 1 Alternative: Load and show previously uploaded datasets ───────
  async function handleLoadPrevious() {
    setLoadingPrev(true)
    try {
      const data = await getUploadedDatasets()
      setPrevDatasets(data)
      setShowPrev((prev) => !prev)
    } catch {
      toast.error('Failed to load previous datasets')
    } finally {
      setLoadingPrev(false)
    }
  }

  function handleSelectPrevious(dataset) {
    clearSession()
    setFile({ name: dataset.filename, size: dataset.file_size })
    setFileId(dataset.id)
    setUploadStatus('done')
    setPrompt('')
    setGenError('')
    setShowPrev(false)
    toast.success(`Selected dataset: "${dataset.filename}"`)
  }

  // ── Step 2: Navigate to Dataset Dashboard in same tab (Phase 1, no LLM) ─
  function handleGenerateDashboard() {
    if (!isUploaded) return
    // Persist selection so state survives page unmount on navigate
    sessionStorage.setItem('upload_fileId',   String(fileId))
    sessionStorage.setItem('upload_filename', file?.name ?? '')
    sessionStorage.setItem('upload_filesize', String(file?.size ?? 0))
    navigate(`/dashboard/view/${fileId}`)
  }

  // ── Delete a previously uploaded dataset from the database ───────────────
  async function handleDeleteDataset(ds) {
    if (!window.confirm(`Delete "${ds.filename}" permanently? This cannot be undone.`)) return
    try {
      await deleteDataset(ds.id)
      setPrevDatasets((prev) => prev.filter((d) => d.id !== ds.id))
      // If the deleted file is currently selected, reset the flow
      if (fileId === ds.id) handleReset()
      toast.success(`"${ds.filename}" deleted.`)
    } catch (err) {
      toast.error(err.response?.data?.detail ?? 'Failed to delete dataset.')
    }
  }

  // ── Step 4: Generate Full AI Report (Phase 2, Gemini LLM) ───────────────
  async function handleGenerateReport() {
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
      toast.error('Report generation failed.')
    } finally {
      setGenerating(false)
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────────────
  function clearSession() {
    sessionStorage.removeItem('upload_fileId')
    sessionStorage.removeItem('upload_filename')
    sessionStorage.removeItem('upload_filesize')
  }

  function handleReset() {
    clearSession()
    setFile(null)
    setUploadProgress(0)
    setUploadStatus('idle')
    setFileId(null)
    setShowPrev(false)
    setPrompt('')
    setGenError('')
    setGenerating(false)
  }

  return (
    <Layout>
      <div style={{ maxWidth: 860, margin: '0 auto' }}>

        {/* ── Page header ──────────────────────────────────────────────── */}
        <div style={{ marginBottom: 28 }}>
          <h1 className="page-title">Upload &amp; Analyse Dataset</h1>
          <p style={{ marginTop: 6, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Upload or select your dataset, explore interactive charts, then prompt Gemini to generate a detailed report.
          </p>
        </div>

        {/* ── 4-step progress indicator ────────────────────────────────── */}
        <div style={{ display: 'flex', marginBottom: 32, position: 'relative' }}>
          {STEPS.map((step, i) => {
            const done   = i < activeStep
            const active = i === activeStep
            return (
              <div
                key={step.label}
                style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, position: 'relative' }}
              >
                <div style={{
                  width: 32, height: 32, borderRadius: '50%',
                  background: done ? 'var(--success)' : active ? 'var(--primary)' : 'var(--bg-elevated)',
                  border: `2px solid ${done ? 'var(--success)' : active ? 'var(--primary)' : 'var(--border)'}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: done || active ? '#fff' : 'var(--text-muted)',
                  fontWeight: 700, fontSize: '0.8rem', zIndex: 1,
                  transition: 'all 0.3s ease',
                }}>
                  {done ? <CheckCircle2 size={16} /> : i + 1}
                </div>
                <span style={{ fontSize: '0.68rem', fontWeight: 600, color: active ? 'var(--primary)' : 'var(--text-muted)', textAlign: 'center' }}>
                  {step.label}
                </span>
                {i < STEPS.length - 1 && (
                  <div style={{
                    position: 'absolute', top: 16, left: '50%', width: '100%',
                    height: 2,
                    background: done ? 'var(--primary)' : 'var(--border)',
                    zIndex: 0, transition: 'background 0.3s ease',
                  }} />
                )}
              </div>
            )
          })}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

          {/* ── STEP 1: Upload / Select Dataset ──────────────────────────── */}
          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <div className="section-title">Step 1 — Upload Dataset</div>
              {isUploaded && (
                <button onClick={handleReset} className="btn-secondary" style={{ padding: '6px 14px', fontSize: '0.78rem' }}>
                  <RefreshCcw size={13} /> Upload different file
                </button>
              )}
            </div>

            {uploadStatus === 'idle' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {/* Drag-and-drop uploader */}
                <UploadButton onFileSelect={handleFileSelect} disabled={false} />

                {/* Divider */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '8px 0' }}>
                  <div style={{ flex: 1, height: 1, background: 'var(--border-light)' }}></div>
                  <span style={{ padding: '0 12px', fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>OR</span>
                  <div style={{ flex: 1, height: 1, background: 'var(--border-light)' }}></div>
                </div>

                {/* Previously uploaded datasets */}
                <div style={{ textAlign: 'center' }}>
                  <button
                    onClick={handleLoadPrevious}
                    disabled={loadingPrev}
                    className="btn-secondary"
                    style={{ padding: '8px 18px', fontSize: '0.82rem', display: 'inline-flex', alignItems: 'center', gap: 6 }}
                  >
                    <Database size={14} />
                    {loadingPrev ? 'Loading datasets…' : 'Choose from Previously Uploaded'}
                  </button>
                </div>

                {/* Dataset list panel */}
                {showPrev && (
                  <div
                    className="glass-card"
                    style={{
                      marginTop: 12, padding: 16, maxHeight: 240,
                      overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 8,
                      border: '1.5px solid var(--border-light)',
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-light)', paddingBottom: 6 }}>
                      <span>Dataset Filename</span>
                      <span>Actions</span>
                    </div>
                    {prevDatasets.length === 0 ? (
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center', padding: '12px 0' }}>
                        No previously uploaded datasets found.
                      </span>
                    ) : (
                      prevDatasets.map((ds) => (
                        <div
                          key={ds.id}
                          style={{
                            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                            padding: '6px 8px', borderRadius: 8,
                            background: 'var(--bg-elevated)', fontSize: '0.8rem',
                          }}
                        >
                          <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '72%' }}>
                            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{ds.filename}</span>
                            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                              {(ds.file_size / 1024).toFixed(1)} KB &bull; {new Date(ds.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <div style={{ display: 'flex', gap: 6 }}>
                            <button
                              onClick={() => handleSelectPrevious(ds)}
                              className="btn-primary"
                              style={{ padding: '4px 10px', fontSize: '0.7rem' }}
                            >
                              Select
                            </button>
                            <button
                              onClick={() => handleDeleteDataset(ds)}
                              className="btn-secondary"
                              title={`Delete ${ds.filename}`}
                              style={{ padding: '4px 8px', fontSize: '0.7rem', color: '#ef4444', borderColor: '#ef4444' }}
                            >
                              <Trash2 size={13} />
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Upload progress / done pill */}
            {(uploadStatus === 'uploading' || uploadStatus === 'done' || uploadStatus === 'error') && file && (
              <UploadProgress
                fileName={file.name}
                fileSize={file.size}
                progress={uploadProgress}
                status={uploadStatus}
              />
            )}
          </div>

          {/* ── STEP 2: Generate Dashboard (Phase 1) ──────────────────────── */}
          <div
            className="glass-card"
            style={{
              padding: '24px',
              opacity: isUploaded ? 1 : 0.45,
              pointerEvents: isUploaded ? 'auto' : 'none',
              transition: 'opacity 0.3s ease',
            }}
          >
            <div className="section-title" style={{ marginBottom: 16 }}>Step 2 — Generate Dataset Dashboard</div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.6 }}>
              InsightAI will clean your dataset, compute descriptive statistics, and generate
              interactive Plotly charts — instantly, without any AI model.
            </p>
            <button
              id="generate-dashboard-btn"
              onClick={handleGenerateDashboard}
              disabled={!isUploaded}
              className="btn-primary"
              style={{ padding: '11px 26px', fontSize: '0.92rem', display: 'flex', alignItems: 'center', gap: 8 }}
            >
              <BarChart2 size={17} />
              Generate Visual Dashboard
            </button>
          </div>

          {/* ── STEP 3 & 4: Prompt + Generate Report (Phase 2) ────────────── */}
          <div
            className="glass-card"
            style={{
              padding: '24px',
              // Enabled as soon as a dataset is uploaded — no longer gated on hasDashboard
              opacity: isUploaded ? 1 : 0.45,
              pointerEvents: isUploaded ? 'auto' : 'none',
              transition: 'opacity 0.3s ease',
            }}
          >
            <div className="section-title" style={{ marginBottom: 6 }}>Step 3 &amp; 4 — AI Report Generation</div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 18 }}>
              Describe the analysis you need. Your prompt must be specific to the uploaded dataset.
            </p>

            {/* Dataset-specific prompt hint */}
            <div style={{
              display: 'flex', alignItems: 'flex-start', gap: 8, marginBottom: 14,
              padding: '10px 14px', borderRadius: 10,
              background: 'var(--primary-light, rgba(99,102,241,0.08))',
              border: '1px solid var(--border)',
              fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.6,
            }}>
              <Info size={14} style={{ flexShrink: 0, marginTop: 2, color: 'var(--primary)' }} />
              <span>
                Your prompt should reference this dataset specifically —
                e.g. <em>"Summarise the monthly sales trends and identify the top 3 performing regions"</em> or
                <em> "Find anomalies in the revenue column and explain possible causes."</em>
              </span>
            </div>

            {/* Prompt input (Step 3) */}
            <PromptInput
              value={prompt}
              onChange={setPrompt}
              disabled={!isUploaded || generating}
              placeholder="e.g. Analyse the sales trends by region and highlight peak months in the dataset…"
            />

            {/* Prompt validation feedback */}
            {promptTooShort && (
              <p style={{ marginTop: 8, fontSize: '0.78rem', color: 'var(--warning, #f59e0b)' }}>
                Please enter a more specific, dataset-related prompt (minimum 10 characters).
              </p>
            )}

            {/* Error alert */}
            {genError && (
              <div className="alert alert-error" style={{ margin: '16px 0 0' }}>
                <AlertCircle size={16} style={{ flexShrink: 0 }} />
                <span>{genError}</span>
              </div>
            )}

            {/* Generate Report button / spinner (Step 4) */}
            <div style={{ marginTop: 20 }}>
              {generating ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14, padding: '12px 0' }}>
                  <div style={{
                    width: 52, height: 52, borderRadius: 14,
                    background: 'var(--primary-light)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Sparkles size={24} color="var(--primary)" />
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
                      AI is generating your report…
                    </div>
                    <div style={{ marginTop: 5, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      This may take 30–120 seconds. Please do not close this tab.
                    </div>
                  </div>
                  <Loader size="md" />
                </div>
              ) : (
                <button
                  id="generate-report-btn"
                  onClick={handleGenerateReport}
                  disabled={!canGenerate}
                  className="btn-primary"
                  style={{ padding: '12px 28px', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: 8 }}
                >
                  <Sparkles size={18} />
                  Generate AI Report
                  <ArrowRight size={16} />
                </button>
              )}
            </div>
          </div>

        </div>
      </div>
    </Layout>
  )
}