import { useState } from 'react'
import { ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react'
import { RiskBadge, ChannelBadge } from './Badges'
import { formatDistanceToNow } from 'date-fns'

function CaseRow({ c, onClick, isOpen }) {
  return (
    <>
      <tr onClick={onClick}
          className="group transition-colors duration-300 cursor-pointer"
          style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
        <td className="py-3.5 px-5"><RiskBadge risk={c.risk_level} /></td>
        <td className="py-3.5 px-5"><ChannelBadge channel={c.channel} /></td>
        <td className="py-3.5 px-5 text-[12px] max-w-[200px] truncate" style={{ color: 'var(--text-secondary)' }}>
          {(c.symptoms || []).join(', ') || '—'}
        </td>
        <td className="py-3.5 px-5 text-[12px]" style={{ color: 'var(--text-muted)' }}>
          {c.state || c.region || '—'}
        </td>
        <td className="py-3.5 px-5 text-[12px] font-mono" style={{ color: 'var(--text-muted)' }}>
          {c.created_at ? formatDistanceToNow(new Date(c.created_at), { addSuffix: true }) : '—'}
        </td>
        <td className="py-3.5 px-5">
          {c.seek_emergency && (
            <div className="w-6 h-6 rounded-full flex items-center justify-center"
                 style={{ background: 'rgba(255,59,92,0.12)' }}>
              <AlertTriangle className="w-3 h-3 animate-pulse" style={{ color: '#FF6B85' }} />
            </div>
          )}
        </td>
        <td className="py-3.5 px-5">
          {isOpen
            ? <ChevronUp className="w-4 h-4" style={{ color: 'var(--text-muted)' }} />
            : <ChevronDown className="w-4 h-4" style={{ color: 'var(--text-muted)' }} />}
        </td>
      </tr>

      {isOpen && (
        <tr style={{ background: 'rgba(255,255,255,0.015)' }}>
          <td colSpan={7} className="px-8 py-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-[12px]">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.12em] mb-2" style={{ color: 'var(--text-muted)' }}>
                  Possible Conditions
                </p>
                <ul className="space-y-1">
                  {(c.conditions || []).map((cond, i) => (
                    <li key={i} style={{ color: 'var(--text-secondary)' }}>• {cond}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.12em] mb-2" style={{ color: 'var(--text-muted)' }}>
                  Recommendation
                </p>
                <p style={{ color: 'var(--text-secondary)' }}>{c.recommendation || '—'}</p>
              </div>
              {(c.home_care_tips || []).length > 0 && (
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.12em] mb-2" style={{ color: 'var(--text-muted)' }}>
                    Home Care
                  </p>
                  <ul className="space-y-1">
                    {c.home_care_tips.map((tip, i) => (
                      <li key={i} style={{ color: 'var(--text-muted)' }}>• {tip}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.12em] mb-2" style={{ color: 'var(--text-muted)' }}>
                  Raw Input
                </p>
                <p className="italic" style={{ color: 'var(--text-muted)' }}>"{c.raw_input || '—'}"</p>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  )
}

export default function CaseTable({ cases = [], loading }) {
  const [openId, setOpenId] = useState(null)

  if (loading) return (
    <div className="bento p-0 space-y-px overflow-hidden">
      {[...Array(5)].map((_, i) => <div key={i} className="h-14 shimmer-loading" />)}
    </div>
  )

  return (
    <div className="bento p-0 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              {['Risk', 'Channel', 'Symptoms', 'Region', 'Time', '', ''].map(h => (
                <th key={h} className="text-left py-3 px-5 text-[10px] font-bold uppercase tracking-[0.12em]"
                    style={{ color: 'var(--text-muted)' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {cases.length === 0 ? (
              <tr><td colSpan={7} className="text-center py-16 text-[13px]" style={{ color: 'var(--text-muted)' }}>No cases found</td></tr>
            ) : (
              cases.map(c => (
                <CaseRow key={c.id} c={c} isOpen={openId === c.id}
                         onClick={() => setOpenId(openId === c.id ? null : c.id)} />
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
