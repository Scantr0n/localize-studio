import { useRef } from 'react'

export default function VideoFramePicker({ frameSrc, videoWidth, videoHeight, anchor, onChange }) {
  const imgRef = useRef(null)

  function handleClick(e) {
    const rect = imgRef.current.getBoundingClientRect()
    const clickX = e.clientX - rect.left
    const clickY = e.clientY - rect.top
    const x = Math.round((clickX / rect.width) * videoWidth)
    const y = Math.round((clickY / rect.height) * videoHeight)
    onChange({ x, y })
  }

  const markerStyle = anchor
    ? {
        left: `${(anchor.x / videoWidth) * 100}%`,
        top: `${(anchor.y / videoHeight) * 100}%`,
      }
    : null

  return (
    <div className="relative inline-block select-none">
      <img
        ref={imgRef}
        src={frameSrc}
        alt="frame preview"
        onClick={handleClick}
        className="rounded-lg border border-neutral-800 max-h-[480px] cursor-crosshair"
      />
      {markerStyle && (
        <div
          className="absolute w-4 h-4 -ml-2 -mt-2 rounded-full bg-indigo-500 border-2 border-white shadow-lg pointer-events-none"
          style={markerStyle}
        />
      )}
    </div>
  )
}
