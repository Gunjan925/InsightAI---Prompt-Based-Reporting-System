// pages/ChatPage.jsx
// Interactive Chatbot Dashboard Page for dataset QA.
// Features:
//   - MySQL Database Persistence for Chat Sessions & Messages per document
//   - Dataset Selector (switch between uploaded files)
//   - Saved chat sessions list loaded directly from MySQL for the current document
//   - Standard chatbot UI (message history, prompt suggestions, user/bot bubbles, typing indicator)

import { useState, useEffect, useRef } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import Loader from '../components/Loader'
import { getUploadedDatasets } from '../services/upload'
import { getChatSessions, createChatSession, deleteChatSession, askChatQuestion } from '../services/chat'
import {
  MessageSquare, Send, Plus, Trash2, Database,
  Bot, User, Sparkles, ArrowLeft, RefreshCw, FileText,
  ChevronRight, CheckCircle2
} from 'lucide-react'
import toast from 'react-hot-toast'

/**
 * Converts basic Markdown to safe HTML for chat bot responses.
 * Handles: bold, italic, bullet lists, numbered lists, headers, code blocks, line breaks.
 */
function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    // Code blocks — bg uses a semi-transparent overlay that works on both themes
    .replace(/```[\w]*\n?([\s\S]*?)```/g, '<pre style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.15);padding:10px 14px;border-radius:8px;overflow-x:auto;font-size:0.82rem;margin:8px 0;"><code>$1</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code style="background:rgba(99,102,241,0.12);padding:2px 6px;border-radius:4px;font-size:0.82rem;color:var(--primary);">$1</code>')
    // H3 — inherit color from bubble so works in both light and dark
    .replace(/^###\s+(.+)$/gm, '<h3 style="font-size:0.95rem;font-weight:700;color:inherit;margin:10px 0 4px;">$1</h3>')
    // H2
    .replace(/^##\s+(.+)$/gm, '<h2 style="font-size:1.05rem;font-weight:800;color:inherit;margin:12px 0 5px;border-bottom:1px solid rgba(99,102,241,0.2);padding-bottom:4px;">$1</h2>')
    // H1
    .replace(/^#\s+(.+)$/gm, '<h1 style="font-size:1.15rem;font-weight:800;color:inherit;margin:12px 0 6px;">$1</h1>')
    // Bold — inherit color, just heavier weight
    .replace(/\*\*(.+?)\*\*/g, '<strong style="font-weight:700;color:inherit;">$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em style="font-style:italic;opacity:0.8;">$1</em>')
    // Bullet list lines
    .replace(/((?:^[ \t]*[-*+][ \t]+.+\n?)+)/gm, (block) => {
      const items = block.trim().split('\n').map(line =>
        `<li style="margin-bottom:5px;padding-left:4px;color:inherit;">${line.replace(/^[ \t]*[-*+][ \t]+/, '').trim()}</li>`
      ).join('')
      return `<ul style="margin:6px 0 6px 16px;padding:0;list-style:disc;color:inherit;">${items}</ul>`
    })
    // Numbered list lines
    .replace(/((?:^[ \t]*\d+\.[ \t]+.+\n?)+)/gm, (block) => {
      const items = block.trim().split('\n').map(line =>
        `<li style="margin-bottom:5px;padding-left:4px;color:inherit;">${line.replace(/^[ \t]*\d+\.[ \t]+/, '').trim()}</li>`
      ).join('')
      return `<ol style="margin:6px 0 6px 18px;padding:0;list-style:decimal;color:inherit;">${items}</ol>`
    })
    // Double newline => paragraph gap
    .replace(/\n\n/g, '<br/><br/>')
    // Single newline
    .replace(/\n/g, '<br/>')
  return html
}

/** Returns current time formatted as HH:MM AM/PM IST */
function getNowIST() {
  return new Date().toLocaleTimeString('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  }) + ' IST'
}

/** Formats any Date object or string (like MySQL '14:45') into IST */
function formatISTMessageTime(timestamp) {
  if (!timestamp) return ''

  // If already formatted with 'IST', return directly
  if (typeof timestamp === 'string' && timestamp.includes('IST')) {
    return timestamp
  }

  // Handle MySQL 24h format "14:45" by interpreting as UTC time today
  if (typeof timestamp === 'string' && /^\d{2}:\d{2}$/.test(timestamp)) {
    const today = new Date().toISOString().split('T')[0]
    const dateObj = new Date(`${today}T${timestamp}:00Z`)
    return dateObj.toLocaleTimeString('en-IN', {
      timeZone: 'Asia/Kolkata',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }) + ' IST'
  }

  return timestamp
}

// Default prompt suggestion chips
const SUGGESTIONS = [
  "Summarise the overall metrics and key attributes of this dataset.",
  "Identify the top 3 trends or patterns in the data.",
  "Find any anomalies or extreme outliers in numerical columns.",
  "What is the average and range for the main metrics?"
]

export default function ChatPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  // ── State ──
  const [datasets, setDatasets] = useState([])
  const [selectedFileId, setSelectedFileId] = useState(null)
  const [selectedDataset, setSelectedDataset] = useState(null)
  const [loadingDatasets, setLoadingDatasets] = useState(true)

  // Chat sessions loaded from MySQL database
  const [sessions, setSessions] = useState([])
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [loadingSessions, setLoadingSessions] = useState(false)

  // Active chat input state
  const [inputQuery, setInputQuery] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  const messagesEndRef = useRef(null)

  // ── 1. Load Uploaded Datasets on Mount ──
  useEffect(() => {
    async function loadData() {
      setLoadingDatasets(true)
      try {
        const list = await getUploadedDatasets()
        setDatasets(list)

        const urlFileId = searchParams.get('fileId')
        if (urlFileId && list.some(d => d.id === parseInt(urlFileId, 10))) {
          const targetId = parseInt(urlFileId, 10)
          setSelectedFileId(targetId)
          setSelectedDataset(list.find(d => d.id === targetId))
        } else if (list.length > 0) {
          setSelectedFileId(list[0].id)
          setSelectedDataset(list[0])
        }
      } catch (err) {
        toast.error("Failed to load uploaded datasets.")
      } finally {
        setLoadingDatasets(false)
      }
    }
    loadData()
  }, [searchParams])

  // ── 2. Load Chat Sessions from MySQL when selectedFileId changes ──
  useEffect(() => {
    if (!selectedFileId) return

    async function loadDbSessions() {
      setLoadingSessions(true)
      try {
        const dbSessions = await getChatSessions(selectedFileId)
        setSessions(dbSessions)

        if (dbSessions.length > 0) {
          setActiveSessionId(dbSessions[0].id)
        } else {
          // Create initial DB session if none exist for this file
          const newSess = await createChatSession(selectedFileId, "New Discussion")
          setSessions([newSess])
          setActiveSessionId(newSess.id)
        }
      } catch (err) {
        console.error("Failed to load chat sessions from DB:", err)
      } finally {
        setLoadingSessions(false)
      }
    }
    loadDbSessions()
  }, [selectedFileId])

  // ── Auto-scroll to bottom of chat thread ──
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [sessions, activeSessionId, isTyping])

  // ── Helpers ──
  const getActiveSession = () => {
    return sessions.find(s => s.id === activeSessionId) || null
  }

  const handleCreateNewSession = async () => {
    if (!selectedFileId) return
    try {
      const newSess = await createChatSession(selectedFileId, "New Discussion")
      setSessions([newSess, ...sessions])
      setActiveSessionId(newSess.id)
      toast.success("New chat thread created")
    } catch (err) {
      toast.error("Failed to create new chat thread")
    }
  }

  const handleDatasetChange = (ds) => {
    setSelectedFileId(ds.id)
    setSelectedDataset(ds)
  }

  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation()
    try {
      await deleteChatSession(sessionId)
      const filtered = sessions.filter(s => s.id !== sessionId)
      setSessions(filtered)

      if (activeSessionId === sessionId) {
        if (filtered.length > 0) {
          setActiveSessionId(filtered[0].id)
        } else {
          handleCreateNewSession()
        }
      }
      toast.success("Chat thread deleted")
    } catch (err) {
      toast.error("Failed to delete chat thread")
    }
  }

  // ── Send Message & Persist to MySQL ──
  const handleSendMessage = async (queryText = inputQuery) => {
    const text = queryText.trim()
    if (!text || !selectedFileId || !selectedDataset || isTyping) return

    const activeSess = getActiveSession()
    const targetSessionId = activeSess ? activeSess.id : null

    // Optimistic user message render
    const userMsg = {
      id: `temp_user_${Date.now()}`,
      sender: 'user',
      text: text,
      timestamp: getNowIST()
    }

    setSessions(prev => prev.map(s => {
      if (s.id === targetSessionId) {
        const title = s.messages.length === 0 ? (text.slice(0, 30) + '...') : s.title
        return { ...s, title, messages: [...s.messages, userMsg] }
      }
      return s
    }))

    setInputQuery('')
    setIsTyping(true)

    try {
      // Call Backend Ask Endpoint (Saves user & bot message to MySQL)
      const res = await askChatQuestion(selectedFileId, text, targetSessionId)

      const botMsg = {
        id: `temp_bot_${Date.now()}`,
        sender: 'bot',
        text: res.response || "No response generated.",
        timestamp: getNowIST()
      }

      setSessions(prev => prev.map(s => {
        if (s.id === (res.session_id || targetSessionId)) {
          return { ...s, id: res.session_id || s.id, messages: [...s.messages, botMsg] }
        }
        return s
      }))

      if (res.session_id) setActiveSessionId(res.session_id)
    } catch (err) {
      toast.error("Failed to fetch response from AI chatbot.")
      const errorMsg = {
        id: `temp_err_${Date.now()}`,
        sender: 'bot',
        text: "Sorry, I encountered an error answering your query. Please ensure the dataset file is valid and try again.",
        timestamp: getNowIST()
      }
      setSessions(prev => prev.map(s => {
        if (s.id === targetSessionId) {
          return { ...s, messages: [...s.messages, errorMsg] }
        }
        return s
      }))
    } finally {
      setIsTyping(false)
    }
  }

  const activeSession = getActiveSession()
  const activeMessages = activeSession ? activeSession.messages : []

  return (
    <Layout>
      <div style={{ display: 'flex', gap: 20, height: 'calc(100vh - 120px)', minHeight: 600 }}>

        {/* ── LEFT SIDEBAR: Datasets & MySQL Saved Chats List ── */}
        <div
          className="glass-card"
          style={{
            width: 280,
            flexShrink: 0,
            display: 'flex',
            flexDirection: 'column',
            padding: 16,
            gap: 16,
            overflow: 'hidden'
          }}
        >
          {/* Top Title & Back */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ fontWeight: 800, fontSize: '0.95rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <MessageSquare size={18} color="var(--primary)" />
              Dataset Chatbot
            </div>
            <button
              onClick={() => navigate('/upload')}
              className="btn-secondary"
              style={{ padding: '4px 8px', fontSize: '0.72rem' }}
              title="Return to upload page"
            >
              <ArrowLeft size={13} /> Upload
            </button>
          </div>

          {/* Dataset Selector Dropdown */}
          <div>
            <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: 6 }}>
              Select Active Dataset
            </label>
            {loadingDatasets ? (
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Loading files...</div>
            ) : datasets.length === 0 ? (
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>No datasets found.</div>
            ) : (
              <select
                value={selectedFileId || ''}
                onChange={(e) => {
                  const ds = datasets.find(d => d.id === parseInt(e.target.value, 10))
                  if (ds) handleDatasetChange(ds)
                }}
                className="input-field"
                style={{ width: '100%', fontSize: '0.8rem', padding: '8px 10px' }}
              >
                {datasets.map(ds => (
                  <option key={ds.id} value={ds.id}>
                    📄 {ds.filename}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* New Chat Button */}
          <button
            onClick={handleCreateNewSession}
            disabled={!selectedFileId}
            className="btn-primary"
            style={{ width: '100%', padding: '9px 14px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
          >
            <Plus size={15} /> New Chat Thread
          </button>

          {/* Saved Sessions from MySQL Database */}
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', padding: '4px 2px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Saved DB Threads ({sessions.length})</span>
              {loadingSessions && <Loader size="sm" />}
            </div>

            {sessions.length === 0 ? (
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '8px 4px' }}>
                No saved chats for this dataset yet.
              </div>
            ) : (
              sessions.map(session => {
                const isActive = session.id === activeSessionId
                return (
                  <div
                    key={session.id}
                    onClick={() => setActiveSessionId(session.id)}
                    style={{
                      padding: '8px 10px',
                      borderRadius: 10,
                      cursor: 'pointer',
                      background: isActive ? 'var(--primary-light)' : 'var(--bg-elevated)',
                      border: `1.5px solid ${isActive ? 'var(--primary)' : 'transparent'}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <div style={{ overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis', flex: 1 }}>
                      <div style={{ fontSize: '0.78rem', fontWeight: isActive ? 700 : 500, color: 'var(--text-primary)' }}>
                        {session.title || 'Untitled Discussion'}
                      </div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 2 }}>
                        {session.messages ? session.messages.length : 0} messages
                      </div>
                    </div>

                    <button
                      onClick={(e) => handleDeleteSession(session.id, e)}
                      style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 3 }}
                      title="Delete saved discussion from MySQL"
                    >
                      <Trash2 size={13} color="#ef4444" />
                    </button>
                  </div>
                )
              })
            )}
          </div>
        </div>

        {/* ── RIGHT MAIN PANEL: Interactive Chatbot Window ── */}
        <div
          className="glass-card"
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            padding: 0,
            overflow: 'hidden'
          }}
        >
          {/* Chat Header */}
          <div
            style={{
              padding: '16px 24px',
              borderBottom: '1px solid var(--border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'var(--bg-surface)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 38, height: 38, borderRadius: 10, background: 'linear-gradient(135deg, var(--primary), var(--secondary))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={22} color="#fff" />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)' }}>
                  {selectedDataset ? selectedDataset.filename : 'Select a Dataset'}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>
                  {selectedDataset ? `${(selectedDataset.file_size / 1024).toFixed(1)} KB • Stored in MySQL Database` : 'No dataset selected'}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '0.72rem', padding: '4px 10px', borderRadius: 20, background: 'var(--success-light, #dcfce7)', color: 'var(--success, #16a34a)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
                <CheckCircle2 size={12} /> Persisted in MySQL Database
              </span>
            </div>
          </div>

          {/* Chat Messages Thread */}
          <div
            style={{
              flex: 1,
              padding: '24px',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: 16,
              background: 'var(--bg-base)'
            }}
          >
            {activeMessages.length === 0 ? (
              <div style={{ margin: 'auto', maxWidth: 480, textAlign: 'center', padding: '20px 0' }}>
                <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--primary-light)', margin: '0 auto 16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Sparkles size={28} color="var(--primary)" />
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: 6 }}>
                  Ask questions about "{selectedDataset?.filename}"
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: 24 }}>
                  Our AI assistant uses Vector Search (RAG) to query the actual rows of your dataset and answer questions accurately. All chat conversations are stored in MySQL.
                </p>

                {/* Prompt Suggestions */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {SUGGESTIONS.map((sug, i) => (
                    <button
                      key={i}
                      onClick={() => handleSendMessage(sug)}
                      className="btn-secondary"
                      style={{
                        padding: '10px 14px',
                        fontSize: '0.8rem',
                        textAlign: 'left',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        borderRadius: 10
                      }}
                    >
                      <span>{sug}</span>
                      <ChevronRight size={14} color="var(--text-muted)" />
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              activeMessages.map((msg) => {
                const isUser = msg.sender === 'user'
                return (
                  <div
                    key={msg.id}
                    style={{
                      display: 'flex',
                      flexDirection: isUser ? 'row-reverse' : 'row',
                      gap: 12,
                      alignItems: 'flex-start'
                    }}
                  >
                    {/* Avatar */}
                    <div
                      style={{
                        width: 32,
                        height: 32,
                        borderRadius: '50%',
                        background: isUser ? 'var(--primary)' : 'var(--secondary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        flexShrink: 0
                      }}
                    >
                      {isUser ? <User size={16} /> : <Bot size={16} />}
                    </div>

                    {/* Message Bubble */}
                    <div
                      style={{
                        maxWidth: '75%',
                        padding: '12px 16px',
                        borderRadius: 14,
                        background: isUser ? 'var(--primary)' : 'var(--bg-surface)',
                        color: isUser ? '#ffffff' : 'var(--text-primary)',
                        border: isUser ? 'none' : '1px solid var(--border-light)',
                        boxShadow: 'var(--shadow-sm)',
                        fontSize: '0.875rem',
                        lineHeight: 1.6,
                      }}
                    >
                      {isUser ? (
                        // User messages: plain text
                        <span style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</span>
                      ) : (
                        // Bot messages: render markdown as formatted HTML
                        <div
                          dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.text) }}
                          style={{ wordBreak: 'break-word' }}
                        />
                      )}

                      <div style={{ fontSize: '0.68rem', opacity: 0.65, marginTop: 8, textAlign: isUser ? 'right' : 'left', fontStyle: 'italic' }}>
                        {formatISTMessageTime(msg.timestamp)}
                      </div>
                    </div>
                  </div>
                )
              })
            )}

            {/* Typing Indicator */}
            {isTyping && (
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
                  <Bot size={16} />
                </div>
                <div style={{ padding: '10px 16px', borderRadius: 14, background: 'var(--bg-surface)', border: '1px solid var(--border-light)', fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Loader size="sm" />
                  <span>Searching dataset context &amp; saving to MySQL DB...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Dock */}
          <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)', background: 'var(--bg-surface)' }}>
            {/* Helper hint */}
            <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: 6, textAlign: 'right' }}>
              Press <kbd style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 4, padding: '1px 5px', fontSize: '0.65rem' }}>Enter</kbd> to send &nbsp;·&nbsp;
              <kbd style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 4, padding: '1px 5px', fontSize: '0.65rem' }}>Shift+Enter</kbd> for new line
            </p>
            <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
              {/* Auto-growing textarea */}
              <textarea
                value={inputQuery}
                onChange={(e) => {
                  setInputQuery(e.target.value)
                  // Auto-grow: reset height then expand to scrollHeight
                  e.target.style.height = 'auto'
                  e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSendMessage()
                    // Reset height after sending
                    e.target.style.height = 'auto'
                  }
                }}
                disabled={!selectedFileId || isTyping}
                placeholder={selectedDataset ? `Ask any question about ${selectedDataset.filename}…` : 'Select a dataset to begin...'}
                className="input-field"
                rows={1}
                style={{
                  flex: 1,
                  padding: '11px 16px',
                  fontSize: '0.88rem',
                  borderRadius: 12,
                  resize: 'none',
                  overflow: 'hidden',
                  lineHeight: 1.5,
                  minHeight: 46,
                  maxHeight: 160,
                }}
              />

              <button
                onClick={() => handleSendMessage()}
                disabled={!selectedFileId || !inputQuery.trim() || isTyping}
                className="btn-primary"
                style={{ padding: '11px 20px', borderRadius: 12, display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0, height: 46 }}
              >
                <Send size={16} />
                <span>Send</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
