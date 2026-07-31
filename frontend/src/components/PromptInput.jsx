// components/PromptInput.jsx
// Natural language prompt input component used on the Upload page.
// Features:
//   - Textarea with live character counter (min 5 / max 1000 chars)
//   - Clickable example prompt chips to pre-fill the textarea
//   - Visual warning when approaching the character limit
// Props:
//   value      (string)  – controlled textarea value
//   onChange   (fn)      – called with new string value on every keystroke
//   disabled   (bool)    – disables interaction during report generation
//   placeholder (string) – custom placeholder text

const EXAMPLE_PROMPTS = [
  'Summarize the key trends and insights in this dataset',
  'Identify outliers and anomalies and explain their impact',
  'Generate a sales performance report with monthly breakdown',
  'Provide a statistical summary with correlation analysis',
  'Highlight the top 5 products by revenue and their growth',
]

const MAX_LENGTH = 1000

export default function PromptInput({ value, onChange, disabled = false, placeholder }) {
  const remaining = MAX_LENGTH - value.length
  const isNearLimit = remaining < 100

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>

      {/* Example prompts */}
      <div>
        <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 8 }}>
          💡 Example prompts (click to use):
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {EXAMPLE_PROMPTS.map((p) => (
            <button
              key={p}
              type="button"
              disabled={disabled}
              onClick={() => onChange(p)}
              style={{
                padding: '4px 12px',
                borderRadius: 99,
                border: '1px solid var(--border)',
                background: 'var(--bg-elevated)',
                color: 'var(--text-secondary)',
                fontSize: '0.75rem',
                cursor: disabled ? 'not-allowed' : 'pointer',
                fontFamily: 'inherit',
                textAlign: 'left',
              }}
              title={p}
            >
              {p.length > 45 ? p.slice(0, 45) + '…' : p}
            </button>
          ))}
        </div>
      </div>

      {/* Textarea */}
      <div style={{ position: 'relative' }}>
        <textarea
          id="prompt-textarea"
          value={value}
          onChange={(e) => onChange(e.target.value.slice(0, MAX_LENGTH))}
          disabled={disabled}
          placeholder={placeholder ?? 'Describe the type of analysis or report you want to generate…'}
          rows={5}
          maxLength={MAX_LENGTH}
          style={{
            width: '100%',
            padding: '12px 14px',
            paddingBottom: 32,
            background: 'var(--bg-elevated)',
            color: 'var(--text-primary)',
            border: `1.5px solid ${isNearLimit ? 'var(--warning)' : 'var(--border)'}`,
            borderRadius: 12,
            fontSize: '0.9rem',
            fontFamily: 'inherit',
            resize: 'vertical',
            outline: 'none',
            lineHeight: 1.6,
            cursor: disabled ? 'not-allowed' : 'text',
            opacity: disabled ? 0.7 : 1,
          }}
          onFocus={(e) => {
            if (!disabled) e.target.style.borderColor = 'var(--primary)'
          }}
          onBlur={(e) => {
            e.target.style.borderColor = isNearLimit ? 'var(--warning)' : 'var(--border)'
          }}
          aria-label="Report generation prompt"
          aria-describedby="prompt-char-count"
        />

        {/* Character counter */}
        <div
          id="prompt-char-count"
          style={{
            position: 'absolute',
            bottom: 10,
            right: 12,
            fontSize: '0.72rem',
            fontWeight: 600,
            color: isNearLimit ? 'var(--warning)' : 'var(--text-muted)',
            pointerEvents: 'none',
          }}
        >
          {value.length} / {MAX_LENGTH}
        </div>
      </div>
    </div>
  )
}