export default function SectionTitle({ eyebrow, title, description }) {
  return (
    <div className="mb-6">
      {eyebrow && (
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
          {eyebrow}
        </p>
      )}
      <h2 className="text-3xl font-bold tracking-tight text-slate-900">{title}</h2>
      {description && <p className="mt-2 max-w-3xl text-sm text-slate-600">{description}</p>}
    </div>
  )
}