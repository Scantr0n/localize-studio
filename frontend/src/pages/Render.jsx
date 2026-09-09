import { useEffect, useState } from 'react'
import { useJob } from '../store/useJob'
import { api } from '../utils/api'
import JobStepper from '../components/JobStepper'
import VideoFramePicker from '../components/VideoFramePicker'

function emptyTrack() {
  return { name: '', style_id: '', language: 'transcript', anchor: null, tagIds: {} }
}

export default function Render() {
  const { job, refresh } = useJob()
  const [styles, setStyles] = useState([])
  const [segments, setSegments] = useState([])
  const [translationLangs, setTranslationLangs] = useState([])
  const [draft, setDraft] = useState(emptyTrack())
  const [tracks, setTracks] = useState([])
  const [rendering, setRendering] = useState(false)
  const [error, setError] = useState(null)
  const [renders, setRenders] = useState([])

  useEffect(() => {
    if (!job) return
    api.getStyles(job.id).then((s) => {
      setStyles(s)
      if (s.length && !draft.style_id) setDraft((d) => ({ ...d, style_id: s[0].id }))
    })
    api.getTranscript(job.id).then((d) => setSegments(d.segments))
    api.getTranslations(job.id).then((all) => setTranslationLangs(Object.keys(all)))
    api.getRenders(job.id).then(setRenders)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [job?.id])

  if (!job) return <div className="p-6 text-neutral-500">Loading…</div>

  const selectedStyle = styles.find((s) => s.id === draft.style_id)

  function toggleTag(segId, text) {
    setDraft((d) => {
      const next = { ...d.tagIds }
      if (segId in next) delete next[segId]
      else next[segId] = text
      return { ...d, tagIds: next }
    })
  }

  function addTrack() {
    if (!draft.name || !draft.style_id) {
      setError('Track needs a name and a style.')
      return
    }
    if (selectedStyle?.needs_anchor && !draft.anchor) {
      setError('Click on the preview frame to place the tag anchor.')
      return
    }
    setError(null)
    const tags = Object.entries(draft.tagIds).map(([segment_id, text]) => ({
      segment_id: Number(segment_id),
      text,
    }))
    setTracks((t) => [...t, { ...draft, tags }])
    setDraft(emptyTrack())
  }

  function removeTrack(idx) {
    setTracks((t) => t.filter((_, i) => i !== idx))
  }

  async function renderAll() {
    setRendering(true)
    setError(null)
    try {
      await api.render(
        job.id,
        tracks.map(({ name, style_id, language, anchor, tags }) => ({
          name,
          style_id,
          language,
          anchor,
          tags,
        }))
      )
      let latest = await refresh()
      while (latest.status === 'rendering') {
        await new Promise((r) => setTimeout(r, 1500))
        latest = await refresh()
      }
      if (latest.status === 'error') {
        setError(latest.error)
      } else {
        setRenders(await api.getRenders(job.id))
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setRendering(false)
    }
  }

  return (
    <div>
      <JobStepper jobId={job.id} current="render" />
      <div className="max-w-3xl mx-auto px-6 py-10">
        <h2 className="text-xl font-medium mb-1">Style & Render</h2>
        <p className="text-neutral-500 text-sm mb-6">
          Build one or more caption tracks (e.g. a native-language version and
          a translated version), then render them all.
        </p>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {/* Track builder */}
        <div className="bg-neutral-900/60 border border-neutral-800 rounded-lg p-4 space-y-4 mb-6">
          <div className="flex gap-3 flex-wrap">
            <input
              placeholder="track name (e.g. track1_zh)"
              value={draft.name}
              onChange={(e) => setDraft({ ...draft, name: e.target.value })}
              className="bg-neutral-950 border border-neutral-700 rounded px-3 py-2 text-sm flex-1 min-w-[160px]"
            />
            <select
              value={draft.style_id}
              onChange={(e) => setDraft({ ...draft, style_id: e.target.value })}
              className="bg-neutral-950 border border-neutral-700 rounded px-3 py-2 text-sm"
            >
              {styles.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.display_name}
                </option>
              ))}
            </select>
            <select
              value={draft.language}
              onChange={(e) => setDraft({ ...draft, language: e.target.value })}
              className="bg-neutral-950 border border-neutral-700 rounded px-3 py-2 text-sm"
            >
              <option value="transcript">Original transcript language</option>
              {translationLangs.map((l) => (
                <option key={l} value={l}>
                  {l} (translated)
                </option>
              ))}
            </select>
          </div>

          {selectedStyle?.needs_anchor && (
            <div>
              <p className="text-xs text-neutral-500 mb-2">
                Click on the frame where the small name/greeting tag should appear:
              </p>
              <VideoFramePicker
                frameSrc={api.frameUrl(job.id)}
                videoWidth={job.working_video?.width || 1080}
                videoHeight={job.working_video?.height || 1920}
                anchor={draft.anchor}
                onChange={(anchor) => setDraft({ ...draft, anchor })}
              />
            </div>
          )}

          <div>
            <p className="text-xs text-neutral-500 mb-2">
              Optionally mark segments to show as a small tag near the anchor (e.g. a greeting or name):
            </p>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {segments.map((seg) => (
                <label key={seg.id} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={seg.id in draft.tagIds}
                    onChange={() => toggleTag(seg.id, seg.text)}
                  />
                  <span className="text-neutral-500 w-16 shrink-0">{seg.start.toFixed(1)}s</span>
                  {seg.id in draft.tagIds ? (
                    <input
                      value={draft.tagIds[seg.id]}
                      onChange={(e) =>
                        setDraft((d) => ({ ...d, tagIds: { ...d.tagIds, [seg.id]: e.target.value } }))
                      }
                      className="bg-neutral-950 border border-neutral-700 rounded px-2 py-1 text-xs flex-1"
                    />
                  ) : (
                    <span className="text-neutral-600 truncate">{seg.text}</span>
                  )}
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={addTrack}
            className="bg-neutral-800 hover:bg-neutral-700 text-sm px-4 py-2 rounded-lg"
          >
            + Add track
          </button>
        </div>

        {/* Track list */}
        {tracks.length > 0 && (
          <div className="space-y-2 mb-6">
            {tracks.map((t, i) => (
              <div
                key={i}
                className="flex items-center justify-between bg-neutral-900/40 border border-neutral-800 rounded-lg px-4 py-2 text-sm"
              >
                <span>
                  <strong>{t.name}</strong> — {t.style_id} — {t.language}
                  {t.tags.length > 0 && ` — ${t.tags.length} tag${t.tags.length > 1 ? 's' : ''}`}
                </span>
                <button onClick={() => removeTrack(i)} className="text-neutral-600 hover:text-red-400">
                  ✕
                </button>
              </div>
            ))}
            <button
              onClick={renderAll}
              disabled={rendering}
              className="w-full bg-indigo-600 hover:bg-indigo-500 py-2.5 rounded-lg font-medium disabled:opacity-50"
            >
              {rendering ? 'Rendering…' : `Render ${tracks.length} track${tracks.length > 1 ? 's' : ''}`}
            </button>
          </div>
        )}

        {/* Completed renders */}
        {renders.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm text-neutral-400 mt-8 mb-2">Completed renders</h3>
            {renders.map((r) => (
              <div key={r.render_id} className="bg-neutral-900/60 border border-neutral-800 rounded-lg p-3">
                <p className="text-sm mb-2">{r.track_name}</p>
                <video
                  src={api.downloadUrl(job.id, r.file)}
                  controls
                  className="max-h-64 rounded"
                />
                <a
                  href={api.downloadUrl(job.id, r.file)}
                  download
                  className="block mt-2 text-indigo-400 text-sm hover:underline"
                >
                  Download
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
