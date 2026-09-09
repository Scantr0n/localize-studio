import { useNavigate } from 'react-router-dom'

const STEPS = [
  { key: 'prepare', label: 'Prepare' },
  { key: 'transcript', label: 'Transcript' },
  { key: 'translate', label: 'Translate' },
  { key: 'render', label: 'Style & Render' },
]

export default function JobStepper({ jobId, current }) {
  const navigate = useNavigate()
  const currentIdx = STEPS.findIndex((s) => s.key === current)

  return (
    <div className="flex items-center gap-2 px-6 py-4 border-b border-neutral-800">
      <button
        onClick={() => navigate('/')}
        className="text-sm text-neutral-500 hover:text-neutral-300 mr-4"
      >
        ← New video
      </button>
      {STEPS.map((step, i) => (
        <div key={step.key} className="flex items-center gap-2">
          {i > 0 && <div className="w-6 h-px bg-neutral-800" />}
          <button
            onClick={() => i <= currentIdx && navigate(`/jobs/${jobId}/${step.key}`)}
            disabled={i > currentIdx}
            className={`text-sm px-3 py-1 rounded-full transition-colors ${
              i === currentIdx
                ? 'bg-indigo-600 text-white'
                : i < currentIdx
                  ? 'text-indigo-400 hover:bg-neutral-800'
                  : 'text-neutral-600 cursor-not-allowed'
            }`}
          >
            {step.label}
          </button>
        </div>
      ))}
    </div>
  )
}
