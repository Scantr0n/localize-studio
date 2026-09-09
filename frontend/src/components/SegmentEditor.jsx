export default function SegmentEditor({ segment, onChange, onDelete }) {
  return (
    <div className="flex gap-3 items-start bg-neutral-900/60 border border-neutral-800 rounded-lg p-3">
      <div className="flex flex-col gap-1 shrink-0">
        <input
          type="number"
          step="0.01"
          value={segment.start}
          onChange={(e) => onChange({ ...segment, start: Number(e.target.value) })}
          className="w-20 bg-neutral-950 border border-neutral-700 rounded px-2 py-1 text-xs text-neutral-300"
          title="start (s)"
        />
        <input
          type="number"
          step="0.01"
          value={segment.end}
          onChange={(e) => onChange({ ...segment, end: Number(e.target.value) })}
          className="w-20 bg-neutral-950 border border-neutral-700 rounded px-2 py-1 text-xs text-neutral-300"
          title="end (s)"
        />
      </div>
      <textarea
        value={segment.text}
        onChange={(e) => onChange({ ...segment, text: e.target.value })}
        rows={2}
        className="flex-1 bg-neutral-950 border border-neutral-700 rounded px-3 py-2 text-sm text-neutral-100 resize-none"
      />
      <button
        onClick={onDelete}
        className="text-neutral-600 hover:text-red-400 text-sm px-2 py-1"
        title="delete segment"
      >
        ✕
      </button>
    </div>
  )
}
