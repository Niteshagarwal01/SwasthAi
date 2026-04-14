import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Cases from './pages/Cases'
import Alerts from './pages/Alerts'
import Analytics from './pages/Analytics'
import Simulate from './pages/Simulate'
import SignInPage from './pages/SignIn'

function Layout({ children }) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-[#0a0f1a]">
        {children}
      </main>
    </div>
  )
}

function ProtectedRoute({ children }) {
  const noAuth = !import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

  // Always call hooks at top level (React rules)
  let isSignedIn = true
  let isLoaded = true

  try {
    if (!noAuth) {
      const auth = useAuth()
      isSignedIn = auth.isSignedIn
      isLoaded = auth.isLoaded
    }
  } catch {
    // Clerk not available — pass through
    return children
  }

  if (noAuth) return children

  if (!isLoaded) return (
    <div className="flex h-screen items-center justify-center">
      <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
  if (!isSignedIn) return <Navigate to="/sign-in" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/*" element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/cases" element={<Cases />} />
                <Route path="/alerts" element={<Alerts />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/simulate" element={<Simulate />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  )
}
