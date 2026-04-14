import { useAnalytics } from '../hooks/useAnalytics'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, RadialBarChart, RadialBar, Legend
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="px-4 py-3 rounded-xl text-xs"
         style={{ background: 'rgba(11,14,20,0.95)', border: '1px solid var(--border-glass)', backdropFilter: 'blur(20px)' }}>
      <p className="font-semibold text-white mb-1.5">{label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span style={{ color: 'var(--text-secondary)' }}>{p.name}: <span className="text-white font-medium">{p.value}</span></span>
        </div>
      ))}
    </div>
  )
}

export default function Analytics() {
  const { summary, symptoms, timeline, regional, channels, loading } = useAnalytics(0)

  const riskData = regional ? (() => {
    let mild = 0, moderate = 0, critical = 0
    regional.forEach(r => { mild += r.mild || 0; moderate += r.moderate || 0; critical += r.critical || 0 })
    return [
      { name: 'Mild', value: mild, color: '#10F0A0' },
      { name: 'Moderate', value: moderate, color: '#F5A623' },
      { name: 'Critical', value: critical, color: '#FF3B5C' },
    ]
  })() : []

  const channelData = channels ? [
    { name: 'WhatsApp', value: channels.channels?.whatsapp || 0, color: '#10F0A0' },
    { name: 'Voice', value: channels.channels?.call || 0, color: '#6366F1' },
  ] : []

  const langData = channels ? [
    { name: 'Hindi', value: channels.languages?.hi || 0, color: '#F5A623' },
    { name: 'English', value: channels.languages?.en || 0, color: '#818CF8' },
  ] : []

  return (
    <div className="relative min-h-screen">
      <div className="mesh-bg" />
      <div className="relative z-10 p-6 lg:p-8 space-y-6 max-w-[1600px] mx-auto">

        <div className="animate-fade-in">
          <h1 className="text-[26px] font-extrabold text-white tracking-tight">Analytics</h1>
          <p className="text-[13px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Deep dive into health data patterns and trends
          </p>
        </div>

        {/* Row 1: Timeline full width */}
        <div className="bento animate-slide-up">
          <h2 className="text-[14px] font-semibold text-white mb-1">30-Day Case Timeline</h2>
          <p className="text-[11px] mb-5" style={{ color: 'var(--text-muted)' }}>Daily cases by severity</p>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={timeline} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
              <defs>
                <linearGradient id="aGreen" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10F0A0" stopOpacity={0.25} /><stop offset="100%" stopColor="#10F0A0" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="aAmber" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#F5A623" stopOpacity={0.2} /><stop offset="100%" stopColor="#F5A623" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="aRed" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FF3B5C" stopOpacity={0.25} /><stop offset="100%" stopColor="#FF3B5C" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="date" tickFormatter={d => d?.slice(5)} tick={{ fontSize: 10 }} stroke="transparent" />
              <YAxis tick={{ fontSize: 10 }} stroke="transparent" />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="mild" stroke="#10F0A0" fill="url(#aGreen)" strokeWidth={2} name="Mild" />
              <Area type="monotone" dataKey="moderate" stroke="#F5A623" fill="url(#aAmber)" strokeWidth={1.5} name="Moderate" />
              <Area type="monotone" dataKey="critical" stroke="#FF3B5C" fill="url(#aRed)" strokeWidth={2} name="Critical" />
              <Legend />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Row 2: 3-col pies */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 stagger">
          {/* Risk Distribution */}
          <div className="bento flex flex-col items-center">
            <h2 className="text-[14px] font-semibold text-white mb-1 self-start">Risk Distribution</h2>
            <p className="text-[11px] mb-4 self-start" style={{ color: 'var(--text-muted)' }}>All time breakdown</p>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={riskData} cx="50%" cy="50%" innerRadius={45} outerRadius={65} dataKey="value" paddingAngle={4} strokeWidth={0}>
                  {riskData.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex gap-4 mt-2">
              {riskData.map(d => (
                <div key={d.name} className="flex items-center gap-1.5 text-[11px]" style={{ color: 'var(--text-secondary)' }}>
                  <span className="w-2 h-2 rounded-full" style={{ background: d.color }} />{d.name}: <span className="text-white font-medium">{d.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Channel Split */}
          <div className="bento flex flex-col items-center">
            <h2 className="text-[14px] font-semibold text-white mb-1 self-start">Channel Split</h2>
            <p className="text-[11px] mb-4 self-start" style={{ color: 'var(--text-muted)' }}>WhatsApp vs Voice</p>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={channelData} cx="50%" cy="50%" innerRadius={45} outerRadius={65} dataKey="value" paddingAngle={4} strokeWidth={0}>
                  {channelData.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex gap-4 mt-2">
              {channelData.map(d => (
                <div key={d.name} className="flex items-center gap-1.5 text-[11px]" style={{ color: 'var(--text-secondary)' }}>
                  <span className="w-2 h-2 rounded-full" style={{ background: d.color }} />{d.name}: <span className="text-white font-medium">{d.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Language */}
          <div className="bento flex flex-col items-center">
            <h2 className="text-[14px] font-semibold text-white mb-1 self-start">Language</h2>
            <p className="text-[11px] mb-4 self-start" style={{ color: 'var(--text-muted)' }}>Hindi vs English</p>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={langData} cx="50%" cy="50%" innerRadius={45} outerRadius={65} dataKey="value" paddingAngle={4} strokeWidth={0}>
                  {langData.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex gap-4 mt-2">
              {langData.map(d => (
                <div key={d.name} className="flex items-center gap-1.5 text-[11px]" style={{ color: 'var(--text-secondary)' }}>
                  <span className="w-2 h-2 rounded-full" style={{ background: d.color }} />{d.name}: <span className="text-white font-medium">{d.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Row 3: Symptoms + Regional */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div className="bento animate-slide-up">
            <h2 className="text-[14px] font-semibold text-white mb-1">Symptom Frequency</h2>
            <p className="text-[11px] mb-4" style={{ color: 'var(--text-muted)' }}>Top reported symptoms (30d)</p>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={symptoms?.slice(0, 10)} layout="vertical" margin={{ left: 0, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10 }} stroke="transparent" />
                <YAxis type="category" dataKey="symptom" width={100} tick={{ fontSize: 11, fill: '#8B94A3' }} stroke="transparent" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" radius={[0, 6, 6, 0]} name="Cases">
                  {symptoms?.slice(0, 10).map((_, i) => (
                    <Cell key={i} fill={`rgba(16,240,160,${0.95 - i * 0.07})`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bento animate-slide-up">
            <h2 className="text-[14px] font-semibold text-white mb-1">State-wise Breakdown</h2>
            <p className="text-[11px] mb-4" style={{ color: 'var(--text-muted)' }}>Top 10 active states</p>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={regional?.slice(0, 10)} layout="vertical" margin={{ left: 0, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10 }} stroke="transparent" />
                <YAxis type="category" dataKey="state" width={120} tick={{ fontSize: 11, fill: '#8B94A3' }} stroke="transparent" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="critical" stackId="a" fill="#FF3B5C" name="Critical" radius={[0, 0, 0, 0]} />
                <Bar dataKey="moderate" stackId="a" fill="#F5A623" name="Moderate" radius={[0, 0, 0, 0]} />
                <Bar dataKey="mild" stackId="a" fill="#10F0A0" name="Mild" radius={[0, 6, 6, 0]} />
                <Legend />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
