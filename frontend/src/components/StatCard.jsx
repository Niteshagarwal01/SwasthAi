export default function StatCard({ title, value, sub, icon: Icon, color = 'emerald', trend, loading, delay = 0 }) {
  const palettes = {
    emerald: {
      icon: 'rgba(16,240,160,0.12)',
      iconBorder: 'rgba(16,240,160,0.15)',
      iconColor: '#10F0A0',
      glow: 'rgba(16,240,160,0.06)',
    },
    poppy: {
      icon: 'rgba(255,59,92,0.12)',
      iconBorder: 'rgba(255,59,92,0.18)',
      iconColor: '#FF6B85',
      glow: 'rgba(255,59,92,0.06)',
    },
    amber: {
      icon: 'rgba(245,166,35,0.12)',
      iconBorder: 'rgba(245,166,35,0.15)',
      iconColor: '#F5C964',
      glow: 'rgba(245,166,35,0.05)',
    },
    indigo: {
      icon: 'rgba(99,102,241,0.12)',
      iconBorder: 'rgba(99,102,241,0.15)',
      iconColor: '#818CF8',
      glow: 'rgba(99,102,241,0.05)',
    },
    cyan: {
      icon: 'rgba(34,211,238,0.12)',
      iconBorder: 'rgba(34,211,238,0.15)',
      iconColor: '#22D3EE',
      glow: 'rgba(34,211,238,0.05)',
    },
  }

  const p = palettes[color] || palettes.emerald

  return (
    <div className="stat-card animate-slide-up" style={{ animationDelay: `${delay}ms` }}>
      {/* Glow orb */}
      <div className="glow-orb" style={{ background: p.glow, top: '-40px', right: '-40px' }} />

      <div className="flex items-start justify-between relative z-10">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center"
             style={{ background: p.icon, border: `1px solid ${p.iconBorder}` }}>
          {Icon && <Icon className="w-[18px] h-[18px]" style={{ color: p.iconColor }} />}
        </div>
        {trend !== undefined && (
          <span className="text-[11px] font-semibold px-2 py-0.5 rounded-md"
                style={{
                  color: trend >= 0 ? '#FF6B85' : '#4AE5A0',
                  background: trend >= 0 ? 'rgba(255,59,92,0.08)' : 'rgba(16,240,160,0.08)',
                }}>
            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
        )}
      </div>

      {loading ? (
        <div className="h-9 w-24 rounded-xl shimmer-loading mt-2" />
      ) : (
        <p className="text-[32px] font-extrabold text-white mt-2 tracking-tight leading-none">
          {value ?? '—'}
        </p>
      )}

      <div className="relative z-10">
        <p className="text-[13px] font-medium" style={{ color: 'var(--text-secondary)' }}>{title}</p>
        {sub && <p className="text-[11px] mt-0.5" style={{ color: 'var(--text-muted)' }}>{sub}</p>}
      </div>
    </div>
  )
}
