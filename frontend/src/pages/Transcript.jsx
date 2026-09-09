import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useJob } from '../store/useJob'
import { api } from '../utils/api'
import JobStepper from '../components/JobStepper'
import SegmentEditor from '../components/SegmentEditor'

const LANGUAGES = [
  { code: 'auto', label: 'Auto-detect' },
  { code: 'en', label: 'English' },
  { code: 'zh', label: 'Chinese' },
  { code: 'tr', label: 'Turkish' },
  { code: 'ja', label: 'Japanese' },
  { code: 'ko', label: 'Korean' },
]

export default function Transcript() {
  const { job, refresh } = useJob()
  const navigate = useNavigate()
  const [language, setLanguage] = useState('auto')
  const [segments, setSegments] = useState(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const isTranscribed = job && ['transcribed', 'translating', 'translated', 'rendering', 'done'].includes(job.status)

  useEffect(() => {
    if (isTranscribed) {
      api.getTranscript(job.id).then((d) => setSegments(d.segments))
    }
  }, [isTranscribed, job?.id])

  if (!job) return <div className="p-6 text-neutral-500">Loading…</div>

  async function startTranscribe() {
    setError(null)
    try {
      await api.transcribe(job.id, language)
      await refresh()
    } catch (e) {
      setError(e.message)
    }
  }

  function updateSegment(idx, updated) {
    setSegments((segs) => segs.map((s, i) => (i === idx ? updated : s)))
  }

  function deleteSegment(idx) {
    setSegments((segs) => segs.filter((_, i) => i !== idx))
  }

  function addSegment() {
    const last = segments[segments.length - 1]
    const start = last ? last.end : 0
    setSegments((segs) => [
      ...segs,
      { id: Math.max(-1, ...segs.map((s) => s.id)) + 1, start, end: start + 1, text: '' },
    ])
  }

  async function saveAndContinue() {
    setSaving(true)
    setError(null)
    try {
      await api.updateTranscript(job.id, segments)
      navigate(`/jobs/${job.id}/translate`)
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <JobStepper jobId={job.id} current="transcript" />
      <div className="max-w-2xl mx-auto px-6 py-10">
        <h2 className="text-xl font-medium mb-1">Transcript</h2>
        <p className="text-neutral-500 text-sm mb-6">
          Whisper's first pass is a starting point, not gospel — fix any lines
          it got wrong before moving on. This matters more than it sounds like
          it should.
        </p>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {job.status === 'prepared' && (
          <div className="flex items-center gap-3">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-sm"
            >
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label}
                </option>
              ))}
            </select>
            <button
              onClick={startTranscribe}
              className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg text-sm font-medium"
            >
              Transcribe
            </button>
          </div>
        )}

        {job.status === 'transcribing' && (
          <p className="text-neutral-400">Transcribing… (large-v3, can take up to a minute on first run)</p>
        )}

        {isTranscribed && segments && (
          <div className="space-y-3">
            {segments.map((seg, i) => (
              <SegmentEditor
                key={seg.id}
                segment={seg}
                onChange={(updated) => updateSegment(i, updated)}
                onDelete={() => deleteSegment(i)}
              />
            ))}
            <button onClick={addSegment} className="text-sm text-indigo-400 hover:underline">
              + Add segment
            </button>
            <button
              onClick={saveAndContinue}
              disabled={saving}
              className="w-full bg-indigo-600 hover:bg-indigo-500 py-2.5 rounded-lg font-medium mt-4 disabled:opacity-50"
            >
              {saving ? 'Saving…' : 'Continue to Translate →'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
