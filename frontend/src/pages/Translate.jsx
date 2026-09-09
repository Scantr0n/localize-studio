import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useJob } from '../store/useJob'
import { api } from '../utils/api'
import JobStepper from '../components/JobStepper'

const LANGUAGES = [
  { code: 'zh', label: 'Chinese' },
  { code: 'en', label: 'English' },
  { code: 'tr', label: 'Turkish' },
  { code: 'ja', label: 'Japanese' },
  { code: 'ko', label: 'Korean' },
]

export default function Translate() {
  const { job, refresh } = useJob()
  const navigate = useNavigate()
  const [targetLang, setTargetLang] = useState('zh')
  const [segments, setSegments] = useState([])
  const [translations, setTranslations] = useState({})
  const [generating, setGenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!job) return
    api.getTranscript(job.id).then((d) => setSegments(d.segments))
  }, [job?.id])

  useEffect(() => {
    if (!job) return
    api.getTranslations(job.id).then((all) => setTranslations(all[targetLang] || {}))
  }, [job?.id, targetLang, job?.status])

  if (!job) return <div className="p-6 text-neutral-500">Loading…</div>

  async function generate() {
    setGenerating(true)
    setError(null)
    try {
      await api.translate(job.id, targetLang)
      // poll until translating finishes
      let latest = await refresh()
      while (latest.status === 'translating') {
        await new Promise((r) => setTimeout(r, 1500))
        latest = await refresh()
      }
      if (latest.status === 'error') {
        setError(latest.error)
      } else {
        const all = await api.getTranslations(job.id)
        setTranslations(all[targetLang] || {})
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setGenerating(false)
    }
  }

  function updateLine(id, value) {
    setTranslations((t) => ({ ...t, [id]: value }))
  }

  async function saveAndContinue() {
    setSaving(true)
    setError(null)
    try {
      await api.updateTranslations(job.id, targetLang, translations)
      navigate(`/jobs/${job.id}/render`)
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const hasTranslations = Object.keys(translations).length > 0

  return (
    <div>
      <JobStepper jobId={job.id} current="translate" />
      <div className="max-w-2xl mx-auto px-6 py-10">
        <h2 className="text-xl font-medium mb-1">Translate</h2>
        <p className="text-neutral-500 text-sm mb-6">
          AI-suggested translations, edited by you before anything gets
          burned onto the video.
        </p>

        <div className="flex items-center gap-3 mb-6">
          <select
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
            className="bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-sm"
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.label}
              </option>
            ))}
          </select>
          <button
            onClick={generate}
            disabled={generating}
            className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
          >
            {generating ? 'Translating…' : hasTranslations ? 'Regenerate all' : 'Generate translations'}
          </button>
        </div>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {hasTranslations && (
          <div className="space-y-3">
            {segments.map((seg) => (
              <div key={seg.id} className="bg-neutral-900/60 border border-neutral-800 rounded-lg p-3">
                <p className="text-neutral-500 text-xs mb-2">{seg.text}</p>
                <textarea
                  value={translations[seg.id] ?? ''}
                  onChange={(e) => updateLine(seg.id, e.target.value)}
                  rows={2}
                  className="w-full bg-neutral-950 border border-neutral-700 rounded px-3 py-2 text-sm text-neutral-100 resize-none"
                />
              </div>
            ))}
            <button
              onClick={saveAndContinue}
              disabled={saving}
              className="w-full bg-indigo-600 hover:bg-indigo-500 py-2.5 rounded-lg font-medium mt-4 disabled:opacity-50"
            >
              {saving ? 'Saving…' : 'Continue to Style & Render →'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
