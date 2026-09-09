import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useJob } from '../store/useJob'
import { api } from '../utils/api'
import JobStepper from '../components/JobStepper'

export default function Prepare() {
  const { job, refresh } = useJob()
  const navigate = useNavigate()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [showOverride, setShowOverride] = useState(false)
  const [override, setOverride] = useState(null)
  const [triggered, setTriggered] = useState(false)

  useEffect(() => {
    if (job && job.status === 'uploaded' && !triggered) {
      setTriggered(true)
      setBusy(true)
      api
        .prepare(job.id)
        .then(() => refresh())
        .catch((e) => setError(e.message))
        .finally(() => setBusy(false))
    }
  }, [job, triggered, refresh])

  if (!job) return <div className="p-6 text-neutral-500">Loading…</div>

  const isPrepared = job.status === 'prepared'

  async function rerunWithOverride() {
    setBusy(true)
    setError(null)
    try {
      await api.prepare(job.id, override)
      await refresh()
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <JobStepper jobId={job.id} current="prepare" />
      <div className="max-w-2xl mx-auto px-6 py-10">
        <h2 className="text-xl font-medium mb-1">Prepare video</h2>
        <p className="text-neutral-500 text-sm mb-6">
          Detecting letterboxing and cropping to a clean vertical frame.
        </p>

        {busy && <p className="text-neutral-400">Working…</p>}
        {error && <p className="text-red-400 text-sm">{error}</p>}

        {isPrepared && (
          <div className="space-y-4">
            <img
              src={api.frameUrl(job.id) + `?t=${job.updated_at}`}
              alt="preview frame"
              className="rounded-lg border border-neutral-800 max-h-[480px] mx-auto"
            />
            <div className="text-sm text-neutral-400">
              Crop: x={job.crop.x} y={job.crop.y} w={job.crop.w} h={job.crop.h}
              {job.crop.auto_detected ? ' (auto-detected)' : ' (manual)'}
            </div>

            <button
              onClick={() => {
                setOverride({ ...job.crop })
                setShowOverride((v) => !v)
              }}
              className="text-sm text-indigo-400 hover:underline"
            >
              {showOverride ? 'Hide manual override' : "Crop looks wrong? Adjust it"}
            </button>

            {showOverride && override && (
              <div className="flex gap-3 items-end flex-wrap">
                {['x', 'y', 'w', 'h'].map((k) => (
                  <label key={k} className="text-xs text-neutral-500">
                    {k}
                    <input
                      type="number"
                      value={override[k]}
                      onChange={(e) => setOverride({ ...override, [k]: Number(e.target.value) })}
                      className="block w-24 mt-1 bg-neutral-900 border border-neutral-700 rounded px-2 py-1 text-neutral-200"
                    />
                  </label>
                ))}
                <button
                  onClick={rerunWithOverride}
                  className="bg-neutral-800 hover:bg-neutral-700 text-sm px-3 py-1.5 rounded"
                >
                  Re-crop
                </button>
              </div>
            )}

            <button
              onClick={() => navigate(`/jobs/${job.id}/transcript`)}
              className="w-full bg-indigo-600 hover:bg-indigo-500 py-2.5 rounded-lg font-medium mt-4"
            >
              Continue to Transcript →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
