export default function LoadingSpinner({ text = 'Analyzing issue...' }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900" />
      <p className="text-sm font-medium text-slate-700">{text}</p>
    </div>
  )
}