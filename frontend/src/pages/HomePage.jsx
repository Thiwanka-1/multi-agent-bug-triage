import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Upload,
  Play,
  FileWarning,
  FileCode2,
  FolderArchive,
  CheckCircle2,
} from 'lucide-react'
import api from '../services/api'
import Card from '../components/ui/Card'
import SectionTitle from '../components/ui/SectionTitle'
import LoadingSpinner from '../components/ui/LoadingSpinner'

const ALLOWED_EXTENSIONS = [
  '.zip',
  '.py',
  '.js',
  '.jsx',
  '.ts',
  '.tsx',
  '.json',
]

export default function HomePage() {
  const navigate = useNavigate()

  const [userInput, setUserInput] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    const file = e.target.files?.[0] || null
    setSelectedFile(file)
  }

  const handleAnalyze = async (e) => {
    e.preventDefault()
    setError('')

    if (!userInput.trim()) {
      setError('Please enter an issue description.')
      return
    }

    if (!selectedFile) {
      setError('Please upload a ZIP or a supported code file.')
      return
    }

    const fileName = selectedFile.name.toLowerCase()
    const isAllowed = ALLOWED_EXTENSIONS.some((ext) => fileName.endsWith(ext))

    if (!isAllowed) {
      setError('Unsupported file type. Please upload a ZIP, .py, .js, .jsx, .ts, .tsx, or .json file.')
      return
    }

    try {
      setLoading(true)

      const formData = new FormData()
      formData.append('user_input', userInput)
      formData.append('codebase_file', selectedFile)

      const response = await api.post('/run-upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      navigate('/results', {
        state: {
          result: response.data,
          formData: {
            userInput,
            fileName: selectedFile.name,
          },
        },
      })
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          'Failed to analyze the upload. Make sure the backend is running.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <SectionTitle
        eyebrow="Dashboard"
        title="Analyze a bug with uploaded code"
        description="Upload a ZIP codebase or a single supported code file, then let the 4-agent system inspect the issue, identify the likely bug, suggest a fix, and generate QA checks."
      />

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Card
          title="Bug analysis input"
          subtitle="Describe the issue and upload the relevant codebase."
          className="shadow-sm"
        >
          <form onSubmit={handleAnalyze} className="space-y-6">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Issue description
              </label>
              <textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Example: Login fails and the app crashes after entering wrong credentials."
                rows={7}
                className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-500 focus:ring-4 focus:ring-slate-200"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Upload codebase
              </label>

              <label className="group flex cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center transition hover:border-slate-500 hover:bg-slate-100">
                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-slate-700 shadow-sm">
                  <Upload size={24} />
                </div>
                <p className="text-sm font-semibold text-slate-800">
                  Click to upload ZIP or code file
                </p>
                <p className="mt-2 text-xs text-slate-500">
                  Supported: .zip, .py, .js, .jsx, .ts, .tsx, .json
                </p>

                <input
                  type="file"
                  accept=".zip,.py,.js,.jsx,.ts,.tsx,.json"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>

              {selectedFile && (
                <div className="mt-4 flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
                  <CheckCircle2 size={18} className="mt-0.5 shrink-0 text-emerald-600" />
                  <div>
                    <p className="text-sm font-medium text-emerald-800">Selected file</p>
                    <p className="text-sm text-emerald-700 break-all">{selectedFile.name}</p>
                  </div>
                </div>
              )}
            </div>

            {error && (
              <div className="flex items-start gap-3 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                <FileWarning size={18} className="mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Play size={16} />
              {loading ? 'Analyzing...' : 'Run analysis'}
            </button>
          </form>
        </Card>

        <div className="space-y-6">
          <Card title="Supported upload modes" subtitle="Use one of these input formats">
            <div className="space-y-3 text-sm text-slate-600">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="mb-2 flex items-center gap-2 text-slate-800">
                  <FolderArchive size={18} />
                  <p className="font-semibold">ZIP codebase</p>
                </div>
                <p>Best for a full project or multiple related files.</p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="mb-2 flex items-center gap-2 text-slate-800">
                  <FileCode2 size={18} />
                  <p className="font-semibold">Single code file</p>
                </div>
                <p>Best for testing one isolated bug in a single file.</p>
              </div>
            </div>
          </Card>

          <Card title="4-agent workflow">
            <div className="space-y-3 text-sm text-slate-600">
              <div className="rounded-xl bg-slate-50 p-3">
                <p className="font-medium text-slate-800">1. Issue Analyst</p>
                <p>Creates a structured bug summary.</p>
              </div>
              <div className="rounded-xl bg-slate-50 p-3">
                <p className="font-medium text-slate-800">2. Codebase Investigator</p>
                <p>Finds the most relevant file and suspicious code.</p>
              </div>
              <div className="rounded-xl bg-slate-50 p-3">
                <p className="font-medium text-slate-800">3. Fix Planner</p>
                <p>Suggests the direct fix and implementation steps.</p>
              </div>
              <div className="rounded-xl bg-slate-50 p-3">
                <p className="font-medium text-slate-800">4. QA Reviewer</p>
                <p>Creates test checks and regression risks.</p>
              </div>
            </div>
          </Card>

          {loading && <LoadingSpinner text="Uploading and analyzing code..." />}
        </div>
      </div>
    </div>
  )
}