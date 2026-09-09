import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../utils/api'

export default function Upload() {
  const navigate = useNavigate()
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  async function handleFile(file) {
    if (!file) return
    setUploading(true)
    setError(null)
    try {
      const job = await api.uploadVideo(file)
      navigate(`/jobs/${job.id}/prepare`)
    } catch (e) {
      setError(e.message)
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">
      <div className="max-w-xl w-full text-center">
        <h1 className="text-3xl font-semibold mb-2">Localize Studio</h1>
        <p className="text-neutral-500 mb-10">
          Upload a client's clip. Transcribe, translate, and burn on styled
          captions for their Chinese-market social accounts.
        </p>
        <div
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragging(false)
            handleFile(e.dataTransfer.files?.[0])
          }}
          onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl py-20 px-6 cursor-pointer transition-colors ${
            dragging ? 'border-indigo-500 bg-indigo-500/10' : 'border-neutral-800 hover:border-neutral-700'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept="video/*"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
          {uploading ? (
            <p className="text-neutral-400">Uploading…</p>
          ) : (
            <>
              <p className="text-neutral-300 mb-1">Drop a video here</p>
              <p className="text-neutral-600 text-sm">or click to browse</p>
            </>
          )}
        </div>
        {error && <p className="text-red-400 text-sm mt-4">{error}</p>}
      </div>
    </div>
  )
}
