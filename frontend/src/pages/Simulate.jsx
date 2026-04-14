import { useState, useRef, useEffect } from 'react'
import { Send, RotateCcw, User, Bot, Stethoscope, Loader2 } from 'lucide-react'
import { simulateWhatsApp } from '../services/api'

export default function Simulate() {
  const [phone] = useState('+91' + Math.floor(9000000000 + Math.random() * 999999999))
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const msgEnd = useRef(null)

  useEffect(() => { msgEnd.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const text = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)

    try {
      const res = await simulateWhatsApp(phone, text)
      setMessages(prev => [...prev, { role: 'assistant', content: res.reply }])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: '⚠️ Error connecting to AI engine. Is the backend running?' }])
    }
    setLoading(false)
  }

  const handleReset = async () => {
    setMessages([])
    await simulateWhatsApp(phone, 'reset').catch(() => {})
  }

  const PRESETS = [
    { label: '🤒 Fever Hindi', msg: 'mujhe tez bukhar hai aur sar dard ho raha hai' },
    { label: '🫁 Breathing', msg: 'I have difficulty breathing and chest tightness' },
    { label: '🤢 Stomach', msg: 'pet mein bahut dard hai aur ulti ho rahi hai' },
    { label: '⚠️ Critical', msg: 'chest pain severe, left arm numb, sweating' },
  ]

  return (
    <div className="relative min-h-screen">
      <div className="mesh-bg" />
      <div className="relative z-10 p-6 lg:p-8 max-w-[1600px] mx-auto">

        <div className="animate-fade-in mb-6">
          <h1 className="text-[26px] font-extrabold text-white tracking-tight">WhatsApp Simulator</h1>
          <p className="text-[13px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Test the AI health engine without a real WhatsApp account · Phone: {phone}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Chat window */}
          <div className="lg:col-span-2 bento p-0 flex flex-col" style={{ height: 'calc(100vh - 180px)' }}>
            {/* Chat header */}
            <div className="px-5 py-4 flex items-center gap-3" style={{ borderBottom: '1px solid var(--border-glass)' }}>
              <div className="w-9 h-9 rounded-full flex items-center justify-center"
                   style={{ background: 'var(--emerald-glow)', border: '1px solid rgba(16,240,160,0.15)' }}>
                <Stethoscope className="w-4 h-4" style={{ color: 'var(--emerald)' }} />
              </div>
              <div>
                <p className="text-[13px] font-semibold text-white">SwasthAI Bot</p>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" style={{ boxShadow: '0 0 4px rgba(16,240,160,0.6)' }} />
                  <span className="text-[10px]" style={{ color: 'var(--emerald)' }}>Online</span>
                </div>
              </div>
              <button onClick={handleReset} className="ml-auto btn-ghost text-[11px]">
                <RotateCcw className="w-3.5 h-3.5" /> New Chat
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-16">
                  <div className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center"
                       style={{ background: 'var(--surface-2)' }}>
                    <Stethoscope className="w-7 h-7" style={{ color: 'var(--text-muted)' }} />
                  </div>
                  <p className="text-[13px] mb-1" style={{ color: 'var(--text-secondary)' }}>Start a conversation</p>
                  <p className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
                    Type symptoms in Hindi or English, or use a preset below
                  </p>
                </div>
              )}
              {messages.map((m, i) => (
                <div key={i} className={`flex gap-3 animate-slide-up ${m.role === 'user' ? 'justify-end' : ''}`}>
                  {m.role === 'assistant' && (
                    <div className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center"
                         style={{ background: 'var(--emerald-glow)', border: '1px solid rgba(16,240,160,0.12)' }}>
                      <Bot className="w-3.5 h-3.5" style={{ color: 'var(--emerald)' }} />
                    </div>
                  )}
                  <div className="max-w-[70%] px-4 py-3 rounded-2xl text-[13px] leading-relaxed whitespace-pre-wrap"
                       style={{
                         background: m.role === 'user' ? 'rgba(99,102,241,0.15)' : 'var(--surface-2)',
                         border: `1px solid ${m.role === 'user' ? 'rgba(99,102,241,0.2)' : 'var(--border-glass)'}`,
                         color: 'var(--text-primary)',
                       }}>
                    {m.content}
                  </div>
                  {m.role === 'user' && (
                    <div className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center"
                         style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.2)' }}>
                      <User className="w-3.5 h-3.5" style={{ color: '#818CF8' }} />
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex gap-3 animate-fade-in">
                  <div className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center"
                       style={{ background: 'var(--emerald-glow)' }}>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" style={{ color: 'var(--emerald)' }} />
                  </div>
                  <div className="px-4 py-3 rounded-2xl" style={{ background: 'var(--surface-2)', border: '1px solid var(--border-glass)' }}>
                    <div className="flex gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={msgEnd} />
            </div>

            {/* Input */}
            <div className="p-4" style={{ borderTop: '1px solid var(--border-glass)' }}>
              <form onSubmit={e => { e.preventDefault(); handleSend() }} className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="Describe symptoms in Hindi or English..."
                  className="input-glass flex-1"
                  disabled={loading}
                />
                <button type="submit" disabled={loading || !input.trim()} className="btn-primary disabled:opacity-30">
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </div>

          {/* Presets & Info */}
          <div className="space-y-5">
            <div className="bento">
              <h3 className="text-[13px] font-semibold text-white mb-3">Quick Presets</h3>
              <div className="space-y-2">
                {PRESETS.map((p, i) => (
                  <button key={i} onClick={() => { setInput(p.msg); }}
                          className="w-full text-left px-4 py-2.5 rounded-xl text-[12px] transition-all duration-300"
                          style={{ background: 'var(--surface-1)', border: '1px solid var(--border-glass)', color: 'var(--text-secondary)' }}
                          onMouseEnter={e => { e.target.style.background = 'var(--surface-3)'; e.target.style.color = 'var(--text-primary)' }}
                          onMouseLeave={e => { e.target.style.background = 'var(--surface-1)'; e.target.style.color = 'var(--text-secondary)' }}>
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="bento">
              <h3 className="text-[13px] font-semibold text-white mb-2">How It Works</h3>
              <div className="space-y-3 text-[11px]" style={{ color: 'var(--text-muted)' }}>
                <div className="flex gap-3 items-start">
                  <span className="w-5 h-5 rounded-md flex items-center justify-center shrink-0 text-[10px] font-bold"
                        style={{ background: 'var(--surface-3)', color: 'var(--emerald)' }}>1</span>
                  <span>Describe your symptoms in Hindi or English</span>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="w-5 h-5 rounded-md flex items-center justify-center shrink-0 text-[10px] font-bold"
                        style={{ background: 'var(--surface-3)', color: 'var(--emerald)' }}>2</span>
                  <span>AI may ask 1-2 follow-up questions</span>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="w-5 h-5 rounded-md flex items-center justify-center shrink-0 text-[10px] font-bold"
                        style={{ background: 'var(--surface-3)', color: 'var(--emerald)' }}>3</span>
                  <span>Receive a health report with risk level, recommendations, and home care tips</span>
                </div>
              </div>
            </div>

            <div className="bento" style={{ background: 'rgba(255,59,92,0.04)', border: '1px solid rgba(255,59,92,0.1)' }}>
              <p className="text-[11px] leading-relaxed" style={{ color: '#FF6B85' }}>
                ⚠️ <strong>Disclaimer:</strong> This is an AI assistant for basic guidance only. 
                For any serious symptoms, please call 108 or visit your nearest hospital immediately.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
