import { useAnalytics } from '../hooks/useAnalytics'
import AlertCard from '../components/AlertCard'
import { CheckCircle, AlertTriangle, Info } from 'lucide-react'

export default function Alerts() {
  const { alerts, loading, refetch } = useAnalytics(0)

  return (
    <div className="relative min-h-screen">
      <div className="mesh-bg" />
      <div className="relative z-10 p-6 lg:p-8 space-y-6 max-w-[1600px] mx-auto">

        <div className="flex items-center justify-between animate-fade-in">
          <div>
            <h1 className="text-[26px] font-extrabold text-white tracking-tight">Outbreak Alerts</h1>
            <p className="text-[13px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
              Automated disease cluster detection and surveillance
            </p>
          </div>
          <button onClick={refetch} className="btn-ghost text-[12px]">Refresh</button>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => <div key={i} className="h-28 rounded-2xl shimmer-loading" />)}
          </div>
        ) : alerts.length === 0 ? (
          <div className="bento flex flex-col items-center justify-center py-24 text-center">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-5"
                 style={{ background: 'var(--emerald-glow)', border: '1px solid rgba(16,240,160,0.15)' }}>
              <CheckCircle className="w-7 h-7" style={{ color: 'var(--emerald)' }} />
            </div>
            <h2 className="text-white font-semibold text-lg mb-1">All Clear</h2>
            <p className="text-[13px]" style={{ color: 'var(--text-muted)' }}>No active outbreak alerts. All regions within normal parameters.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 stagger">
            {alerts.map(a => <AlertCard key={a.id} alert={a} />)}
          </div>
        )}

        {/* Info card */}
        <div className="bento animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-start gap-4">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
                 style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.15)' }}>
              <Info className="w-4 h-4" style={{ color: '#818CF8' }} />
            </div>
            <div>
              <h3 className="text-[13px] font-semibold text-white mb-1">How Detection Works</h3>
              <p className="text-[12px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                SwasthAI scans all cases every 30 minutes. If <strong style={{ color: 'var(--emerald)' }}>5+ cases</strong> with 
                similar symptoms appear from the same region within <strong style={{ color: 'var(--emerald)' }}>48 hours</strong>, 
                an outbreak alert fires. Alerts are graded Low → Medium → High → Critical based on case volume and symptom severity.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
