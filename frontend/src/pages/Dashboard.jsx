import { Users, AlertTriangle, MapPin, Bell, MessageSquare, Phone, RefreshCw, Activity, Zap, Shield } from 'lucide-react'
import { useAnalytics, useCases } from '../hooks/useAnalytics'
import StatCard from '../components/StatCard'
import AlertCard from '../components/AlertCard'
import CaseTable from '../components/CaseTable'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend, PieChart, Pie, Cell
} from 'recharts'

function EKGWave() {
  return (
    <svg viewBox="0 0 400 60" className="w-full h-8 opacity-25" preserveAspectRatio="none">
      <path
        d="M0,30 L40,30 L50,30 L60,10 L70,50 L80,25 L90,35 L100,30 L200,30 L210,30 L220,8 L230,52 L240,22 L250,38 L260,30 L400,30"
        fill="none" stroke="var(--emerald)" strokeWidth="1.5"
        strokeDasharray="400" className="animate-ekg"
      />
    </svg>
  )
}

function LivePulse() {
  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <div className="w-2 h-2 rounded-full bg-emerald-400" style={{ boxShadow: '0 0 8px rgba(16,240,160,0.6)' }} />
        <div className="absolute inset-0 w-2 h-2 rounded-full bg-emerald-400 animate-ping opacity-30" />
      </div>
      <span className="text-[11px] font-semibold tracking-wider uppercase" style={{ color: 'var(--emerald)' }}>Live</span>
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="px-4 py-3 rounded-xl text-xs"
         style={{ background: 'rgba(11,14,20,0.95)', border: '1px solid var(--border-glass)', backdropFilter: 'blur(20px)', boxShadow: 'var(--shadow-elevated)' }}>
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

export default function Dashboard() {
  const { summary, symptoms, timeline, regional, alerts, channels, loading, lastUpdated, refetch } = useAnalytics()
  const { cases } = useCases({ limit: 6 })

  const pieData = channels ? [
    { name: 'WhatsApp', value: channels.channels?.whatsapp || 0, color: '#10F0A0' },
    { name: 'Voice', value: channels.channels?.call || 0, color: '#6366F1' },
  ] : []

  return (
    <div className="relative min-h-screen">
      {/* Breathing mesh background */}
      <div className="mesh-bg" />

      <div className="relative z-10 p-6 lg:p-8 space-y-6 max-w-[1600px] mx-auto">

        {/* ── Header ────────────────────────────────────────── */}
        <div className="flex items-center justify-between animate-fade-in">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-[26px] font-extrabold text-white tracking-tight">Health Dashboard</h1>
              <LivePulse />
            </div>
            <p className="text-[13px]" style={{ color: 'var(--text-muted)' }}>
              Real-time rural health intelligence · {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {lastUpdated && (
              <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
                {lastUpdated.toLocaleTimeString()}
              </span>
            )}
            <button onClick={refetch} className="btn-ghost">
              <RefreshCw className="w-4 h-4" /> Refresh
            </button>
          </div>
        </div>

        {/* ── Outbreak Alert Banner ─────────────────────────── */}
        {alerts.length > 0 && (
          <div className="rounded-2xl p-4 relative overflow-hidden animate-slide-up"
               style={{ background: 'rgba(255,59,92,0.06)', border: '1px solid rgba(255,59,92,0.15)' }}>
            <div className="absolute inset-0 opacity-30">
              <div className="absolute top-0 left-0 w-40 h-40 rounded-full" style={{ background: 'radial-gradient(circle, rgba(255,59,92,0.15), transparent 70%)' }} />
            </div>
            <div className="flex items-center gap-3 relative z-10">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                   style={{ background: 'rgba(255,59,92,0.15)', border: '1px solid rgba(255,59,92,0.2)' }}>
                <AlertTriangle className="w-4 h-4" style={{ color: '#FF6B85' }} />
              </div>
              <div>
                <p className="text-[13px] font-semibold" style={{ color: '#FF6B85' }}>
                  {alerts.length} Active Outbreak Alert{alerts.length > 1 ? 's' : ''}
                </p>
                <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
                  {alerts[0]?.region} — {(alerts[0]?.symptom_cluster || []).join(', ')}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ── KPI Row 1 ─────────────────────────────────────── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 stagger">
          <StatCard title="Total Cases" value={summary?.total_cases?.toLocaleString()} icon={Users} color="emerald" delay={0} loading={loading} sub="All time" />
          <StatCard title="Critical Today" value={summary?.critical_today} icon={AlertTriangle} color="poppy" delay={50} loading={loading} sub="Immediate attention" />
          <StatCard title="Active Regions" value={summary?.active_regions} icon={MapPin} color="indigo" delay={100} loading={loading} sub="States reporting" />
          <StatCard title="Outbreak Alerts" value={summary?.active_alerts} icon={Shield} color="amber" delay={150} loading={loading} sub="Active warnings" />
        </div>

        {/* ── KPI Row 2 ─────────────────────────────────────── */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 stagger">
          <StatCard title="Today's Cases" value={summary?.cases_today} icon={Zap} color="cyan" delay={0} loading={loading} />
          <StatCard title="Emergencies" value={summary?.emergency_today} icon={Activity} color="poppy" delay={50} loading={loading} sub="108 referrals" />
          <StatCard title="WhatsApp" value={summary?.whatsapp_cases?.toLocaleString()} icon={MessageSquare} color="emerald" delay={100} loading={loading} />
          <StatCard title="Voice Calls" value={summary?.call_cases?.toLocaleString()} icon={Phone} color="indigo" delay={150} loading={loading} />
        </div>

        {/* ── Chart Row ────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">

          {/* Timeline */}
          <div className="lg:col-span-8 bento animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-[14px] font-semibold text-white">Case Trend</h2>
                <p className="text-[11px]" style={{ color: 'var(--text-muted)' }}>30-day daily breakdown by severity</p>
              </div>
              <EKGWave />
            </div>
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={timeline} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
                <defs>
                  <linearGradient id="gCrit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#FF3B5C" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#FF3B5C" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gMod" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#F5A623" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="#F5A623" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gMild" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10F0A0" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="#10F0A0" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
                <XAxis dataKey="date" tickFormatter={d => d?.slice(5)} tick={{ fontSize: 10 }} stroke="transparent" />
                <YAxis tick={{ fontSize: 10 }} stroke="transparent" />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="critical" stroke="#FF3B5C" fill="url(#gCrit)" strokeWidth={2} name="Critical" />
                <Area type="monotone" dataKey="moderate" stroke="#F5A623" fill="url(#gMod)" strokeWidth={1.5} name="Moderate" />
                <Area type="monotone" dataKey="mild" stroke="#10F0A0" fill="url(#gMild)" strokeWidth={1.5} name="Mild" />
                <Legend />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Channel Distribution */}
          <div className="lg:col-span-4 bento animate-slide-up flex flex-col" style={{ animationDelay: '0.15s' }}>
            <h2 className="text-[14px] font-semibold text-white mb-1">Channels</h2>
            <p className="text-[11px] mb-4" style={{ color: 'var(--text-muted)' }}>WhatsApp vs Voice</p>
            <div className="flex-1 flex items-center justify-center">
              <ResponsiveContainer width="100%" height={140}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={40} outerRadius={60} dataKey="value" paddingAngle={4} strokeWidth={0}>
                    {pieData.map((e, i) => <Cell key={i} fill={e.color} />)}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-5 mt-3">
              {pieData.map(d => (
                <div key={d.name} className="flex items-center gap-2 text-[12px]" style={{ color: 'var(--text-secondary)' }}>
                  <span className="w-2 h-2 rounded-full" style={{ background: d.color, boxShadow: `0 0 6px ${d.color}40` }} />
                  {d.name}: <span className="text-white font-medium">{d.value}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-white/[0.04]">
              <p className="text-[11px] font-semibold mb-2" style={{ color: 'var(--text-muted)' }}>Language</p>
              <div className="flex gap-4">
                {channels && (
                  <>
                    <div className="flex items-center gap-1.5 text-[12px]" style={{ color: 'var(--text-secondary)' }}>
                      <span className="w-2 h-2 rounded-full bg-amber-400" />Hindi: <span className="text-white font-medium">{channels.languages?.hi || 0}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-[12px]" style={{ color: 'var(--text-secondary)' }}>
                      <span className="w-2 h-2 rounded-full bg-purple-400" />English: <span className="text-white font-medium">{channels.languages?.en || 0}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ── Symptoms + Regional ──────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Top Symptoms */}
          <div className="bento animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <h2 className="text-[14px] font-semibold text-white mb-1">Top Symptoms</h2>
            <p className="text-[11px] mb-4" style={{ color: 'var(--text-muted)' }}>Most reported in last 30 days</p>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={symptoms?.slice(0, 8)} layout="vertical" margin={{ left: 0, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10 }} stroke="transparent" />
                <YAxis type="category" dataKey="symptom" width={90} tick={{ fontSize: 11, fill: '#8B94A3' }} stroke="transparent" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" radius={[0, 6, 6, 0]} name="Cases">
                  {symptoms?.slice(0, 8).map((_, i) => (
                    <Cell key={i} fill={`rgba(16,240,160,${0.9 - i * 0.08})`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Regional */}
          <div className="bento animate-slide-up" style={{ animationDelay: '0.25s' }}>
            <h2 className="text-[14px] font-semibold text-white mb-1">Regional Spread</h2>
            <p className="text-[11px] mb-4" style={{ color: 'var(--text-muted)' }}>Cases by state</p>
            <div className="space-y-3 max-h-[240px] overflow-y-auto pr-1">
              {regional?.slice(0, 10).map((r, i) => {
                const maxCount = regional?.[0]?.total || 1
                const pct = (r.total / maxCount) * 100
                return (
                  <div key={r.state} className="group animate-slide-in" style={{ animationDelay: `${i * 40}ms` }}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[12px] font-medium" style={{ color: 'var(--text-secondary)' }}>{r.state}</span>
                      <div className="flex items-center gap-2">
                        {r.critical > 0 && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: 'rgba(255,59,92,0.1)', color: '#FF6B85' }}>
                            {r.critical} crit
                          </span>
                        )}
                        <span className="text-[12px] font-semibold text-white">{r.total}</span>
                      </div>
                    </div>
                    <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--surface-2)' }}>
                      <div className="h-full rounded-full transition-all duration-700"
                           style={{
                             width: `${pct}%`,
                             background: r.critical > 2 ? 'linear-gradient(90deg, #FF3B5C, #FF6B85)' : 'linear-gradient(90deg, var(--emerald-dim), var(--emerald))',
                             boxShadow: r.critical > 2 ? '0 0 8px rgba(255,59,92,0.3)' : '0 0 8px rgba(16,240,160,0.2)',
                           }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* ── Alerts Preview ──────────────────────────────── */}
        {alerts.length > 0 && (
          <div className="animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <h2 className="text-[14px] font-semibold text-white mb-3">Outbreak Alerts</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {alerts.slice(0, 4).map(a => <AlertCard key={a.id} alert={a} />)}
            </div>
          </div>
        )}

        {/* ── Recent Cases ────────────────────────────────── */}
        <div className="animate-slide-up" style={{ animationDelay: '0.35s' }}>
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-[14px] font-semibold text-white">Recent Cases</h2>
              <p className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Latest consultations</p>
            </div>
            <a href="/cases" className="text-[12px] font-medium" style={{ color: 'var(--emerald)' }}>View all →</a>
          </div>
          <CaseTable cases={cases} loading={false} />
        </div>
      </div>
    </div>
  )
}
