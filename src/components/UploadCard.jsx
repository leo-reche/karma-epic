import { useRef, useState } from 'react'

export default function UploadCard({ file, onSelect }) {
  const input = useRef(null)
  const [dragging, setDragging] = useState(false)

  const select = (files) => {
    if (files.length) onSelect(files[0])
  }

  return (
    <section className="card">
      <h2>Upload your video</h2>
      <button
        type="button"
        className={dragging ? 'drop dragging' : 'drop'}
        onClick={() => input.current.click()}
        onDragOver={(event) => {
          event.preventDefault()
          setDragging(true)
        }}
        onDragLeave={(event) => {
          if (!event.currentTarget.contains(event.relatedTarget)) setDragging(false)
        }}
        onDrop={(event) => {
          event.preventDefault()
          setDragging(false)
          select(event.dataTransfer.files)
        }}
      >
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M12 15V3M7 8l5-5 5 5M4 15v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4" />
        </svg>
        <strong>{file ? file.name : 'Drop a video here'}</strong>
        <span className="hint">
          {file ? 'Click to choose another' : 'or click to browse. MP4, MOV, WebM'}
        </span>
      </button>
      <input
        ref={input}
        type="file"
        accept="video/*,.mkv"
        hidden
        onChange={(event) => {
          select(event.target.files)
          event.target.value = ''
        }}
      />
    </section>
  )
}
