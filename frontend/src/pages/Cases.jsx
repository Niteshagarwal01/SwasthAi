import { useState, useEffect } from 'react'
import { Filter, Search } from 'lucide-react'
import { getCases } from '../services/api'
import CaseTable from '../components/CaseTable'

export default function Cases() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [risk, setRisk] = useState('')
  const [channel, setChannel] = useState('')

  const fetchCases = async () => {
    setLoading(true)
    const params = { page, limit: 25 }
    if (risk) params.risk = risk
    if (channel) params.channel = channel
    const data = await getCases(params).catch(() => [])
    setCases(data)
    setLoading(false)
  }

  useEffect(() => { fetchCases() }, [page, risk, channel])

  return (
    <div className="relative min-h-screen">
      <div className="mesh-bg" />
      <div className="relative z-10 p-6 lg:p-8 space-y-6 max-w-[1600px] mx-auto">

        <div className="animate-fade-in">
          <h1 className="text-[26px] font-extrabold text-white tracking-tight">Cases</h1>
          <p className="text-[13px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
            All reported health consultations via WhatsApp and voice calls
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 animate-slide-up">
          <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl"
               style={{ background: 'var(--surface-1)', border: '1px solid var(--border-glass)' }}>
            <Filter className="w-4 h-4" style={{ color: 'var(--text-muted)' }} />
            <select value={risk} onChange={e => { setRisk(e.target.value); setPage(1) }}
                    className="bg-transparent text-[12px] outline-none" style={{ color: 'var(--text-secondary)' }}>
              <option value="">All Risk Levels</option>
              <option value="critical">Critical</option>
              <option value="moderate">Moderate</option>
              <option value="mild">Mild</option>
            </select>
          </div>
          <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl"
               style={{ background: 'var(--surface-1)', border: '1px solid var(--border-glass)' }}>
            <select value={channel} onChange={e => { setChannel(e.target.value); setPage(1) }}
                    className="bg-transparent text-[12px] outline-none" style={{ color: 'var(--text-secondary)' }}>
              <option value="">All Channels</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="call">Voice Call</option>
            </select>
          </div>
          <button onClick={fetchCases} className="btn-ghost text-[12px]">Refresh</button>
        </div>

        <CaseTable cases={cases} loading={loading} />

        {/* Pagination */}
        <div className="flex items-center justify-center gap-4 animate-fade-in">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                  className="btn-ghost disabled:opacity-20 text-[12px]">← Previous</button>
          <div className="px-4 py-1.5 rounded-lg text-[12px] font-medium"
               style={{ background: 'var(--surface-2)', color: 'var(--text-secondary)' }}>
            Page {page}
          </div>
          <button onClick={() => setPage(p => p + 1)} disabled={cases.length < 25}
                  className="btn-ghost disabled:opacity-20 text-[12px]">Next →</button>
        </div>
      </div>
    </div>
  )
}
