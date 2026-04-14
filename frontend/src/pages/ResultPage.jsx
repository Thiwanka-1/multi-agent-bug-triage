import { useLocation, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  FileCode2,
  ShieldCheck,
  Wrench,
  SearchCheck,
  UploadCloud,
} from 'lucide-react'
import Card from '../components/ui/Card'
import SectionTitle from '../components/ui/SectionTitle'

function ListBlock({ items = [] }) {
  if (!items.length) {
    return <p className="text-sm text-slate-500">No data available.</p>
  }

  return (
    <ul className="space-y-2">
      {items.map((item, index) => (
        <li
          key={`${item}-${index}`}
          className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700"
        >
          {item}
        </li>
      ))}
    </ul>
  )
}

function KeyValue({ label, value }) {
  return (
    <div className="rounded-xl bg-slate-50 px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 break-words text-sm text-slate-800">{value || '—'}</p>
    </div>
  )
}

export default function ResultPage() {
  const location = useLocation()
  const navigate = useNavigate()

  const result = location.state?.result
  const formData = location.state?.formData

  if (!result) {
    return (
      <Card title="No results found">
        <p className="text-sm text-slate-600">
          No analysis result is available in this page yet.
        </p>
        <button
          onClick={() => navigate('/')}
          className="mt-4 inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
        >
          <ArrowLeft size={16} />
          Go back
        </button>
      </Card>
    )
  }

  const issueSummary = result.issue_summary?.llm_summary || {}
  const codeFindings = result.code_findings || {}
  const fixPlan = result.fix_plan || {}
  const qaReport = result.qa_report || {}
  const trace = result.trace || []

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <SectionTitle
          eyebrow="Analysis Result"
          title="Bug triage output"
          description="Review the structured output produced by the 4-agent workflow."
        />
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 rounded-2xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
        >
          <ArrowLeft size={16} />
          New analysis
        </button>
      </div>

      <Card title="Submitted input" subtitle="Original issue details and uploaded file">
        <div className="grid gap-4 lg:grid-cols-3">
          <KeyValue label="Issue description" value={formData?.userInput} />
          <KeyValue label="Uploaded file" value={formData?.fileName || 'Not provided'} />
          <KeyValue label="Upload kind" value={result.upload_kind || 'Unknown'} />
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Issue Summary" subtitle="Produced by Issue Analyst">
          <div className="grid gap-3">
            <KeyValue label="Title" value={issueSummary.title} />
            <KeyValue label="Severity" value={issueSummary.severity} />
            <KeyValue label="Suspected Module" value={issueSummary.suspected_module} />
            <KeyValue label="Problem Description" value={issueSummary.problem_description} />
            <KeyValue label="Expected Behavior" value={issueSummary.expected_behavior} />
            <KeyValue
              label="Next Investigation Focus"
              value={issueSummary.next_investigation_focus}
            />
          </div>
        </Card>

        <Card title="Relevant Files" subtitle="Most relevant file paths selected by the investigator">
          <ListBlock items={result.relevant_files || []} />
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card title="Code Findings" subtitle="Produced by Codebase Investigator">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-slate-800">
              <SearchCheck size={18} />
              <span className="font-medium">Investigation result</span>
            </div>
            <KeyValue label="Probable Cause" value={codeFindings.probable_cause} />
            <KeyValue label="Suspicious Statement" value={codeFindings.suspicious_statement} />
            <KeyValue label="Notes" value={codeFindings.notes} />
          </div>
        </Card>

        <Card title="Fix Plan" subtitle="Produced by Fix Planner">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-slate-800">
              <Wrench size={18} />
              <span className="font-medium">Suggested fix</span>
            </div>
            <KeyValue label="Priority" value={fixPlan.priority} />
            <KeyValue label="Direct Fix" value={fixPlan.direct_fix} />
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Implementation Steps
              </p>
              <ListBlock items={fixPlan.implementation_steps || []} />
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Regression Checks
              </p>
              <ListBlock items={fixPlan.regression_checks || []} />
            </div>
          </div>
        </Card>

        <Card title="QA Report" subtitle="Produced by QA Reviewer">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-slate-800">
              <ShieldCheck size={18} />
              <span className="font-medium">Validation output</span>
            </div>
            <KeyValue label="Decision" value={qaReport.decision} />
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                QA Checklist
              </p>
              <ListBlock items={qaReport.qa_checklist || []} />
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Acceptance Criteria
              </p>
              <ListBlock items={qaReport.acceptance_criteria || []} />
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Regression Risks
              </p>
              <ListBlock items={qaReport.regression_risks || []} />
            </div>
          </div>
        </Card>
      </div>

      <Card title="Upload & Agent Trace" subtitle="Upload details and execution trace">
        <div className="mb-6 grid gap-4 lg:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="mb-2 flex items-center gap-2 text-slate-900">
              <UploadCloud size={18} />
              <p className="font-semibold">Upload details</p>
            </div>
            <p className="text-sm text-slate-700">
              <span className="font-medium">Kind:</span> {result.upload_kind || 'Unknown'}
            </p>
            <p className="mt-2 break-all text-sm text-slate-700">
              <span className="font-medium">Processed path:</span> {result.project_path || '—'}
            </p>
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {trace.map((item, index) => (
            <div
              key={`${item.agent}-${index}`}
              className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
            >
              <div className="mb-3 flex items-center gap-2 text-slate-900">
                <FileCode2 size={18} />
                <p className="font-semibold">{item.agent}</p>
              </div>
              <p className="text-sm text-slate-700">
                <span className="font-medium">Step:</span> {item.step}
              </p>
              <p className="mt-2 text-sm text-slate-700">
                <span className="font-medium">Tool:</span> {item.tool_used}
              </p>
              <p className="mt-2 text-sm text-slate-700">
                <span className="font-medium">Summary:</span> {item.summary}
              </p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}