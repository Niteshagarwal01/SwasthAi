export function RiskBadge({ risk }) {
  const cfg = {
    critical: { bg: 'rgba(255,59,92,0.12)', color: '#FF6B85', border: 'rgba(255,59,92,0.2)', dot: '#FF3B5C', label: 'Critical', pulse: true },
    moderate: { bg: 'rgba(245,166,35,0.1)',  color: '#F5C964', border: 'rgba(245,166,35,0.18)', dot: '#F5A623', label: 'Moderate', pulse: false },
    mild:     { bg: 'rgba(16,240,160,0.1)',  color: '#4AE5A0', border: 'rgba(16,240,160,0.18)', dot: '#10F0A0', label: 'Mild', pulse: false },
  }
  const c = cfg[risk] || cfg.mild

  return (
    <span className="badge" style={{ background: c.bg, color: c.color, border: `1px solid ${c.border}` }}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.pulse ? 'animate-pulse' : ''}`}
            style={{ background: c.dot, boxShadow: c.pulse ? `0 0 6px ${c.dot}80` : 'none' }} />
      {c.label}
    </span>
  )
}

export function ChannelBadge({ channel }) {
  return channel === 'whatsapp' ? (
    <span className="badge" style={{ background: 'rgba(16,240,160,0.08)', color: '#4AE5A0', border: '1px solid rgba(16,240,160,0.15)' }}>
      💬 WhatsApp
    </span>
  ) : (
    <span className="badge" style={{ background: 'rgba(99,102,241,0.08)', color: '#818CF8', border: '1px solid rgba(99,102,241,0.15)' }}>
      📞 Call
    </span>
  )
}
