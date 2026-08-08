// pages/Upload.jsx
// Two-phase AI workflow page:
//
// Phase 1 — Instant Dataset Dashboard (no LLM)
//   Step 1: User uploads a CSV/Excel file  → file stored in MySQL, fileId returned
//   Step 2: User clicks "Generate Dashboard" → POST /api/dashboard/generate
//           → AI Service cleans data, computes stats, builds Plotly charts
//           → Charts rendered instantly via <DatasetDashboard> (iframe-based, no dangerouslySetInnerHTML)
//
// Phase 2 — AI Report (Gemini LLM)
//   Step 3: Prompt textarea appears below the dashboard
//   Step 4: User clicks "Generate Report"  → POST /api/report/generate
//           → AI Service embeds data into ChromaDB, calls Gemini, compiles HTML report
//           → User redirected to /report/:id
//
// State machine:
//   'idle'          → no file selected yet
//   'uploading'     → file upload in progress
//   'uploaded'      → file stored, fileId known, dashboard not yet fetched
//   'dashLoading'   → POST /api/dashboard/generate in progress (spinner)
//   'dashReady'     → charts loaded, prompt can be entered
//   'generating'    → POST /api/report/generate in progress
//   'done'          → report created, navigating away
//
// API calls:
//   POST /api/upload                  (uploadDataset in upload.js)
//   POST /api/dashboard/generate      (generateDashboard in report.js)
//   POST /api/report/generate         (generateReport in report.js)

import { useState }         from 'react'
import { useNavigate }      from 'react-router-dom'
import Layout               from '../components/Layout'
import UploadButton         from '../components/upload/UploadButton'
import UploadProgress       from '../components/upload/UploadProgress'
import PromptInput          from '../components/PromptInput'
import Loader               from '../components/Loader'
import DatasetDashboard     from '../components/DatasetDashboard'
import { uploadDataset, getUploadedDatasets }    from '../services/upload'
import { generateDashboard, generateReport } from '../services/report'
import {
  CheckCircle2, Sparkles, AlertCircle,
  RefreshCcw, BarChart2, ArrowRight, Database,
} from 'lucide-react'
import toast from 'react-hot-toast'

// Step indicator config — drives the top progress bar
const STEPS = [
  { label: 'Upload Dataset' },
  { label: 'View Dashboard' },
  { label: 'Enter Prompt'   },
  { label: 'Generate Report' },
]

