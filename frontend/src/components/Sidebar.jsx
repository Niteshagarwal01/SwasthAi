import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, FileText, AlertTriangle, BarChart3,
  MessageSquare, LogOut, Activity, Heart
} from 'lucide-react'
import { useUser, useClerk } from '@clerk/clerk-react'

const NAV = [
  { to: '/',          icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/cases',     icon: FileText,        label: 'Cases' },
  { to: '/alerts',    icon: AlertTriangle,   label: 'Alerts' },
  { to: '/analytics', icon: BarChart3,       label: 'Analytics' },
  { to: '/simulate',  icon: MessageSquare,   label: 'Simulate' },
]

function useClerkSafe() {
  const hasClerk = !!import.meta.env.VITE_CLERK_PUBLISHABLE_KEY
  try {
    if (!hasClerk) return { user: null, signOut: null }
    const { user } = useUser()
    const { signOut } = useClerk()
    return { user, signOut }
  } catch {
    return { user: null, signOut: null }
  }
}

export default function Sidebar() {
  const location = useLocation()
  const { user, signOut } = useClerkSafe()

  return (
    <aside className="w-[260px] shrink-0 flex flex-col h-screen border-r border-white/[0.04] relative z-10"
           style={{ background: 'rgba(11,14,20,0.85)', backdropFilter: 'blur(40px)' }}>
      {/* Logo */}
      <div className="px-6 pt-7 pb-5">
        <div className="flex items-center gap-3.5">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center relative"
                 style={{ background: 'linear-gradient(135deg, rgba(16,240,160,0.15), rgba(16,240,160,0.05))', border: '1px solid rgba(16,240,160,0.2)' }}>
              <Heart className="w-5 h-5 text-emerald-400" />
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-400"
                 style={{ boxShadow: '0 0 8px rgba(16,240,160,0.6)' }}>
              <div className="w-full h-full rounded-full bg-emerald-400 animate-ping opacity-40" />
            </div>
          </div>
          <div>
            <h1 className="text-white font-bold text-[15px] tracking-tight">SwasthAI</h1>
            <p className="text-[11px] tracking-widest uppercase" style={{ color: 'var(--text-muted)' }}>
              Health Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="mx-5 h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent" />

      {/* Navigation */}
      <nav className="flex-1 px-3 py-5 space-y-1">
        <p className="px-3.5 pb-2 text-[10px] font-semibold uppercase tracking-[0.15em]"
           style={{ color: 'var(--text-muted)' }}>Overview</p>
        {NAV.slice(0, 3).map(({ to, icon: Icon, label }) => {
          const active = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
          return (
            <NavLink key={to} to={to} className={active ? 'nav-item-active' : 'nav-item-inactive'}>
              <Icon className="w-[18px] h-[18px]" />
              {label}
              {active && to === '/alerts' && (
                <span className="ml-auto w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center"
                      style={{ background: 'rgba(255,59,92,0.2)', color: '#FF6B85' }}>!</span>
              )}
            </NavLink>
          )
        })}

        <p className="px-3.5 pt-5 pb-2 text-[10px] font-semibold uppercase tracking-[0.15em]"
           style={{ color: 'var(--text-muted)' }}>Tools</p>
        {NAV.slice(3).map(({ to, icon: Icon, label }) => {
          const active = location.pathname.startsWith(to)
          return (
            <NavLink key={to} to={to} className={active ? 'nav-item-active' : 'nav-item-inactive'}>
              <Icon className="w-[18px] h-[18px]" />
              {label}
            </NavLink>
          )
        })}
      </nav>

      {/* System Status */}
      <div className="mx-4 mb-3">
        <div className="rounded-xl p-3.5 relative overflow-hidden"
             style={{ background: 'rgba(16,240,160,0.04)', border: '1px solid rgba(16,240,160,0.08)' }}>
          <div className="absolute top-0 right-0 w-20 h-20 rounded-full"
               style={{ background: 'radial-gradient(circle, rgba(16,240,160,0.08), transparent 70%)' }} />
          <div className="flex items-center gap-2 relative z-10">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400"
                 style={{ boxShadow: '0 0 6px rgba(16,240,160,0.8)' }} />
            <span className="text-[11px] font-semibold tracking-wide" style={{ color: 'var(--emerald)' }}>
              System Online
            </span>
          </div>
          <p className="text-[10px] mt-1.5 pl-3.5" style={{ color: 'var(--text-muted)' }}>
            WhatsApp · Voice · AI Engine
          </p>
        </div>
      </div>

      {/* User */}
      <div className="px-4 py-4 border-t border-white/[0.04]">
        {user ? (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full overflow-hidden ring-1 ring-white/10">
              {user.imageUrl ? (
                <img src={user.imageUrl} alt="" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-xs font-bold"
                     style={{ background: 'var(--emerald-glow)', color: 'var(--emerald)' }}>
                  {user.firstName?.[0] || 'A'}
                </div>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[13px] font-medium text-white truncate">{user.firstName || 'Admin'}</p>
              <p className="text-[11px] truncate" style={{ color: 'var(--text-muted)' }}>
                {user.primaryEmailAddress?.emailAddress}
              </p>
            </div>
            <button onClick={() => signOut?.()} className="p-1.5 rounded-lg hover:bg-white/5 transition-colors"
                    style={{ color: 'var(--text-muted)' }}>
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                 style={{ background: 'var(--surface-2)', color: 'var(--text-muted)' }}>D</div>
            <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Demo Mode</p>
          </div>
        )}
      </div>
    </aside>
  )
}
