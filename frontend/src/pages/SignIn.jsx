import { SignIn } from '@clerk/clerk-react'
import { Heart } from 'lucide-react'

export default function SignInPage() {
  const noAuth = !import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

  if (noAuth) {
    window.location.href = '/'
    return null
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative">
      <div className="mesh-bg" />

      <div className="relative z-10 flex flex-col items-center animate-fade-in">
        {/* Logo */}
        <div className="mb-8 flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center"
               style={{ background: 'linear-gradient(135deg, rgba(16,240,160,0.15), rgba(16,240,160,0.05))', border: '1px solid rgba(16,240,160,0.2)' }}>
            <Heart className="w-6 h-6" style={{ color: 'var(--emerald)' }} />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">SwasthAI</h1>
            <p className="text-[11px] uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Health Intelligence Platform</p>
          </div>
        </div>

        <SignIn
          appearance={{
            elements: {
              rootBox: 'mx-auto',
              card: 'bg-[#0f1219] border border-white/[0.07] shadow-2xl rounded-2xl',
              headerTitle: 'text-white',
              headerSubtitle: 'text-gray-500',
              socialButtonsBlockButton: 'bg-white/5 border-white/10 text-white hover:bg-white/10',
              formFieldLabel: 'text-gray-400',
              formFieldInput: 'bg-white/5 border-white/10 text-white',
              formButtonPrimary: 'bg-emerald-500 hover:bg-emerald-600',
              footerActionLink: 'text-emerald-400 hover:text-emerald-300',
            }
          }}
        />
      </div>
    </div>
  )
}
