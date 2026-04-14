import { AlertTriangle } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const SEV = {
  critical: { bg: 'rgba(255,59,92,0.06)',  border: 'rgba(255,59,92,0.15)',  text: '#FF6B85', dot: '#FF3B5C',  glow: 'rgba(255,59,92,0.08)' },
  high:     { bg: 'rgba(255,140,50,0.06)', border: 'rgba(255,140,50,0.15)', text: '#FF9E5C', dot: '#FF8C32',  glow: 'rgba(255,140,50,0.08)' },
  medium:   { bg: 'rgba(245,166,35,0.06)', border: 'rgba(245,166,35,0.12)', text: '#F5C964', dot: '#F5A623',  glow: 'rgba(245,166,35,0.06)' },
  low:      { bg: 'rgba(99,102,241,0.06)', border: 'rgba(99,102,241,0.12)', text: '#818CF8', dot: '#6366F1',  glow: 'rgba(99,102,241,0.06)' },
}

export default function AlertCard({ alert }) {
  const s = SEV[alert.severity] || SEV.medium

  return (
    <div className="rounded-2xl p-5 relative overflow-hidden transition-all duration-500 hover:scale-[1.01]"
         style={{ background: s.bg, border: `1px solid ${s.border}` }}>
      {/* Volumetric glow */}
      <div className="absolute top-0 right-0 w-32 h-32 rounded-full pointer-events-none"
           style={{ background: `radial-gradient(circle, ${s.glow}, transparent 70%)` }} />

      <div className="flex items-start gap-4 relative z-10">
        <div className="mt-0.5 w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
             style={{ background: s.bg, border: `1px solid ${s.border}` }}>
          <AlertTriangle className="w-4 h-4" style={{ color: s.text }} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: s.dot, boxShadow: `0 0 8px ${s.dot}80` }} />
            <span className="text-[10px] font-bold uppercase tracking-[0.12em]" style={{ color: s.text }}>
              {alert.severity} severity
            </span>
            <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
              · {alert.created_at ? formatDistanceToNow(new Date(alert.created_at), { addSuffix: true }) : ''}
            </span>
          </div>

          <h3 className="text-white font-semibold text-[13px] mb-1">
            {alert.region} — {(alert.symptom_cluster || []).join(', ')}
          </h3>

          <p className="text-[12px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
            {alert.description}
          </p>

          <div className="flex items-center gap-4 mt-3">
            <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
              📊 {alert.case_count} cases
            </span>
            {alert.state && (
              <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>📍 {alert.state}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
