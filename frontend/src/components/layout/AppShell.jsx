import { ShieldAlert } from 'lucide-react'

export default function AppShell({ children }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 text-slate-900">
      <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-6 py-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-sm">
            <ShieldAlert size={24} />
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight">
              Multi-Agent Bug Triage System
            </h1>
            <p className="text-sm text-slate-500">
              Local issue analysis with structured multi-agent reasoning
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
    </div>
  )
}