export default function Upload() {
  const navigate = useNavigate()

  // ── File upload state ───────────────────────────────────────────────────
  const [file,           setFile]           = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus,   setUploadStatus]   = useState('idle')   // idle | uploading | done | error
  const [fileId,         setFileId]         = useState(null)

  // ── Dashboard state (Phase 1) ───────────────────────────────────────────
  const [dashLoading,    setDashLoading]    = useState(false)
  const [dashData,       setDashData]       = useState(null)     // response from /api/dashboard/generate
  const [dashError,      setDashError]      = useState('')

  // ── Report generation state (Phase 2) ──────────────────────────────────
  const [prompt,         setPrompt]         = useState('')
  const [generating,     setGenerating]     = useState(false)
  const [genError,       setGenError]       = useState('')

  // Previous uploads state
  const [prevDatasets,   setPrevDatasets]   = useState([])
  const [showPrev,       setShowPrev]       = useState(false)
  const [loadingPrev,    setLoadingPrev]    = useState(false)

  // Derived flags
  const isUploaded  = uploadStatus === 'done' && fileId !== null
  const hasDashboard = dashData !== null
  const canDash     = isUploaded && !dashLoading && !hasDashboard
  const canGenerate = hasDashboard && prompt.trim().length >= 5 && !generating

  // Current active step index (0-based) for the progress bar
  const activeStep = !isUploaded ? 0
    : !hasDashboard             ? 1
    : !generating               ? 2
    :                             3

  // ── Step 1: File selected → upload immediately ──────────────────────────
  async function handleFileSelect(selectedFile) {
    setFile(selectedFile)
    setUploadProgress(0)
    setUploadStatus('uploading')
    setFileId(null)
    setDashData(null)
    setDashError('')
    setGenError('')
    setPrompt('')

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

  // Load previous uploads
  async function handleLoadPrevious() {
    setLoadingPrev(true)
    try {
      const data = await getUploadedDatasets()
      setPrevDatasets(data)
      setShowPrev(!showPrev)
    } catch (err) {
      toast.error("Failed to load previous datasets")
    } finally {
      setLoadingPrev(false)
    }
  }

  // Select a previously uploaded dataset
  function handleSelectPrevious(dataset) {
    setFile({ name: dataset.filename, size: dataset.file_size })
    setFileId(dataset.id)
    setUploadStatus('done')
    setShowPrev(false)
    toast.success(`Selected: "${dataset.filename}"`)
  }

  // ── Step 2: Generate Dataset Dashboard (Phase 1, no LLM) ───────────────
  async function handleGenerateDashboard() {
    if (!canDash) return
    setDashLoading(true)
    setDashError('')

    try {
      const data = await generateDashboard(fileId)
      setDashData(data)
      toast.success('Dataset dashboard generated!')
    } catch (err) {
      const msg = err.response?.data?.detail ?? 'Dashboard generation failed. Please try again.'
      setDashError(msg)
      toast.error('Dashboard generation failed.')
    } finally {
      setDashLoading(false)
    }
  }

  // ── Step 4: Generate Full AI Report (Phase 2, Gemini LLM) ──────────────
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

  // ── Reset: start over with a new file ──────────────────────────────────
  function handleReset() {
    setFile(null)
    setUploadProgress(0)
    setUploadStatus('idle')
    setFileId(null)
    setDashData(null)
    setDashError('')
    setDashLoading(false)
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
            Upload your dataset, explore the instant dashboard, then generate a deep AI-powered report.
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

          {/* ── STEP 1: Upload ─────────────────────────────────────────── */}
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
                <UploadButton onFileSelect={handleFileSelect} disabled={false} />
                
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '8px 0' }}>
                  <div style={{ flex: 1, height: 1, background: 'var(--border-light)' }}></div>
                  <span style={{ padding: '0 12px', fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>OR</span>
                  <div style={{ flex: 1, height: 1, background: 'var(--border-light)' }}></div>
                </div>

                <div style={{ textAlign: 'center' }}>
                  <button
                    onClick={handleLoadPrevious}
                    disabled={loadingPrev}
                    className="btn-secondary"
                    style={{ padding: '8px 18px', fontSize: '0.82rem', display: 'inline-flex', alignItems: 'center', gap: 6 }}
                  >
                    <Database size={14} />
                    {loadingPrev ? "Loading datasets..." : "Choose from Previously Uploaded"}
                  </button>
                </div>

                {showPrev && (
                  <div 
                    className="glass-card" 
                    style={{ 
                      marginTop: 12, 
                      padding: 16, 
                      maxHeight: 220, 
                      overflowY: 'auto', 
                      display: 'flex', 
                      flexDirection: 'column', 
                      gap: 8,
                      border: '1.5px solid var(--border-light)'
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-light)', paddingBottom: 6 }}>
                      <span>Dataset Filename</span>
                      <span>Action</span>
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
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'space-between', 
                            padding: '6px 8px', 
                            borderRadius: 8,
                            background: 'var(--bg-elevated)',
                            fontSize: '0.8rem'
                          }}
                        >
                          <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '75%' }}>
                            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{ds.filename}</span>
                            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                              {(ds.file_size / 1024).toFixed(1)} KB &bull; {new Date(ds.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <button
                            onClick={() => handleSelectPrevious(ds)}
                            className="btn-primary"
                            style={{ padding: '4px 10px', fontSize: '0.7rem' }}
                          >
                            Select
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            )}

            {(uploadStatus === 'uploading' || uploadStatus === 'done' || uploadStatus === 'error') && file && (
              <UploadProgress
                fileName={file.name}
                fileSize={file.size}
                progress={uploadProgress}
                status={uploadStatus}
              />
            )}
          </div>

          {/* ── STEP 2: Generate Dashboard (Phase 1) ──────────────────── */}
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

            {/* Error alert */}
            {dashError && (
              <div className="alert alert-error" style={{ marginBottom: 16 }}>
                <AlertCircle size={16} style={{ flexShrink: 0 }} />
                <span>{dashError}</span>
              </div>
            )}

            {/* Loading state */}
            {dashLoading && (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14, padding: '20px 0' }}>
                <Loader size="md" />
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Analysing dataset…</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    Computing statistics and generating charts. No AI model is being called.
                  </div>
                </div>
              </div>
            )}

            {/* Button (shown before dashboard is loaded) */}
            {!dashLoading && !hasDashboard && (
              <div>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.6 }}>
                  InsightAI will immediately clean your dataset, calculate statistics, and produce
                  interactive charts — without calling any AI model.
                </p>
                <button
                  id="generate-dashboard-btn"
                  onClick={handleGenerateDashboard}
                  disabled={!canDash}
                  className="btn-primary"
                  style={{ padding: '11px 26px', fontSize: '0.92rem' }}
                >
                  <BarChart2 size={17} />
                  Generate Dashboard
                </button>
              </div>
            )}

            {/* Inline charts (shown once dashboard data arrives) */}
            {!dashLoading && hasDashboard && (
              <DatasetDashboard data={dashData} />
            )}
          </div>

          {/* ── STEP 3 & 4: Prompt + Generate Report (Phase 2) ─────────── */}
          <div
            className="glass-card"
            style={{
              padding: '24px',
              opacity: hasDashboard ? 1 : 0.45,
              pointerEvents: hasDashboard ? 'auto' : 'none',
              transition: 'opacity 0.3s ease',
            }}
          >
            <div className="section-title" style={{ marginBottom: 6 }}>Step 3 &amp; 4 — AI Report Generation</div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: 18 }}>
              Describe the analysis you need. InsightAI will use Gemini to produce a comprehensive report.
            </p>

            {/* Prompt input (Step 3) */}
            <PromptInput
              value={prompt}
              onChange={setPrompt}
              disabled={!hasDashboard || generating}
              placeholder="e.g. Summarise key trends and generate a monthly performance breakdown…"
            />
            {prompt.trim().length > 0 && prompt.trim().length < 5 && (
              <p style={{ marginTop: 8, fontSize: '0.78rem', color: 'var(--warning)' }}>
                Prompt must be at least 5 characters.
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
                  style={{ padding: '12px 28px', fontSize: '0.95rem' }}
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