import { useEffect, useState } from 'react'
import ResultCard from './components/ResultCard.jsx'
import UploadCard from './components/UploadCard.jsx'
import { processVideo } from './processVideo.js'

const isVideo = (file) => file.type.startsWith('video/') || /\.(mp4|mov|webm|mkv|avi|m4v)$/i.test(file.name)

export default function App() {
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [markdown, setMarkdown] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const ignore = (event) => event.preventDefault()
    window.addEventListener('dragover', ignore)
    window.addEventListener('drop', ignore)
    return () => {
      window.removeEventListener('dragover', ignore)
      window.removeEventListener('drop', ignore)
    }
  }, [])

  useEffect(() => {
    if (!file) return
    const controller = new AbortController()
    processVideo(file, { onProgress: setProgress, signal: controller.signal })
      .then(setMarkdown)
      .catch(() => {
        if (controller.signal.aborted) return
        setFile(null)
        setError('Something went wrong. Please try again.')
      })
    return () => controller.abort()
  }, [file])

  const selectFile = (next) => {
    if (!isVideo(next)) {
      setError('Please choose a video file (MP4, MOV or WebM).')
      return
    }
    setError('')
    setProgress(0)
    setMarkdown(null)
    setFile(next)
  }

  return (
    <main>
      <h1>
        The <b>Karma-LLMifier</b>
      </h1>
      <p className="intro">Turn a video into a text file you can ask your AI about.</p>
      <div className="flow">
        <UploadCard file={file} onSelect={selectFile} />
        <svg className="arrow" width="72" height="16" viewBox="0 0 72 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M2 8h66M61 2l8 6-8 6" />
        </svg>
        <ResultCard file={file} progress={progress} markdown={markdown} />
      </div>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      <p className="notice">Preview version: processing is not connected yet, so the download is a sample.</p>
    </main>
  )
}
